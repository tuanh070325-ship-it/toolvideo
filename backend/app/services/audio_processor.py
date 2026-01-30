"""
Audio processing service for extracting, converting, and mixing audio
"""

from pathlib import Path
from typing import Optional, Tuple
import asyncio
from app.core.logger import logger
from app.core.config import settings
from app.utils.ffmpeg_ops import ffmpeg_ops
import uuid

class AudioProcessor: 
    """Handle audio operations"""

    async def process_final_mix(
        self,
        voice_path: Path,
        bgm_path: Optional[Path] = None,
        bgm_volume: float = 0.12,
        ducking: bool = True
    ) -> Path:
        """
        Process the final audio mix for video.
        1. Normalize voice for consistent loudness.
        2. Mix with BGM using auto-ducking (if BGM provided).
        """
        try:
            logger.info(f"Processing final audio mix: Voice={voice_path}, BGM={bgm_path}")
            
            # Step 1: Normalize Voice
            norm_voice_path = Path(settings.TEMP_DIR) / f"norm_{voice_path.name}"
            await ffmpeg_ops.normalize_audio(voice_path, norm_voice_path)
            
            if not bgm_path:
                return norm_voice_path
                
            # Step 2: Mix with BGM
            output_path = Path(settings.TEMP_DIR) / f"mixed_{uuid.uuid4().hex[:8]}.m4a"
            final_path = await ffmpeg_ops.add_background_music(
                voice_path=norm_voice_path,
                bgm_path=bgm_path,
                output_path=output_path,
                bgm_volume=bgm_volume,
                ducking=ducking
            )
            
            return final_path

        except Exception as e:
            logger.error(f"Final mix processing error: {e}")
            return voice_path # Fallback to original voice


    async def extract_audio(self, video_path: Path) -> Path:
        """Extract audio from video"""
        return await ffmpeg_ops.extract_audio(
            video_path,
            Path(settings.TEMP_DIR) / f"audio_{video_path.stem}.wav",
        )

    async def get_audio_duration(self, audio_path: Path) -> float:
        """Get audio duration in seconds"""
        try:
            import wave
            with wave.open(str(audio_path), 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration = frames / float(rate)
                return duration
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0.0

    async def create_silence(self, duration: float, output_path: Path) -> Path:
        """Create silence audio file"""
        try:
            import wave
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            sample_rate = 44100
            num_frames = int(duration * sample_rate)
            
            with wave. open(str(output_path), 'w') as wav_file:
                wav_file.setnchannels(2)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(b'\x00\x00' * num_frames * 2)
            
            logger.info(f"Silence created:  {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error creating silence: {e}")
            raise


audio_processor = AudioProcessor()