"""
Advanced Deodexer Engine with enhanced capabilities
"""

import os
import subprocess
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Callable, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import time
import hashlib
import json
from datetime import datetime

from .config import config
from .logger import logger
from ..database.models import DeodexingJob, JobStatus
from ..utils.file_utils import FileValidator, FileAnalyzer
from ..utils.performance import PerformanceMonitor
from ..ml.optimizer import DeodexingOptimizer


class DeodexingStatus(Enum):
    """Status enumeration for deodexing operations"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DeodexingResult:
    """Result container for deodexing operations"""
    file_path: str
    status: DeodexingStatus
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    duration: float = 0.0
    file_size: int = 0
    metadata: Dict[str, Any] = None


class DeodexerEngine:
    """Advanced deodexing engine with comprehensive features"""
    
    def __init__(self):
        self.baksmali_jar = self._find_baksmali_jar()
        self.performance_monitor = PerformanceMonitor()
        self.optimizer = DeodexingOptimizer()
        self.file_validator = FileValidator()
        self.file_analyzer = FileAnalyzer()
        self._job_callbacks: Dict[str, List[Callable]] = {}
        self._active_jobs: Dict[str, DeodexingJob] = {}
        
        # Initialize Java environment check
        self._check_prerequisites()
    
    def _find_baksmali_jar(self) -> Optional[str]:
        """Automatically locate baksmali JAR file"""
        search_paths = [
            config.get('deodexing.baksmali_jar_path'),
            './baksmali.jar',
            '/usr/local/bin/baksmali.jar',
            os.path.expanduser('~/tools/baksmali.jar'),
            './tools/baksmali.jar'
        ]
        
        for path in search_paths:
            if path and os.path.isfile(path):
                logger.info("Found baksmali JAR", path=path)
                return path
        
        logger.warning("Baksmali JAR not found in standard locations")
        return None
    
    def _check_prerequisites(self) -> bool:
        """Check system prerequisites for deodexing"""
        try:
            # Check Java
            result = subprocess.run(
                ["java", "-version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode != 0:
                raise RuntimeError("Java not found")
            
            logger.info("Java environment verified")
            
            # Check baksmali availability
            if not self.baksmali_jar:
                logger.warning("Baksmali JAR not configured")
                return False
            
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.error("Prerequisites check failed", error=str(e))
            return False
    
    def set_baksmali_jar(self, jar_path: str) -> bool:
        """Set baksmali JAR path with validation"""
        if not os.path.isfile(jar_path):
            logger.error("Baksmali JAR file not found", path=jar_path)
            return False
        
        self.baksmali_jar = jar_path
        logger.info("Baksmali JAR path updated", path=jar_path)
        return True
    
    async def deodex_file_async(
        self, 
        odex_file: str, 
        framework_dir: str,
        output_dir: str,
        api_level: int = None,
        job_id: str = None
    ) -> DeodexingResult:
        """Asynchronously deodex a single file with comprehensive monitoring"""
        
        start_time = time.time()
        api_level = api_level or config.get('deodexing.default_api_level', 29)
        
        # Validate inputs
        if not self.file_validator.validate_odex_file(odex_file):
            return DeodexingResult(
                file_path=odex_file,
                status=DeodexingStatus.FAILED,
                error_message="Invalid ODEX file format"
            )
        
        # Analyze file for optimization
        file_info = self.file_analyzer.analyze_file(odex_file)
        optimized_params = self.optimizer.optimize_parameters(file_info)
        
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate output path
            output_file_path = os.path.join(
                output_dir, 
                os.path.splitext(os.path.basename(odex_file))[0]
            )
            
            # Build command with optimized parameters
            command = [
                "java", "-jar", self.baksmali_jar,
                "deodex",
                "-a", str(api_level),
                "-d", framework_dir,
                "-o", output_file_path,
                odex_file
            ]
            
            # Add optimization flags
            command.extend(optimized_params.get('baksmali_flags', []))
            
            logger.info("Starting deodexing", 
                       file=odex_file, 
                       api_level=api_level,
                       job_id=job_id)
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            duration = time.time() - start_time
            
            if process.returncode == 0:
                # Success
                file_size = os.path.getsize(odex_file)
                
                result = DeodexingResult(
                    file_path=odex_file,
                    status=DeodexingStatus.COMPLETED,
                    output_path=output_file_path,
                    duration=duration,
                    file_size=file_size,
                    metadata={
                        'api_level': api_level,
                        'command': ' '.join(command),
                        'stdout': stdout.decode('utf-8', errors='ignore'),
                        'optimization_applied': bool(optimized_params)
                    }
                )
                
                logger.info("Deodexing completed successfully", 
                           file=odex_file, 
                           duration=duration,
                           job_id=job_id)
                
                # Log performance metrics
                self.performance_monitor.log_operation(
                    'deodex_file', duration, file_size
                )
                
                return result
            else:
                # Failure
                error_message = stderr.decode('utf-8', errors='ignore')
                
                logger.error("Deodexing failed", 
                           file=odex_file, 
                           error=error_message,
                           job_id=job_id)
                
                return DeodexingResult(
                    file_path=odex_file,
                    status=DeodexingStatus.FAILED,
                    error_message=error_message,
                    duration=duration
                )
                
        except Exception as e:
            duration = time.time() - start_time
            logger.error("Deodexing exception", 
                        file=odex_file, 
                        error=str(e),
                        job_id=job_id)
            
            return DeodexingResult(
                file_path=odex_file,
                status=DeodexingStatus.FAILED,
                error_message=str(e),
                duration=duration
            )
    
    async def deodex_batch_async(
        self,
        input_dir: str,
        framework_dir: str,
        output_dir: str,
        api_level: int = None,
        max_workers: int = None,
        progress_callback: Callable[[Dict[str, Any]], None] = None
    ) -> List[DeodexingResult]:
        """Asynchronously deodex multiple files with progress tracking"""
        
        max_workers = max_workers or config.get('deodexing.max_workers', 4)
        api_level = api_level or config.get('deodexing.default_api_level', 29)
        
        # Find all ODEX files
        odex_files = self._find_odex_files(input_dir)
        total_files = len(odex_files)
        
        if total_files == 0:
            logger.warning("No ODEX files found", directory=input_dir)
            return []
        
        logger.info("Starting batch deodexing", 
                   total_files=total_files, 
                   max_workers=max_workers)
        
        results = []
        completed = 0
        
        # Create semaphore to limit concurrent operations
        semaphore = asyncio.Semaphore(max_workers)
        
        async def process_file(odex_file: str) -> DeodexingResult:
            async with semaphore:
                relative_path = os.path.relpath(os.path.dirname(odex_file), input_dir)
                file_output_dir = os.path.join(output_dir, relative_path)
                
                result = await self.deodex_file_async(
                    odex_file, framework_dir, file_output_dir, api_level
                )
                
                nonlocal completed
                completed += 1
                
                # Progress callback
                if progress_callback:
                    progress_callback({
                        'completed': completed,
                        'total': total_files,
                        'current_file': odex_file,
                        'result': result
                    })
                
                return result
        
        # Process all files concurrently
        tasks = [process_file(odex_file) for odex_file in odex_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error("Task failed", file=odex_files[i], error=str(result))
                valid_results.append(DeodexingResult(
                    file_path=odex_files[i],
                    status=DeodexingStatus.FAILED,
                    error_message=str(result)
                ))
            else:
                valid_results.append(result)
        
        # Log summary
        successful = sum(1 for r in valid_results if r.status == DeodexingStatus.COMPLETED)
        failed = sum(1 for r in valid_results if r.status == DeodexingStatus.FAILED)
        
        logger.info("Batch deodexing completed", 
                   total=total_files, 
                   successful=successful, 
                   failed=failed)
        
        return valid_results
    
    def _find_odex_files(self, directory: str) -> List[str]:
        """Recursively find all ODEX files in directory"""
        odex_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.odex'):
                    odex_files.append(os.path.join(root, file))
        return odex_files
    
    def generate_report(self, results: List[DeodexingResult]) -> Dict[str, Any]:
        """Generate comprehensive deodexing report"""
        total_files = len(results)
        successful = sum(1 for r in results if r.status == DeodexingStatus.COMPLETED)
        failed = sum(1 for r in results if r.status == DeodexingStatus.FAILED)
        
        total_duration = sum(r.duration for r in results)
        total_size = sum(r.file_size for r in results if r.file_size > 0)
        
        report = {
            'summary': {
                'total_files': total_files,
                'successful': successful,
                'failed': failed,
                'success_rate': (successful / total_files * 100) if total_files > 0 else 0,
                'total_duration': total_duration,
                'total_size_mb': total_size / (1024 * 1024),
                'average_duration': total_duration / total_files if total_files > 0 else 0
            },
            'results': [
                {
                    'file': r.file_path,
                    'status': r.status.value,
                    'output_path': r.output_path,
                    'duration': r.duration,
                    'error': r.error_message
                }
                for r in results
            ],
            'errors': [
                {'file': r.file_path, 'error': r.error_message}
                for r in results if r.status == DeodexingStatus.FAILED
            ],
            'generated_at': datetime.now().isoformat()
        }
        
        return report
    
    def export_report(self, results: List[DeodexingResult], format: str = 'json') -> str:
        """Export deodexing report in various formats"""
        report = self.generate_report(results)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format.lower() == 'json':
            filename = f"deodexing_report_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
        elif format.lower() == 'csv':
            import csv
            filename = f"deodexing_report_{timestamp}.csv"
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['file', 'status', 'duration', 'error'])
                writer.writeheader()
                for result in report['results']:
                    writer.writerow(result)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        logger.info("Report exported", filename=filename, format=format)
        return filename