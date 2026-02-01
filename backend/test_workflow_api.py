"""
Test Workflow API with Correct Format
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

print("🎬 Testing Workflow API with Correct Format\n")
print("="*70)

# Example 1: Simple Trim Workflow
print("\n1️⃣ Creating Trim Workflow...")

trim_workflow = {
    "name": "Trim TikTok Video",
    "description": "Cut video to first 30 seconds",
    "nodes": [
        {
            "id": "trim_node_1",
            "type": "VideoTrim",
            "inputs": {
                "video_path": "data/downloads/tiktok_1769926054.mp4",
                "start_time": 0,
                "end_time": 30
            },
            "outputs": {
                "output_path": "data/processed/tiktok_trimmed.mp4"
            },
            "position": {
                "x": 100,
                "y": 100
            }
        }
    ],
    "connections": [],
    "metadata": {
        "category": "video_editing",
        "tags": ["trim", "tiktok"]
    }
}

print(json.dumps(trim_workflow, indent=2))

try:
    response = requests.post(
        f"{BASE_URL}/workflows/create",
        json=trim_workflow
    )
    
    if response.status_code == 200:
        workflow_data = response.json()
        print(f"\n✅ Workflow created successfully!")
        print(f"   ID: {workflow_data['id']}")
        print(f"   Name: {workflow_data['name']}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.json())
        
except Exception as e:
    print(f"\n❌ Error: {e}")

# Example 2: Pipeline with Connections
print("\n" + "="*70)
print("\n2️⃣ Creating Pipeline Workflow (Download → Trim → Resize)...")

pipeline_workflow = {
    "name": "Complete Video Pipeline",
    "description": "Download → Trim → Resize workflow",
    "nodes": [
        {
            "id": "download_1",
            "type": "VideoDownload",
            "inputs": {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "platform": "youtube"
            },
            "outputs": {
                "video_path": ""
            },
            "position": {"x": 100, "y": 100}
        },
        {
            "id": "trim_1",
            "type": "VideoTrim",
            "inputs": {
                "video_path": "",
                "start_time": 10,
                "end_time": 40
            },
            "outputs": {
                "output_path": "data/processed/trimmed.mp4"
            },
            "position": {"x": 300, "y": 100}
        },
        {
            "id": "resize_1",
            "type": "VideoResize",
            "inputs": {
                "video_path": "",
                "width": 1080,
                "height": 1920
            },
            "outputs": {
                "output_path": "data/processed/final_vertical.mp4"
            },
            "position": {"x": 500, "y": 100}
        }
    ],
    "connections": [
        {
            "source_node": "download_1",
            "source_output": "video_path",
            "target_node": "trim_1",
            "target_input": "video_path"
        },
        {
            "source_node": "trim_1",
            "source_output": "output_path",
            "target_node": "resize_1",
            "target_input": "video_path"
        }
    ],
    "metadata": {
        "category": "complete_pipeline",
        "tags": ["download", "trim", "resize", "youtube"]
    }
}

print(json.dumps(pipeline_workflow, indent=2))

try:
    response = requests.post(
        f"{BASE_URL}/workflows/create",
        json=pipeline_workflow
    )
    
    if response.status_code == 200:
        workflow_data = response.json()
        print(f"\n✅ Pipeline workflow created successfully!")
        print(f"   ID: {workflow_data['id']}")
        print(f"   Nodes: {len(workflow_data['nodes'])}")
        print(f"   Connections: {len(workflow_data['connections'])}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.json())
        
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*70)
print("\n📝 Workflow Format Requirements:")
print("  ✓ Each node must have: id, type, inputs, outputs, position")
print("  ✓ Must include 'connections' array (can be empty)")
print("  ✓ Connections link nodes: source_node → target_node")
print("\n✅ Test complete!")
