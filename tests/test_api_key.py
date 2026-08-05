#!/usr/bin/env python3
"""
Test the backend API key
"""

import requests
import json

# API Configuration
API_URL = "http://luminarimud.com:8000/api"
API_KEY = "0Hdn8wEggBM5KW42cAG0r3wVFDc4pYNu"

def test_api_endpoint(name, method, endpoint, data=None):
    """Test a single API endpoint"""
    print(f"\n🧪 Testing {name}...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    url = f"{API_URL}{endpoint}"
    print(f"   URL: {url}")
    print(f"   Method: {method}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        else:
            response = requests.delete(url, headers=headers)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Success!")
            data = response.json()
            # Show preview of response
            if isinstance(data, list):
                print(f"   Response: List with {len(data)} items")
                if len(data) > 0:
                    print(f"   First item: {json.dumps(data[0], indent=2)[:200]}...")
            elif isinstance(data, dict):
                preview = json.dumps(data, indent=2)[:300]
                print(f"   Response preview: {preview}...")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    print("=" * 60)
    print("BACKEND API KEY TEST")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:]}")
    
    results = []
    
    # Test health endpoint (usually doesn't require auth)
    results.append(test_api_endpoint(
        "Health Check",
        "GET",
        "/health"
    ))
    
    # Test regions endpoints
    results.append(test_api_endpoint(
        "List Regions",
        "GET",
        "/regions?include_descriptions=false"
    ))
    
    # Test specific region
    results.append(test_api_endpoint(
        "Get Region 1000004",
        "GET",
        "/regions/1000004?include_descriptions=true"
    ))
    
    # Test paths
    results.append(test_api_endpoint(
        "List Paths",
        "GET",
        "/paths"
    ))
    
    # Test points
    results.append(test_api_endpoint(
        "List Points",
        "GET",
        "/points"
    ))
    
    # Test creating a region (if auth works)
    test_region = {
        "name": "API Test Region",
        "vnum": 999999,
        "region_type": 1,
        "coordinates": [[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]],
        "color": "#FF0000"
    }
    
    results.append(test_api_endpoint(
        "Create Test Region",
        "POST",
        "/regions",
        test_region
    ))
    
    # If creation worked, try to delete it
    if results[-1]:
        results.append(test_api_endpoint(
            "Delete Test Region",
            "DELETE",
            "/regions/999999"
        ))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ API key is valid and working!")
        print("All endpoints are accessible with this key.")
    elif passed > 0:
        print("⚠️  API key works for some endpoints but not all.")
        print("This might be expected if some operations require special permissions.")
    else:
        print("❌ API key doesn't seem to be working.")
        print("Please check if the key is correct.")
    
    return passed > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)