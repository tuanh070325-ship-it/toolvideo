"""Simple test for templates endpoint"""
import requests

print("Testing /api/workflows/templates...")
response = requests.get("http://localhost:8000/api/workflows/templates")
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

print("\n\nTesting /api/workflows/list...")
response2 = requests.get("http://localhost:8000/api/workflows/list")
print(f"Status: {response2.status_code}")
print(f"Response: {response2.text[:500]}")
