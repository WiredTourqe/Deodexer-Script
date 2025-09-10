"""
Database models for Deodexer Pro
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from enum import Enum
import json
from datetime import datetime
from typing import Dict, Any, Optional

Base = declarative_base()


class JobStatus(Enum):
    """Job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DeodexingJob(Base):
    """Model for deodexing job tracking"""
    __tablename__ = 'deodexing_jobs'
    
    id = Column(Integer, primary_key=True)
    job_name = Column(String(255), nullable=False)
    status = Column(String(50), default=JobStatus.PENDING.value)
    input_directory = Column(String(500), nullable=False)
    output_directory = Column(String(500), nullable=False)
    framework_directory = Column(String(500), nullable=False)
    api_level = Column(Integer, default=29)
    max_workers = Column(Integer, default=4)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Progress tracking
    total_files = Column(Integer, default=0)
    processed_files = Column(Integer, default=0)
    successful_files = Column(Integer, default=0)
    failed_files = Column(Integer, default=0)
    
    # Performance metrics
    total_duration = Column(Float, default=0.0)
    total_size_bytes = Column(Integer, default=0)
    
    # Configuration and metadata
    configuration = Column(Text)  # JSON string
    error_message = Column(Text, nullable=True)
    
    # Relationships
    file_results = relationship("FileResult", back_populates="job", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'job_name': self.job_name,
            'status': self.status,
            'input_directory': self.input_directory,
            'output_directory': self.output_directory,
            'framework_directory': self.framework_directory,
            'api_level': self.api_level,
            'max_workers': self.max_workers,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'successful_files': self.successful_files,
            'failed_files': self.failed_files,
            'total_duration': self.total_duration,
            'total_size_bytes': self.total_size_bytes,
            'configuration': json.loads(self.configuration) if self.configuration else {},
            'error_message': self.error_message
        }
    
    def get_progress_percentage(self) -> float:
        """Get job progress as percentage"""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100
    
    def get_success_rate(self) -> float:
        """Get success rate as percentage"""
        if self.processed_files == 0:
            return 0.0
        return (self.successful_files / self.processed_files) * 100


class FileResult(Base):
    """Model for individual file processing results"""
    __tablename__ = 'file_results'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('deodexing_jobs.id'), nullable=False)
    
    # File information
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    file_hash = Column(String(64), nullable=True)  # SHA-256 hash
    
    # Processing information
    status = Column(String(50), default=JobStatus.PENDING.value)
    output_path = Column(String(500), nullable=True)
    processing_duration = Column(Float, default=0.0)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Error information
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    
    # Metadata
    metadata = Column(Text)  # JSON string for additional data
    
    # Relationships
    job = relationship("DeodexingJob", back_populates="file_results")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size_bytes': self.file_size_bytes,
            'file_hash': self.file_hash,
            'status': self.status,
            'output_path': self.output_path,
            'processing_duration': self.processing_duration,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'error_code': self.error_code,
            'metadata': json.loads(self.metadata) if self.metadata else {}
        }


class SystemMetrics(Base):
    """Model for system performance metrics"""
    __tablename__ = 'system_metrics'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=func.now())
    
    # Performance metrics
    cpu_usage_percent = Column(Float, default=0.0)
    memory_usage_percent = Column(Float, default=0.0)
    memory_usage_bytes = Column(Integer, default=0)
    disk_usage_percent = Column(Float, default=0.0)
    
    # Application metrics
    active_jobs = Column(Integer, default=0)
    active_workers = Column(Integer, default=0)
    files_processed_per_hour = Column(Float, default=0.0)
    average_processing_time = Column(Float, default=0.0)
    
    # Additional data
    metadata = Column(Text)  # JSON string


class UserSession(Base):
    """Model for user session tracking"""
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), unique=True, nullable=False)
    
    # Session information
    created_at = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    # User preferences (JSON)
    preferences = Column(Text)
    
    # Session statistics
    jobs_created = Column(Integer, default=0)
    files_processed = Column(Integer, default=0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'is_active': self.is_active,
            'preferences': json.loads(self.preferences) if self.preferences else {},
            'jobs_created': self.jobs_created,
            'files_processed': self.files_processed
        }