"""Check registered routes"""
import requests

# Check all routes
response = requests.get("http://localhost:8000/openapi.json")
if response.status_code == 200:
    openapi = response.json()
    paths = openapi.get("paths", {})
    
    print("=== All Registered Routes ===\n")
    workflow_routes = []
    for path in sorted(paths.keys()):
        if "workflow" in path.lower():
            workflow_routes.append(path)
            methods = list(paths[path].keys())
            print(f"{path} - {methods}")
    
    print(f"\n=== Total Workflow Routes: {len(workflow_routes)} ===")
    
    # Check specifically for templates
    if "/api/workflows/templates" in paths:
        print("\n✅ /api/workflows/templates EXISTS")
    else:
        print("\n❌ /api/workflows/templates NOT FOUND")
        print("\nLooking for similar routes:")
        for path in paths.keys():
            if "template" in path.lower():
                print(f"  - {path}")
else:
    print(f"Failed to get OpenAPI spec: {response.status_code}")
