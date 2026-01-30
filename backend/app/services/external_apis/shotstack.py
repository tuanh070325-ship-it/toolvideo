"""
Shotstack API Client for Video Rendering

Shotstack is a cloud-based video editing API that provides:
- Video rendering with templates
- Text overlays
- Video concatenation
- Audio mixing
- Transitions and effects

Documentation: https://shotstack.io/docs/api/
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from app.core.logger import logger
from app.core.config import settings
from .base import BaseAPIClient, APIError, APIErrorCategory, PollingClient, RetryConfig


class ShotstackRenderStatus(Enum):
    """Status values for Shotstack renders"""
    QUEUED = "queued"
    FETCHING = "fetching"
    RENDERING = "rendering"
    SAVING = "saving"
    DONE = "done"
    FAILED = "failed"


@dataclass
class ShotstackRenderResult:
    """Result of a Shotstack render job"""
    id: str
    status: ShotstackRenderStatus
    url: Optional[str] = None
    poster: Optional[str] = None
    thumbnail: Optional[str] = None
    duration: Optional[float] = None
    render_time: Optional[float] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    error_message: Optional[str] = None
    
    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "ShotstackRenderResult":
        """Create from API response"""
        response_data = data.get("response", data)
        return cls(
            id=response_data.get("id", ""),
            status=ShotstackRenderStatus(response_data.get("status", "queued")),
            url=response_data.get("url"),
            poster=response_data.get("poster"),
            thumbnail=response_data.get("thumbnail"),
            duration=response_data.get("data", {}).get("duration"),
            render_time=response_data.get("renderTime"),
            created=datetime.fromisoformat(response_data["created"]) if response_data.get("created") else None,
            updated=datetime.fromisoformat(response_data["updated"]) if response_data.get("updated") else None,
            error_message=response_data.get("error"),
        )


class ShotstackClient(BaseAPIClient):
    """
    Client for Shotstack Video Editing API.
    
    Features:
    - Create video edits with JSON timeline
    - Add text overlays, transitions
    - Merge multiple video clips
    - Poll for render completion
    - Download rendered videos
    
    Usage:
        async with ShotstackClient(api_key="...") as client:
            result = await client.render_video(timeline)
            final = await client.wait_for_render(result.id)
    """
    
    api_name = "shotstack"
    
    # Shotstack uses sandbox for testing, production for live
    SANDBOX_URL = "https://api.shotstack.io/stage/edit"
    PRODUCTION_URL = "https://api.shotstack.io/edit/v1"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        use_sandbox: bool = True,
        timeout: float = 60.0,
        retry_config: Optional[RetryConfig] = None,
    ):
        api_key = api_key or getattr(settings, 'SHOTSTACK_API_KEY', None)
        super().__init__(api_key=api_key, timeout=timeout, retry_config=retry_config)
        
        self.base_url = self.SANDBOX_URL if use_sandbox else self.PRODUCTION_URL
        self._polling_client = PollingClient(
            poll_interval=3.0,
            max_polls=200,  # ~10 minutes for long renders
            backoff_multiplier=1.2,
            max_interval=15.0,
        )
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Override to use x-api-key header"""
        return {
            "User-Agent": f"VideoTool/{settings.APP_VERSION}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-api-key": self.api_key or "",
        }
    
    async def health_check(self) -> bool:
        """Check if Shotstack API is available"""
        try:
            # Try to get a non-existent render to test connectivity
            await self.get("/render/test-health-check")
            return True
        except APIError as e:
            # 404 is expected, means API is working
            if e.status_code == 404:
                return True
            # Auth errors mean API is up but key is bad
            if e.category == APIErrorCategory.AUTH_ERROR:
                logger.warning("Shotstack API key is invalid")
                return False
            return False
        except Exception as e:
            logger.error(f"Shotstack health check failed: {e}")
            return False
    
    async def render_video(
        self,
        timeline: Dict[str, Any],
        output: Optional[Dict[str, Any]] = None,
        callback: Optional[str] = None,
    ) -> ShotstackRenderResult:
        """
        Submit a video for rendering.
        
        Args:
            timeline: Shotstack timeline definition with tracks, clips, etc.
            output: Output format settings (resolution, fps, etc.)
            callback: Webhook URL for status updates
            
        Returns:
            ShotstackRenderResult with render ID
        """
        # Default output settings
        if output is None:
            output = {
                "format": "mp4",
                "resolution": "hd",  # 1080p
                "fps": 30,
                "quality": "high",
            }
        
        payload = {
            "timeline": timeline,
            "output": output,
        }
        
        if callback:
            payload["callback"] = callback
        
        logger.info(f"[Shotstack] Submitting render job...")
        response = await self.post("/render", json=payload)
        
        result = ShotstackRenderResult.from_response(response)
        logger.info(f"[Shotstack] Render job created: {result.id}")
        
        return result
    
    async def get_render_status(self, render_id: str) -> ShotstackRenderResult:
        """Get the status of a render job"""
        response = await self.get(f"/render/{render_id}")
        return ShotstackRenderResult.from_response(response)
    
    async def wait_for_render(
        self,
        render_id: str,
        on_progress: Optional[Callable[[ShotstackRenderResult], None]] = None,
    ) -> ShotstackRenderResult:
        """
        Wait for a render to complete.
        
        Args:
            render_id: The render job ID
            on_progress: Optional callback for progress updates
            
        Returns:
            Final ShotstackRenderResult with video URL
        """
        async def check_status():
            return await self.get_render_status(render_id)
        
        def is_complete(result: ShotstackRenderResult) -> bool:
            return result.status == ShotstackRenderStatus.DONE
        
        def is_failed(result: ShotstackRenderResult) -> bool:
            return result.status == ShotstackRenderStatus.FAILED
        
        def progress_wrapper(result: ShotstackRenderResult):
            logger.info(f"[Shotstack] Render {render_id}: {result.status.value}")
            if on_progress:
                on_progress(result)
        
        logger.info(f"[Shotstack] Waiting for render {render_id}...")
        return await self._polling_client.poll_until_complete(
            check_status=check_status,
            is_complete=is_complete,
            is_failed=is_failed,
            on_progress=progress_wrapper,
        )
    
    async def render_and_wait(
        self,
        timeline: Dict[str, Any],
        output: Optional[Dict[str, Any]] = None,
        on_progress: Optional[Callable[[ShotstackRenderResult], None]] = None,
    ) -> ShotstackRenderResult:
        """
        Submit a render and wait for completion.
        
        Convenience method that combines render_video and wait_for_render.
        """
        result = await self.render_video(timeline, output)
        return await self.wait_for_render(result.id, on_progress)
    
    # ===================== TIMELINE BUILDERS =====================
    
    @staticmethod
    def create_video_clip(
        src: str,
        start: float = 0,
        length: Optional[float] = None,
        offset: Optional[dict] = None,
        scale: float = 1.0,
        opacity: float = 1.0,
        transition: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """
        Create a video clip asset for the timeline.
        
        Args:
            src: Video URL
            start: Start time in timeline (seconds)
            length: Duration to use from source (auto if None)
            offset: Crop offset {x, y}
            scale: Scale factor (1.0 = original)
            opacity: Opacity (0.0 - 1.0)
            transition: Transition effect {in, out}
        """
        asset = {
            "type": "video",
            "src": src,
        }
        
        if length:
            asset["trim"] = length
        
        if offset:
            asset["offset"] = offset
        
        clip = {
            "asset": asset,
            "start": start,
            "scale": scale,
            "opacity": opacity,
        }
        
        if length:
            clip["length"] = length
        
        if transition:
            clip["transition"] = transition
        
        return clip
    
    @staticmethod
    def create_text_clip(
        text: str,
        start: float,
        length: float,
        style: str = "minimal",
        color: str = "#ffffff",
        size: str = "medium",
        position: str = "bottom",
        background: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a text overlay clip.
        
        Args:
            text: Text content
            start: Start time in timeline
            length: Duration of text display
            style: Text style (minimal, blockbuster, etc.)
            color: Text color (hex)
            size: Text size (small, medium, large, x-large)
            position: Position (top, topRight, right, bottomRight, bottom, bottomLeft, left, topLeft, center)
            background: Background color (hex) or None for transparent
        """
        asset = {
            "type": "title",
            "text": text,
            "style": style,
            "color": color,
            "size": size,
            "position": position,
        }
        
        if background:
            asset["background"] = background
        
        return {
            "asset": asset,
            "start": start,
            "length": length,
        }
    
    @staticmethod
    def create_audio_clip(
        src: str,
        start: float = 0,
        length: Optional[float] = None,
        volume: float = 1.0,
        effect: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create an audio clip.
        
        Args:
            src: Audio URL
            start: Start time in timeline
            length: Duration
            volume: Volume level (0.0 - 1.0)
            effect: Audio effect (fadeIn, fadeOut, fadeInFadeOut)
        """
        asset = {
            "type": "audio",
            "src": src,
            "volume": volume,
        }
        
        if effect:
            asset["effect"] = effect
        
        clip = {
            "asset": asset,
            "start": start,
        }
        
        if length:
            clip["length"] = length
        
        return clip
    
    @staticmethod
    def build_timeline(
        video_clips: List[Dict],
        audio_clips: Optional[List[Dict]] = None,
        text_clips: Optional[List[Dict]] = None,
        background: str = "#000000",
        soundtrack: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Build a complete timeline from clips.
        
        Args:
            video_clips: List of video clips
            audio_clips: List of audio clips
            text_clips: List of text overlay clips
            background: Background color
            soundtrack: Optional soundtrack config
            
        Returns:
            Complete timeline object for render
        """
        tracks = []
        
        # Text overlays on top
        if text_clips:
            tracks.append({"clips": text_clips})
        
        # Video track
        if video_clips:
            tracks.append({"clips": video_clips})
        
        # Audio tracks
        if audio_clips:
            for audio in audio_clips:
                tracks.append({"clips": [audio]})
        
        timeline = {
            "background": background,
            "tracks": tracks,
        }
        
        if soundtrack:
            timeline["soundtrack"] = soundtrack
        
        return timeline


# Factory function
def get_shotstack_client(use_sandbox: bool = True) -> ShotstackClient:
    """Get a Shotstack client instance"""
    return ShotstackClient(use_sandbox=use_sandbox)
