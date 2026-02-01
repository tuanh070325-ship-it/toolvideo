"""Video management API endpoints"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
import uuid
from datetime import datetime

from app.core.logger import logger
from app.services.video_downloader import VideoDownloader
from app.core.config import settings

router = APIRouter(prefix="/videos", tags=["videos"])


class VideoDownloadRequest(BaseModel):
    """Request to download a video"""
    url: str
    platform: Optional[str] = None


class VideoResponse(BaseModel):
    """Video metadata response"""
    id: str
    url: str
    title: Optional[str] = None
    platform: Optional[str] = None
    status: str
    file_path: Optional[str] = None
    thumbnail: Optional[str] = None
    duration: Optional[float] = None
    created_at: str


@router.post("/download", response_model=VideoResponse)
async def download_video(request: VideoDownloadRequest, background_tasks: BackgroundTasks):
    """Download video from URL
    
    Supports: YouTube, TikTok, Instagram, Douyin
    """
    try:
        logger.info(f"Downloading video: {request.url}")
        
        # Generate video ID
        video_id = str(uuid.uuid4())[:8]
        
        # Download video
        downloader = VideoDownloader()
        result = await downloader.download(
            url=request.url,
            output_dir=Path(settings.DOWNLOADS_DIR)
        )
        
        # Extract metadata
        video_path = Path(result.get("path", ""))
        
        return VideoResponse(
            id=video_id,
            url=request.url,
            title=result.get("title", "Unknown"),
            platform=request.platform or "unknown",
            status="completed",
            file_path=str(video_path) if video_path.exists() else None,
            thumbnail=result.get("thumbnail"),
            duration=result.get("duration"),
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Video download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=dict)
async def list_videos():
    """List all downloaded videos"""
    try:
        videos = []
        downloads_dir = Path(settings.DOWNLOADS_DIR)
        
        if downloads_dir.exists():
            for video_file in downloads_dir.glob("*.mp4"):
                videos.append({
                    "id": video_file.stem,
                    "title": video_file.stem,
                    "file_path": str(video_file),
                    "status": "completed",
                    "created_at": datetime.fromtimestamp(video_file.stat().st_mtime).isoformat()
                })
        
        return {"videos": videos}
        
    except Exception as e:
        logger.error(f"Failed to list videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}")
async def get_video(video_id: str):
    """Get video by ID"""
    try:
        # Search for video file
        downloads_dir = Path(settings.DOWNLOADS_DIR)
        video_path = downloads_dir / f"{video_id}.mp4"
        
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="Video not found")
        
        return VideoResponse(
            id=video_id,
            url="",
            title=video_id,
            platform="unknown",
            status="completed",
            file_path=str(video_path),
            created_at=datetime.fromtimestamp(video_path.stat().st_mtime).isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{video_id}")
async def delete_video(video_id: str):
    """Delete a video"""
    try:
        downloads_dir = Path(settings.DOWNLOADS_DIR)
        video_path = downloads_dir / f"{video_id}.mp4"
        
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="Video not found")
        
        video_path.unlink()
        
        return {"message": f"Video {video_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete video: {e}")
        raise HTTPException(status_code=500, detail=str(e))
