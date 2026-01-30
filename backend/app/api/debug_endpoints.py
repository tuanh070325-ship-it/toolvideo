"""
Debug and Logging API Endpoints

Provides endpoints for:
- Real-time log streaming
- Pipeline status monitoring
- Debug mode configuration
- System diagnostics
"""

import asyncio
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from app.core.logger import logger
from app.core.config import settings


router = APIRouter(prefix="/debug", tags=["debug"])


class LogEntry(BaseModel):
    """Log entry model"""
    id: str
    timestamp: str
    level: str
    stage: Optional[str] = None
    message: str
    details: Optional[dict] = None
    duration: Optional[float] = None


class PipelineStageStatus(BaseModel):
    """Pipeline stage status model"""
    name: str
    status: str  # pending, running, completed, failed, skipped
    progress: float
    message: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    error: Optional[str] = None


class PipelineStatus(BaseModel):
    """Pipeline status model"""
    job_id: str
    total_stages: int
    completed_stages: int
    current_stage: Optional[str] = None
    overall_progress: float
    status: str  # pending, running, completed, failed
    stages: dict
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    error: Optional[str] = None


class DebugConfigResponse(BaseModel):
    """Debug configuration response"""
    debug_mode: bool
    log_level: str
    api_logs_enabled: bool
    verbose_errors: bool
    performance_tracking: bool


class SystemDiagnostics(BaseModel):
    """System diagnostics response"""
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None
    disk_usage_percent: Optional[float] = None
    active_jobs: int = 0
    queue_size: int = 0
    uptime_seconds: float = 0
    python_version: str = ""
    ffmpeg_available: bool = False
    api_keys_configured: dict = {}


# In-memory log store (for demo - in production use Redis or similar)
_log_store: List[dict] = []
_pipeline_status: dict = {}
MAX_LOGS = 1000
MAX_PIPELINE_JOBS = 100  # Limit pipeline status storage


def add_log(
    level: str,
    message: str,
    stage: Optional[str] = None,
    details: Optional[dict] = None,
    duration: Optional[float] = None,
) -> dict:
    """Add a log entry to the store"""
    import uuid
    
    log = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "stage": stage,
        "message": message,
        "details": details,
        "duration": duration,
    }
    
    _log_store.append(log)
    
    # Trim if exceeds max
    if len(_log_store) > MAX_LOGS:
        _log_store.pop(0)
    
    return log


def update_pipeline_status(job_id: str, status: dict):
    """Update pipeline status with size limit"""
    _pipeline_status[job_id] = status
    
    # Trim if exceeds max (remove oldest entries)
    if len(_pipeline_status) > MAX_PIPELINE_JOBS:
        oldest_keys = sorted(_pipeline_status.keys())[:len(_pipeline_status) - MAX_PIPELINE_JOBS]
        for key in oldest_keys:
            _pipeline_status.pop(key, None)


def get_pipeline_status(job_id: str) -> Optional[dict]:
    """Get pipeline status"""
    return _pipeline_status.get(job_id)


@router.get("/logs", response_model=List[LogEntry])
async def get_logs(
    limit: int = Query(default=100, ge=1, le=1000),
    level: Optional[str] = Query(default=None),
    stage: Optional[str] = Query(default=None),
    since: Optional[str] = Query(default=None, description="ISO timestamp"),
):
    """Get recent logs with optional filtering"""
    logs = _log_store[-limit:]
    
    # Filter by level
    if level:
        logs = [l for l in logs if l["level"] == level]
    
    # Filter by stage
    if stage:
        logs = [l for l in logs if l.get("stage") == stage]
    
    # Filter by timestamp
    if since:
        try:
            # Handle both 'Z' suffix and '+00:00' format
            since_normalized = since.rstrip('Z')
            if '+' not in since_normalized and '-' not in since_normalized[-6:]:
                since_normalized += '+00:00'
            since_dt = datetime.fromisoformat(since_normalized)
            
            filtered_logs = []
            for l in logs:
                ts = l["timestamp"].rstrip('Z')
                if '+' not in ts and '-' not in ts[-6:]:
                    ts += '+00:00'
                log_dt = datetime.fromisoformat(ts)
                if log_dt > since_dt:
                    filtered_logs.append(l)
            logs = filtered_logs
        except (ValueError, TypeError):
            pass
    
    return logs


@router.delete("/logs")
async def clear_logs():
    """Clear all logs"""
    _log_store.clear()
    return {"message": "Logs cleared", "count": 0}


@router.get("/logs/stream")
async def stream_logs(
    level: Optional[str] = Query(default=None),
):
    """Stream logs in real-time using Server-Sent Events"""
    async def event_generator():
        last_index = len(_log_store)
        max_idle_count = 600  # ~5 minutes of idle time before closing
        idle_count = 0
        
        while idle_count < max_idle_count:
            # Check for new logs
            if len(_log_store) > last_index:
                new_logs = _log_store[last_index:]
                last_index = len(_log_store)
                idle_count = 0  # Reset idle counter
                
                for log in new_logs:
                    if level and log["level"] != level:
                        continue
                    yield f"data: {json.dumps(log)}\n\n"
            else:
                idle_count += 1
            
            await asyncio.sleep(0.5)
        
        # Send close event when timing out
        yield f"event: close\ndata: {json.dumps({'reason': 'timeout'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/pipeline/{job_id}", response_model=PipelineStatus)
async def get_pipeline_job_status(job_id: str):
    """Get pipeline status for a specific job"""
    status = get_pipeline_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return status


@router.get("/config", response_model=DebugConfigResponse)
async def get_debug_config():
    """Get current debug configuration"""
    return DebugConfigResponse(
        debug_mode=settings.DEBUG,
        log_level="DEBUG" if settings.DEBUG else "INFO",
        api_logs_enabled=True,
        verbose_errors=settings.DEBUG,
        performance_tracking=True,
    )


@router.get("/diagnostics", response_model=SystemDiagnostics)
async def get_system_diagnostics():
    """Get system diagnostics information"""
    import sys
    import subprocess
    import time as time_module
    
    diagnostics = SystemDiagnostics(
        python_version=sys.version,
    )
    
    # CPU and Memory
    try:
        import psutil
        diagnostics.cpu_percent = psutil.cpu_percent()
        diagnostics.memory_percent = psutil.virtual_memory().percent
        diagnostics.disk_usage_percent = psutil.disk_usage('/').percent
        diagnostics.uptime_seconds = time_module.time() - psutil.boot_time()
    except ImportError:
        pass
    
    # Check FFmpeg
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        diagnostics.ffmpeg_available = result.returncode == 0
    except Exception:
        diagnostics.ffmpeg_available = False
    
    # API Keys status (masked)
    diagnostics.api_keys_configured = {
        "openai": bool(settings.OPENAI_API_KEY),
        "google": bool(settings.GOOGLE_API_KEY),
        "gemini": bool(settings.GEMINI_API_KEY),
        "deepgram": bool(settings.DEEPGRAM_API_KEY),
        "elevenlabs": bool(settings.ELEVENLABS_API_KEY),
        "shotstack": bool(settings.SHOTSTACK_API_KEY),
        "pexels": bool(settings.PEXELS_API_KEY),
        "groq": bool(settings.GROQ_API_KEY),
    }
    
    return diagnostics


@router.post("/test-log")
async def create_test_log(
    level: str = Query(default="info"),
    message: str = Query(default="Test log message"),
    stage: Optional[str] = Query(default=None),
):
    """Create a test log entry (for development/testing)"""
    if not settings.DEBUG:
        raise HTTPException(status_code=403, detail="Test logs only available in debug mode")
    
    log = add_log(level=level, message=message, stage=stage)
    return log


# Helper function to integrate with existing logging
def create_pipeline_logger(job_id: str, callback=None):
    """Create a logger that sends updates to both the log store and optional callback"""
    
    class PipelineLogger:
        def __init__(self, job_id: str, callback=None):
            self.job_id = job_id
            self.callback = callback
        
        def log(self, level: str, message: str, stage: str = None, details: dict = None, duration: float = None):
            # Add to log store
            log = add_log(
                level=level,
                message=message,
                stage=stage,
                details={"job_id": self.job_id, **(details or {})},
                duration=duration,
            )
            
            # Also log to standard logger
            getattr(logger, level)(f"[Job:{self.job_id}] {message}")
            
            # Call callback if provided
            if self.callback:
                self.callback(log)
        
        def info(self, message: str, **kwargs):
            self.log("info", message, **kwargs)
        
        def success(self, message: str, **kwargs):
            self.log("success", message, **kwargs)
        
        def warning(self, message: str, **kwargs):
            self.log("warning", message, **kwargs)
        
        def error(self, message: str, **kwargs):
            self.log("error", message, **kwargs)
        
        def debug(self, message: str, **kwargs):
            self.log("debug", message, **kwargs)
        
        def update_pipeline(self, status: dict):
            update_pipeline_status(self.job_id, status)
            if self.callback:
                self.callback({"type": "pipeline_update", "status": status})
    
    return PipelineLogger(job_id, callback)
