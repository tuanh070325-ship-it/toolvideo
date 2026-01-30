"""
External API Services Package

This package contains integrations with external video processing APIs:
- Shotstack (Video Rendering)
- Pexels (Stock Media)
- Deepgram (Transcription)
- ElevenLabs (TTS)

All clients inherit from BaseAPIClient which provides:
- Retry logic with exponential backoff
- Error mapping and categorization
- Request/response logging
- Rate limit handling
"""

from .base import BaseAPIClient, APIError, APIErrorCategory
from .shotstack import ShotstackClient
from .pexels import PexelsClient

__all__ = [
    "BaseAPIClient",
    "APIError", 
    "APIErrorCategory",
    "ShotstackClient",
    "PexelsClient",
]
