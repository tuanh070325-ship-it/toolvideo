import asyncio
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
import yt_dlp
from app.core.logger import logger

from app.services.platform_detector import PlatformDetector


class VideoDownloader:
    """Download videos from various platforms with enhanced error handling"""

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=60.0,  # Tăng timeout lên 60s
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
            verify=False,  # Bỏ qua SSL verify nếu bị block
        )
        self.detector = PlatformDetector()

    async def download(self, url: str, output_dir: Path) -> dict[str, Any]:
        """Download video from URL with retry mechanism"""
        platform = self.detector.detect(url)
        logger.info(f"Downloading from {platform}: {url}")

        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = int(time.time())

        # Retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if platform == "tiktok":
                    result = await self._download_tiktok(url, output_dir, timestamp)
                elif platform == "douyin":
                    result = await self._download_douyin(url, output_dir, timestamp)
                elif platform == "youtube":
                    result = await self._download_youtube(url, output_dir, timestamp)
                elif platform == "instagram":
                    result = await self._download_instagram(url, output_dir, timestamp)
                else:
                    result = await self._download_generic(url, output_dir, timestamp)

                if not result:
                    raise Exception("Download helper returned None")

                result["platform"] = platform.value
                return result

            except Exception as e:
                logger.error(f"Download attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                    logger.info(f"Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise Exception(f"Failed to download after {max_retries} attempts: {str(e)}")

    async def _download_tiktok(self, url: str, output_dir: Path, timestamp: int) -> dict[str, Any]:
        """Download TikTok video without watermark - Multiple fallbacks"""

        # Method 1: Try TikWM API
        try:
            logger.info("Trying TikWM API...")
            api_url = f"https://www.tikwm.com/api/?url={url}&hd=1"

            response = await self.client.get(api_url, timeout=30.0)
            data = response.json()

            if data.get("code") == 0 and data.get("data"):
                video_data = data["data"]

                # Try HD first, then fall back to SD
                video_url = (
                    video_data.get("hdplay")
                    or video_data.get("play")
                    or video_data.get("wmplay")
                )

                if video_url:
                    output_path = output_dir / f"tiktok_{timestamp}.mp4"
                    await self._download_file(video_url, output_path)

                    return {
                        "path": str(output_path),
                        "title": video_data.get("title", ""),
                        "author": video_data.get("author", {}).get("nickname", ""),
                        "duration": video_data.get("duration", 0),
                        "resolution": "720p" if video_data.get("hdplay") else "480p",
                        "no_watermark": True,
                        "method": "tikwm_api",
                    }
        except Exception as e:
            logger.warning(f"TikWM API failed: {e}")

        # Method 2: Try SnapTik API
        try:
            logger.info("Trying SnapTik API...")
            api_url = f"https://snaptik.app/api.php?url={url}"

            response = await self.client.get(api_url, timeout=30.0)
            data = response.json()

            if data.get("success") and data.get("data"):
                video_url = data["data"].get("download_url")
                if video_url:
                    output_path = output_dir / f"tiktok_{timestamp}.mp4"
                    await self._download_file(video_url, output_path)

                    return {
                        "path": str(output_path),
                        "title": data["data"].get("title", ""),
                        "author": data["data"].get("author", ""),
                        "duration": 0,
                        "resolution": "720p",
                        "no_watermark": True,
                        "method": "snaptik_api",
                    }
        except Exception as e:
            logger.warning(f"SnapTik API failed: {e}")

        # Method 3: Fallback to yt-dlp with custom options
        logger.info("Trying yt-dlp as fallback...")
        try:
            return await self._download_with_ytdlp(
                url=url,
                output_dir=output_dir,
                prefix="tiktok",
                format_selector="best[ext=mp4]/best",
                extra_opts={
                    "http_headers": {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Referer": "https://www.tiktok.com/",
                    },
                    "nocheckcertificate": True,
                    "retries": 5,
                    "fragment_retries": 5,
                },
            )
        except Exception as e:
            logger.warning(
                f"yt-dlp fallback failed for TikTok: {e}. Trying page-scrape fallback..."
            )

            try:
                # Try to fetch page and extract playAddr or og:video URL
                resp = await self.client.get(url, timeout=30.0)
                page_text = resp.content
                text_str = page_text.decode("utf-8", errors="ignore")

                # look for playAddr (common in TikTok page payloads)
                m = re.search(r'"playAddr":"([^\"]+)"', text_str)
                if m:
                    video_url = m.group(1).encode("utf-8").decode("unicode_escape")
                    output_path = output_dir / f"tiktok_{timestamp}.mp4"
                    await self._download_file(video_url, output_path)

                    return {
                        "path": str(output_path),
                        "title": "",
                        "author": "",
                        "duration": 0,
                        "resolution": "unknown",
                        "no_watermark": False,
                        "method": "page_scrape",
                    }

                # fallback: og:video
                m2 = re.search(r'<meta property="og:video" content="([^"]+)"', text_str)
                if m2:
                    video_url = m2.group(1)
                    output_path = output_dir / f"tiktok_{timestamp}.mp4"
                    await self._download_file(video_url, output_path)

                    return {
                        "path": str(output_path),
                        "title": "",
                        "author": "",
                        "duration": 0,
                        "resolution": "unknown",
                        "no_watermark": False,
                        "method": "page_scrape_og",
                    }

            except Exception as e2:
                logger.warning(f"Page scrape fallback failed: {e2}")

            # Reraise original exception so caller records failure
            raise

    async def _download_douyin(self, url: str, output_dir: Path, timestamp: int) -> dict[str, Any]:
        """Download Douyin video"""
        try:
            api_url = f"https://douyin.wtf/api?url={url}"
            response = await self.client.get(api_url, timeout=30.0)
            data = response.json()

            if data.get("status") == "success":
                video_data = data["video_data"]
                video_url = video_data.get("nwm_video_url") or video_data.get("video_url")

                if video_url:
                    output_path = output_dir / f"douyin_{timestamp}.mp4"
                    await self._download_file(video_url, output_path)

                    return {
                        "path": str(output_path),
                        "title": video_data.get("desc", ""),
                        "author": video_data.get("author", {}).get("nickname", ""),
                        "duration": video_data.get("duration", 0),
                        "resolution": "720p",
                        "no_watermark": True,
                        "method": "douyin_api",
                    }
        except Exception as e:
            logger.warning(f"Douyin API failed: {e}")

        # Fallback to yt-dlp
        return await self._download_with_ytdlp(url, output_dir, "douyin")

    async def _download_youtube(self, url: str, output_dir: Path, timestamp: int) -> dict[str, Any]:
        """Download YouTube video"""
        return await self._download_with_ytdlp(
            url=url,
            output_dir=output_dir,
            prefix="youtube",
            format_selector="bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            extra_opts={
                "writeinfojson": True,
                "writethumbnail": True,
                "writesubtitles": False,
                "writeautomaticsub": False,
                "subtitleslangs": ["en", "vi"],
            },
        )

    async def _download_instagram(
        self, url: str, output_dir: Path, timestamp: int
    ) -> dict[str, Any]:
        """Download Instagram video"""
        return await self._download_with_ytdlp(
            url=url, output_dir=output_dir, prefix="instagram", format_selector="best[ext=mp4]/best"
        )

    async def _download_generic(self, url: str, output_dir: Path, timestamp: int) -> dict[str, Any]:
        """Download generic video"""
        try:
            parsed = urlparse(url)
            filename = parsed.path.split("/")[-1] or f"video_{timestamp}"
            if not filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv", ".webm")):
                filename = f"{filename}.mp4"

            output_path = output_dir / filename
            await self._download_file(url, output_path)

            return {
                "path": str(output_path),
                "title": filename,
                "author": "",
                "duration": 0,
                "resolution": "unknown",
                "method": "direct_download",
            }
        except Exception as e:
            logger.error(f"Generic download failed: {e}")
            raise Exception(f"Failed to download video: {str(e)}")

    async def _download_with_ytdlp(
        self,
        url: str,
        output_dir: Path,
        prefix: str,
        format_selector: str = "best[ext=mp4]/best",
        extra_opts: dict = None,
    ) -> dict[str, Any]:
        """Download using yt-dlp with enhanced options and full error logging"""
        import re
        import traceback

        ydl_opts = {
            "format": format_selector,
            "outtmpl": str(output_dir / f"{prefix}_%(id)s.%(ext)s"),
            "quiet": False,
            "no_warnings": False,
            "extract_flat": False,
            "nocheckcertificate": True,
            "retries": 5,
            "fragment_retries": 5,
            "skip_unavailable_fragments": True,
            "keepvideo": False,
            "merge_output_format": "mp4",
            "postprocessors": [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                }
            ],
            # Add realistic User-Agent to avoid bot detection
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-us,en;q=0.5",
                "Sec-Fetch-Mode": "navigate",
            },
        }


        # Merge extra options
        if extra_opts:
            ydl_opts.update(extra_opts)

        # Log download attempt
        logger.info(f"=== yt-dlp Download Attempt ===")
        logger.info(f"URL: {url}")
        logger.info(f"Output Dir: {output_dir}")
        logger.info(f"Format Selector: {format_selector}")
        logger.debug(f"Full options: {ydl_opts}")

        try:
            # Run yt-dlp in thread to avoid blocking
            loop = asyncio.get_event_loop()
            logger.info(f"[yt-dlp] Starting extraction...")
            info = await loop.run_in_executor(None, lambda: self._ytdlp_extract_info(url, ydl_opts))

            if not info:
                logger.error("[yt-dlp] Returned None info")
                raise Exception("Failed to extract video info (info is None)")
            
            logger.info(f"✅ [yt-dlp] Extraction successful! Video ID: {info.get('id')}, Title: {info.get('title', 'N/A')[:50]}")

            video_id = info.get("id", str(int(time.time())))
            ext = info.get("ext", "mp4")
            video_path = output_dir / f"{prefix}_{video_id}.{ext}"

            # Verify file exists
            if not video_path.exists():
                logger.error(f"[yt-dlp] Downloaded file not found: {video_path}")
                raise Exception(f"Downloaded file not found at expected path: {video_path}")
            
            logger.info(f"[yt-dlp] File saved: {video_path} ({video_path.stat().st_size / 1024 / 1024:.2f} MB)")

            # Handle thumbnail
            thumbnail_path = None
            if info.get("thumbnail"):
                try:
                    thumbnail_path = output_dir / f"{prefix}_{video_id}.jpg"
                    await self._download_file(info["thumbnail"], thumbnail_path)
                    logger.info(f"[yt-dlp] Thumbnail saved: {thumbnail_path}")
                except Exception as e:
                    logger.warning(f"[yt-dlp] Failed to download thumbnail: {e}")

            return {
                "path": str(video_path),
                "title": info.get("title", ""),
                "author": info.get("uploader", ""),
                "duration": info.get("duration", 0),
                "resolution": f"{info.get('width', 0)}x{info.get('height', 0)}",
                "description": info.get("description", ""),
                "thumbnail": str(thumbnail_path) if thumbnail_path else None,
                "subtitles": info.get("subtitles", {}),
                "no_watermark": False,
                "method": "yt_dlp",
            }

        except Exception as e:
            # Capture full error details
            error_type = type(e).__name__
            error_msg = str(e)
            full_traceback = traceback.format_exc()
            
            # Remove ANSI color codes
            clean_msg = re.sub(r'\x1b\[[0-9;]*m', '', error_msg)
            
            # Log comprehensive error information
            logger.error(f"❌ [yt-dlp] Download failed!")
            logger.error(f"  → URL: {url}")
            logger.error(f"  → Error Type: {error_type}")
            logger.error(f"  → Error Message (cleaned): {clean_msg}")
            logger.error(f"  → Error Message (raw): {error_msg}")
            logger.error(f"  → Full Traceback:\n{full_traceback}")
            
            # Categorize error for better user feedback
            error_lower = clean_msg.lower()
            
            if "sign in" in error_lower or "login" in error_lower:
                user_msg = "Video requires authentication. Please use a public video URL."
            elif "private" in error_lower:
                user_msg = "Cannot download private videos. Please use a public video URL."
            elif "not available" in error_lower or "unavailable" in error_lower:
                user_msg = "Video is not available (may be deleted, geo-restricted, or platform-blocked)."
            elif "403" in error_lower or "forbidden" in error_lower:
                user_msg = "Access forbidden - video may be region-locked or require authentication."
            elif "404" in error_lower or "not found" in error_lower:
                user_msg = "Video not found - it may have been deleted or the URL is incorrect."
            elif "timeout" in error_lower or "timed out" in error_lower:
                user_msg = "Connection timeout - please check your internet connection and try again."
            elif "429" in error_lower or "rate" in error_lower:
                user_msg = "Rate limited by platform - please wait a few minutes and try again."
            else:
                user_msg = clean_msg
            
            raise Exception(f"Failed to download video with yt-dlp: {user_msg}")

    def _ytdlp_extract_info(self, url: str, opts: dict) -> dict:
        """Extract info using yt-dlp (blocking call) with output logging"""
        
        # Custom logger to capture yt-dlp output
        class YTDLPLogger:
            def debug(self, msg):
                if msg.startswith('[debug] '):
                    logger.debug(f"[yt-dlp] {msg[8:]}")
                else:
                    logger.debug(f"[yt-dlp] {msg}")
            
            def info(self, msg):
                logger.info(f"[yt-dlp] {msg}")
            
            def warning(self, msg):
                logger.warning(f"[yt-dlp] {msg}")
            
            def error(self, msg):
                logger.error(f"[yt-dlp] {msg}")
        
        # Add custom logger to options
        opts['logger'] = YTDLPLogger()
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=True)

    async def _download_file(self, url: str, output_path: Path):
        """Download file from URL with progress logging"""
        try:
            async with self.client.stream("GET", url) as response:
                response.raise_for_status()

                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0
                last_logged_progress = 0

                with open(output_path, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            # Log every 10%
                            if progress >= last_logged_progress + 10:
                                logger.info(f"Download progress: {progress}%")
                                last_logged_progress = progress

                logger.info(f"✅ Downloaded {downloaded:,} bytes to {output_path.name}")

        except Exception as e:
            logger.error(f"File download failed: {e}")
            if output_path.exists():
                output_path.unlink(missing_ok=True)
            raise

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
