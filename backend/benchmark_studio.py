
import asyncio
import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path("d:/video_tool/backend")))

from app.services.studio_service import studio_service

async def benchmark():
    topic = "Mẹo rã đông thịt nhanh và an toàn"
    print(f"--- Benchmarking Topic: {topic} ---")
    
    # 1. Generate Ideas
    print("\n[1] Generating Ideas...")
    ideas = await studio_service.generate_ideas(topic)
    print(json.dumps(ideas, indent=2, ensure_ascii=False))
    
    if not ideas:
        print("Failed to generate ideas.")
        return

    # 2. Select the first idea and generate script
    selected_idea = ideas[0]['title']
    char_config = {
        "role": "Bà và cháu gái",
        "addressing": "Bà - Cháu",
        "style": "3D Animation"
    }
    
    print(f"\n[2] Generating Script for: {selected_idea}")
    script = await studio_service.generate_full_script(selected_idea, char_config)
    print(json.dumps(script, indent=2, ensure_ascii=False))
    
    # 3. Test Image Prompt Generation (just the first scene)
    if script and script.get('scenes'):
        first_scene = script['scenes'][0]
        print(f"\n[3] Testing Image Prompt for Scene 1: {first_scene['visual_description']}")
        # Note: We won't actually call the AI image generator to save cost/time, 
        # but we'll inspect the prompt logic in the service.
        
if __name__ == "__main__":
    asyncio.run(benchmark())
