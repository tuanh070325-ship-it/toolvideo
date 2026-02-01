"""
Quick Start: Edit Your Downloaded Videos
Run this to test video editing features
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

print("🎬 Video Editing Quick Start\n")
print("="*70)

# Check available videos
print("\n📁 Checking downloaded videos...")
response = requests.get(f"{BASE_URL}/videos")
videos = response.json().get("videos", [])

if not videos:
    print("❌ No videos found. Please download a video first!")
    print("\nTo download:")
    print(f"  curl -X POST {BASE_URL}/videos/download \\")
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}\'')
    exit(1)

print(f"✅ Found {len(videos)} video(s):")
for i, video in enumerate(videos, 1):
    print(f"  {i}. {video['title']} ({video['file_path']})")

# Use first video for demo
demo_video = videos[0]
print(f"\n🎯 Using: {demo_video['title']}")
print(f"   Path: {demo_video['file_path']}")

# Example 1: Trim video
print("\n" + "="*70)
print("Example 1: Trim Video (First 30 seconds)")
print("="*70)

trim_workflow = {
    "name": "Quick Trim Demo",
    "description": "Trim to first 30 seconds",
    "nodes": [{
        "type": "trim",
        "input_file": demo_video['file_path'],
        "start_time": 0,
        "end_time": 30,
        "output_file": "data/processed/demo_trimmed.mp4"
    }]
}

print(f"\n📝 Workflow:")
print(json.dumps(trim_workflow, indent=2))

print("\n🚀 To execute this workflow, run:")
print(f"curl -X POST {BASE_URL}/workflows/execute \\")
print('  -H "Content-Type: application/json" \\')
print(f"  -d '{json.dumps(trim_workflow)}'")

# Example 2: Resize for TikTok/Shorts
print("\n" + "="*70)
print("Example 2: Resize for TikTok/Shorts (1080x1920)")
print("="*70)

resize_workflow = {
    "name": "Resize to Vertical",
    "description": "Convert to 9:16 format",
    "nodes": [{
        "type": "resize",
        "input_file": demo_video['file_path'],
        "width": 1080,
        "height": 1920,
        "output_file": "data/processed/demo_vertical.mp4"
    }]
}

print(f"\n📝 Workflow:")
print(json.dumps(resize_workflow, indent=2))

# Summary
print("\n" + "="*70)
print("📚 Next Steps:")
print("="*70)
print("\n1. Test trim workflow:")
print(f"   python -c \"import requests; r=requests.post('{BASE_URL}/workflows/execute', json={trim_workflow}); print(r.json())\"")

print("\n2. Check processed videos:")
print("   dir data\\processed")

print("\n3. View full guide:")
print("   Open: C:\\Users\\Admin\\.gemini\\antigravity\\brain\\fb01a11d-967d-4372-b5f7-a0a9bc4612bc\\video_editing_guide.md")

print("\n4. Create custom workflow:")
print("   - Open http://localhost:3000/workflows")
print("   - Click 'Create Workflow'")
print("   - Add nodes and execute")

print("\n✅ Your videos are ready to edit!")
print(f"   Total videos: {len(videos)}")
print(f"   Demo video: {demo_video['title']}")
