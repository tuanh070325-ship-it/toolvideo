"""
TTS Service for Voice Generation
Supports OpenAI and EdgeTTS
"""

from pathlib import Path
from typing import Optional
import uuid
from app.core.config import settings
from app.core.logger import logger

class TTSService:
    """Text-to-Speech Service"""
    
    def __init__(self):
        self.openai_client = None
    
    async def _get_openai_client(self):
        if not self.openai_client and settings.OPENAI_API_KEY:
            try:
                from openai import AsyncOpenAI
                self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            except ImportError:
                logger.warning("OpenAI library not installed")
            except Exception as e:
                logger.error(f"Failed to init OpenAI client: {e}")
        return self.openai_client

    async def generate_speech(
        self,
        text: str,
        output_path: Optional[Path] = None,
        voice: str = "alloy",  # OpenAI: alloy, echo, fable, onyx, nova, shimmer
        provider: str = "auto"  # auto, openai, edge-tts
    ) -> Path:
        """Generate speech from text"""
        
        if not output_path:
            output_path = Path(settings.TEMP_DIR) / f"tts_{uuid.uuid4().hex[:8]}.mp3"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine provider
        if provider == "auto":
            if settings.OPENAI_API_KEY:
                provider = "openai"
                voice = voice if voice in ["alloy", "echo", "f fable", "onyx", "nova", "shimmer"] else "alloy"
            else:
                provider = "edge-tts"
                
        logger.info(f"Generating TTS using {provider} with voice {voice}")
        
        try:
            if provider == "openai":
                return await self._generate_openai(text, voice, output_path)
            elif provider == "edge-tts":
                return await self._generate_edge_tts(text, voice, output_path)
            else:
                raise ValueError(f"Unknown TTS provider: {provider}")
                
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            raise

    async def _generate_openai(self, text: str, voice: str, output_path: Path) -> Path:
        client = await self._get_openai_client()
        if not client:
            raise ValueError("OpenAI client not available (check API key and installation)")
            
        response = await client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        response.stream_to_file(output_path)
        return output_path

    async def _generate_edge_tts(self, text: str, voice: str, output_path: Path) -> Path:
        try:
            import edge_tts
        except ImportError:
            raise ImportError("edge-tts not installed. Run: pip install edge-tts")
            
        # Default voice mapping if OpenAI generic names passed
        voice_map = {
            "alloy": "en-US-GuyNeural",
            "echo": "en-US-ChristopherNeural", 
            "fable": "en-GB-SoniaNeural",
            "onyx": "en-US-EricNeural",
            "nova": "en-US-MichelleNeural",
            "shimmer": "en-US-AnaNeural"
        }
        
        edge_voice = voice_map.get(voice, voice)
        if not edge_voice or edge_voice == "default":
             edge_voice = "en-US-ChristopherNeural" # Good male voice
             
        communicate = edge_tts.Communicate(text, edge_voice)
        await communicate.save(str(output_path))
        
        return output_path

tts_service = TTSService()
