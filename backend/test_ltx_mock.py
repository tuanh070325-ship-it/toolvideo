
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path.cwd()))

from app.services.generation.ltx_video_service import LTXVideoService

async def test_ltx_mock():
    print("\n--- Testing LTX Video Service (Mock) ---")
    try:
        service = LTXVideoService()
        
        # Test text-to-video
        print("Generating Text-to-Video mock...")
        result = await service.generate_video(
            prompt="A cinematic shot of a cyberpunk city",
            width=1280,
            height=720,
            num_frames=30
        )
        
        # Check for path (mock returns 'path', real might return 'video_path')
        video_path = result.get("path") or result.get("video_path")
        
        if video_path and Path(video_path).exists():
            print(f"✅ Text-to-Video success: {video_path}")
        else:
            print(f"❌ Text-to-Video failed: Output file missing. Result: {result}")

        # Test image-to-video (mock)
        print("Generating Image-to-Video mock...")
        # create dummy image
        dummy_img = Path("temp_test_img.jpg")
        dummy_img.touch()
        
        result_i2v = await service.image_to_video(
            image_path=str(dummy_img),
            prompt="Animate this image",
            width=1024,
            height=576
        )
        
        if result_i2v["video_path"] and Path(result_i2v["video_path"]).exists():
             print(f"✅ Image-to-Video success: {result_i2v['video_path']}")
        else:
             print(f"❌ Image-to-Video failed: Output file missing")
             
        # Clean up
        if dummy_img.exists():
            dummy_img.unlink()
            
    except Exception as e:
        print(f"❌ LTX Service Test Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_ltx_mock())
