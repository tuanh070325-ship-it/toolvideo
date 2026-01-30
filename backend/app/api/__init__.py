# app/api/__init__.py
from fastapi import APIRouter

from app.api.endpoints import router
from app.api.studio_endpoints import router as studio_router

api_router = APIRouter()
api_router.include_router(router, tags=["videos"])
api_router.include_router(studio_router)
