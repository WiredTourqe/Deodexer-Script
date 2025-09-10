"""
Performance monitoring utilities
"""

import time
import psutil
import threading
from typing import Dict, Any, List, Callable, Optional
from collections import defaultdict, deque
from datetime import datetime

from ..core.logger import logger


class PerformanceMonitor:
    """Advanced performance monitoring and metrics collection"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.operation_metrics = defaultdict(lambda: deque(maxlen=history_size))
        self.system_metrics = deque(maxlen=history_size)
        self.monitoring_active = False
        self.monitoring_thread = None
        self._start_monitoring()
    
    def _start_monitoring(self) -> None:
        """Start background system monitoring"""
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitoring_thread.start()
    
    def _monitor_system(self) -> None:
        """Background system monitoring loop"""
        while self.monitoring_active:
            try:
                metrics = self._collect_system_metrics()
                self.system_metrics.append(metrics)
                time.sleep(30)  # Collect every 30 seconds
            except Exception as e:
                logger.error("System monitoring error", error=str(e))
                time.sleep(60)  # Wait longer on error
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'timestamp': datetime.now(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / (1024**3),
                'memory_total_gb': memory.total / (1024**3),
                'disk_percent': disk.percent,
                'disk_used_gb': disk.used / (1024**3),
                'disk_total_gb': disk.total / (1024**3)
            }
        except Exception as e:
            logger.error("Failed to collect system metrics", error=str(e))
            return {
                'timestamp': datetime.now(),
                'error': str(e)
            }
    
    def log_operation(self, operation: str, duration: float, file_size: int = 0, **kwargs) -> None:
        """Log operation performance metrics"""
        try:
            metrics = {
                'timestamp': datetime.now(),
                'operation': operation,
                'duration': duration,
                'file_size': file_size,
                'throughput_mb_s': (file_size / (1024 * 1024)) / duration if duration > 0 else 0,
                **kwargs
            }
            
            self.operation_metrics[operation].append(metrics)
            
            logger.info("Performance metric recorded", 
                       operation=operation, 
                       duration=duration,
                       file_size_mb=file_size / (1024 * 1024) if file_size > 0 else 0)
            
        except Exception as e:
            logger.error("Failed to log operation metrics", error=str(e))
    
    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """Get statistics for a specific operation"""
        try:
            metrics = list(self.operation_metrics[operation])
            if not metrics:
                return {'operation': operation, 'count': 0}
            
            durations = [m['duration'] for m in metrics]
            throughputs = [m['throughput_mb_s'] for m in metrics if m['throughput_mb_s'] > 0]
            
            stats = {
                'operation': operation,
                'count': len(metrics),
                'avg_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'total_duration': sum(durations),
                'last_operation': metrics[-1]['timestamp'].isoformat()
            }
            
            if throughputs:
                stats.update({
                    'avg_throughput_mb_s': sum(throughputs) / len(throughputs),
                    'max_throughput_mb_s': max(throughputs)
                })
            
            return stats
            
        except Exception as e:
            logger.error("Failed to calculate operation stats", error=str(e))
            return {'operation': operation, 'error': str(e)}
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        try:
            if not self.system_metrics:
                return {'error': 'No system metrics available'}
            
            recent_metrics = list(self.system_metrics)[-10:]  # Last 10 measurements
            
            cpu_values = [m['cpu_percent'] for m in recent_metrics if 'cpu_percent' in m]
            memory_values = [m['memory_percent'] for m in recent_metrics if 'memory_percent' in m]
            
            if not cpu_values or not memory_values:
                return {'error': 'Insufficient metrics data'}
            
            stats = {
                'current_cpu_percent': cpu_values[-1] if cpu_values else 0,
                'avg_cpu_percent': sum(cpu_values) / len(cpu_values),
                'max_cpu_percent': max(cpu_values),
                'current_memory_percent': memory_values[-1] if memory_values else 0,
                'avg_memory_percent': sum(memory_values) / len(memory_values),
                'max_memory_percent': max(memory_values),
                'measurements_count': len(recent_metrics),
                'last_update': recent_metrics[-1]['timestamp'].isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error("Failed to calculate system stats", error=str(e))
            return {'error': str(e)}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        try:
            summary = {
                'system': self.get_system_stats(),
                'operations': {},
                'total_operations': 0,
                'monitoring_active': self.monitoring_active
            }
            
            for operation in self.operation_metrics.keys():
                operation_stats = self.get_operation_stats(operation)
                summary['operations'][operation] = operation_stats
                summary['total_operations'] += operation_stats.get('count', 0)
            
            return summary
            
        except Exception as e:
            logger.error("Failed to generate performance summary", error=str(e))
            return {'error': str(e)}
    
    def reset_metrics(self) -> None:
        """Reset all collected metrics"""
        try:
            self.operation_metrics.clear()
            self.system_metrics.clear()
            logger.info("Performance metrics reset")
        except Exception as e:
            logger.error("Failed to reset metrics", error=str(e))
    
    def stop_monitoring(self) -> None:
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        logger.info("Performance monitoring stopped")


class OperationTimer:
    """Context manager for timing operations"""
    
    def __init__(self, operation_name: str, monitor: PerformanceMonitor, **kwargs):
        self.operation_name = operation_name
        self.monitor = monitor
        self.kwargs = kwargs
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        # Log the operation
        self.monitor.log_operation(
            self.operation_name, 
            duration, 
            **self.kwargs
        )
        
        return False  # Don't suppress exceptions