"""Comprehensive API Testing Suite for Video Tool"""

import asyncio
import httpx
import json
from pathlib import Path
from datetime import datetime


BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

# Test results storage
test_results = {
    "passed": [],
    "failed": [],
    "skipped": [],
    "total": 0
}


def log_test(name: str, status: str, details: str = ""):
    """Log test result"""
    test_results["total"] += 1
    result = {
        "name": name,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    
    if status == "PASS":
        test_results["passed"].append(result)
        print(f"✅ {name}")
    elif status == "FAIL":
        test_results["failed"].append(result)
        print(f"❌ {name}: {details}")
    else:
        test_results["skipped"].append(result)
        print(f"⏭️  {name}: {details}")
    
    if details and status == "PASS":
        print(f"   {details}")


async def test_health_check():
    """Test health check endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                log_test("Health Check", "PASS", f"Status: {data.get('status')}")
            else:
                log_test("Health Check", "FAIL", f"Status code: {response.status_code}")
    except Exception as e:
        log_test("Health Check", "FAIL", str(e))


async def test_generation_status():
    """Test LTX-Video generation status endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/generation/status")
            if response.status_code == 200:
                data = response.json()
                log_test("Generation Status", "PASS", 
                        f"Available: {data.get('available')}, Device: {data.get('device')}")
            else:
                log_test("Generation Status", "FAIL", f"Status code: {response.status_code}")
    except Exception as e:
        log_test("Generation Status", "FAIL", str(e))


async def test_workflow_list():
    """Test workflow list endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/workflows/list")
            if response.status_code == 200:
                data = response.json()
                count = len(data.get("workflows", []))
                log_test("Workflow List", "PASS", f"Found {count} workflows")
            else:
                log_test("Workflow List", "FAIL", f"Status code: {response.status_code}")
    except Exception as e:
        log_test("Workflow List", "FAIL", str(e))


async def test_workflow_templates():
    """Test workflow templates endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/workflows/templates")
            if response.status_code == 200:
                data = response.json()
                count = len(data.get("templates", []))
                log_test("Workflow Templates", "PASS", f"Found {count} templates")
            else:
                log_test("Workflow Templates", "FAIL", f"Status code: {response.status_code}")
    except Exception as e:
        log_test("Workflow Templates", "FAIL", str(e))


async def test_create_workflow():
    """Test workflow creation"""
    try:
        workflow_data = {
            "name": "Test Workflow",
            "description": "Automated test workflow",
            "nodes": [
                {
                    "id": "analyzer_1",
                    "type": "VideoAnalyzer",
                    "position": {"x": 100, "y": 100}
                }
            ],
            "connections": [],
            "metadata": {
                "category": "test",
                "tags": ["automated", "test"]
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/workflows/create",
                json=workflow_data
            )
            if response.status_code == 200:
                data = response.json()
                log_test("Create Workflow", "PASS", f"ID: {data.get('workflow_id')}")
                return data.get('workflow_id')
            else:
                log_test("Create Workflow", "FAIL", f"Status code: {response.status_code}")
                return None
    except Exception as e:
        log_test("Create Workflow", "FAIL", str(e))
        return None


async def test_get_workflow(workflow_id: str):
    """Test get workflow by ID"""
    if not workflow_id:
        log_test("Get Workflow", "SKIP", "No workflow ID")
        return
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/workflows/{workflow_id}")
            if response.status_code == 200:
                data = response.json()
                log_test("Get Workflow", "PASS", f"Name: {data.get('name')}")
            else:
                log_test("Get Workflow", "FAIL", f"Status code: {response.status_code}")
    except Exception as e:
        log_test("Get Workflow", "FAIL", str(e))


async def test_execute_workflow(workflow_id: str):
    """Test workflow execution"""
    if not workflow_id:
        log_test("Execute Workflow", "SKIP", "No workflow ID")
        return
    
    try:
        execution_data = {
            "workflow_id": workflow_id,
            "inputs": {
                "video_path": "test_video.mp4"
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{API_BASE}/workflows/execute",
                json=execution_data
            )
            if response.status_code == 200:
                data = response.json()
                log_test("Execute Workflow", "PASS", 
                        f"Execution ID: {data.get('execution_id')}")
            else:
                log_test("Execute Workflow", "FAIL", f"Status code: {response.status_code}")
    except Exception as e:
        log_test("Execute Workflow", "FAIL", str(e))


async def test_delete_workflow(workflow_id: str):
    """Test workflow deletion"""
    if not workflow_id:
        log_test("Delete Workflow", "SKIP", "No workflow ID")
        return
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{API_BASE}/workflows/{workflow_id}")
            if response.status_code == 200:
                log_test("Delete Workflow", "PASS", "Workflow deleted")
            else:
                log_test("Delete Workflow", "FAIL", f"Status code: {response.status_code}")
    except Exception as e:
        log_test("Delete Workflow", "FAIL", str(e))


async def test_video_endpoints():
    """Test existing video processing endpoints"""
    endpoints = [
        ("/videos", "GET", "List Videos"),
        ("/studio/projects", "GET", "List Projects"),
    ]
    
    async with httpx.AsyncClient() as client:
        for path, method, name in endpoints:
            try:
                if method == "GET":
                    response = await client.get(f"{API_BASE}{path}")
                
                if response.status_code == 200:
                    log_test(name, "PASS", f"Response OK")
                else:
                    log_test(name, "FAIL", f"Status code: {response.status_code}")
            except Exception as e:
                log_test(name, "FAIL", str(e))


async def run_all_tests():
    """Run all API tests"""
    print("\n" + "="*70)
    print("🧪 COMPREHENSIVE API TEST SUITE")
    print("="*70 + "\n")
    
    print("📡 Testing Core Endpoints...")
    await test_health_check()
    
    print("\n🎨 Testing Generation Endpoints...")
    await test_generation_status()
    
    print("\n⚙️ Testing Workflow Endpoints...")
    await test_workflow_list()
    await test_workflow_templates()
    
    print("\n🔧 Testing Workflow CRUD Operations...")
    workflow_id = await test_create_workflow()
    await test_get_workflow(workflow_id)
    await test_execute_workflow(workflow_id)
    await test_delete_workflow(workflow_id)
    
    print("\n🎬 Testing Video Processing Endpoints...")
    await test_video_endpoints()
    
    # Print summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {test_results['total']}")
    print(f"✅ Passed: {len(test_results['passed'])}")
    print(f"❌ Failed: {len(test_results['failed'])}")
    print(f"⏭️  Skipped: {len(test_results['skipped'])}")
    
    if test_results['failed']:
        print("\n❌ Failed Tests:")
        for test in test_results['failed']:
            print(f"   - {test['name']}: {test['details']}")
    
    success_rate = (len(test_results['passed']) / test_results['total'] * 100) if test_results['total'] > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    print("="*70 + "\n")
    
    # Save results to file
    results_file = Path("backend/test_results.json")
    with open(results_file, "w") as f:
        json.dump(test_results, f, indent=2)
    print(f"📝 Results saved to: {results_file}\n")


if __name__ == "__main__":
    print("\n🚀 Starting API Tests...")
    print("⚠️  Make sure backend is running on http://localhost:8000\n")
    
    asyncio.run(run_all_tests())
    
    print("✨ All tests completed!\n")
