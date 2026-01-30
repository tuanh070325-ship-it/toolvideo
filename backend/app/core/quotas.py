
from datetime import datetime, date
from typing import Dict, Optional
import json
from pathlib import Path

from app.core.config import settings
from app.core.logger import logger

class QuotaManager:
    """
    Manages API usage quotas to prevent excessive costs/token usage.
    Tracks usage in a simple JSON file for persistence (sqlite/redis could be used for higher scale).
    """
    
    def __init__(self):
        self.quota_file = Path(settings.DATA_DIR) / "quotas.json"
        self._ensure_quota_file()
        self.limits = {
            "openai": settings.QUOTA_OPENAI_TOKENS_DAILY,
            "gemini": settings.QUOTA_GEMINI_REQUESTS_DAILY,
            "tts_chars": settings.QUOTA_TTS_CHARS_DAILY,
            "video_jobs": settings.QUOTA_VIDEO_JOBS_DAILY
        }

    def _ensure_quota_file(self):
        if not self.quota_file.exists():
            self._save_quotas({})

    def _load_quotas(self) -> Dict:
        try:
            if self.quota_file.exists():
                return json.loads(self.quota_file.read_text())
            return {}
        except Exception as e:
            logger.error(f"Error loading quotas: {e}")
            return {}

    def _save_quotas(self, data: Dict):
        try:
            self.quota_file.parent.mkdir(parents=True, exist_ok=True)
            self.quota_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Error saving quotas: {e}")

    def get_usage(self, provider: str, date_str: str = None) -> int:
        """Get usage for a provider on a specific date (defaults to today)"""
        if not date_str:
            date_str = date.today().isoformat()
            
        quotas = self._load_quotas()
        return quotas.get(date_str, {}).get(provider, 0)

    def check_quota(self, provider: str, estimated_cost: int = 1) -> bool:
        """
        Check if the request would exceed the quota.
        estimated_cost: Number of tokens, chars, or requests.
        """
        if provider not in self.limits or self.limits[provider] == -1:
            return True # No limit
            
        current_usage = self.get_usage(provider)
        if current_usage + estimated_cost > self.limits[provider]:
            logger.warning(f"Quota exceeded for {provider}. Usage: {current_usage}, Limit: {self.limits[provider]}, Cost: {estimated_cost}")
            return False
            
        return True

    def increment_usage(self, provider: str, amount: int = 1):
        """Increment usage counter"""
        try:
            date_str = date.today().isoformat()
            quotas = self._load_quotas()
            
            if date_str not in quotas:
                quotas[date_str] = {}
                
            current = quotas[date_str].get(provider, 0)
            quotas[date_str][provider] = current + amount
            
            self._save_quotas(quotas)
            logger.info(f"Quota usage updated for {provider}: +{amount} (Total: {current + amount})")
        except Exception as e:
            logger.error(f"Error incrementing usage: {e}")

quota_manager = QuotaManager()
