"""
Advanced logging system for Deodexer Pro
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import structlog
from rich.console import Console
from rich.logging import RichHandler

from .config import config


class Logger:
    """Advanced logging system with structured logging and rich formatting"""
    
    def __init__(self, name: str = "deodexer_pro"):
        self.name = name
        self.console = Console()
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup comprehensive logging configuration"""
        log_level = config.get('logging.level', 'INFO')
        log_file = config.get('logging.file', 'logs/deodexer_pro.log')
        max_size = config.get('logging.max_size', 10485760)  # 10MB
        backup_count = config.get('logging.backup_count', 5)
        
        # Create logs directory
        log_dir = Path(log_file).parent
        log_dir.mkdir(exist_ok=True)
        
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.dev.ConsoleRenderer(colors=True)
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, log_level.upper())
            ),
            logger_factory=structlog.WriteLoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler with rich formatting
        console_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=True,
            markup=True,
            rich_tracebacks=True
        )
        console_handler.setLevel(getattr(logging, log_level.upper()))
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(detailed_formatter)
        
        # Add handlers
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        
        # Setup application logger
        self.logger = structlog.get_logger(self.name)
    
    def get_logger(self, name: Optional[str] = None) -> structlog.BoundLogger:
        """Get a logger instance"""
        logger_name = name or self.name
        return structlog.get_logger(logger_name)
    
    def log_operation(self, operation: str, status: str = "started", **kwargs):
        """Log operation with structured data"""
        self.logger.info(
            "Operation",
            operation=operation,
            status=status,
            timestamp=datetime.now().isoformat(),
            **kwargs
        )
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        self.logger.info(
            "Performance",
            operation=operation,
            duration_ms=round(duration * 1000, 2),
            **kwargs
        )
    
    def log_error(self, error: Exception, context: str = "", **kwargs):
        """Log error with full context"""
        self.logger.error(
            "Error occurred",
            error_type=type(error).__name__,
            error_message=str(error),
            context=context,
            **kwargs,
            exc_info=True
        )
    
    def log_security_event(self, event_type: str, severity: str = "info", **kwargs):
        """Log security-related events"""
        security_logger = structlog.get_logger("security")
        security_logger.info(
            "Security Event",
            event_type=event_type,
            severity=severity,
            timestamp=datetime.now().isoformat(),
            **kwargs
        )
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, **kwargs):
        """Log API requests"""
        api_logger = structlog.get_logger("api")
        api_logger.info(
            "API Request",
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            **kwargs
        )
    
    def log_database_operation(self, operation: str, table: str = "", **kwargs):
        """Log database operations"""
        db_logger = structlog.get_logger("database")
        db_logger.info(
            "Database Operation",
            operation=operation,
            table=table,
            **kwargs
        )
    
    def set_level(self, level: str) -> None:
        """Change logging level at runtime"""
        logging.getLogger().setLevel(getattr(logging, level.upper()))
        self.logger.info("Logging level changed", new_level=level)
    
    def create_context_logger(self, **context) -> structlog.BoundLogger:
        """Create a logger with bound context"""
        return self.logger.bind(**context)


# Global logger instance
logger_instance = Logger()
logger = logger_instance.get_logger()