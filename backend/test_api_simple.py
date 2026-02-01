"""Simple API test using requests library"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url, method="GET", data=None):
    """Test a single endpoint"""
    try:
        print(f"\n🧪 Testing: {name}")
        print(f"   URL: {url}")
        
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ PASS - Response: {json.dumps(data, indent=2)[:200]}...")
                return True
            except:
                print(f"   ✅ PASS - Response received")
                return True
        else:
            print(f"   ❌ FAIL - Status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ FAIL - Connection refused. Is backend running?")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ FAIL - Request timeout")
        return False
    except Exception as e:
        print(f"   ❌ FAIL - {str(e)}")
        return False


def main():
    print("="*70)
    print("🚀 SIMPLE API TEST SUITE")
    print("="*70)
    
    results = []
    
    # Test 1: Health Check
    results.append(test_endpoint(
        "Health Check",
        f"{BASE_URL}/api/health"
    ))
    
    # Test 2: API Docs
    results.append(test_endpoint(
        "API Documentation",
        f"{BASE_URL}/api/docs"
    ))
    
    # Test 3: Generation Status
    results.append(test_endpoint(
        "Generation Status",
        f"{BASE_URL}/api/generation/status"
    ))
    
    # Test 4: Workflow List
    results.append(test_endpoint(
        "Workflow List",
        f"{BASE_URL}/api/workflows/list"
    ))
    
    # Test 5: Workflow Templates
    results.append(test_endpoint(
        "Workflow Templates",
        f"{BASE_URL}/api/workflows/templates"
    ))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Total: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
