"""
Database manager for Deodexer Pro
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, and_, or_, desc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
import json

from .models import Base, DeodexingJob, FileResult, SystemMetrics, UserSession, JobStatus
from ..core.config import config
from ..core.logger import logger


class DatabaseManager:
    """Advanced database management with comprehensive operations"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or config.get('database.path', 'data/deodexer_pro.db')
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database connection and create tables"""
        try:
            # Create database directory if it doesn't exist
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            # Create engine
            self.engine = create_engine(
                f'sqlite:///{self.db_path}',
                echo=config.get('database.echo', False),
                pool_pre_ping=True
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("Database initialized successfully", db_path=self.db_path)
            
        except Exception as e:
            logger.error("Database initialization failed", error=str(e))
            raise
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    # Job Management
    def create_job(
        self,
        job_name: str,
        input_directory: str,
        output_directory: str,
        framework_directory: str,
        api_level: int = 29,
        max_workers: int = 4,
        configuration: Dict[str, Any] = None
    ) -> DeodexingJob:
        """Create a new deodexing job"""
        with self.get_session() as session:
            try:
                job = DeodexingJob(
                    job_name=job_name,
                    input_directory=input_directory,
                    output_directory=output_directory,
                    framework_directory=framework_directory,
                    api_level=api_level,
                    max_workers=max_workers,
                    configuration=json.dumps(configuration or {}),
                    status=JobStatus.PENDING.value
                )
                
                session.add(job)
                session.commit()
                session.refresh(job)
                
                logger.info("Job created", job_id=job.id, job_name=job_name)
                return job
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error("Failed to create job", error=str(e))
                raise
    
    def get_job(self, job_id: int) -> Optional[DeodexingJob]:
        """Get job by ID"""
        with self.get_session() as session:
            return session.query(DeodexingJob).filter(DeodexingJob.id == job_id).first()
    
    def get_jobs(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[DeodexingJob]:
        """Get jobs with optional filtering"""
        with self.get_session() as session:
            query = session.query(DeodexingJob)
            
            if status:
                query = query.filter(DeodexingJob.status == status)
            
            return query.order_by(desc(DeodexingJob.created_at)).offset(offset).limit(limit).all()
    
    def update_job_status(
        self,
        job_id: int,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """Update job status"""
        with self.get_session() as session:
            try:
                job = session.query(DeodexingJob).filter(DeodexingJob.id == job_id).first()
                if not job:
                    return False
                
                job.status = status
                if error_message:
                    job.error_message = error_message
                
                if status == JobStatus.RUNNING.value and not job.started_at:
                    job.started_at = datetime.now()
                elif status in [JobStatus.COMPLETED.value, JobStatus.FAILED.value, JobStatus.CANCELLED.value]:
                    job.completed_at = datetime.now()
                
                session.commit()
                logger.info("Job status updated", job_id=job_id, status=status)
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error("Failed to update job status", job_id=job_id, error=str(e))
                return False
    
    def update_job_progress(
        self,
        job_id: int,
        total_files: int = None,
        processed_files: int = None,
        successful_files: int = None,
        failed_files: int = None
    ) -> bool:
        """Update job progress metrics"""
        with self.get_session() as session:
            try:
                job = session.query(DeodexingJob).filter(DeodexingJob.id == job_id).first()
                if not job:
                    return False
                
                if total_files is not None:
                    job.total_files = total_files
                if processed_files is not None:
                    job.processed_files = processed_files
                if successful_files is not None:
                    job.successful_files = successful_files
                if failed_files is not None:
                    job.failed_files = failed_files
                
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error("Failed to update job progress", job_id=job_id, error=str(e))
                return False
    
    def delete_job(self, job_id: int) -> bool:
        """Delete job and all associated results"""
        with self.get_session() as session:
            try:
                job = session.query(DeodexingJob).filter(DeodexingJob.id == job_id).first()
                if not job:
                    return False
                
                session.delete(job)
                session.commit()
                
                logger.info("Job deleted", job_id=job_id)
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error("Failed to delete job", job_id=job_id, error=str(e))
                return False
    
    # File Result Management
    def add_file_result(
        self,
        job_id: int,
        file_path: str,
        status: str,
        output_path: Optional[str] = None,
        duration: float = 0.0,
        error_message: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> FileResult:
        """Add file processing result"""
        with self.get_session() as session:
            try:
                file_result = FileResult(
                    job_id=job_id,
                    file_path=file_path,
                    file_name=os.path.basename(file_path),
                    status=status,
                    output_path=output_path,
                    processing_duration=duration,
                    error_message=error_message,
                    metadata=json.dumps(metadata or {}),
                    completed_at=datetime.now() if status in [JobStatus.COMPLETED.value, JobStatus.FAILED.value] else None
                )
                
                # Set file size if file exists
                if os.path.exists(file_path):
                    file_result.file_size_bytes = os.path.getsize(file_path)
                
                session.add(file_result)
                session.commit()
                session.refresh(file_result)
                
                return file_result
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error("Failed to add file result", error=str(e))
                raise
    
    def get_file_results(self, job_id: int) -> List[FileResult]:
        """Get all file results for a job"""
        with self.get_session() as session:
            return session.query(FileResult).filter(FileResult.job_id == job_id).all()
    
    def get_failed_files(self, job_id: int) -> List[FileResult]:
        """Get failed file results for a job"""
        with self.get_session() as session:
            return session.query(FileResult).filter(
                and_(
                    FileResult.job_id == job_id,
                    FileResult.status == JobStatus.FAILED.value
                )
            ).all()
    
    # System Metrics
    def record_system_metrics(
        self,
        cpu_usage: float,
        memory_usage: float,
        memory_bytes: int,
        disk_usage: float,
        active_jobs: int = 0,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Record system performance metrics"""
        with self.get_session() as session:
            try:
                metrics = SystemMetrics(
                    cpu_usage_percent=cpu_usage,
                    memory_usage_percent=memory_usage,
                    memory_usage_bytes=memory_bytes,
                    disk_usage_percent=disk_usage,
                    active_jobs=active_jobs,
                    metadata=json.dumps(metadata or {})
                )
                
                session.add(metrics)
                session.commit()
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error("Failed to record system metrics", error=str(e))
    
    def get_system_metrics(
        self,
        hours: int = 24,
        limit: int = 1000
    ) -> List[SystemMetrics]:
        """Get system metrics for the specified time period"""
        with self.get_session() as session:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            return session.query(SystemMetrics).filter(
                SystemMetrics.timestamp >= cutoff_time
            ).order_by(desc(SystemMetrics.timestamp)).limit(limit).all()
    
    # Session Management
    def create_session(self, session_id: str) -> UserSession:
        """Create user session"""
        with self.get_session() as session:
            try:
                user_session = UserSession(session_id=session_id)
                session.add(user_session)
                session.commit()
                session.refresh(user_session)
                return user_session
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error("Failed to create user session", error=str(e))
                raise
    
    def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity"""
        with self.get_session() as session:
            try:
                user_session = session.query(UserSession).filter(
                    UserSession.session_id == session_id
                ).first()
                
                if user_session:
                    user_session.last_activity = datetime.now()
                    session.commit()
                    return True
                return False
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error("Failed to update session activity", error=str(e))
                return False
    
    # Analytics and Reporting
    def get_job_statistics(self) -> Dict[str, Any]:
        """Get comprehensive job statistics"""
        with self.get_session() as session:
            try:
                total_jobs = session.query(DeodexingJob).count()
                completed_jobs = session.query(DeodexingJob).filter(
                    DeodexingJob.status == JobStatus.COMPLETED.value
                ).count()
                failed_jobs = session.query(DeodexingJob).filter(
                    DeodexingJob.status == JobStatus.FAILED.value
                ).count()
                running_jobs = session.query(DeodexingJob).filter(
                    DeodexingJob.status == JobStatus.RUNNING.value
                ).count()
                
                total_files = session.query(FileResult).count()
                successful_files = session.query(FileResult).filter(
                    FileResult.status == JobStatus.COMPLETED.value
                ).count()
                
                return {
                    'total_jobs': total_jobs,
                    'completed_jobs': completed_jobs,
                    'failed_jobs': failed_jobs,
                    'running_jobs': running_jobs,
                    'success_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
                    'total_files_processed': total_files,
                    'successful_files': successful_files,
                    'file_success_rate': (successful_files / total_files * 100) if total_files > 0 else 0
                }
                
            except SQLAlchemyError as e:
                logger.error("Failed to get job statistics", error=str(e))
                return {}
    
    def cleanup_old_data(self, days: int = 30) -> None:
        """Clean up old data older than specified days"""
        with self.get_session() as session:
            try:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Delete old completed jobs
                old_jobs = session.query(DeodexingJob).filter(
                    and_(
                        DeodexingJob.completed_at < cutoff_date,
                        DeodexingJob.status.in_([JobStatus.COMPLETED.value, JobStatus.FAILED.value])
                    )
                ).all()
                
                for job in old_jobs:
                    session.delete(job)
                
                # Delete old system metrics
                session.query(SystemMetrics).filter(
                    SystemMetrics.timestamp < cutoff_date
                ).delete()
                
                session.commit()
                logger.info("Old data cleaned up", deleted_jobs=len(old_jobs), cutoff_days=days)
                
            except SQLAlchemyError as e:
                session.rollback()
                logger.error("Failed to cleanup old data", error=str(e))