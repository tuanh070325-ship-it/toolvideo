"""
Video Translation & Dubbing Service
Inspired by jianchang512/pyvideotrans

Features:
- Extract audio from video
- Transcribe in original language
- Translate to target language
- Generate AI voice in target language
- Replace original audio with new dubbed audio
- Preserve background music
"""

import asyncio
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List

from app.core.logger import logger
from app.core.config import settings


class VideoTranslationService:
    """Service for video translation and AI dubbing"""
    
    SUPPORTED_LANGUAGES = {
        'vi': 'Vietnamese',
        'en': 'English', 
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean',
        'th': 'Thai',
        'id': 'Indonesian',
        'ms': 'Malay',
        'fr': 'French',
        'de': 'German',
        'es': 'Spanish',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ar': 'Arabic',
        'hi': 'Hindi',
    }
    
    # Language to Edge TTS voice mapping
    LANGUAGE_VOICES = {
        'vi': 'vi-VN-HoaiMyNeural',
        'en': 'en-US-JennyNeural',
        'zh': 'zh-CN-XiaoxiaoNeural',
        'ja': 'ja-JP-NanamiNeural',
        'ko': 'ko-KR-SunHiNeural',
        'th': 'th-TH-PremwadeeNeural',
        'id': 'id-ID-GadisNeural',
        'ms': 'ms-MY-YasminNeural',
        'fr': 'fr-FR-DeniseNeural',
        'de': 'de-DE-KatjaNeural',
        'es': 'es-ES-ElviraNeural',
        'pt': 'pt-BR-FranciscaNeural',
        'ru': 'ru-RU-SvetlanaNeural',
        'ar': 'ar-SA-ZariyahNeural',
        'hi': 'hi-IN-SwaraNeural',
    }
    
    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.output_dir = Path(settings.PROCESSED_DIR)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def translate_video(
        self,
        video_path: Path,
        source_language: str = "auto",
        target_language: str = "vi",
        voice: Optional[str] = None,
        preserve_bgm: bool = True,
        output_path: Optional[Path] = None,
        ai_provider: str = "auto"
    ) -> Dict[str, Any]:
        """
        Translate and dub video to target language
        
        Args:
            video_path: Path to input video
            source_language: Source language code or 'auto' for detection
            target_language: Target language code
            voice: TTS voice ID (optional, auto-selected based on language)
            preserve_bgm: Whether to preserve background music
            output_path: Output path (optional)
            ai_provider: AI provider for translation
            
        Returns:
            Dict with translation result
        """
        try:
            job_id = str(uuid.uuid4())[:8]
            output_path = output_path or self.output_dir / f"translated_{job_id}.mp4"
            
            logger.info(f"Translating video to {target_language}: {video_path}")
            
            # Step 1: Extract audio
            logger.info("Step 1: Extracting audio...")
            audio_path = await self._extract_audio(video_path)
            
            # Step 2: Transcribe audio
            logger.info("Step 2: Transcribing audio...")
            transcription = await self._transcribe_audio(
                audio_path, source_language, ai_provider
            )
            
            if not transcription.get('success'):
                return transcription
            
            detected_language = transcription.get('language', source_language)
            original_text = transcription.get('text', '')
            segments = transcription.get('segments', [])
            
            logger.info(f"Detected language: {detected_language}")
            logger.info(f"Transcribed text: {original_text[:200]}...")
            
            # Step 3: Translate text
            logger.info(f"Step 3: Translating to {target_language}...")
            translation = await self._translate_text(
                original_text, detected_language, target_language, ai_provider
            )
            
            if not translation.get('success'):
                return translation
            
            translated_text = translation.get('translated_text', '')
            logger.info(f"Translated text: {translated_text[:200]}...")
            
            # Step 4: Generate TTS audio
            logger.info("Step 4: Generating dubbed audio...")
            voice = voice or self.LANGUAGE_VOICES.get(target_language, 'en-US-JennyNeural')
            tts_result = await self._generate_tts(translated_text, voice)
            
            if not tts_result.get('success'):
                return tts_result
            
            dubbed_audio_path = Path(tts_result['audio_path'])
            
            # Step 5: Handle background music preservation
            if preserve_bgm:
                logger.info("Step 5: Separating and preserving background music...")
                bgm_audio = await self._separate_bgm(audio_path)
                if bgm_audio:
                    dubbed_audio_path = await self._mix_audio(
                        dubbed_audio_path, bgm_audio
                    )
            
            # Step 6: Replace audio in video
            logger.info("Step 6: Replacing audio in video...")
            result = await self._replace_audio(video_path, dubbed_audio_path, output_path)
            
            if result.get('success'):
                result.update({
                    "source_language": detected_language,
                    "target_language": target_language,
                    "original_text": original_text,
                    "translated_text": translated_text,
                    "voice_used": voice
                })
            
            # Cleanup temp files
            audio_path.unlink(missing_ok=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Video translation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _extract_audio(self, video_path: Path) -> Path:
        """Extract audio from video"""
        audio_path = self.temp_dir / f"audio_{uuid.uuid4()[:8]}.wav"
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            str(audio_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        return audio_path
    
    async def _transcribe_audio(
        self, 
        audio_path: Path, 
        language: str,
        ai_provider: str
    ) -> Dict[str, Any]:
        """Transcribe audio using AI"""
        try:
            from app.services.ai.transcription_service import get_transcription_provider
            
            transcriber = await get_transcription_provider(ai_provider)
            result = await transcriber.transcribe(
                audio_path, 
                language=language if language != "auto" else None
            )
            
            return {
                "success": True,
                "text": result.get("text", ""),
                "segments": result.get("segments", []),
                "language": result.get("language", language),
                "duration": result.get("duration", 0)
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _translate_text(
        self,
        text: str,
        source_language: str,
        target_language: str,
        ai_provider: str
    ) -> Dict[str, Any]:
        """Translate text using AI"""
        try:
            from app.services.ai.story_generator import get_story_generator
            
            generator = await get_story_generator(ai_provider)
            
            prompt = f"""Translate the following text from {self.SUPPORTED_LANGUAGES.get(source_language, source_language)} to {self.SUPPORTED_LANGUAGES.get(target_language, target_language)}.
Keep the tone and style natural for the target language. Only output the translation, no explanations.

Text to translate:
{text}"""
            
            translated = await generator.generate_story(
                prompt=prompt,
                max_length=len(text) * 2,
                style="translation",
                language=target_language
            )
            
            return {
                "success": True,
                "translated_text": translated
            }
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_tts(self, text: str, voice: str) -> Dict[str, Any]:
        """Generate TTS audio"""
        try:
            from app.services.ai.tts_provider import get_tts_provider
            
            tts = await get_tts_provider("edge")
            output_path = self.temp_dir / f"tts_{uuid.uuid4()[:8]}.mp3"
            
            audio_path, duration = await tts.synthesize(
                text=text,
                voice=voice,
                output_path=output_path
            )
            
            return {
                "success": True,
                "audio_path": str(audio_path),
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _separate_bgm(self, audio_path: Path) -> Optional[Path]:
        """Separate background music from vocals"""
        try:
            from app.services.audio_separator import audio_separator
            
            result = await audio_separator.separate(audio_path)
            
            if result.get('success') and result.get('instrumental_path'):
                return Path(result['instrumental_path'])
            
            return None
            
        except Exception as e:
            logger.warning(f"BGM separation failed, continuing without: {e}")
            return None
    
    async def _mix_audio(self, vocals: Path, bgm: Path) -> Path:
        """Mix dubbed vocals with background music"""
        try:
            output_path = self.temp_dir / f"mixed_{uuid.uuid4()[:8]}.mp3"
            
            cmd = [
                "ffmpeg", "-y",
                "-i", str(vocals),
                "-i", str(bgm),
                "-filter_complex",
                "[0:a]volume=1.0[a1];[1:a]volume=0.3[a2];[a1][a2]amix=inputs=2:duration=longest",
                "-c:a", "libmp3lame",
                str(output_path)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            return output_path
            
        except Exception as e:
            logger.warning(f"Audio mixing failed, using vocals only: {e}")
            return vocals
    
    async def _replace_audio(
        self, 
        video_path: Path, 
        audio_path: Path, 
        output_path: Path
    ) -> Dict[str, Any]:
        """Replace video audio with new audio"""
        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-i", str(audio_path),
                "-c:v", "copy",
                "-c:a", "aac",
                "-map", "0:v:0",
                "-map", "1:a:0",
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
                "output_path": str(output_path)
            }
            
        except Exception as e:
            logger.error(f"Audio replacement failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def clone_voice(
        self,
        reference_audio: Path,
        text: str,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Clone voice from reference audio (placeholder for future implementation)
        This would use GPT-SoVITS or similar model
        """
        # For now, fallback to standard TTS
        return await self._generate_tts(text, self.LANGUAGE_VOICES.get('vi'))


# Global instance
video_translation = VideoTranslationService()
