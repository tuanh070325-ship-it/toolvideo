"""Test video download API directly"""
import requests
import json

url = "http://localhost:8000/api/videos/download"
payload = {
    "url": "https://www.youtube.com/watch?v=0RFOqurWgzI",
    "platform": "youtube"
}

print("Testing video download API...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("\n" + "="*50 + "\n")

try:
    response = requests.post(url, json=payload, timeout=60)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse Body:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
    print(f"Response text: {response.text if 'response' in locals() else 'N/A'}")
