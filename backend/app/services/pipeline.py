"""
Video Processing Pipeline

A clear, modular pipeline for video processing with:
- Well-defined stages (Download → Transcribe → Edit → Render → Export)
- Progress tracking per stage
- Comprehensive logging
- Error handling with retry logic
- Queue support for batch processing

Architecture:
    Pipeline → Stage → Step
    
Each stage has:
- clear inputs/outputs
- progress percentage
- timing information
- error recovery
"""

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic

from app.core.logger import logger
from app.core.config import settings


class PipelineStage(Enum):
    """Stages in the video processing pipeline"""
    UPLOAD = "upload"
    DOWNLOAD = "download"
    TRANSCRIBE = "transcribe"
    ANALYZE = "analyze"
    GENERATE_STORY = "generate_story"
    GENERATE_TTS = "generate_tts"
    EDIT = "edit"
    RENDER = "render"
    EXPORT = "export"
    UPLOAD_OUTPUT = "upload_output"


class StageStatus(Enum):
    """Status of a pipeline stage"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageProgress:
    """Progress information for a single stage"""
    stage: PipelineStage
    status: StageStatus = StageStatus.PENDING
    progress: float = 0.0  # 0-100
    message: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get stage duration in seconds"""
        if self.start_time:
            end = self.end_time or datetime.now(timezone.utc)
            return (end - self.start_time).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "stage": self.stage.value,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass
class PipelineProgress:
    """Overall pipeline progress"""
    job_id: str
    total_stages: int
    completed_stages: int = 0
    current_stage: Optional[PipelineStage] = None
    overall_progress: float = 0.0  # 0-100
    status: str = "pending"  # pending, running, completed, failed
    stages: Dict[str, StageProgress] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get total duration in seconds"""
        if self.start_time:
            end = self.end_time or datetime.now(timezone.utc)
            return (end - self.start_time).total_seconds()
        return None
    
    def calculate_overall_progress(self) -> float:
        """Calculate overall progress from stage progress"""
        if not self.stages:
            return 0.0
        
        stage_weight = 100.0 / len(self.stages)
        total = 0.0
        
        for stage_progress in self.stages.values():
            if stage_progress.status == StageStatus.COMPLETED:
                total += stage_weight
            elif stage_progress.status == StageStatus.RUNNING:
                total += stage_weight * (stage_progress.progress / 100.0)
            elif stage_progress.status == StageStatus.SKIPPED:
                total += stage_weight
        
        return min(total, 100.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "job_id": self.job_id,
            "total_stages": self.total_stages,
            "completed_stages": self.completed_stages,
            "current_stage": self.current_stage.value if self.current_stage else None,
            "overall_progress": self.calculate_overall_progress(),
            "status": self.status,
            "stages": {k: v.to_dict() for k, v in self.stages.items()},
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "error": self.error,
        }


class ProgressCallback:
    """Callback interface for progress updates"""
    
    def __init__(self, callback: Optional[Callable[[PipelineProgress], None]] = None):
        self._callback = callback
    
    def update(self, progress: PipelineProgress):
        """Send progress update"""
        if self._callback:
            self._callback(progress)
    
    async def update_async(self, progress: PipelineProgress):
        """Async progress update"""
        if self._callback:
            if asyncio.iscoroutinefunction(self._callback):
                await self._callback(progress)
            else:
                self._callback(progress)


T = TypeVar('T')


class PipelineContext(Generic[T]):
    """
    Context object passed through pipeline stages.
    
    Carries:
    - Input/output data between stages
    - Configuration
    - Progress tracking
    - Logging
    """
    
    def __init__(
        self,
        job_id: str,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[ProgressCallback] = None,
    ):
        self.job_id = job_id
        self.input_data = input_data
        self.config = config or {}
        self.progress_callback = progress_callback or ProgressCallback()
        
        # Stage outputs
        self.outputs: Dict[str, Any] = {}
        
        # Pipeline progress
        self.pipeline_progress: Optional[PipelineProgress] = None
        
        # Temp files to clean up
        self.temp_files: List[Path] = []
        
        # Debug mode
        self.debug_mode = self.config.get("debug_mode", settings.DEBUG)
    
    def set_output(self, stage: PipelineStage, key: str, value: Any):
        """Set output from a stage"""
        stage_key = stage.value
        if stage_key not in self.outputs:
            self.outputs[stage_key] = {}
        self.outputs[stage_key][key] = value
    
    def get_output(self, stage: PipelineStage, key: str, default: Any = None) -> Any:
        """Get output from a previous stage"""
        return self.outputs.get(stage.value, {}).get(key, default)
    
    def add_temp_file(self, path: Path):
        """Track temp file for cleanup"""
        self.temp_files.append(path)
    
    async def cleanup(self):
        """Clean up temp files"""
        for path in self.temp_files:
            try:
                if path.exists():
                    path.unlink()
                    logger.debug(f"Cleaned up temp file: {path}")
            except Exception as e:
                logger.warning(f"Failed to clean up {path}: {e}")
    
    def log(self, level: str, message: str, **kwargs):
        """Log with job context"""
        extra = {"job_id": self.job_id, **kwargs}
        getattr(logger, level)(f"[Job:{self.job_id}] {message}", extra={"props": extra})


class BasePipelineStage(ABC):
    """
    Base class for pipeline stages.
    
    Each stage:
    1. Validates input
    2. Executes operation
    3. Sets output
    4. Reports progress
    """
    
    stage: PipelineStage = None
    name: str = "base_stage"
    description: str = ""
    
    async def execute(self, context: PipelineContext) -> bool:
        """
        Execute the stage.
        
        Returns:
            True if successful, False if failed
        """
        stage_progress = context.pipeline_progress.stages.get(self.stage.value)
        if not stage_progress:
            return False
        
        try:
            # Start stage
            stage_progress.status = StageStatus.RUNNING
            stage_progress.start_time = datetime.now(timezone.utc)
            stage_progress.message = f"Starting {self.name}..."
            
            context.log("info", f"Stage {self.name} started")
            await context.progress_callback.update_async(context.pipeline_progress)
            
            # Validate inputs
            if not await self.validate(context):
                raise ValueError(f"Validation failed for stage {self.name}")
            
            # Execute stage logic
            result = await self.run(context)
            
            # Complete stage
            stage_progress.status = StageStatus.COMPLETED
            stage_progress.progress = 100.0
            stage_progress.end_time = datetime.now(timezone.utc)
            stage_progress.message = f"Completed {self.name}"
            
            context.pipeline_progress.completed_stages += 1
            context.log("info", f"Stage {self.name} completed in {stage_progress.duration_seconds:.2f}s")
            
            await context.progress_callback.update_async(context.pipeline_progress)
            
            return result
            
        except Exception as e:
            stage_progress.status = StageStatus.FAILED
            stage_progress.error = str(e)
            stage_progress.end_time = datetime.now(timezone.utc)
            stage_progress.message = f"Failed: {str(e)}"
            
            context.log("error", f"Stage {self.name} failed: {e}")
            await context.progress_callback.update_async(context.pipeline_progress)
            
            raise
    
    async def update_progress(self, context: PipelineContext, progress: float, message: str = ""):
        """Update stage progress"""
        stage_progress = context.pipeline_progress.stages.get(self.stage.value)
        if stage_progress:
            stage_progress.progress = progress
            if message:
                stage_progress.message = message
            await context.progress_callback.update_async(context.pipeline_progress)
    
    @abstractmethod
    async def validate(self, context: PipelineContext) -> bool:
        """Validate stage inputs"""
        pass
    
    @abstractmethod
    async def run(self, context: PipelineContext) -> bool:
        """Execute stage logic"""
        pass


class VideoPipeline:
    """
    Video processing pipeline orchestrator.
    
    Usage:
        pipeline = VideoPipeline()
        pipeline.add_stage(DownloadStage())
        pipeline.add_stage(TranscribeStage())
        pipeline.add_stage(EditStage())
        
        result = await pipeline.execute(input_data, config)
    """
    
    def __init__(self, name: str = "video_pipeline"):
        self.name = name
        self.stages: List[BasePipelineStage] = []
        self._stage_map: Dict[PipelineStage, BasePipelineStage] = {}
    
    def add_stage(self, stage: BasePipelineStage) -> "VideoPipeline":
        """Add a stage to the pipeline"""
        self.stages.append(stage)
        self._stage_map[stage.stage] = stage
        return self
    
    def remove_stage(self, stage_type: PipelineStage) -> "VideoPipeline":
        """Remove a stage from the pipeline"""
        self.stages = [s for s in self.stages if s.stage != stage_type]
        self._stage_map.pop(stage_type, None)
        return self
    
    async def execute(
        self,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[PipelineProgress], None]] = None,
    ) -> Dict[str, Any]:
        """
        Execute the pipeline.
        
        Args:
            input_data: Input data for the pipeline
            config: Configuration options
            progress_callback: Callback for progress updates
            
        Returns:
            Pipeline result with outputs from all stages
        """
        job_id = str(uuid.uuid4())[:8]
        
        # Create context
        context = PipelineContext(
            job_id=job_id,
            input_data=input_data,
            config=config,
            progress_callback=ProgressCallback(progress_callback),
        )
        
        # Initialize progress
        context.pipeline_progress = PipelineProgress(
            job_id=job_id,
            total_stages=len(self.stages),
            start_time=datetime.now(timezone.utc),
            status="running",
        )
        
        # Initialize stage progress
        for stage in self.stages:
            context.pipeline_progress.stages[stage.stage.value] = StageProgress(
                stage=stage.stage,
                status=StageStatus.PENDING,
            )
        
        logger.info(f"[Pipeline:{self.name}] Starting job {job_id} with {len(self.stages)} stages")
        
        try:
            # Execute stages
            for stage in self.stages:
                context.pipeline_progress.current_stage = stage.stage
                await context.progress_callback.update_async(context.pipeline_progress)
                
                success = await stage.execute(context)
                
                if not success:
                    raise RuntimeError(f"Stage {stage.name} returned failure")
            
            # Complete pipeline
            context.pipeline_progress.status = "completed"
            context.pipeline_progress.end_time = datetime.now(timezone.utc)
            context.pipeline_progress.current_stage = None
            
            logger.info(
                f"[Pipeline:{self.name}] Job {job_id} completed in "
                f"{context.pipeline_progress.duration_seconds:.2f}s"
            )
            
            return {
                "success": True,
                "job_id": job_id,
                "outputs": context.outputs,
                "progress": context.pipeline_progress.to_dict(),
            }
            
        except Exception as e:
            context.pipeline_progress.status = "failed"
            context.pipeline_progress.error = str(e)
            context.pipeline_progress.end_time = datetime.now(timezone.utc)
            
            logger.error(f"[Pipeline:{self.name}] Job {job_id} failed: {e}")
            
            return {
                "success": False,
                "job_id": job_id,
                "error": str(e),
                "outputs": context.outputs,
                "progress": context.pipeline_progress.to_dict(),
            }
            
        finally:
            # Cleanup temp files if not in debug mode
            if not context.debug_mode:
                await context.cleanup()


# ===================== CONCRETE STAGES =====================

class DownloadStage(BasePipelineStage):
    """Stage for downloading video from URL"""
    
    stage = PipelineStage.DOWNLOAD
    name = "download"
    description = "Download video from URL"
    
    async def validate(self, context: PipelineContext) -> bool:
        """Validate download inputs"""
        url = context.input_data.get("url") or context.input_data.get("video_url")
        if not url:
            raise ValueError("No video URL provided")
        return True
    
    async def run(self, context: PipelineContext) -> bool:
        """Execute download"""
        from app.services.video_downloader import VideoDownloader
        
        url = context.input_data.get("url") or context.input_data.get("video_url")
        output_dir = Path(settings.TEMP_DIR) / context.job_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        await self.update_progress(context, 10, "Initializing download...")
        
        downloader = VideoDownloader()
        try:
            await self.update_progress(context, 30, f"Downloading from {url[:50]}...")
            
            result = await downloader.download(url, output_dir)
            
            await self.update_progress(context, 90, "Download complete")
            
            # Store output
            context.set_output(self.stage, "video_path", result["path"])
            context.set_output(self.stage, "metadata", result)
            context.add_temp_file(Path(result["path"]))
            
            return True
        finally:
            await downloader.close()


class TranscribeStage(BasePipelineStage):
    """Stage for transcribing audio to text"""
    
    stage = PipelineStage.TRANSCRIBE
    name = "transcribe"
    description = "Transcribe audio to text"
    
    async def validate(self, context: PipelineContext) -> bool:
        """Validate transcription inputs"""
        video_path = context.get_output(PipelineStage.DOWNLOAD, "video_path")
        if not video_path or not Path(video_path).exists():
            raise ValueError("No video file found for transcription")
        return True
    
    async def run(self, context: PipelineContext) -> bool:
        """Execute transcription"""
        from app.services.ai.transcription_service import get_transcription_provider
        
        video_path = Path(context.get_output(PipelineStage.DOWNLOAD, "video_path"))
        language = context.config.get("language", "vi")
        
        await self.update_progress(context, 10, "Initializing transcription...")
        
        provider = get_transcription_provider()
        
        await self.update_progress(context, 30, "Transcribing audio...")
        
        result = await provider.transcribe(video_path, language=language)
        
        await self.update_progress(context, 90, "Transcription complete")
        
        # Store output
        context.set_output(self.stage, "transcript", result.get("text", ""))
        context.set_output(self.stage, "segments", result.get("segments", []))
        context.set_output(self.stage, "language", result.get("language", language))
        
        return True


class EditStage(BasePipelineStage):
    """Stage for video editing"""
    
    stage = PipelineStage.EDIT
    name = "edit"
    description = "Edit video (resize, add effects)"
    
    async def validate(self, context: PipelineContext) -> bool:
        """Validate edit inputs"""
        video_path = context.get_output(PipelineStage.DOWNLOAD, "video_path")
        if not video_path or not Path(video_path).exists():
            raise ValueError("No video file found for editing")
        return True
    
    async def run(self, context: PipelineContext) -> bool:
        """Execute editing"""
        from app.services.video_editor import video_editor
        
        video_path = Path(context.get_output(PipelineStage.DOWNLOAD, "video_path"))
        target_platform = context.config.get("target_platform", "tiktok")
        
        await self.update_progress(context, 10, "Preparing video...")
        
        output_path = Path(settings.PROCESSED_DIR) / f"{context.job_id}_edited.mp4"
        
        await self.update_progress(context, 30, f"Editing for {target_platform}...")
        
        result = await video_editor.process_video_for_reup(
            video_path=video_path,
            target_platform=target_platform,
            output_path=output_path,
            add_text=context.config.get("add_text", True),
            text_segments=context.config.get("text_segments"),
            new_audio_path=Path(context.config["audio_path"]) if context.config.get("audio_path") else None,
        )
        
        await self.update_progress(context, 90, "Edit complete")
        
        # Store output
        context.set_output(self.stage, "output_path", result.get("output_path"))
        context.set_output(self.stage, "thumbnail_path", result.get("thumbnail_path"))
        context.set_output(self.stage, "metadata", result)
        
        return result.get("success", False)


class TTSStage(BasePipelineStage):
    """Stage for text-to-speech generation"""
    
    stage = PipelineStage.GENERATE_TTS
    name = "generate_tts"
    description = "Generate AI voice from text"
    
    async def validate(self, context: PipelineContext) -> bool:
        """Validate TTS inputs"""
        text = context.config.get("narration_text") or context.get_output(PipelineStage.GENERATE_STORY, "story_text")
        if not text:
            # TTS is optional, can be skipped
            context.log("info", "No text for TTS, skipping")
            return False
        return True
    
    async def run(self, context: PipelineContext) -> bool:
        """Execute TTS generation"""
        from app.services.ai.tts_provider import get_tts_provider
        
        text = context.config.get("narration_text") or context.get_output(PipelineStage.GENERATE_STORY, "story_text")
        voice = context.config.get("voice", settings.EDGE_TTS_VOICE)
        speed = context.config.get("speed", 1.0)
        
        await self.update_progress(context, 10, "Initializing TTS...")
        
        provider = get_tts_provider()
        
        await self.update_progress(context, 30, f"Generating voice with {voice}...")
        
        audio_path, timing = await provider.synthesize(
            text=text,
            voice=voice,
            speed=speed,
            with_timing=True,
        )
        
        await self.update_progress(context, 90, "TTS complete")
        
        # Store output
        context.set_output(self.stage, "audio_path", str(audio_path))
        context.set_output(self.stage, "word_timing", timing)
        context.add_temp_file(audio_path)
        
        return True


# Factory functions for common pipelines

def create_reup_pipeline() -> VideoPipeline:
    """Create a pipeline for video reup"""
    pipeline = VideoPipeline(name="reup_pipeline")
    pipeline.add_stage(DownloadStage())
    pipeline.add_stage(TranscribeStage())
    pipeline.add_stage(TTSStage())
    pipeline.add_stage(EditStage())
    return pipeline


def create_story_pipeline() -> VideoPipeline:
    """Create a pipeline for story video creation"""
    pipeline = VideoPipeline(name="story_pipeline")
    pipeline.add_stage(DownloadStage())
    pipeline.add_stage(TTSStage())
    pipeline.add_stage(EditStage())
    return pipeline
