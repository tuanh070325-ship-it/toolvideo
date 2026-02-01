"""Opik monitoring and observability service"""

import os
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.core.logger import logger

# Try to import Opik
try:
    import opik
    from opik import track, Opik
    from opik.evaluation import evaluate
    from opik.evaluation.metrics import Hallucination, AnswerRelevance, Moderation
    OPIK_AVAILABLE = True
except ImportError:
    logger.warning("Opik not available. Install with: pip install opik")
    OPIK_AVAILABLE = False
    # Create dummy decorator
    def track(func):
        """Dummy track decorator when opik not available"""
        return func
    Opik = None


class OpikService:
    """Service for monitoring and evaluating LLM/AI operations using Opik"""
    
    def __init__(self, api_key: Optional[str] = None, workspace: Optional[str] = None):
        """Initialize Opik service
        
        Args:
            api_key: Opik API key (defaults to OPIK_API_KEY env var)
            workspace: Opik workspace name (defaults to OPIK_WORKSPACE env var)
        """
        if not OPIK_AVAILABLE:
            logger.warning("Opik monitoring disabled - package not installed")
            self.enabled = False
            return
        
        self.api_key = api_key or os.getenv("OPIK_API_KEY")
        self.workspace = workspace or os.getenv("OPIK_WORKSPACE", "video-tool")
        self.project = os.getenv("OPIK_PROJECT", "production")
        
        if not self.api_key:
            logger.warning("Opik API key not found. Monitoring disabled.")
            self.enabled = False
            return
        
        try:
            # Initialize Opik client
            self.client = Opik(
                api_key=self.api_key,
                workspace=self.workspace,
            )
            self.enabled = True
            logger.info(f"✅ Opik monitoring enabled (workspace: {self.workspace})")
        except Exception as e:
            logger.error(f"Failed to initialize Opik: {e}")
            self.enabled = False
    
    @track
    async def track_video_download(
        self,
        url: str,
        platform: str,
        result: Dict[str, Any],
        duration: float
    ) -> Dict[str, Any]:
        """Track video download operation
        
        Args:
            url: Video URL
            platform: Platform name (tiktok, youtube, etc.)
            result: Download result
            duration: Operation duration in seconds
            
        Returns:
            Tracking metadata
        """
        if not self.enabled:
            return {}
        
        try:
            metadata = {
                "operation": "video_download",
                "platform": platform,
                "url": url,
                "duration": duration,
                "success": "path" in result,
                "file_size": result.get("file_size_mb", 0),
                "resolution": result.get("resolution", "unknown"),
            }
            
            return metadata
        except Exception as e:
            logger.error(f"Failed to track video download: {e}")
            return {}
    
    @track
    async def track_video_generation(
        self,
        prompt: str,
        model: str,
        result: Dict[str, Any],
        duration: float
    ) -> Dict[str, Any]:
        """Track AI video generation
        
        Args:
            prompt: Generation prompt
            model: Model name (e.g., ltx-video)
            result: Generation result
            duration: Operation duration
            
        Returns:
            Tracking metadata
        """
        if not self.enabled:
            return {}
        
        try:
            metadata = {
                "operation": "video_generation",
                "model": model,
                "prompt": prompt,
                "duration": duration,
                "success": "path" in result,
                "num_frames": result.get("num_frames", 0),
                "resolution": result.get("resolution", "unknown"),
                "file_size": result.get("file_size_mb", 0),
            }
            
            return metadata
        except Exception as e:
            logger.error(f"Failed to track video generation: {e}")
            return {}
    
    @track
    async def track_llm_call(
        self,
        model: str,
        prompt: str,
        response: str,
        duration: float,
        tokens_used: Optional[int] = None
    ) -> Dict[str, Any]:
        """Track LLM API call
        
        Args:
            model: LLM model name
            prompt: Input prompt
            response: Model response
            duration: Call duration
            tokens_used: Number of tokens used
            
        Returns:
            Tracking metadata
        """
        if not self.enabled:
            return {}
        
        try:
            metadata = {
                "operation": "llm_call",
                "model": model,
                "prompt_length": len(prompt),
                "response_length": len(response),
                "duration": duration,
                "tokens_used": tokens_used,
            }
            
            return metadata
        except Exception as e:
            logger.error(f"Failed to track LLM call: {e}")
            return {}
    
    @track
    async def track_event(
        self,
        name: str,
        input_data: Optional[Dict] = None,
        output_data: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Track generic event
        
        Args:
            name: Event name
            input_data: Input data
            output_data: Output data
            metadata: Additional metadata
        """
        if not self.enabled:
            return {}
        
        try:
            self.client.log_trace(
                name=name,
                input=input_data or {},
                output=output_data or {},
                metadata=metadata or {}
            )
            return {"success": True}
        except Exception as e:
            logger.error(f"Failed to track event: {e}")
            return {"success": False, "error": str(e)}

    @track
    async def track_video_processing(
        self,
        operation: str,
        input_path: str,
        output_path: str,
        duration: float,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Track video processing operation
        
        Args:
            operation: Operation name (resize, crop, add_captions, etc.)
            input_path: Input video path
            output_path: Output video path
            duration: Processing duration
            metadata: Additional metadata
            
        Returns:
            Tracking metadata
        """
        if not self.enabled:
            return {}
        
        try:
            track_data = {
                "operation": f"video_processing_{operation}",
                "input_path": input_path,
                "output_path": output_path,
                "duration": duration,
                **(metadata or {})
            }
            
            return track_data
        except Exception as e:
            logger.error(f"Failed to track video processing: {e}")
            return {}
    
    async def evaluate_text_quality(
        self,
        text: str,
        reference: Optional[str] = None
    ) -> Dict[str, Any]:
        """Evaluate text quality using Opik metrics
        
        Args:
            text: Text to evaluate
            reference: Reference text (if available)
            
        Returns:
            Evaluation scores
        """
        if not self.enabled:
            return {}
        
        try:
            scores = {}
            
            # Check for hallucination if reference provided
            if reference:
                hallucination_metric = Hallucination()
                scores["hallucination"] = hallucination_metric.score(
                    input=text,
                    output=reference
                )
            
            # Check moderation
            moderation_metric = Moderation()
            scores["moderation"] = moderation_metric.score(input=text)
            
            return scores
        except Exception as e:
            logger.error(f"Failed to evaluate text quality: {e}")
            return {}
    
    async def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict] = None
    ):
        """Log error to Opik
        
        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context
        """
        if not self.enabled:
            return
        
        try:
            self.client.log_trace(
                name=f"error_{error_type}",
                input={"context": context or {}},
                output={"error": error_message},
                metadata={
                    "error_type": error_type,
                    "timestamp": datetime.now().isoformat(),
                }
            )
        except Exception as e:
            logger.error(f"Failed to log error to Opik: {e}")
    
    async def get_metrics_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get summary of metrics for the last N days
        
        Args:
            days: Number of days to look back
            
        Returns:
            Metrics summary
        """
        if not self.enabled:
            return {"error": "Opik not enabled"}
        
        try:
            # TODO: Implement metrics retrieval from Opik API
            return {
                "period_days": days,
                "total_operations": 0,
                "average_duration": 0,
                "error_rate": 0,
            }
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {"error": str(e)}


# Global instance
_opik_service = None

def get_opik_service() -> OpikService:
    """Get global Opik service instance"""
    global _opik_service
    if _opik_service is None:
        _opik_service = OpikService()
    return _opik_service
