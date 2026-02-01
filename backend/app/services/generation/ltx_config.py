"""Configuration for LTX-Video generation service"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List


@dataclass
class LTXConfig:
    """Configuration for LTX-Video generation"""
    
    # Model settings
    model_path: str = field(
        default="models/ltx-video/ltxv-13b-0.9.8-distilled.safetensors",
        metadata={"help": "Path to LTX-Video model checkpoint"}
    )
    text_encoder_path: str = field(
        default="google/t5-v1_1-xxl",
        metadata={"help": "Path to T5 text encoder"}
    )
    precision: str = field(
        default="bfloat16",
        metadata={"help": "Model precision: bfloat16, float8_e4m3fn, or mixed_precision"}
    )
    device: str = field(
        default="cuda",
        metadata={"help": "Device to run on: cuda, mps, or cpu"}
    )
    
    # Generation settings
    height: int = field(
        default=704,
        metadata={"help": "Height of output video"}
    )
    width: int = field(
        default=1216,
        metadata={"help": "Width of output video"}
    )
    num_frames: int = field(
        default=121,
        metadata={"help": "Number of frames to generate"}
    )
    frame_rate: int = field(
        default=30,
        metadata={"help": "Frame rate of output video"}
    )
    
    # Inference settings
    num_inference_steps: int = field(
        default=50,
        metadata={"help": "Number of denoising steps"}
    )
    guidance_scale: float = field(
        default=3.0,
        metadata={"help": "Classifier-free guidance scale"}
    )
    negative_prompt: str = field(
        default="worst quality, inconsistent motion, blurry, jittery, distorted",
        metadata={"help": "Negative prompt"}
    )
    
    # Advanced settings
    offload_to_cpu: bool = field(
        default=False,
        metadata={"help": "Offload model to CPU when not in use"}
    )
    enhance_prompt: bool = field(
        default=False,
        metadata={"help": "Use AI to enhance prompts"}
    )
    image_cond_noise_scale: float = field(
        default=0.15,
        metadata={"help": "Noise scale for image conditioning"}
    )
    
    # Output settings
    output_dir: Path = field(
        default_factory=lambda: Path("backend/data/outputs/generated"),
        metadata={"help": "Output directory for generated videos"}
    )
    
    @classmethod
    def from_env(cls) -> "LTXConfig":
        """Create config from environment variables"""
        return cls(
            model_path=os.getenv("LTX_MODEL_PATH", cls.model_path),
            text_encoder_path=os.getenv("LTX_TEXT_ENCODER_PATH", cls.text_encoder_path),
            precision=os.getenv("LTX_PRECISION", cls.precision),
            device=os.getenv("LTX_DEVICE", cls.device),
            height=int(os.getenv("LTX_HEIGHT", cls.height)),
            width=int(os.getenv("LTX_WIDTH", cls.width)),
            num_frames=int(os.getenv("LTX_NUM_FRAMES", cls.num_frames)),
            frame_rate=int(os.getenv("LTX_FRAME_RATE", cls.frame_rate)),
            num_inference_steps=int(os.getenv("LTX_INFERENCE_STEPS", cls.num_inference_steps)),
            guidance_scale=float(os.getenv("LTX_GUIDANCE_SCALE", cls.guidance_scale)),
            offload_to_cpu=os.getenv("LTX_OFFLOAD_CPU", "false").lower() == "true",
            enhance_prompt=os.getenv("LTX_ENHANCE_PROMPT", "false").lower() == "true",
        )
    
    def validate(self) -> bool:
        """Validate configuration"""
        # Check if model path exists
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        
        # Validate dimensions (must be divisible by 32)
        if self.height % 32 != 0:
            raise ValueError(f"Height must be divisible by 32, got {self.height}")
        if self.width % 32 != 0:
            raise ValueError(f"Width must be divisible by 32, got {self.width}")
        
        # Validate num_frames (must be N*8+1)
        if (self.num_frames - 1) % 8 != 0:
            raise ValueError(f"num_frames must be N*8+1, got {self.num_frames}")
        
        # Validate device
        if self.device not in ["cuda", "mps", "cpu"]:
            raise ValueError(f"Invalid device: {self.device}")
        
        return True
