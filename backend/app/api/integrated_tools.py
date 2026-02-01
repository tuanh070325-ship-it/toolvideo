"""
API Routes for Integrated Video Tools
Combines features from:
- ShortGPT (auto video generation)
- MoneyPrinterTurbo (batch video creation)
- Pyvideotrans (translation & dubbing)
- AnimeGANv3 (style transfer)
- Auto-Editor (silence removal)
"""

import uuid
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.core.config import settings

router = APIRouter(prefix="/tools", tags=["integrated-tools"])


# ==================== REQUEST MODELS ====================

class ShortVideoRequest(BaseModel):
    """Request for short video generation"""
    topic: str = Field(..., description="Main topic or keyword")
    platform: str = Field("tiktok", description="Target platform: tiktok, reels, shorts, youtube")
    style: str = Field("storytelling", description="Content style")
    duration: int = Field(60, description="Target duration in seconds")
    voice: Optional[str] = Field(None, description="TTS voice ID")
    language: str = Field("vi", description="Content language")
    add_captions: bool = Field(True, description="Whether to add subtitles")
    ai_provider: str = Field("auto", description="AI provider")


class BatchVideoRequest(BaseModel):
    """Request for batch video generation"""
    topics: List[str] = Field(..., description="List of topics")
    platform: str = Field("tiktok", description="Target platform")
    style: str = Field("storytelling", description="Content style")
    language: str = Field("vi", description="Content language")


class VideoTranslationRequest(BaseModel):
    """Request for video translation"""
    video_url: str = Field(..., description="Source video URL")
    source_language: str = Field("auto", description="Source language (auto-detect)")
    target_language: str = Field("vi", description="Target language")
    voice: Optional[str] = Field(None, description="TTS voice ID")
    preserve_bgm: bool = Field(True, description="Preserve background music")
    ai_provider: str = Field("auto", description="AI provider")


class StyleTransferRequest(BaseModel):
    """Request for video style transfer"""
    video_url: str = Field(..., description="Source video URL")
    style: str = Field("anime_hayao", description="Style to apply")
    intensity: float = Field(1.0, description="Style intensity (0.0-1.0)")
    preserve_audio: bool = Field(True, description="Keep original audio")


class AutoEditRequest(BaseModel):
    """Request for automatic video editing"""
    video_url: str = Field(..., description="Source video URL")
    remove_silence: bool = Field(True, description="Remove silent segments")
    threshold_db: float = Field(-30.0, description="Silence threshold in dB")
    min_silence_duration: float = Field(0.5, description="Minimum silence duration")
    speed_up_silence: Optional[float] = Field(None, description="Speed up silence instead of removing")
    margin: float = Field(0.1, description="Keep margin around speech")


class SmartTrimRequest(BaseModel):
    """Request for smart video trimming"""
    video_url: str = Field(..., description="Source video URL")
    target_duration: int = Field(60, description="Target duration in seconds")
    keep_start: bool = Field(True, description="Always keep beginning")
    keep_end: bool = Field(True, description="Always keep ending")


# ==================== HELPER FUNCTIONS ====================

async def download_video_to_path(url: str, output_dir: Path) -> Path:
    """Download video from URL to local path"""
    from app.services.video_downloader import VideoDownloader
    
    downloader = VideoDownloader()
    result = await downloader.download(url, output_dir)
    
    if not result or not result.get("path"):
        raise HTTPException(status_code=400, detail="Failed to download video")
    
    return Path(result["path"])


# ==================== SHORT VIDEO GENERATION ====================

@router.post("/short-video/generate")
async def generate_short_video(request: ShortVideoRequest, background_tasks: BackgroundTasks):
    """
    Generate a complete short video from a topic
    
    Uses AI to:
    - Generate script
    - Create narration
    - Find/generate background footage
    - Add captions
    - Mix background music
    """
    try:
        from app.services.short_video_generator import short_video_generator
        
        logger.info(f"Generating short video: {request.topic}")
        
        result = await short_video_generator.generate_from_topic(
            topic=request.topic,
            platform=request.platform,
            style=request.style,
            duration=request.duration,
            voice=request.voice,
            language=request.language,
            add_captions=request.add_captions,
            ai_provider=request.ai_provider
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Generation failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Short video generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/short-video/batch")
async def batch_generate_videos(request: BatchVideoRequest, background_tasks: BackgroundTasks):
    """Generate multiple videos in batch from a list of topics"""
    try:
        from app.services.short_video_generator import short_video_generator
        
        logger.info(f"Batch generating {len(request.topics)} videos")
        
        results = await short_video_generator.batch_generate(
            topics=request.topics,
            platform=request.platform,
            style=request.style,
            language=request.language
        )
        
        success_count = sum(1 for r in results if r.get("success"))
        
        return {
            "success": True,
            "total": len(request.topics),
            "successful": success_count,
            "failed": len(request.topics) - success_count,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/short-video/styles")
async def get_short_video_styles():
    """Get available video styles for short video generation"""
    from app.services.short_video_generator import short_video_generator
    
    return {
        "styles": short_video_generator.get_available_styles(),
        "platforms": short_video_generator.get_available_platforms()
    }


# ==================== VIDEO TRANSLATION & DUBBING ====================

@router.post("/translate")
async def translate_video(request: VideoTranslationRequest, background_tasks: BackgroundTasks):
    """
    Translate and dub video to another language
    
    Process:
    1. Download video
    2. Transcribe audio
    3. Translate text
    4. Generate TTS in target language
    5. Replace audio (optionally preserve BGM)
    """
    try:
        from app.services.video_translation import video_translation
        
        logger.info(f"Translating video to {request.target_language}: {request.video_url}")
        
        # Download video
        temp_dir = Path(settings.TEMP_DIR) / f"translate_{uuid.uuid4()[:8]}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        video_path = await download_video_to_path(request.video_url, temp_dir)
        
        result = await video_translation.translate_video(
            video_path=video_path,
            source_language=request.source_language,
            target_language=request.target_language,
            voice=request.voice,
            preserve_bgm=request.preserve_bgm,
            ai_provider=request.ai_provider
        )
        
        # Cleanup
        video_path.unlink(missing_ok=True)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Translation failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/translate/languages")
async def get_supported_languages():
    """Get supported languages for translation"""
    from app.services.video_translation import video_translation
    
    return {
        "languages": [
            {"code": code, "name": name}
            for code, name in video_translation.SUPPORTED_LANGUAGES.items()
        ],
        "voices": video_translation.LANGUAGE_VOICES
    }


# ==================== STYLE TRANSFER ====================

@router.post("/style-transfer")
async def apply_style_transfer(request: StyleTransferRequest, background_tasks: BackgroundTasks):
    """
    Apply artistic style transfer to video
    
    Available styles include anime, cartoon, sketch, and more
    """
    try:
        from app.services.video_style_transfer import video_style_transfer
        
        logger.info(f"Applying {request.style} style to video: {request.video_url}")
        
        # Download video
        temp_dir = Path(settings.TEMP_DIR) / f"style_{uuid.uuid4()[:8]}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        video_path = await download_video_to_path(request.video_url, temp_dir)
        
        result = await video_style_transfer.apply_style(
            video_path=video_path,
            style=request.style,
            intensity=request.intensity,
            preserve_audio=request.preserve_audio
        )
        
        # Cleanup
        video_path.unlink(missing_ok=True)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Style transfer failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Style transfer error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/style-transfer/styles")
async def get_available_styles():
    """Get available styles for style transfer"""
    from app.services.video_style_transfer import video_style_transfer
    
    return {
        "styles": video_style_transfer.get_available_styles()
    }


# ==================== AUTO EDITOR ====================

@router.post("/auto-edit/analyze")
async def analyze_video_audio(video_url: str = Query(..., description="Video URL")):
    """Analyze video audio to detect speech and silence segments"""
    try:
        from app.services.auto_editor import auto_editor
        
        logger.info(f"Analyzing audio: {video_url}")
        
        # Download video
        temp_dir = Path(settings.TEMP_DIR) / f"analyze_{uuid.uuid4()[:8]}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        video_path = await download_video_to_path(video_url, temp_dir)
        
        result = await auto_editor.analyze_audio_levels(video_path)
        
        # Cleanup
        video_path.unlink(missing_ok=True)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Analysis failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-edit/remove-silence")
async def remove_video_silence(request: AutoEditRequest, background_tasks: BackgroundTasks):
    """
    Remove or speed up silent segments in video
    
    Great for making content more engaging and reducing video length
    """
    try:
        from app.services.auto_editor import auto_editor
        
        logger.info(f"Removing silence from: {request.video_url}")
        
        # Download video
        temp_dir = Path(settings.TEMP_DIR) / f"silence_{uuid.uuid4()[:8]}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        video_path = await download_video_to_path(request.video_url, temp_dir)
        
        result = await auto_editor.remove_silence(
            video_path=video_path,
            threshold_db=request.threshold_db,
            min_silence_duration=request.min_silence_duration,
            margin=request.margin,
            speed_up_silence=request.speed_up_silence
        )
        
        # Cleanup
        video_path.unlink(missing_ok=True)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Silence removal failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Silence removal error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-edit/smart-trim")
async def smart_trim_video(request: SmartTrimRequest, background_tasks: BackgroundTasks):
    """
    Smart trim video to target duration while preserving important content
    """
    try:
        from app.services.auto_editor import auto_editor
        
        logger.info(f"Smart trimming video to {request.target_duration}s: {request.video_url}")
        
        # Download video
        temp_dir = Path(settings.TEMP_DIR) / f"trim_{uuid.uuid4()[:8]}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        video_path = await download_video_to_path(request.video_url, temp_dir)
        
        result = await auto_editor.smart_trim(
            video_path=video_path,
            target_duration=request.target_duration,
            keep_start=request.keep_start,
            keep_end=request.keep_end
        )
        
        # Cleanup
        video_path.unlink(missing_ok=True)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Smart trim failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Smart trim error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DOWNLOAD PROCESSED FILES ====================

@router.get("/download/{filename}")
async def download_processed_file(filename: str):
    """Download a processed video file"""
    try:
        file_path = Path(settings.PROCESSED_DIR) / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            media_type="video/mp4",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ALL TOOLS INFO ====================

@router.get("/info")
async def get_tools_info():
    """Get information about all integrated tools"""
    return {
        "tools": [
            {
                "id": "short-video",
                "name": "Tạo Video Ngắn Tự Động",
                "name_en": "Short Video Generator",
                "description": "Tạo video ngắn hoàn chỉnh từ một từ khóa hoặc chủ đề",
                "source": "ShortGPT + MoneyPrinterTurbo",
                "endpoints": [
                    "/api/tools/short-video/generate",
                    "/api/tools/short-video/batch",
                    "/api/tools/short-video/styles"
                ]
            },
            {
                "id": "translate",
                "name": "Dịch & Lồng Tiếng Video",
                "name_en": "Video Translation & Dubbing",
                "description": "Dịch video sang ngôn ngữ khác với giọng AI",
                "source": "Pyvideotrans",
                "endpoints": [
                    "/api/tools/translate",
                    "/api/tools/translate/languages"
                ]
            },
            {
                "id": "style-transfer",
                "name": "Chuyển Đổi Phong Cách Video",
                "name_en": "Video Style Transfer",
                "description": "Chuyển đổi video sang phong cách anime, hoạt hình, nghệ thuật",
                "source": "AnimeGANv3",
                "endpoints": [
                    "/api/tools/style-transfer",
                    "/api/tools/style-transfer/styles"
                ]
            },
            {
                "id": "auto-edit",
                "name": "Chỉnh Sửa Video Tự Động",
                "name_en": "Automatic Video Editor",
                "description": "Tự động cắt im lặng, tăng tốc, cắt gọn video",
                "source": "Auto-Editor",
                "endpoints": [
                    "/api/tools/auto-edit/analyze",
                    "/api/tools/auto-edit/remove-silence",
                    "/api/tools/auto-edit/smart-trim"
                ]
            }
        ],
        "version": "1.0.0"
    }
