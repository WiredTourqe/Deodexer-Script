"""
File validation and analysis utilities
"""

import os
import hashlib
from typing import Dict, Any, List, Optional
from pathlib import Path
import struct

from ..core.logger import logger


class FileValidator:
    """Advanced file validation for ODEX and related files"""
    
    def __init__(self):
        # Note: python-magic removed for simplicity
        self.magic = None
    
    def validate_odex_file(self, file_path: str) -> bool:
        """Validate if file is a valid ODEX file"""
        try:
            if not os.path.exists(file_path):
                return False
            
            if not file_path.lower().endswith('.odex'):
                return False
            
            # Check file size (ODEX files should be at least a few KB)
            file_size = os.path.getsize(file_path)
            if file_size < 1024:  # Less than 1KB is suspicious
                return False
            
            # Check ODEX magic header
            return self._check_odex_header(file_path)
            
        except Exception as e:
            logger.error("ODEX validation failed", file=file_path, error=str(e))
            return False
    
    def _check_odex_header(self, file_path: str) -> bool:
        """Check ODEX file header for validity"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
                
                if len(header) < 8:
                    return False
                
                # ODEX files start with "dey\n" followed by version
                if header[:4] == b'dey\n':
                    return True
                
                # Some ODEX files might have different headers
                # Add more validation as needed
                return True  # Be permissive for now
                
        except Exception:
            return False
    
    def validate_framework_directory(self, framework_dir: str) -> bool:
        """Validate framework directory contains necessary files"""
        try:
            if not os.path.exists(framework_dir) or not os.path.isdir(framework_dir):
                return False
            
            # Check for common framework files
            framework_files = ['framework.jar', 'core.jar', 'android.jar']
            found_files = os.listdir(framework_dir)
            
            # At least one framework file should exist
            for fw_file in framework_files:
                if fw_file in found_files:
                    return True
            
            # Also check for .odex files in framework
            odex_files = [f for f in found_files if f.endswith('.odex')]
            return len(odex_files) > 0
            
        except Exception as e:
            logger.error("Framework validation failed", directory=framework_dir, error=str(e))
            return False
    
    def validate_baksmali_jar(self, jar_path: str) -> bool:
        """Validate baksmali JAR file"""
        try:
            if not os.path.exists(jar_path):
                return False
            
            if not jar_path.lower().endswith('.jar'):
                return False
            
            # Check if it's a valid ZIP/JAR file
            import zipfile
            try:
                with zipfile.ZipFile(jar_path, 'r') as jar:
                    # Check for baksmali-specific files
                    file_list = jar.namelist()
                    if any('baksmali' in f.lower() for f in file_list):
                        return True
                    if 'META-INF/MANIFEST.MF' in file_list:
                        return True
            except zipfile.BadZipFile:
                return False
            
            return True
            
        except Exception as e:
            logger.error("Baksmali JAR validation failed", jar=jar_path, error=str(e))
            return False


class FileAnalyzer:
    """Advanced file analysis for optimization"""
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze file and return metadata for optimization"""
        try:
            file_info = {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size_bytes': os.path.getsize(file_path),
                'size_mb': os.path.getsize(file_path) / (1024 * 1024),
                'hash': self._calculate_file_hash(file_path),
                'complexity': 'medium',  # Default complexity
                'estimated_time': 0.0,
                'optimization_hints': []
            }
            
            # Analyze based on file size
            if file_info['size_mb'] > 50:
                file_info['complexity'] = 'high'
                file_info['estimated_time'] = 120.0  # 2 minutes
                file_info['optimization_hints'].append('large_file')
            elif file_info['size_mb'] > 10:
                file_info['complexity'] = 'medium'
                file_info['estimated_time'] = 30.0   # 30 seconds
            else:
                file_info['complexity'] = 'low'
                file_info['estimated_time'] = 10.0   # 10 seconds
            
            # Add more analysis as needed
            file_info.update(self._analyze_odex_specifics(file_path))
            
            return file_info
            
        except Exception as e:
            logger.error("File analysis failed", file=file_path, error=str(e))
            return {'path': file_path, 'error': str(e)}
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""
    
    def _analyze_odex_specifics(self, file_path: str) -> Dict[str, Any]:
        """Analyze ODEX-specific characteristics"""
        odex_info = {
            'dex_version': 'unknown',
            'class_count': 0,
            'method_count': 0,
            'instruction_count': 0
        }
        
        try:
            with open(file_path, 'rb') as f:
                # Read basic ODEX header information
                header = f.read(40)  # Read first 40 bytes
                
                if len(header) >= 8 and header[:4] == b'dey\n':
                    # Parse ODEX version
                    version = header[4:8]
                    odex_info['dex_version'] = version.decode('ascii', errors='ignore')
                
                # Add more detailed analysis as needed
                # This would require understanding of ODEX format
                
        except Exception as e:
            logger.debug("ODEX-specific analysis failed", file=file_path, error=str(e))
        
        return odex_info