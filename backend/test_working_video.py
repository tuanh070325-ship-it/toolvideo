"""Test with a known working public video"""
import requests
import json

# Try a very popular, definitely public video
test_urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
    "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # Me at the zoo (first YouTube video)
]

for test_url in test_urls:
    print(f"\n{'='*60}")
    print(f"Testing: {test_url}")
    print('='*60)
    
    payload = {
        "url": test_url,
        "platform": "youtube"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/videos/download",
            json=payload,
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS!")
            print(f"Title: {data.get('title')}")
            print(f"Path: {data.get('file_path')}")
            break
        else:
            print(f"❌ FAILED: {response.json().get('detail')}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
