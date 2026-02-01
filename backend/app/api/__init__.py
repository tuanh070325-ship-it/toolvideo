# app/api/__init__.py
from fastapi import APIRouter

from app.api.endpoints import router
from app.api.studio_endpoints import router as studio_router
from app.api.generation import router as generation_router
from app.api.workflows import router as workflows_router
from app.api.videos import router as videos_router
from app.api.integrated_tools import router as integrated_tools_router

api_router = APIRouter()
api_router.include_router(router, tags=["videos"])
api_router.include_router(studio_router)
api_router.include_router(generation_router)
api_router.include_router(workflows_router)
api_router.include_router(videos_router)
api_router.include_router(integrated_tools_router)
