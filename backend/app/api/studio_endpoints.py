from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.schemas import (
    StudioIdeaRequest, 
    StudioIdeaResponse, 
    StudioScriptRequest, 
    StudioScriptResponse,
    StudioIdea,
    StudioImageRequest,
    StudioImageResponse,
    StudioAudioRequest,
    StudioAudioResponse
)
from fastapi.responses import FileResponse
import os
from app.services.studio_service import studio_service
from app.core.logger import logger

router = APIRouter(prefix="/studio", tags=["Studio"])

@router.post("/ideas", response_model=StudioIdeaResponse)
async def generate_studio_ideas(request: StudioIdeaRequest):
    """Brainstorm 5 viral ideas for a topic"""
    try:
        ideas_raw = await studio_service.generate_ideas(request.topic)
        ideas = [StudioIdea(**item) for item in ideas_raw]
        return StudioIdeaResponse(success=True, ideas=ideas)
    except Exception as e:
        logger.error(f"Studio Ideas Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-script", response_model=StudioScriptResponse)
async def generate_studio_script(request: StudioScriptRequest):
    """Generate full scene-by-scene script from an idea"""
    try:
        script_data = await studio_service.generate_full_script(
            request.idea_title, 
            request.character_config.dict()
        )
        return StudioScriptResponse(success=True, **script_data)
    except Exception as e:
        logger.error(f"Studio Script Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-image", response_model=StudioImageResponse)
async def generate_studio_image(request: StudioImageRequest):
    """Generate AI image for a scene"""
    try:
        image_url = await studio_service.generate_scene_image(
            request.visual_description, 
            request.char_role
        )
        return StudioImageResponse(success=True, image_url=image_url)
    except Exception as e:
        logger.error(f"Studio Image Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-audio", response_model=StudioAudioResponse)
async def generate_studio_audio(request: StudioAudioRequest):
    """Generate AI voice for a scene dialogue"""
    try:
        audio_url = await studio_service.generate_scene_audio(
            request.text, 
            request.voice
        )
        return StudioAudioResponse(success=True, audio_url=audio_url)
    except Exception as e:
        logger.error(f"Studio Audio Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export-zip")
async def export_studio_project(request: StudioScriptResponse):
    """Export all project assets as a ZIP file"""
    try:
        zip_path = await studio_service.export_project_zip(request.dict())
        return FileResponse(
            zip_path, 
            media_type="application/zip", 
            filename=os.path.basename(zip_path)
        )
    except Exception as e:
        logger.error(f"Studio Export Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
