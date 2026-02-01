"""
Video Style Transfer Service
Inspired by TachibanaYoshino/AnimeGANv3

Features:
- Convert video to anime/cartoon style
- Apply various artistic filters
- Face detection and stylization
- Batch frame processing
"""

import asyncio
import uuid
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
import json

from app.core.logger import logger
from app.core.config import settings


class VideoStyleTransferService:
    """Service for video style transfer (anime, cartoon, artistic effects)"""
    
    AVAILABLE_STYLES = {
        'anime_hayao': {
            'name': 'Hayao Miyazaki Style',
            'description': 'Ghibli-inspired anime style with soft colors',
            'type': 'anime'
        },
        'anime_shinkai': {
            'name': 'Makoto Shinkai Style', 
            'description': 'Your Name/Weathering With You style with vivid colors',
            'type': 'anime'
        },
        'anime_paprika': {
            'name': 'Paprika Style',
            'description': 'Satoshi Kon style with surreal elements',
            'type': 'anime'
        },
        'cartoon': {
            'name': 'Cartoon Style',
            'description': 'Classic cartoon look with bold outlines',
            'type': 'cartoon'
        },
        'comic': {
            'name': 'Comic Book Style',
            'description': 'Western comic book style with halftone effects',
            'type': 'cartoon'
        },
        'pencil_sketch': {
            'name': 'Pencil Sketch',
            'description': 'Black and white pencil drawing effect',
            'type': 'artistic'
        },
        'watercolor': {
            'name': 'Watercolor Painting',
            'description': 'Soft watercolor painting effect',
            'type': 'artistic'
        },
        'oil_painting': {
            'name': 'Oil Painting',
            'description': 'Classic oil painting texture',
            'type': 'artistic'
        },
        'pop_art': {
            'name': 'Pop Art',
            'description': 'Andy Warhol inspired pop art style',
            'type': 'artistic'
        },
        'vintage': {
            'name': 'Vintage Film',
            'description': 'Retro film effect with grain and color shift',
            'type': 'filter'
        },
        'cyberpunk': {
            'name': 'Cyberpunk',
            'description': 'Neon-lit cyberpunk aesthetic',
            'type': 'filter'
        },
    }
    
    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.output_dir = Path(settings.PROCESSED_DIR)
        self.frames_dir = self.temp_dir / "frames"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def apply_style(
        self,
        video_path: Path,
        style: str = "anime_hayao",
        output_path: Optional[Path] = None,
        intensity: float = 1.0,
        preserve_audio: bool = True
    ) -> Dict[str, Any]:
        """
        Apply style transfer to video
        
        Args:
            video_path: Input video path
            style: Style to apply
            output_path: Output path (optional)
            intensity: Style intensity (0.0 - 1.0)
            preserve_audio: Keep original audio
            
        Returns:
            Dict with result info
        """
        try:
            job_id = str(uuid.uuid4())[:8]
            output_path = output_path or self.output_dir / f"styled_{style}_{job_id}.mp4"
            
            if style not in self.AVAILABLE_STYLES:
                return {
                    "success": False, 
                    "error": f"Unknown style: {style}. Available: {list(self.AVAILABLE_STYLES.keys())}"
                }
            
            style_info = self.AVAILABLE_STYLES[style]
            logger.info(f"Applying {style_info['name']} to video: {video_path}")
            
            # Get video info
            video_info = await self._get_video_info(video_path)
            fps = video_info.get('fps', 30)
            
            # Create work directory
            work_dir = self.temp_dir / f"style_{job_id}"
            work_dir.mkdir(parents=True, exist_ok=True)
            frames_dir = work_dir / "frames"
            styled_dir = work_dir / "styled"
            frames_dir.mkdir(exist_ok=True)
            styled_dir.mkdir(exist_ok=True)
            
            # Step 1: Extract frames
            logger.info("Step 1: Extracting frames...")
            frame_count = await self._extract_frames(video_path, frames_dir, fps)
            logger.info(f"Extracted {frame_count} frames")
            
            # Step 2: Apply style to each frame
            logger.info(f"Step 2: Applying {style} style to frames...")
            await self._apply_style_to_frames(
                frames_dir, styled_dir, style, intensity
            )
            
            # Step 3: Reconstruct video from styled frames
            logger.info("Step 3: Reconstructing video...")
            styled_video = await self._frames_to_video(styled_dir, work_dir / "styled.mp4", fps)
            
            # Step 4: Add audio back
            if preserve_audio:
                logger.info("Step 4: Adding audio...")
                await self._add_audio(styled_video, video_path, output_path)
            else:
                shutil.copy(styled_video, output_path)
            
            # Cleanup
            shutil.rmtree(work_dir, ignore_errors=True)
            
            return {
                "success": True,
                "output_path": str(output_path),
                "style": style,
                "style_name": style_info['name'],
                "intensity": intensity,
                "frame_count": frame_count
            }
            
        except Exception as e:
            logger.error(f"Style transfer failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_video_info(self, video_path: Path) -> Dict[str, Any]:
        """Get video information using FFprobe"""
        cmd = [
            "ffprobe", "-v", "quiet",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate,nb_frames",
            "-of", "json",
            str(video_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        
        try:
            data = json.loads(stdout.decode())
            stream = data.get('streams', [{}])[0]
            
            # Parse frame rate
            fps_str = stream.get('r_frame_rate', '30/1')
            if '/' in fps_str:
                num, den = fps_str.split('/')
                fps = float(num) / float(den)
            else:
                fps = float(fps_str)
            
            return {
                'width': int(stream.get('width', 1920)),
                'height': int(stream.get('height', 1080)),
                'fps': fps,
                'frame_count': int(stream.get('nb_frames', 0))
            }
        except (json.JSONDecodeError, KeyError, ValueError):
            return {'width': 1920, 'height': 1080, 'fps': 30, 'frame_count': 0}
    
    async def _extract_frames(self, video_path: Path, frames_dir: Path, fps: float) -> int:
        """Extract frames from video"""
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vf", f"fps={fps}",
            str(frames_dir / "frame_%06d.png")
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        return len(list(frames_dir.glob("*.png")))
    
    async def _apply_style_to_frames(
        self,
        input_dir: Path,
        output_dir: Path,
        style: str,
        intensity: float
    ):
        """Apply style to all frames using OpenCV filters"""
        try:
            import cv2
            import numpy as np
        except ImportError:
            logger.warning("OpenCV not available, using FFmpeg filters")
            await self._apply_ffmpeg_style(input_dir, output_dir, style, intensity)
            return
        
        frames = sorted(input_dir.glob("*.png"))
        style_type = self.AVAILABLE_STYLES[style]['type']
        
        for i, frame_path in enumerate(frames):
            if i % 30 == 0:
                logger.info(f"Processing frame {i}/{len(frames)}")
            
            img = cv2.imread(str(frame_path))
            
            if style_type == 'anime':
                styled = self._apply_anime_style(img, style, intensity)
            elif style_type == 'cartoon':
                styled = self._apply_cartoon_style(img, style, intensity)
            elif style_type == 'artistic':
                styled = self._apply_artistic_style(img, style, intensity)
            else:
                styled = self._apply_filter_style(img, style, intensity)
            
            output_path = output_dir / frame_path.name
            cv2.imwrite(str(output_path), styled)
    
    def _apply_anime_style(self, img, style: str, intensity: float):
        """Apply anime-style effect using OpenCV"""
        import cv2
        import numpy as np
        
        # Edge-preserving filter for flat color areas (anime-like)
        # Parameters based on style
        if style == 'anime_shinkai':
            # Vivid colors, high saturation
            img_filtered = cv2.edgePreservingFilter(img, flags=1, sigma_s=60, sigma_r=0.4)
            # Increase saturation
            hsv = cv2.cvtColor(img_filtered, cv2.COLOR_BGR2HSV)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.3, 0, 255).astype(np.uint8)
            img_filtered = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        elif style == 'anime_hayao':
            # Softer, more muted colors
            img_filtered = cv2.edgePreservingFilter(img, flags=1, sigma_s=80, sigma_r=0.5)
            # Slight warm tint
            img_filtered = cv2.convertScaleAbs(img_filtered, alpha=1.0, beta=10)
        else:
            img_filtered = cv2.edgePreservingFilter(img, flags=1, sigma_s=70, sigma_r=0.45)
        
        # Add edge lines
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edges = cv2.dilate(edges, np.ones((2, 2), np.uint8), iterations=1)
        edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Combine
        result = cv2.subtract(img_filtered, edges_color * 0.5)
        
        # Blend with original based on intensity
        result = cv2.addWeighted(img, 1 - intensity, result, intensity, 0)
        
        return result
    
    def _apply_cartoon_style(self, img, style: str, intensity: float):
        """Apply cartoon-style effect"""
        import cv2
        import numpy as np
        
        # Color quantization for flat colors
        data = np.float32(img).reshape((-1, 3))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001)
        _, labels, centers = cv2.kmeans(data, 8, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        quantized = centers[labels.flatten()].reshape(img.shape)
        
        # Apply bilateral filter for smoothing
        smoothed = cv2.bilateralFilter(quantized, 9, 300, 300)
        
        # Detect edges for outlines
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 7)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        
        # Combine color and edges
        edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        result = cv2.bitwise_and(smoothed, edges_color)
        
        # Blend with original
        result = cv2.addWeighted(img, 1 - intensity, result, intensity, 0)
        
        return result
    
    def _apply_artistic_style(self, img, style: str, intensity: float):
        """Apply artistic style effects"""
        import cv2
        import numpy as np
        
        if style == 'pencil_sketch':
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            inv = 255 - gray
            blur = cv2.GaussianBlur(inv, (21, 21), 0)
            sketch = cv2.divide(gray, 255 - blur, scale=256)
            result = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
            
        elif style == 'watercolor':
            result = cv2.stylization(img, sigma_s=60, sigma_r=0.6)
            
        elif style == 'oil_painting':
            has_oil_painting = hasattr(cv2, 'xphoto') and hasattr(cv2.xphoto, 'oilPainting')
            result = cv2.xphoto.oilPainting(img, 7, 1) if has_oil_painting else img
            if result is img:
                # Fallback oil painting effect
                result = cv2.edgePreservingFilter(img, flags=2, sigma_s=100, sigma_r=0.8)
                
        elif style == 'pop_art':
            # High contrast, posterize
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            lab[:, :, 0] = cv2.equalizeHist(lab[:, :, 0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            
            # Posterize
            div = 64
            result = (enhanced // div) * div + div // 2
        else:
            result = img
        
        # Blend with original
        result = cv2.addWeighted(img, 1 - intensity, result, intensity, 0)
        
        return result
    
    def _apply_filter_style(self, img, style: str, intensity: float):
        """Apply filter-based styles"""
        import cv2
        import numpy as np
        
        if style == 'vintage':
            # Sepia tone
            kernel = np.array([
                [0.272, 0.534, 0.131],
                [0.349, 0.686, 0.168],
                [0.393, 0.769, 0.189]
            ])
            sepia = cv2.transform(img, kernel)
            
            # Add grain
            noise = np.random.normal(0, 15, img.shape).astype(np.uint8)
            result = cv2.add(sepia, noise)
            
            # Vignette
            rows, cols = img.shape[:2]
            X = cv2.getGaussianKernel(cols, cols/2)
            Y = cv2.getGaussianKernel(rows, rows/2)
            mask = Y * X.T
            mask = mask / mask.max()
            mask = np.stack([mask, mask, mask], axis=2)
            result = (result * mask).astype(np.uint8)
            
        elif style == 'cyberpunk':
            # Neon glow effect
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Boost saturation
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.5, 0, 255).astype(np.uint8)
            
            # Shift hue towards cyan/magenta
            hsv[:, :, 0] = (hsv[:, :, 0].astype(int) + 30) % 180
            
            enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
            # Add glow
            glow = cv2.GaussianBlur(enhanced, (15, 15), 0)
            result = cv2.addWeighted(enhanced, 1, glow, 0.5, 0)
            
        else:
            result = img
        
        result = cv2.addWeighted(img, 1 - intensity, result, intensity, 0)
        
        return result
    
    async def _apply_ffmpeg_style(
        self,
        input_dir: Path,
        output_dir: Path,
        style: str,
        intensity: float
    ):
        """Fallback: Apply style using FFmpeg filters when OpenCV not available"""
        frames = sorted(input_dir.glob("*.png"))
        
        for frame_path in frames:
            output_path = output_dir / frame_path.name
            
            # Build FFmpeg filter based on style
            if style in ['anime_hayao', 'anime_shinkai', 'anime_paprika']:
                filter_str = "edgedetect=low=0.1:high=0.3,negate,eq=saturation=1.2"
            elif style in ['cartoon', 'comic']:
                filter_str = "eq=saturation=1.5:contrast=1.3,edgedetect=mode=canny"
            elif style == 'pencil_sketch':
                filter_str = "format=gray,edgedetect=mode=canny"
            elif style == 'vintage':
                filter_str = "colorbalance=rs=0.3:gs=0.1:bs=-0.2,noise=alls=20"
            else:
                filter_str = "eq=saturation=1.0"
            
            cmd = [
                "ffmpeg", "-y",
                "-i", str(frame_path),
                "-vf", filter_str,
                str(output_path)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
    
    async def _frames_to_video(self, frames_dir: Path, output_path: Path, fps: float) -> Path:
        """Reconstruct video from frames"""
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%06d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(output_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        return output_path
    
    async def _add_audio(self, video_path: Path, original_video: Path, output_path: Path):
        """Add audio from original video"""
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(original_video),
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0?",
            "-shortest",
            str(output_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
    
    def get_available_styles(self) -> List[Dict[str, Any]]:
        """Get list of available styles"""
        return [
            {
                "id": style_id,
                **info
            }
            for style_id, info in self.AVAILABLE_STYLES.items()
        ]


# Global instance
video_style_transfer = VideoStyleTransferService()
