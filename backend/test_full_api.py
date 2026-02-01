"""
Comprehensive API Test with Real YouTube Video
Testing all endpoints with: https://www.youtube.com/watch?v=0RFOqurWgzI
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
YOUTUBE_URL = "https://www.youtube.com/watch?v=0RFOqurWgzI"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}ℹ {text}{RESET}")

# Test 1: Health Check
def test_health():
    print_header("TEST 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check passed: {data}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False

# Test 2: Video Download
def test_video_download():
    print_header("TEST 2: Video Download from YouTube")
    print_info(f"URL: {YOUTUBE_URL}")
    
    try:
        payload = {
            "url": YOUTUBE_URL,
            "platform": "youtube"
        }
        
        print_info("Sending download request...")
        response = requests.post(
            f"{BASE_URL}/videos/download",
            json=payload,
            timeout=60
        )
        
        print_info(f"Response status: {response.status_code}")
        print_info(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Video download initiated successfully!")
            print_info(f"Video ID: {data.get('id', 'N/A')}")
            print_info(f"Title: {data.get('title', 'N/A')}")
            print_info(f"Status: {data.get('status', 'N/A')}")
            return data.get('id')
        else:
            print_error(f"Download failed: {response.status_code}")
            print_error(f"Error: {response.text}")
            return None
    except Exception as e:
        print_error(f"Download error: {str(e)}")
        return None

# Test 3: List Videos
def test_list_videos():
    print_header("TEST 3: List Videos")
    try:
        response = requests.get(f"{BASE_URL}/videos", timeout=5)
        if response.status_code == 200:
            data = response.json()
            videos = data.get('videos', [])
            print_success(f"Found {len(videos)} videos")
            for video in videos[:3]:  # Show first 3
                print_info(f"  - {video.get('title', 'Unknown')} ({video.get('status', 'N/A')})")
            return True
        else:
            print_error(f"List videos failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"List videos error: {str(e)}")
        return False

# Test 4: Generation Status
def test_generation_status():
    print_header("TEST 4: AI Generation Status")
    try:
        response = requests.get(f"{BASE_URL}/generation/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success("Generation service status:")
            print_info(f"  Available: {data.get('available', False)}")
            print_info(f"  Device: {data.get('device', 'N/A')}")
            print_info(f"  Model Loaded: {data.get('model_loaded', False)}")
            if data.get('message'):
                print_info(f"  Message: {data.get('message')}")
            return True
        else:
            print_error(f"Generation status failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Generation status error: {str(e)}")
        return False

# Test 5: Workflow List
def test_workflow_list():
    print_header("TEST 5: Workflow List")
    try:
        response = requests.get(f"{BASE_URL}/workflows/list", timeout=5)
        if response.status_code == 200:
            data = response.json()
            workflows = data.get('workflows', [])
            print_success(f"Found {len(workflows)} workflows")
            for wf in workflows[:3]:
                print_info(f"  - {wf.get('name', 'Unknown')}")
            return True
        else:
            print_error(f"Workflow list failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Workflow list error: {str(e)}")
        return False

# Test 6: Workflow Templates
def test_workflow_templates():
    """Test 6: Get workflow templates"""
    print_header("TEST 6: Workflow Templates")
    
    try:
        response = requests.get(f"{BASE_URL}/workflows/templates")
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get("templates", [])
            print_success(f"Found {len(templates)} templates")
            for template in templates:
                print_info(f"  - {template.get('name')}")
            return True
        else:
            print_error(f"Templates failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Templates error: {e}")
        return False

# Test 7: Create Workflow
def test_create_workflow():
    print_header("TEST 7: Create Test Workflow")
    try:
        workflow_data = {
            "name": "Test YouTube Download Workflow",
            "description": "Automated test workflow for YouTube video download",
            "nodes": [
                {
                    "id": "download_1",
                    "type": "VideoDownload",
                    "position": {"x": 100, "y": 100},
                    "data": {"url": YOUTUBE_URL}
                }
            ],
            "connections": [],
            "metadata": {
                "category": "test",
                "tags": ["youtube", "download", "test"]
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/workflows/create",
            json=workflow_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            workflow_id = data.get('workflow_id')
            print_success(f"Workflow created: {workflow_id}")
            return workflow_id
        else:
            print_error(f"Create workflow failed: {response.status_code}")
            print_error(f"Error: {response.text}")
            return None
    except Exception as e:
        print_error(f"Create workflow error: {str(e)}")
        return None

# Run all tests
def run_all_tests():
    print_header("🚀 COMPREHENSIVE API TEST SUITE")
    print_info(f"Testing with YouTube URL: {YOUTUBE_URL}")
    print_info(f"Backend: {BASE_URL}")
    print_info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    tests = [
        ("Health Check", test_health),
        ("Video Download", test_video_download),
        ("List Videos", test_list_videos),
        ("Generation Status", test_generation_status),
        ("Workflow List", test_workflow_list),
        ("Workflow Templates", test_workflow_templates),
        ("Create Workflow", test_create_workflow),
    ]
    
    for test_name, test_func in tests:
        results["total"] += 1
        try:
            result = test_func()
            if result or result is True:
                results["passed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {str(e)}")
            results["failed"] += 1
        
        time.sleep(1)  # Pause between tests
    
    # Summary
    print_header("📊 TEST SUMMARY")
    print(f"Total Tests: {results['total']}")
    print(f"{GREEN}Passed: {results['passed']}{RESET}")
    print(f"{RED}Failed: {results['failed']}{RESET}")
    
    success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if results['failed'] == 0:
        print(f"\n{GREEN}✅ ALL TESTS PASSED!{RESET}")
    else:
        print(f"\n{YELLOW}⚠️  Some tests failed. Check logs above.{RESET}")
    
    print(f"\n{BLUE}{'='*70}{RESET}\n")

if __name__ == "__main__":
    run_all_tests()
