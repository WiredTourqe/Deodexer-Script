"""
Simplified logging system for Deodexer Pro
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from .config import config


class SimpleLogger:
    """Simplified logging system using standard Python logging"""
    
    def __init__(self, name: str = "deodexer_pro"):
        self.name = name
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup comprehensive logging configuration"""
        log_level = config.get('logging.level', 'INFO')
        log_file = config.get('logging.file', 'logs/deodexer_pro.log')
        max_size = config.get('logging.max_size', 10485760)  # 10MB
        backup_count = config.get('logging.backup_count', 5)
        
        # Create logs directory
        try:
            log_dir = Path(log_file).parent
            log_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            log_file = 'deodexer_pro.log'  # Fallback to current directory
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler with rotation
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            
            # Detailed formatter for file
            detailed_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(file_handler)
        except Exception:
            pass  # Skip file logging if there are permission issues
        
        # Add console handler
        root_logger.addHandler(console_handler)
        
        # Setup application logger
        self.logger = logging.getLogger(self.name)
    
    def get_logger(self, name: Optional[str] = None):
        """Get a logger instance"""
        logger_name = name or self.name
        return logging.getLogger(logger_name)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log_with_context(self.logger.info, message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log_with_context(self.logger.debug, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log_with_context(self.logger.warning, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log_with_context(self.logger.error, message, **kwargs)
    
    def _log_with_context(self, log_func, message: str, **kwargs):
        """Log message with context"""
        if kwargs:
            context_str = " | ".join(f"{k}={v}" for k, v in kwargs.items())
            full_message = f"{message} | {context_str}"
        else:
            full_message = message
        log_func(full_message)


class Logger:
    """Compatibility wrapper for the simplified logger"""
    
    def __init__(self, name: str = "deodexer_pro"):
        self.simple_logger = SimpleLogger(name)
    
    def get_logger(self, name: Optional[str] = None):
        """Get a logger instance"""
        return self.simple_logger.get_logger(name)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.simple_logger.info(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.simple_logger.debug(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.simple_logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.simple_logger.error(message, **kwargs)
    
    def log_operation(self, operation: str, status: str = "started", **kwargs):
        """Log operation with structured data"""
        self.info(f"Operation: {operation} - {status}", **kwargs)
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        self.info(f"Performance: {operation}", duration_ms=round(duration * 1000, 2), **kwargs)
    
    def log_error(self, error: Exception, context: str = "", **kwargs):
        """Log error with full context"""
        self.error(f"Error in {context}: {str(error)}", error_type=type(error).__name__, **kwargs)


# Global logger instance
logger_instance = Logger()
logger = logger_instance