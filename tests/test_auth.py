#!/usr/bin/env python3
"""
Authentication test script for Wildeditor API.

Tests the server-only backend service credential boundary.
"""

import os
import requests
import json
from typing import Optional

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")
SERVICE_KEY = os.getenv("WILDEDITOR_BACKEND_SERVICE_KEY", "")

def test_health_endpoint():
    """Test the public health endpoint."""
    print("🔍 Testing health endpoint (should be public)...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint accessible")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")

def test_auth_status(api_key: Optional[str] = None):
    """Test the authentication status endpoint."""
    print(f"🔍 Testing auth status endpoint {'with API key' if api_key else 'without API key'}...")
    
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    try:
        response = requests.get(f"{API_BASE_URL}/auth/status", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if api_key and response.status_code == 200:
            print("✅ API key authentication working")
        elif not api_key and response.status_code == 401:
            print("✅ Authentication properly required")
        else:
            print(f"⚠️  Unexpected response")
            
    except Exception as e:
        print(f"❌ Auth status error: {e}")

def test_read_endpoints(service_key: str):
    """Test authenticated read-only endpoints."""
    print("🔍 Testing authenticated read-only endpoints...")
    
    endpoints = [
        "/regions",
        "/paths",
        "/paths/types",
        "/points?x=0&y=0"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(
                f"{API_BASE_URL}{endpoint}",
                headers={"Authorization": f"Bearer {service_key}"},
            )
            if response.status_code in [200, 404]:  # 404 is OK if no data exists
                print(f"✅ GET {endpoint} - accessible")
            else:
                print(f"❌ GET {endpoint} - status {response.status_code}")
        except Exception as e:
            print(f"❌ GET {endpoint} - error: {e}")

def test_protected_endpoints(api_key: str):
    """Test write endpoints (should require API key)."""
    print("🔍 Testing protected endpoints...")
    
    # Test without API key first
    print("   Testing without API key (should fail)...")
    test_data = {
        "name": "Test Path",
        "vnum": 99999,
        "zone_vnum": 1,
        "path_type": 1,
        "coordinates": [{"x": 0, "y": 0}, {"x": 1, "y": 1}],
        "path_props": 11
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/paths",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 401:
            print("✅ POST /paths properly requires authentication")
        else:
            print(f"⚠️  POST /paths without auth: {response.status_code}")
    except Exception as e:
        print(f"❌ POST /paths without auth error: {e}")
    
    # Test with API key
    print("   Testing with API key (should work)...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/paths",
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )
        if response.status_code == 201:
            print("✅ POST /paths with API key successful")
            created_path = response.json()
            
            # Clean up - delete the test path
            delete_response = requests.delete(
                f"{API_BASE_URL}/paths/{created_path['vnum']}",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            if delete_response.status_code == 204:
                print("✅ DELETE /paths with API key successful")
            else:
                print(f"⚠️  DELETE /paths cleanup failed: {delete_response.status_code}")
                
        elif response.status_code == 400 and "already exists" in response.text:
            print("✅ POST /paths with API key works (path already exists)")
        else:
            print(f"❌ POST /paths with API key failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ POST /paths with API key error: {e}")

def main():
    """Run all authentication tests."""
    print("🧪 Wildeditor API Authentication Tests")
    print("=" * 50)
    
    # Test public endpoints
    test_health_endpoint()
    print()
    
    # Test authentication status
    test_auth_status()  # Without API key
    if SERVICE_KEY:
        test_auth_status(SERVICE_KEY)  # With server-only service key
    print()
    
    # Test read-only endpoints
    if SERVICE_KEY:
        test_read_endpoints(SERVICE_KEY)
    print()
    
    # Test protected endpoints
    if SERVICE_KEY:
        test_protected_endpoints(SERVICE_KEY)
    else:
        print("⚠️  WILDEDITOR_BACKEND_SERVICE_KEY not set - skipping protected endpoint tests")
    
    print()
    print("✅ Authentication tests completed!")

if __name__ == "__main__":
    if not SERVICE_KEY:
        print("⚠️  Warning: WILDEDITOR_BACKEND_SERVICE_KEY environment variable not set")
        print("   Some tests will be skipped")
        print()
    
    main()
