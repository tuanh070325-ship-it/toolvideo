"""Video processing workflow nodes"""

from typing import Dict, Any
from pathlib import Path
from .base_node import BaseNode, NodeType
from app.core.logger import logger

# Note: VideoDownloader and VideoProcessor will be imported when needed
# to avoid circular dependencies


class VideoDownloadNode(BaseNode):
    """Node for downloading videos from URLs"""
    
    def __init__(self, node_id: str):
        super().__init__(
            node_id=node_id,
            name="Video Download",
            node_type=NodeType.INPUT,
            inputs=["url", "platform"],
            outputs=["video_path", "metadata"],
            description="Download video from URL (TikTok, YouTube, Instagram, etc.)"
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Download video from URL"""
        url = inputs["url"]
        platform = inputs.get("platform", "auto")
        
        logger.info(f"Downloading video from: {url}")
        
        # Import here to avoid circular dependency
        from app.services.video_downloader import VideoDownloader
        downloader = VideoDownloader()
        
        # Download video
        result = await downloader.download(url, platform)
        
        return {
            "video_path": result["path"],
            "metadata": result.get("metadata", {})
        }


class VideoProcessNode(BaseNode):
    """Node for processing videos"""
    
    def __init__(self, node_id: str):
        super().__init__(
            node_id=node_id,
            name="Video Process",
            node_type=NodeType.PROCESS,
            inputs=["video_path", "operations"],
            outputs=["processed_path"],
            description="Process video (resize, crop, add effects, etc.)"
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process video with specified operations"""
        video_path = inputs["video_path"]
        operations = inputs.get("operations", {})
        
        logger.info(f"Processing video: {video_path}")
        
        # Process video based on operations
        output_path = video_path.replace(".mp4", "_processed.mp4")
        
        # TODO: Implement actual video processing
        # For now, just return the input path
        logger.info(f"Video processing operations: {operations}")
        
        return {
            "processed_path": output_path
        }


class VideoExportNode(BaseNode):
    """Node for exporting final video"""
    
    def __init__(self, node_id: str):
        super().__init__(
            node_id=node_id,
            name="Video Export",
            node_type=NodeType.OUTPUT,
            inputs=["video_path", "format", "quality"],
            outputs=["export_path"],
            description="Export video in specified format and quality"
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Export video"""
        video_path = inputs["video_path"]
        format_type = inputs.get("format", "mp4")
        quality = inputs.get("quality", "high")
        
        logger.info(f"Exporting video: {video_path}")
        
        # For now, just copy to output directory
        output_dir = Path("backend/data/outputs/exported")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        export_path = output_dir / f"export_{Path(video_path).name}"
        
        # TODO: Implement actual export with format conversion
        import shutil
        shutil.copy2(video_path, export_path)
        
        return {
            "export_path": str(export_path)
        }


class AddCaptionsNode(BaseNode):
    """Node for adding captions to video"""
    
    def __init__(self, node_id: str):
        super().__init__(
            node_id=node_id,
            name="Add Captions",
            node_type=NodeType.PROCESS,
            inputs=["video_path", "captions", "style"],
            outputs=["captioned_path"],
            description="Add captions/subtitles to video"
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Add captions to video"""
        video_path = inputs["video_path"]
        captions = inputs.get("captions", [])
        style = inputs.get("style", "default")
        
        logger.info(f"Adding captions to: {video_path}")
        
        # TODO: Implement caption addition
        output_path = video_path.replace(".mp4", "_captioned.mp4")
        
        return {
            "captioned_path": output_path
        }



class VideoTrimNode(BaseNode):
    """Node for trimming video"""
    
    def __init__(self, node_id: str):
        super().__init__(
            node_id=node_id,
            name="Video Trim",
            node_type=NodeType.PROCESS,
            inputs=["video_path", "start_time", "end_time"],
            outputs=["output_path"],
            description="Trim video to specified duration"
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Trim video"""
        video_path = inputs["video_path"]
        start_time = float(inputs.get("start_time", 0))
        end_time = float(inputs.get("end_time", 0))
        
        logger.info(f"Trimming video: {video_path} from {start_time} to {end_time}")
        
        from app.services.video_editor import video_editor
        output_path = Path(video_path).parent.parent / "processed" / f"trimmed_{Path(video_path).name}"
        
        result_path = await video_editor.cut_video(
            video_path=Path(video_path),
            start_time=start_time,
            end_time=end_time,
            output_path=output_path
        )
        
        return {
            "output_path": str(result_path)
        }


class VideoResizeNode(BaseNode):
    """Node for resizing video"""
    
    def __init__(self, node_id: str):
        super().__init__(
            node_id=node_id,
            name="Video Resize",
            node_type=NodeType.PROCESS,
            inputs=["video_path", "width", "height", "crop"],
            outputs=["output_path"],
            description="Resize video to specified dimensions"
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Resize video"""
        video_path = inputs["video_path"]
        width = int(inputs.get("width", 1080))
        height = int(inputs.get("height", 1920))
        
        logger.info(f"Resizing video: {video_path} to {width}x{height}")
        
        from app.services.video_editor import video_editor
        
        # Determine platform based on ratio (approximate)
        ratio = width / height
        platform = "tiktok" if ratio < 1 else "youtube"
        
        # Use private method for now or add public resize method to VideoEditor
        # For this fix, we'll use _resize_for_platform but we should really expose a resize method
        # Let's use internal ffmpeg_ops directly or add a resize method to VideoEditor
        # Actually video_editor has _resize_for_platform, but we want custom dimensions
        
        from app.utils.ffmpeg_ops import ffmpeg_ops
        output_path = Path(video_path).parent.parent / "processed" / f"resized_{Path(video_path).name}"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        result_path = await ffmpeg_ops.resize_video(
            input_path=Path(video_path),
            width=width,
            height=height,
            output_path=output_path
        )
        
        return {
            "output_path": str(result_path)
        }


class VideoMergeNode(BaseNode):
    """Node for merging videos"""
    
    def __init__(self, node_id: str):
        super().__init__(
            node_id=node_id,
            name="Video Merge",
            node_type=NodeType.PROCESS,
            inputs=["input_files"],
            outputs=["output_path"],
            description="Merge multiple videos into one"
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge videos"""
        input_files = inputs.get("input_files", [])
        if isinstance(input_files, str):
             # Handle single file or comma-separated
             input_files = [input_files]
             
        logger.info(f"Merging {len(input_files)} videos")
        
        from app.utils.ffmpeg_ops import ffmpeg_ops
        output_path = Path(input_files[0]).parent.parent / "processed" / f"merged_{len(input_files)}_videos.mp4"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        input_paths = [Path(f) for f in input_files]
        await ffmpeg_ops.concatenate_videos(input_paths, output_path)
        
        return {
            "output_path": str(output_path)
        }



class VideoReupNode(BaseNode):
    """Node for auto-reup video processing"""
    
    def __init__(self, node_id: str):
        super().__init__(
            node_id=node_id,
            name="Video Reup",
            node_type=NodeType.PROCESS,
            inputs=["video_path", "audio_path", "platform", "add_captions"],
            outputs=["output_path", "thumbnail_path"],
            description="Process video for reupload (resize, new audio, captions)"
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process video for reup"""
        video_path = inputs["video_path"]
        audio_path = inputs.get("audio_path")
        platform = inputs.get("platform", "tiktok")
        add_captions = inputs.get("add_captions", True)
        
        logger.info(f"Processing reup for {platform}")
        
        from app.services.video_editor import video_editor
        from pathlib import Path
        
        # If audio_path provided, use it
        new_audio = Path(audio_path) if audio_path else None
        
        result = await video_editor.process_video_for_reup(
            video_path=Path(video_path),
            target_platform=platform,
            new_audio_path=new_audio,
            add_text=add_captions,
            # For simplicity in this node, we assume captions are auto-generated 
            # or passed via text_segments if we want to expand inputs later
            text_segments=None # We'll need a separate TranscriptionNode -> segments flow for full captions
        )
        
        if not result["success"]:
            raise Exception(result.get("error", "Unknown error in reup processing"))
            
        return {
            "output_path": result["output_path"],
            "thumbnail_path": result.get("thumbnail_path", "")
        }
