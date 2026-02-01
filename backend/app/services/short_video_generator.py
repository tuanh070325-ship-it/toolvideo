"""
Short Video Generator Service
Inspired by RayVentura/ShortGPT and harry0703/MoneyPrinterTurbo

Features:
- Auto-generate scripts from topics/keywords
- Find/download stock footage
- Generate AI narration
- Add captions/subtitles
- Assemble complete short videos (TikTok, Reels, Shorts)
"""

import asyncio
import uuid
import random
from pathlib import Path
from typing import Optional, Dict, Any, List
import json

from app.core.logger import logger
from app.core.config import settings


class ShortVideoGeneratorService:
    """Service for automated short video generation"""
    
    VIDEO_PLATFORMS = {
        'tiktok': {'width': 1080, 'height': 1920, 'max_duration': 180},
        'reels': {'width': 1080, 'height': 1920, 'max_duration': 90},
        'shorts': {'width': 1080, 'height': 1920, 'max_duration': 60},
        'youtube': {'width': 1920, 'height': 1080, 'max_duration': 600},
    }
    
    VIDEO_STYLES = {
        'storytelling': {
            'name': 'Story Narration',
            'description': 'Engaging narrative with background footage',
            'bgm_style': 'cinematic'
        },
        'educational': {
            'name': 'Educational/Tutorial',
            'description': 'Informative content with visual aids',
            'bgm_style': 'upbeat'
        },
        'news': {
            'name': 'News/Facts',
            'description': 'Quick news or interesting facts',
            'bgm_style': 'news'
        },
        'motivation': {
            'name': 'Motivational',
            'description': 'Inspiring quotes and messages',
            'bgm_style': 'inspiring'
        },
        'entertainment': {
            'name': 'Entertainment',
            'description': 'Fun and engaging content',
            'bgm_style': 'cheerful'
        },
        'horror': {
            'name': 'Horror/Creepy',
            'description': 'Scary stories and content',
            'bgm_style': 'dark'
        },
    }
    
    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.output_dir = Path(settings.PROCESSED_DIR)
        self.assets_dir = Path(settings.DATA_DIR) / "assets"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_from_topic(
        self,
        topic: str,
        platform: str = "tiktok",
        style: str = "storytelling",
        duration: int = 60,
        voice: Optional[str] = None,
        language: str = "vi",
        add_captions: bool = True,
        ai_provider: str = "auto"
    ) -> Dict[str, Any]:
        """
        Generate complete short video from a topic
        
        Args:
            topic: Main topic or keyword
            platform: Target platform (tiktok, reels, shorts, youtube)
            style: Content style
            duration: Target duration in seconds
            voice: TTS voice ID
            language: Content language
            add_captions: Whether to add subtitles
            ai_provider: AI provider to use
            
        Returns:
            Dict with generation result
        """
        try:
            job_id = str(uuid.uuid4())[:8]
            work_dir = self.temp_dir / f"shortgen_{job_id}"
            work_dir.mkdir(parents=True, exist_ok=True)
            
            platform_config = self.VIDEO_PLATFORMS.get(platform, self.VIDEO_PLATFORMS['tiktok'])
            style_config = self.VIDEO_STYLES.get(style, self.VIDEO_STYLES['storytelling'])
            
            logger.info(f"Generating {style} video about '{topic}' for {platform}")
            
            # Step 1: Generate script
            logger.info("Step 1: Generating script...")
            script = await self._generate_script(
                topic, style, duration, language, ai_provider
            )
            
            if not script.get('success'):
                return script
            
            script_text = script['script']
            scenes = script.get('scenes', [])
            
            logger.info(f"Script generated: {script_text[:200]}...")
            
            # Step 2: Generate narration audio
            logger.info("Step 2: Generating narration...")
            narration = await self._generate_narration(
                script_text, voice, language
            )
            
            if not narration.get('success'):
                return narration
            
            audio_path = Path(narration['audio_path'])
            audio_duration = narration.get('duration', duration)
            
            # Step 3: Find/generate background footage
            logger.info("Step 3: Finding background footage...")
            footage = await self._find_footage(
                scenes, audio_duration, platform_config, work_dir
            )
            
            if not footage.get('success'):
                # Fallback: generate colored background
                footage = await self._generate_fallback_background(
                    audio_duration, platform_config, work_dir
                )
            
            video_path = Path(footage['video_path'])
            
            # Step 4: Add narration to video
            logger.info("Step 4: Combining audio and video...")
            combined = await self._combine_audio_video(
                video_path, audio_path, work_dir / "combined.mp4"
            )
            
            # Step 5: Add captions/subtitles
            if add_captions:
                logger.info("Step 5: Adding captions...")
                captioned = await self._add_captions(
                    Path(combined['video_path']), 
                    script_text,
                    language,
                    work_dir / "captioned.mp4"
                )
                final_video = Path(captioned.get('video_path', combined['video_path']))
            else:
                final_video = Path(combined['video_path'])
            
            # Step 6: Add background music
            logger.info("Step 6: Adding background music...")
            bgm_style = style_config['bgm_style']
            final_output = self.output_dir / f"short_{platform}_{job_id}.mp4"
            
            result = await self._add_background_music(
                final_video, bgm_style, final_output
            )
            
            # Cleanup
            import shutil
            shutil.rmtree(work_dir, ignore_errors=True)
            
            return {
                "success": True,
                "output_path": str(final_output),
                "job_id": job_id,
                "topic": topic,
                "platform": platform,
                "style": style,
                "duration": audio_duration,
                "script": script_text,
                "scenes": scenes,
                "language": language,
                "has_captions": add_captions
            }
            
        except Exception as e:
            logger.error(f"Short video generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_script(
        self,
        topic: str,
        style: str,
        duration: int,
        language: str,
        ai_provider: str
    ) -> Dict[str, Any]:
        """Generate video script using AI"""
        try:
            from app.services.ai.story_generator import get_story_generator
            
            generator = await get_story_generator(ai_provider)
            
            # Estimate word count based on duration (avg 2.5 words/second for speech)
            word_count = int(duration * 2.5)
            
            style_prompts = {
                'storytelling': f"Write an engaging story about {topic}. Make it dramatic and captivating.",
                'educational': f"Create an educational script explaining {topic}. Be informative and clear.",
                'news': f"Write a news-style report about {topic}. Be factual and concise.",
                'motivation': f"Create a motivational speech about {topic}. Be inspiring and uplifting.",
                'entertainment': f"Write a fun and entertaining script about {topic}. Be humorous and engaging.",
                'horror': f"Write a creepy, scary story about {topic}. Build tension and suspense.",
            }
            
            lang_name = "Vietnamese" if language == "vi" else "English"
            
            prompt = f"""{style_prompts.get(style, style_prompts['storytelling'])}

Requirements:
- Write in {lang_name}
- Target length: approximately {word_count} words (for {duration} seconds of narration)
- Format: Natural spoken language suitable for voiceover
- Include scene descriptions in [brackets] for visual cues
- Make it suitable for short-form video content (TikTok, Reels)

Output the script only, no additional explanations."""
            
            script_text = await generator.generate_story(
                prompt=prompt,
                max_length=word_count * 6,  # Approximate characters
                style=style,
                language=language
            )
            
            # Parse scene descriptions from script
            scenes = self._parse_scenes(script_text)
            
            # Clean script of scene markers for narration
            clean_script = self._clean_script(script_text)
            
            return {
                "success": True,
                "script": clean_script,
                "scenes": scenes,
                "word_count": len(clean_script.split())
            }
            
        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _parse_scenes(self, script: str) -> List[Dict[str, Any]]:
        """Extract scene descriptions from script"""
        import re
        scenes = []
        
        # Find all [bracketed descriptions]
        pattern = r'\[([^\]]+)\]'
        matches = re.findall(pattern, script)
        
        for i, match in enumerate(matches):
            scenes.append({
                "index": i,
                "description": match,
                "keywords": match.lower().split()[:5]
            })
        
        # If no scenes found, create generic ones
        if not scenes:
            scenes = [
                {"index": 0, "description": "opening shot", "keywords": ["intro", "opening"]},
                {"index": 1, "description": "main content", "keywords": ["content", "main"]},
                {"index": 2, "description": "closing shot", "keywords": ["outro", "closing"]}
            ]
        
        return scenes
    
    def _clean_script(self, script: str) -> str:
        """Remove scene markers from script for narration"""
        import re
        return re.sub(r'\[([^\]]+)\]', '', script).strip()
    
    async def _generate_narration(
        self,
        script: str,
        voice: Optional[str],
        language: str
    ) -> Dict[str, Any]:
        """Generate TTS narration"""
        try:
            from app.services.ai.tts_provider import get_tts_provider
            
            # Default voices
            default_voices = {
                'vi': 'vi-VN-HoaiMyNeural',
                'en': 'en-US-JennyNeural',
            }
            
            voice = voice or default_voices.get(language, default_voices['en'])
            
            tts = await get_tts_provider("edge")
            output_path = self.temp_dir / f"narration_{uuid.uuid4()[:8]}.mp3"
            
            audio_path, duration = await tts.synthesize(
                text=script,
                voice=voice,
                output_path=output_path
            )
            
            return {
                "success": True,
                "audio_path": str(audio_path),
                "duration": duration,
                "voice": voice
            }
            
        except Exception as e:
            logger.error(f"Narration generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _find_footage(
        self,
        scenes: List[Dict[str, Any]],
        duration: float,
        platform_config: Dict[str, Any],
        work_dir: Path
    ) -> Dict[str, Any]:
        """Find or generate background footage"""
        try:
            # Try to use local stock footage if available
            stock_dir = self.assets_dir / "stock_videos"
            
            if stock_dir.exists():
                videos = list(stock_dir.glob("*.mp4"))
                if videos:
                    # Use random stock video
                    selected = random.choice(videos)
                    
                    # Resize and loop to match duration
                    output_path = work_dir / "footage.mp4"
                    await self._prepare_footage(
                        selected, output_path, duration, platform_config
                    )
                    
                    return {
                        "success": True,
                        "video_path": str(output_path),
                        "source": "stock"
                    }
            
            # Fallback: Generate gradient background
            return await self._generate_fallback_background(
                duration, platform_config, work_dir
            )
            
        except Exception as e:
            logger.warning(f"Finding footage failed: {e}, using fallback")
            return await self._generate_fallback_background(
                duration, platform_config, work_dir
            )
    
    async def _prepare_footage(
        self,
        input_path: Path,
        output_path: Path,
        duration: float,
        platform_config: Dict[str, Any]
    ):
        """Prepare footage (resize, loop, crop)"""
        width = platform_config['width']
        height = platform_config['height']
        
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1",
            "-i", str(input_path),
            "-t", str(duration),
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}",
            "-c:v", "libx264",
            "-an",
            str(output_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
    
    async def _generate_fallback_background(
        self,
        duration: float,
        platform_config: Dict[str, Any],
        work_dir: Path
    ) -> Dict[str, Any]:
        """Generate a gradient/animated background"""
        try:
            width = platform_config['width']
            height = platform_config['height']
            output_path = work_dir / "background.mp4"
            
            # Generate animated gradient background
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", f"gradients=s={width}x{height}:duration={duration}:speed=0.5:seed={random.randint(0,1000)}",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                str(output_path)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await process.communicate()
            
            # If gradients filter not available, use solid color
            if not output_path.exists() or output_path.stat().st_size == 0:
                colors = ["0x1a1a2e", "0x16213e", "0x0f3460", "0x1e5631", "0x3b0944"]
                color = random.choice(colors)
                
                cmd = [
                    "ffmpeg", "-y",
                    "-f", "lavfi",
                    "-i", f"color=c={color}:s={width}x{height}:d={duration}",
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
            
            return {
                "success": True,
                "video_path": str(output_path),
                "source": "generated"
            }
            
        except Exception as e:
            logger.error(f"Background generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _combine_audio_video(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path
    ) -> Dict[str, Any]:
        """Combine audio and video"""
        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-i", str(audio_path),
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                str(output_path)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            return {
                "success": True,
                "video_path": str(output_path)
            }
            
        except Exception as e:
            logger.error(f"Audio-video combine failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _add_captions(
        self,
        video_path: Path,
        script: str,
        language: str,
        output_path: Path
    ) -> Dict[str, Any]:
        """Add word-by-word captions to video"""
        try:
            from app.services.text_overlay_engine import text_overlay_engine, TextStyle
            
            # Create text segments from script
            words = script.split()
            duration = await self._get_video_duration(video_path)
            
            # Calculate timing for each word
            word_duration = duration / len(words)
            segments = []
            
            for i, word in enumerate(words):
                segments.append({
                    "text": word,
                    "start": i * word_duration,
                    "end": (i + 1) * word_duration
                })
            
            # Apply text overlay
            style = TextStyle(
                font_size=48,
                font_color="#FFFFFF",
                stroke_color="#000000",
                stroke_width=2,
                position="bottom",
                bg_color="rgba(0,0,0,0.5)",
                padding=10
            )
            
            result = await text_overlay_engine.add_text_overlay(
                video_path=video_path,
                output_path=output_path,
                text_segments=segments,
                style=style
            )
            
            return {
                "success": True,
                "video_path": str(output_path)
            }
            
        except Exception as e:
            logger.warning(f"Caption addition failed, continuing without: {e}")
            # Return original video if captions fail
            return {"success": True, "video_path": str(video_path)}
    
    async def _add_background_music(
        self,
        video_path: Path,
        bgm_style: str,
        output_path: Path
    ) -> Dict[str, Any]:
        """Add background music to video"""
        try:
            # Check for BGM files
            bgm_dir = self.assets_dir / "bgm"
            bgm_file = bgm_dir / f"{bgm_style}.mp3"
            
            if not bgm_file.exists():
                # Try any mp3 in bgm folder
                bgm_files = list(bgm_dir.glob("*.mp3")) if bgm_dir.exists() else []
                if bgm_files:
                    bgm_file = random.choice(bgm_files)
                else:
                    # No BGM available, just copy video
                    import shutil
                    shutil.copy(video_path, output_path)
                    return {
                        "success": True,
                        "video_path": str(output_path),
                        "bgm": None
                    }
            
            # Mix BGM with existing audio
            duration = await self._get_video_duration(video_path)
            
            cmd = [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-stream_loop", "-1",
                "-i", str(bgm_file),
                "-t", str(duration),
                "-filter_complex",
                "[0:a]volume=1.0[a1];[1:a]volume=0.15[a2];[a1][a2]amix=inputs=2:duration=shortest[a]",
                "-map", "0:v",
                "-map", "[a]",
                "-c:v", "copy",
                "-c:a", "aac",
                str(output_path)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            return {
                "success": True,
                "video_path": str(output_path),
                "bgm": str(bgm_file)
            }
            
        except Exception as e:
            logger.warning(f"BGM addition failed, copying without BGM: {e}")
            import shutil
            shutil.copy(video_path, output_path)
            return {"success": True, "video_path": str(output_path), "bgm": None}
    
    async def _get_video_duration(self, video_path: Path) -> float:
        """Get video duration"""
        cmd = [
            "ffprobe", "-v", "quiet",
            "-show_entries", "format=duration",
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
            return float(data['format']['duration'])
        except (json.JSONDecodeError, KeyError, ValueError):
            return 60.0
    
    async def batch_generate(
        self,
        topics: List[str],
        platform: str = "tiktok",
        style: str = "storytelling",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Generate multiple videos in batch"""
        results = []
        
        for i, topic in enumerate(topics):
            logger.info(f"Generating video {i+1}/{len(topics)}: {topic}")
            result = await self.generate_from_topic(
                topic=topic,
                platform=platform,
                style=style,
                **kwargs
            )
            results.append({
                "topic": topic,
                "index": i,
                **result
            })
        
        return results
    
    def get_available_styles(self) -> List[Dict[str, Any]]:
        """Get available video styles"""
        return [
            {"id": style_id, **info}
            for style_id, info in self.VIDEO_STYLES.items()
        ]
    
    def get_available_platforms(self) -> List[Dict[str, Any]]:
        """Get available platforms"""
        return [
            {
                "id": platform_id,
                "name": platform_id.title(),
                **info
            }
            for platform_id, info in self.VIDEO_PLATFORMS.items()
        ]


# Global instance
short_video_generator = ShortVideoGeneratorService()
