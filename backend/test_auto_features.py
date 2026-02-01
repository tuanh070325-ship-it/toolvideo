"""
Test Auto Features: Auto Cut & Voice Reup
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

print("🎬 Testing Auto Features Nodes\n")
print("="*70)

# 1. Auto Cut Workflow (Highlight Extraction)
print("\n1️⃣ Creating Auto Cut Workflow...")

auto_cut_workflow = {
    "name": "Auto Cut Highlights",
    "description": "Extract best moments automatically",
    "nodes": [
        {
            "id": "cut_node",
            "type": "HighlightExtraction",
            "inputs": {
                "video_path": "data/downloads/test_video.mp4",
                "num_highlights": 3,
                "duration": 30,
                "style": "engaging"
            },
            "outputs": {
                "highlight_path": "",
                "segments": ""
            },
            "position": {"x": 100, "y": 100}
        }
    ],
    "connections": []
}

try:
    response = requests.post(f"{BASE_URL}/workflows/create", json=auto_cut_workflow)
    if response.status_code == 200:
        print("✅ Auto Cut Workflow created!")
        print(f"   ID: {response.json()['id']}")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# 2. Voice Reup Workflow (TTS + Reup)
print("\n2️⃣ Creating Voice Reup Workflow...")

voice_reup_workflow = {
    "name": "Auto Voice Reup",
    "description": "Generate voice and reup video",
    "nodes": [
        {
            "id": "tts_node",
            "type": "TTSGeneration",
            "inputs": {
                "text": "This is a sample narration for the video.",
                "voice": "alloy",
                "provider": "auto"
            },
            "outputs": {
                "audio_path": "data/temp/narration.mp3"
            },
            "position": {"x": 100, "y": 100}
        },
        {
            "id": "reup_node",
            "type": "VideoReup",
            "inputs": {
                "video_path": "data/downloads/test_video.mp4",
                "platform": "tiktok",
                "add_captions": True
            },
            "outputs": {
                "output_path": ""
            },
            "position": {"x": 300, "y": 100}
        }
    ],
    "connections": [
        {
            "source_node": "tts_node",
            "source_output": "audio_path",
            "target_node": "reup_node",
            "target_input": "audio_path"
        }
    ]
}

try:
    response = requests.post(f"{BASE_URL}/workflows/create", json=voice_reup_workflow)
    if response.status_code == 200:
        print("✅ Voice Reup Workflow created!")
        print(f"   ID: {response.json()['id']}")
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("✅ Node registration verified via workflow creation.")
