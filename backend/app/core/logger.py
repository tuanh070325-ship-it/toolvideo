import logging
import sys
from loguru import logger
from app.core.config import settings

def setup_logging():
    """Setup logging configuration using Loguru"""
    # Remove default handler
    logger.remove()
    
    # Disable icons to prevent UnicodeEncodeError on Windows redirected stdout
    for level in ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]:
        logger.level(level, icon="")
    
    # Add console handler
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Add rotating file handler with JSON format
    logger.add(
        settings.LOG_FILE,
        rotation="10 MB",
        retention="5 days",
        level="INFO",
        serialize=True,
        encoding="utf-8"
    )

    # Intercept standard logging
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Intercept uvicorn logs
    for name in ["uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine"]:
        logging_logger = logging.getLogger(name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    return logger

# Call setup immediately
setup_logging()
