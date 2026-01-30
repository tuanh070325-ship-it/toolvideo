import logging
import json
import sys
import uuid
from typing import Any, Dict
from contextvars import ContextVar
from datetime import datetime, timezone
from app.core.config import settings

# Context variable to track request ID across async calls
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="system")

class JSONFormatter(logging.Formatter):
    """Format logs as JSON with extra context"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "request_id": request_id_ctx.get(),
        }
        
        # Add extra fields if present
        if hasattr(record, "props"):
            log_obj.update(record.props)
            
        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_obj)

def get_request_id() -> str:
    """Get current request ID"""
    return request_id_ctx.get()

def set_request_id(req_id: str):
    """Set current request ID"""
    request_id_ctx.set(req_id)

class StructuredLogger(logging.Logger):
    """Logger that accepts extra properties"""
    
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
        if extra is None:
            extra = {}
            
        # Add current request ID to all logs
        extra.update({"request_id": request_id_ctx.get()})
        
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)
        
    def info_with_props(self, msg: str, props: Dict[str, Any], **kwargs):
        """Log info with structured properties"""
        self.info(msg, extra={"props": props}, **kwargs)
        
    def error_with_props(self, msg: str, props: Dict[str, Any], **kwargs):
        """Log error with structured properties"""
        self.error(msg, extra={"props": props}, **kwargs)

def setup_logging():
    """Configure structured logging for the application"""
    # Replace default logger class
    logging.setLoggerClass(StructuredLogger)
    
    # Root logger config
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    # Console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler (rotating) - optional, for persistent logs
    import os
    log_dir = os.path.dirname(settings.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        
    file_handler = logging.handlers.RotatingFileHandler(
        settings.LOG_FILE, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)
    
    return logging.getLogger("app")
