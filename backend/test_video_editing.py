"""
Quick Video Editing Examples
Test the video editing features with your downloaded videos
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

# Your downloaded videos
TIKTOK_VIDEO = "data/downloads/tiktok_1769926054.mp4"
YOUTUBE_VIDEO = "data/downloads/youtube_dQw4w9WgXcQ.mp4"

print("🎬 Video Editing Examples\n")
print("="*60)

# Example 1: Trim TikTok Video (First 15 seconds)
print("\n1️⃣ Trimming TikTok video to first 15 seconds...")
workflow_trim = {
    "name": "Trim TikTok Video",
    "description": "Cut to first 15 seconds",
    "nodes": [
        {
            "type": "VideoTrim",
            "input_file": TIKTOK_VIDEO,
            "start_time": 0,
            "end_time": 15,
            "output_file": "data/processed/tiktok_trimmed.mp4"
        }
    ]
}

print(f"Workflow: {json.dumps(workflow_trim, indent=2)}")
print("\nTo execute:")
print(f"curl -X POST {BASE_URL}/workflows/execute \\")
print(f"  -H 'Content-Type: application/json' \\")
print(f"  -d '{json.dumps(workflow_trim)}'")

# Example 2: Resize YouTube Video to Vertical (Shorts format)
print("\n" + "="*60)
print("\n2️⃣ Resizing YouTube video to vertical format (1080x1920)...")
workflow_resize = {
    "name": "Convert to Shorts Format",
    "description": "Resize to 9:16 ratio for TikTok/Shorts",
    "nodes": [
        {
            "type": "VideoResize",
            "input_file": YOUTUBE_VIDEO,
            "width": 1080,
            "height": 1920,
            "crop": "center",
            "output_file": "data/processed/youtube_vertical.mp4"
        }
    ]
}

print(f"Workflow: {json.dumps(workflow_resize, indent=2)}")

# Example 3: Merge Multiple Videos
print("\n" + "="*60)
print("\n3️⃣ Merging TikTok and YouTube videos...")
workflow_merge = {
    "name": "Merge Videos",
    "description": "Combine multiple videos",
    "nodes": [
        {
            "type": "VideoMerge",
            "input_files": [
                TIKTOK_VIDEO,
                YOUTUBE_VIDEO
            ],
            "output_file": "data/processed/merged_compilation.mp4"
        }
    ]
}

print(f"Workflow: {json.dumps(workflow_merge, indent=2)}")

# Example 4: Complete Pipeline (Download → Trim → Resize)
print("\n" + "="*60)
print("\n4️⃣ Complete pipeline: Download → Trim → Resize...")
workflow_complete = {
    "name": "Complete Video Pipeline",
    "description": "Download, trim, and resize in one workflow",
    "nodes": [
        {
            "id": "download",
            "type": "VideoDownload",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        },
        {
            "id": "trim",
            "type": "VideoTrim",
            "input": "{{download.output}}",
            "start_time": 10,
            "end_time": 40
        },
        {
            "id": "resize",
            "type": "VideoResize",
            "input": "{{trim.output}}",
            "width": 1080,
            "height": 1920
        }
    ]
}

print(f"Workflow: {json.dumps(workflow_complete, indent=2)}")

print("\n" + "="*60)
print("\n📝 How to Execute:")
print("1. Save any workflow above to a JSON file")
print("2. Execute via API:")
print(f"   curl -X POST {BASE_URL}/workflows/execute -d @workflow.json")
print("\n3. Or use Python:")
print("""
import requests
response = requests.post(
    'http://localhost:8000/api/workflows/execute',
    json=workflow_trim
)
print(response.json())
""")

print("\n✅ Your videos are ready to edit!")
print(f"   - TikTok: {TIKTOK_VIDEO}")
print(f"   - YouTube: {YOUTUBE_VIDEO}")
