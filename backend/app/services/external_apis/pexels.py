"""
Pexels API Client for Stock Videos and Images

Pexels provides free stock videos and photos with:
- 200 requests/hour free
- No attribution required (but appreciated)
- High quality HD/4K content
- Global CDN delivery

Documentation: https://www.pexels.com/api/documentation/
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from app.core.logger import logger
from app.core.config import settings
from .base import BaseAPIClient, RetryConfig


class PexelsOrientation(Enum):
    """Video/Photo orientation"""
    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"
    SQUARE = "square"


class PexelsSize(Enum):
    """Video size filter"""
    LARGE = "large"
    MEDIUM = "medium"
    SMALL = "small"


@dataclass
class PexelsVideoFile:
    """Video file variant"""
    id: int
    quality: str
    file_type: str
    width: int
    height: int
    fps: float
    link: str
    
    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "PexelsVideoFile":
        return cls(
            id=data.get("id", 0),
            quality=data.get("quality", ""),
            file_type=data.get("file_type", ""),
            width=data.get("width", 0),
            height=data.get("height", 0),
            fps=data.get("fps", 0.0),
            link=data.get("link", ""),
        )


@dataclass
class PexelsVideo:
    """Pexels video result"""
    id: int
    width: int
    height: int
    duration: int
    url: str
    image: str  # Thumbnail
    user: Dict[str, Any]
    video_files: List[PexelsVideoFile]
    video_pictures: List[Dict]
    
    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "PexelsVideo":
        return cls(
            id=data.get("id", 0),
            width=data.get("width", 0),
            height=data.get("height", 0),
            duration=data.get("duration", 0),
            url=data.get("url", ""),
            image=data.get("image", ""),
            user=data.get("user", {}),
            video_files=[PexelsVideoFile.from_response(f) for f in data.get("video_files", [])],
            video_pictures=data.get("video_pictures", []),
        )
    
    def get_best_quality_file(self, max_width: int = 1920) -> Optional[PexelsVideoFile]:
        """Get the best quality file up to max_width"""
        suitable = [f for f in self.video_files if f.width <= max_width and f.file_type == "video/mp4"]
        if not suitable:
            suitable = [f for f in self.video_files if f.file_type == "video/mp4"]
        
        if suitable:
            # Sort by width descending
            suitable.sort(key=lambda x: x.width, reverse=True)
            return suitable[0]
        return None
    
    def get_hd_url(self) -> Optional[str]:
        """Get HD quality video URL"""
        for f in self.video_files:
            if f.quality == "hd" and f.file_type == "video/mp4":
                return f.link
        # Fallback to best available
        best = self.get_best_quality_file()
        return best.link if best else None


@dataclass
class PexelsSearchResult:
    """Search results container"""
    page: int
    per_page: int
    total_results: int
    videos: List[PexelsVideo]
    next_page: Optional[str]
    
    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "PexelsSearchResult":
        return cls(
            page=data.get("page", 1),
            per_page=data.get("per_page", 15),
            total_results=data.get("total_results", 0),
            videos=[PexelsVideo.from_response(v) for v in data.get("videos", [])],
            next_page=data.get("next_page"),
        )


class PexelsClient(BaseAPIClient):
    """
    Client for Pexels Stock Video/Photo API.
    
    Features:
    - Search videos by keyword
    - Filter by orientation, size, duration
    - Get popular videos
    - Curated collections
    
    Rate limits:
    - 200 requests/hour (free)
    - 20,000 requests/month
    
    Usage:
        async with PexelsClient(api_key="...") as client:
            results = await client.search_videos("nature", per_page=10)
            for video in results.videos:
                url = video.get_hd_url()
    """
    
    api_name = "pexels"
    base_url = "https://api.pexels.com"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        retry_config: Optional[RetryConfig] = None,
    ):
        api_key = api_key or getattr(settings, 'PEXELS_API_KEY', None)
        super().__init__(api_key=api_key, timeout=timeout, retry_config=retry_config)
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Pexels uses Authorization header"""
        return {
            "User-Agent": f"VideoTool/{settings.APP_VERSION}",
            "Accept": "application/json",
            "Authorization": self.api_key or "",
        }
    
    async def health_check(self) -> bool:
        """Check if Pexels API is available"""
        try:
            result = await self.search_videos("test", per_page=1)
            return True
        except Exception as e:
            logger.error(f"Pexels health check failed: {e}")
            return False
    
    async def search_videos(
        self,
        query: str,
        orientation: Optional[PexelsOrientation] = None,
        size: Optional[PexelsSize] = None,
        locale: str = "en-US",
        page: int = 1,
        per_page: int = 15,
    ) -> PexelsSearchResult:
        """
        Search for videos by keyword.
        
        Args:
            query: Search keyword
            orientation: Filter by orientation (landscape, portrait, square)
            size: Filter by size (large >= 4K, medium >= Full HD, small >= HD)
            locale: Locale for search (default: en-US)
            page: Page number
            per_page: Results per page (max 80)
            
        Returns:
            PexelsSearchResult with videos
        """
        params = {
            "query": query,
            "locale": locale,
            "page": page,
            "per_page": min(per_page, 80),
        }
        
        if orientation:
            params["orientation"] = orientation.value
        if size:
            params["size"] = size.value
        
        logger.info(f"[Pexels] Searching videos: {query}")
        response = await self.get("/videos/search", params=params)
        
        result = PexelsSearchResult.from_response(response)
        logger.info(f"[Pexels] Found {result.total_results} videos")
        
        return result
    
    async def get_popular_videos(
        self,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
        min_duration: Optional[int] = None,
        max_duration: Optional[int] = None,
        page: int = 1,
        per_page: int = 15,
    ) -> PexelsSearchResult:
        """
        Get popular videos.
        
        Args:
            min_width: Minimum video width
            min_height: Minimum video height
            min_duration: Minimum duration in seconds
            max_duration: Maximum duration in seconds
            page: Page number
            per_page: Results per page
            
        Returns:
            PexelsSearchResult with popular videos
        """
        params = {
            "page": page,
            "per_page": min(per_page, 80),
        }
        
        if min_width:
            params["min_width"] = min_width
        if min_height:
            params["min_height"] = min_height
        if min_duration:
            params["min_duration"] = min_duration
        if max_duration:
            params["max_duration"] = max_duration
        
        logger.info("[Pexels] Fetching popular videos")
        response = await self.get("/videos/popular", params=params)
        
        return PexelsSearchResult.from_response(response)
    
    async def get_video(self, video_id: int) -> PexelsVideo:
        """
        Get a specific video by ID.
        
        Args:
            video_id: Pexels video ID
            
        Returns:
            PexelsVideo object
        """
        response = await self.get(f"/videos/videos/{video_id}")
        return PexelsVideo.from_response(response)
    
    async def find_background_video(
        self,
        theme: str,
        duration_range: tuple = (10, 60),
        orientation: PexelsOrientation = PexelsOrientation.PORTRAIT,
    ) -> Optional[PexelsVideo]:
        """
        Find a suitable background video for content.
        
        Args:
            theme: Theme/keyword to search
            duration_range: (min, max) duration in seconds
            orientation: Video orientation
            
        Returns:
            Best matching PexelsVideo or None
        """
        result = await self.search_videos(
            query=theme,
            orientation=orientation,
            per_page=20,
        )
        
        min_dur, max_dur = duration_range
        suitable = [
            v for v in result.videos
            if min_dur <= v.duration <= max_dur
        ]
        
        if suitable:
            # Return first suitable video
            return suitable[0]
        
        # If no exact match, return any video
        if result.videos:
            return result.videos[0]
        
        return None


# Factory function
def get_pexels_client() -> PexelsClient:
    """Get a Pexels client instance"""
    return PexelsClient()
