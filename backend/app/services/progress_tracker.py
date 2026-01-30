from datetime import datetime, timezone
import json
import logging
import math
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import VideoJob, JobStatus
from app.database import SessionLocal

logger = logging.getLogger(__name__)

class ProgressTracker:
    # Processing speed constants (MB/sec) based on benchmarking
    SPEED_DOWNLOAD = 5.0  # 5 MB/s
    SPEED_TRANSCODE_CPU = 0.5  # 0.5 MB/s
    SPEED_TRANSCODE_GPU = 5.0  # 5 MB/s (10x faster)
    SPEED_UPLOAD = 2.0  # 2 MB/s
    
    # Base overhead per step (seconds)
    OVERHEAD_INIT = 2
    OVERHEAD_ANALYSIS = 5
    
    def __init__(self, db: Session):
        self.db = db

    def estimate_processing_time(self, file_size_mb: float, options: Dict[str, Any] = None) -> int:
        """
        Estimate total processing duration in seconds based on file size and options.
        Using a heuristic model that can be refined with actual data.
        """
        if not file_size_mb or file_size_mb <= 0:
            return 60  # Default fallback
            
        options = options or {}
        use_gpu = options.get("use_gpu", True)
        transcode_speed = self.SPEED_TRANSCODE_GPU if use_gpu else self.SPEED_TRANSCODE_CPU
        
        # Estimate time for each stage
        t_download = file_size_mb / self.SPEED_DOWNLOAD
        t_process = (file_size_mb / transcode_speed) * 1.5  # 1.5x for multiple passes/filters
        t_upload = file_size_mb / self.SPEED_UPLOAD
        
        # Add fixed overheads
        total_time = t_download + t_process + t_upload + self.OVERHEAD_INIT + self.OVERHEAD_ANALYSIS
        
        # Add time for specific features
        if options.get("add_ai_narration"):
            total_time += 15  # Fixed cost for TTS generation
            
        return int(math.ceil(total_time))

    def start_tracking(self, job_id: str, file_size_mb: float = None, options: Dict[str, Any] = None):
        """Initialize progress tracking for a job"""
        job = self.db.query(VideoJob).filter(VideoJob.id == job_id).first()
        if not job:
            logger.error(f"Job not found for tracking: {job_id}")
            return

        estimated_time = self.estimate_processing_time(file_size_mb, options)
        
        job.file_size_mb = file_size_mb
        job.estimated_duration_seconds = estimated_time
        job.processing_start_time = datetime.now(timezone.utc)
        job.steps_completed = []
        job.progress = 0.0
        
        self.db.commit()
        logger.info(f"Started tracking job {job_id}. Size: {file_size_mb}MB, Est: {estimated_time}s")

    def update_progress(self, job_id: str, step: str, percentage: float, current_service: str = None):
        """Update job progress and current step"""
        job = self.db.query(VideoJob).filter(VideoJob.id == job_id).first()
        if not job:
            return

        job.current_step = step
        # Ensure progress is monotonic (never goes backwards)
        job.progress = max(job.progress or 0.0, percentage)
        
        if current_service:
            job.current_api_service = current_service
            
        self.db.commit()
        logger.info(f"Job {job_id} [{percentage}%]: {step} ({current_service or 'internal'})")

    def log_step_completion(self, job_id: str, step_name: str, duration_ms: int, metadata: Dict = None):
        """Log a completed step with timing metrics"""
        job = self.db.query(VideoJob).filter(VideoJob.id == job_id).first()
        if not job:
            return

        step_record = {
            "step": step_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration_ms,
            "metadata": metadata or {}
        }
        
        # Append to existing list (handling None case)
        current_steps = list(job.steps_completed) if job.steps_completed else []
        current_steps.append(step_record)
        job.steps_completed = current_steps
        
        self.db.commit()
        logger.info(f"Job {job_id} finished step '{step_name}' in {duration_ms}ms")

    def fail_job(self, job_id: str, error_message: str, error_context: Dict = None):
        """Mark job as failed with comprehensive error logging"""
        job = self.db.query(VideoJob).filter(VideoJob.id == job_id).first()
        if not job:
            return

        job.status = JobStatus.FAILED
        job.error_message = error_message
        job.processing_end_time = datetime.now(timezone.utc)
        
        # Log error in steps history too
        self.log_step_completion(job_id, "ERROR", 0, {
            "error": error_message,
            "context": error_context
        })
        
        self.db.commit()
        logger.error(f"Job {job_id} FAILED: {error_message} | Context: {error_context}")

    def complete_job(self, job_id: str):
        """Mark job as completed"""
        job = self.db.query(VideoJob).filter(VideoJob.id == job_id).first()
        if not job:
            return

        job.status = JobStatus.COMPLETED
        job.progress = 100.0
        job.processing_end_time = datetime.now(timezone.utc)
        job.current_step = "finished"
        
        self.db.commit()
        duration = (job.processing_end_time - job.processing_start_time).total_seconds() \
            if job.processing_start_time else 0
            
        logger.info(f"Job {job_id} COMPLETED in {duration:.2f}s")
