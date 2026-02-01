"""AI generation workflow nodes"""

from typing import Dict, Any
from .base_node import BaseNode, NodeType
from app.services.generation import LTXVideoService
from app.core.logger import logger


class LTXGenerationNode(BaseNode):
    """Node for LTX-Video AI generation"""
    
    def __init__(self, node_id: str):
        super().__init__(
            node_id=node_id,
            name="LTX Video Generation",
            node_type=NodeType.PROCESS,
            inputs=["prompt", "negative_prompt", "seed", "num_frames"],
            outputs=["video_path", "metadata"],
            description="Generate video using LTX-Video AI"
        )
        self.service = None
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video from prompt"""
        prompt = inputs["prompt"]
        negative_prompt = inputs.get("negative_prompt")
        seed = inputs.get("seed")
        num_frames = inputs.get("num_frames", 121)
        
        logger.info(f"Generating video: {prompt[:50]}...")
        
        # Initialize service if needed
        if self.service is None:
            self.service = LTXVideoService()
            await self.service.initialize()
        
        # Generate video
        result = await self.service.generate_video(
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
            num_frames=num_frames
        )
        
        return {
            "video_path": result["path"],
            "metadata": result
        }


class ImageToVideoNode(BaseNode):
    """Node for image-to-video generation"""
    
    def __init__(self, node_id: str):
        super().__init__(
            node_id=node_id,
            name="Image to Video",
            node_type=NodeType.PROCESS,
            inputs=["image_path", "prompt", "num_frames"],
            outputs=["video_path", "metadata"],
            description="Animate image using AI"
        )
        self.service = None
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video from image"""
        image_path = inputs["image_path"]
        prompt = inputs["prompt"]
        num_frames = inputs.get("num_frames", 121)
        
        logger.info(f"Animating image: {image_path}")
        
        # Initialize service if needed
        if self.service is None:
            self.service = LTXVideoService()
            await self.service.initialize()
        
        # Generate video
        result = await self.service.image_to_video(
            image_path=image_path,
            prompt=prompt,
            num_frames=num_frames
        )
        
        return {
            "video_path": result["path"],
            "metadata": result
        }


class PromptEnhancerNode(BaseNode):
    """Node for enhancing prompts with AI"""
    
    def __init__(self, node_id: str):
        super().__init__(
            node_id=node_id,
            name="Prompt Enhancer",
            node_type=NodeType.PROCESS,
            inputs=["prompt"],
            outputs=["enhanced_prompt"],
            description="Enhance prompt using AI for better results"
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance prompt"""
        prompt = inputs["prompt"]
        
        logger.info(f"Enhancing prompt: {prompt[:50]}...")
        
        # TODO: Implement prompt enhancement using LLM
        enhanced = f"{prompt}, highly detailed, cinematic lighting, professional quality"
        
        return {
            "enhanced_prompt": enhanced
        }

class TTSGenerationNode(BaseNode):
    """Node for Text-to-Speech generation"""
    
    def __init__(self, node_id: str):
        super().__init__(
            node_id=node_id,
            name="Text to Speech",
            node_type=NodeType.PROCESS,
            inputs=["text", "voice", "provider"],
            outputs=["audio_path"],
            description="Generate speech from text"
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audio from text"""
        text = inputs["text"]
        voice = inputs.get("voice", "alloy")
        provider = inputs.get("provider", "auto")
        
        logger.info(f"Generating speech: {text[:30]}...")
        
        from app.services.generation.tts_service import tts_service
        
        audio_path = await tts_service.generate_speech(
            text=text,
            voice=voice,
            provider=provider
        )
        
        return {
            "audio_path": str(audio_path)
        }
