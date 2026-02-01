"""API routes for AI video generation"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from pathlib import Path

from app.services.generation import LTXVideoService, LTXConfig
from app.services.monitoring import get_opik_service
from app.core.logger import logger
import time

router = APIRouter(prefix="/generation", tags=["generation"])

# Initialize service (lazy loading)
ltx_service: Optional[LTXVideoService] = None


class TextToVideoRequest(BaseModel):
    """Request for text-to-video generation"""
    prompt: str = Field(..., description="Text description of video to generate")
    negative_prompt: Optional[str] = Field(None, description="What to avoid")
    seed: Optional[int] = Field(None, description="Random seed")
    height: Optional[int] = Field(704, description="Video height (divisible by 32)")
    width: Optional[int] = Field(1216, description="Video width (divisible by 32)")
    num_frames: Optional[int] = Field(121, description="Number of frames (N*8+1)")
    num_inference_steps: Optional[int] = Field(50, description="Denoising steps")
    guidance_scale: Optional[float] = Field(3.0, description="Guidance scale")


class ImageToVideoRequest(BaseModel):
    """Request for image-to-video generation"""
    image_path: str = Field(..., description="Path to input image")
    prompt: str = Field(..., description="Animation description")
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None
    num_frames: Optional[int] = Field(121, description="Number of frames")
    num_inference_steps: Optional[int] = Field(50, description="Denoising steps")


class GenerationResponse(BaseModel):
    """Response from video generation"""
    success: bool
    video_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


async def get_ltx_service() -> LTXVideoService:
    """Get or create LTX service instance"""
    global ltx_service
    if ltx_service is None:
        ltx_service = LTXVideoService()
        await ltx_service.initialize()
    return ltx_service


@router.post("/text-to-video", response_model=GenerationResponse)
async def generate_video_from_text(
    request: TextToVideoRequest,
    background_tasks: BackgroundTasks
):
    """Generate video from text prompt using LTX-Video
    
    This endpoint uses state-of-the-art AI to generate high-quality videos
    from text descriptions. Supports up to 4K resolution and 50 FPS.
    """
    try:
        logger.info(f"Text-to-video request: {request.prompt[:50]}...")
        start_time = time.time()
        
        # Get service
        service = await get_ltx_service()
        
        # Generate video
        result = await service.generate_video(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            seed=request.seed,
            height=request.height,
            width=request.width,
            num_frames=request.num_frames,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
        )
        
        duration = time.time() - start_time
        
        # Track with Opik
        opik = get_opik_service()
        background_tasks.add_task(
            opik.track_video_generation,
            prompt=request.prompt,
            model="ltx-video",
            result=result,
            duration=duration
        )
        
        return GenerationResponse(
            success=True,
            video_path=result["path"],
            metadata=result
        )
        
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        return GenerationResponse(
            success=False,
            error=str(e)
        )


@router.post("/image-to-video", response_model=GenerationResponse)
async def generate_video_from_image(
    request: ImageToVideoRequest,
    background_tasks: BackgroundTasks
):
    """Generate video from input image using LTX-Video
    
    Animate a static image based on text description.
    """
    try:
        logger.info(f"Image-to-video request: {request.image_path}")
        start_time = time.time()
        
        # Validate image exists
        if not Path(request.image_path).exists():
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Get service
        service = await get_ltx_service()
        
        # Generate video
        result = await service.image_to_video(
            image_path=request.image_path,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            seed=request.seed,
            num_frames=request.num_frames,
            num_inference_steps=request.num_inference_steps,
        )
        
        duration = time.time() - start_time
        
        # Track with Opik
        opik = get_opik_service()
        background_tasks.add_task(
            opik.track_video_generation,
            prompt=f"i2v: {request.prompt}",
            model="ltx-video-i2v",
            result=result,
            duration=duration
        )
        
        return GenerationResponse(
            success=True,
            video_path=result["path"],
            metadata=result
        )
        
    except Exception as e:
        logger.error(f"Image-to-video generation failed: {e}")
        return GenerationResponse(
            success=False,
            error=str(e)
        )


@router.get("/status")
async def get_generation_status():
    """Get status of generation service"""
    global ltx_service
    
    if ltx_service is None:
        # Try to create service to check availability
        try:
            temp_service = LTXVideoService()
            status = temp_service.get_status()
            return status
        except Exception as e:
            return {
                "available": False,
                "device": "N/A",
                "model_loaded": False,
                "message": f"Service not available: {str(e)}"
            }
    
    return ltx_service.get_status()


@router.post("/cleanup")
async def cleanup_service():
    """Clean up generation service resources"""
    global ltx_service
    
    if ltx_service:
        await ltx_service.cleanup()
        ltx_service = None
        return {"message": "Service cleaned up successfully"}
    
    return {"message": "Service not initialized"}
