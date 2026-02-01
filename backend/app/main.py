import os
import time
from contextlib import asynccontextmanager

import anyio
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.core.logger import logger
from sqlalchemy import text

from app.utils.structured_logger import set_request_id
from app.api import api_router
from app.core.config import settings
# from app.core.logger import setup_logging  <-- Removed old logger setup
from app.database import Base, SessionLocal, engine
from app.utils.file_utils import ensure_dirs
import uuid

# ... (Previous imports)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Use structured logger
    # Logger is already setup in app.core.logger
    
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.APP_ENV}")
    
    # ... (Rest of lifespan function remains similar)
    
    # Create DB tables (sync engine) - run in thread to avoid blocking
    try:
        await anyio.to_thread.run_sync(lambda: Base.metadata.create_all(bind=engine))
        # Ensure runtime columns exist for backward compatibility when migrations are
        # not present or have not been applied (development convenience).
        from app.database import ensure_video_jobs_columns

        await anyio.to_thread.run_sync(ensure_video_jobs_columns)

        logger.info("OK: Database tables created and schema checked")
    except Exception as e:
        logger.error(f"ERR: Database error: {e}")

    # Ensure directories exist
    try:
        ensure_dirs()
        logger.info("OK: Directories created")
    except Exception as e:
        logger.error(f"ERR: Directory error: {e}")

    yield
    logger.info("👋 Shutting down...")


# Initialize structured logging
# Logger is already setup in app.core.logger

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered video reuploading tool for TikTok, YouTube, Facebook, Instagram, Douyin",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Set up CORS
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Add unique Request ID to every request"""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    set_request_id(request_id)
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow requests (>1s) as warnings
    if process_time > 1.0:
        logger.warning(f"Slow request: {request.method} {request.url.path} took {process_time:.2f}s")
        
    return response


from pathlib import Path
from fastapi.staticfiles import StaticFiles
from app.api.comfy_routes import router as comfy_router

if os.path.exists("data/processed"):
    app.mount("/processed", StaticFiles(directory="data/processed"), name="processed")

app.include_router(api_router, prefix="/api")
app.include_router(comfy_router)

# Mount ComfyUI frontend
comfy_web_path = Path("backend/comfy_web")
ensure_dirs([comfy_web_path]) # Ensure it exists to avoid errors if not yet downloaded
if comfy_web_path.exists():
    app.mount("/comfyui", StaticFiles(directory=str(comfy_web_path), html=True), name="comfyui")
    logger.info(f"Mounted ComfyUI frontend at /comfyui")



@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "health": "/api/health",
        "status": "running",
    }


@app.get("/api/health")
async def health_check():
    from redis import Redis

    checks = {"api": True, "database": False, "redis": False, "storage": False}

    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")

    try:
        redis_client = Redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        checks["redis"] = True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")

    if os.path.exists("data") and os.access("data", os.W_OK):
        checks["storage"] = True

    status_code = 200 if all(checks.values()) else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all(checks.values()) else "unhealthy",
            "checks": checks,
            "timestamp": time.time(),
            "version": settings.APP_VERSION,
        },
    )
