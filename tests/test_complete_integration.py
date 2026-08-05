#!/usr/bin/env python3
"""
Complete integration test for MCP server with backend API
Tests both direct API access and MCP tool calls
"""

import json
import os
import requests
import sys
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = os.getenv("WILDEDITOR_BACKEND_URL", "http://127.0.0.1:8000/api")
MCP_URL = os.getenv("WILDEDITOR_MCP_URL", "http://127.0.0.1:8001/mcp")
BACKEND_SERVICE_KEY = os.getenv("WILDEDITOR_BACKEND_SERVICE_KEY", "")
MCP_KEY = os.getenv("WILDEDITOR_MCP_KEY", "")

def test_backend_direct(name: str, endpoint: str) -> bool:
    """Test direct backend API access"""
    print(f"\n🔍 Testing Backend Direct: {name}")
    
    headers = {
        "Authorization": f"Bearer {BACKEND_SERVICE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   ✅ Success: Got {len(data)} items")
            else:
                print(f"   ✅ Success: Got response")
            return True
        else:
            print(f"   ❌ Failed: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_mcp_tool(name: str, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict]:
    """Test MCP tool call"""
    print(f"\n🤖 Testing MCP Tool: {name}")
    
    headers = {
        "X-API-Key": MCP_KEY,
        "Content-Type": "application/json"
    }
    
    request_data = {
        "jsonrpc": "2.0",
        "id": f"test-{tool_name}",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    try:
        response = requests.post(
            f"{MCP_URL}/request",
            headers=headers,
            json=request_data,
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "error" in result:
                print(f"   ❌ MCP Error: {result['error']}")
                return None
            else:
                print(f"   ✅ MCP call successful")
                # Parse the actual result
                if "result" in result and "content" in result["result"]:
                    content = result["result"]["content"]
                    if isinstance(content, list) and len(content) > 0:
                        text_content = content[0].get("text", "")
                        try:
                            # Try to parse as JSON
                            actual_data = json.loads(text_content)
                            if "error" in actual_data:
                                print(f"   ⚠️  Tool returned error: {actual_data['error']}")
                                return None
                            else:
                                print(f"   📊 Data received from tool")
                                return actual_data
                        except:
                            print(f"   📝 Text response: {text_content[:200]}")
                            return {"text": text_content}
                return result
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"   ❌ Request timed out after 30 seconds")
        return None
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def main():
    missing = [
        name
        for name, value in (
            ("WILDEDITOR_BACKEND_SERVICE_KEY", BACKEND_SERVICE_KEY),
            ("WILDEDITOR_MCP_KEY", MCP_KEY),
        )
        if not value
    ]
    if missing:
        print(f"Missing required operator credentials: {', '.join(missing)}")
        return False

    print("=" * 70)
    print("COMPLETE INTEGRATION TEST")
    print("=" * 70)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"MCP URL: {MCP_URL}")
    print("Server credentials are present; values and previews are suppressed.")
    
    # Track results
    backend_results = []
    mcp_results = []
    
    print("\n" + "=" * 70)
    print("PHASE 1: BACKEND API DIRECT ACCESS")
    print("=" * 70)
    
    # Test backend endpoints directly
    backend_results.append(test_backend_direct("Health Check", "/health"))
    backend_results.append(test_backend_direct("List Regions", "/regions?include_descriptions=false"))
    backend_results.append(test_backend_direct("Get Region 1000004", "/regions/1000004"))
    backend_results.append(test_backend_direct("List Paths", "/paths"))
    backend_results.append(test_backend_direct("List Points", "/points"))
    
    print("\n" + "=" * 70)
    print("PHASE 2: MCP TOOL CALLS (USING BACKEND API)")
    print("=" * 70)
    
    # Test MCP tools that use the backend API
    result = test_mcp_tool(
        "Analyze Region",
        "analyze_region",
        {
            "region_id": 1000004,
            "include_paths": False
        }
    )
    mcp_results.append(result is not None)
    
    result = test_mcp_tool(
        "Search Regions",
        "search_regions",
        {
            "include_descriptions": "false",
            "limit": 5
        }
    )
    mcp_results.append(result is not None)
    
    result = test_mcp_tool(
        "Find Path",
        "find_path",
        {
            "start_region_id": 1000004,
            "end_region_id": 1000003
        }
    )
    mcp_results.append(result is not None)
    
    result = test_mcp_tool(
        "Analyze Terrain Map",
        "analyze_complete_terrain_map",
        {
            "center_x": 0,
            "center_y": 0,
            "radius": 3
        }
    )
    mcp_results.append(result is not None)
    
    # Test AI-powered tool (will use template fallback if no AI configured)
    result = test_mcp_tool(
        "Generate Description",
        "generate_region_description",
        {
            "region_name": "Test Valley",
            "terrain_theme": "mystical forest",
            "description_style": "descriptive",
            "description_length": "brief"
        }
    )
    mcp_results.append(result is not None)
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    backend_passed = sum(backend_results)
    backend_total = len(backend_results)
    mcp_passed = sum(mcp_results)
    mcp_total = len(mcp_results)
    
    print(f"\nBackend API Direct: {backend_passed}/{backend_total} tests passed")
    print(f"MCP Tool Calls: {mcp_passed}/{mcp_total} tests passed")
    
    total_passed = backend_passed + mcp_passed
    total_tests = backend_total + mcp_total
    
    print(f"\nOverall: {total_passed}/{total_tests} tests passed")
    
    print("\n" + "=" * 70)
    print("CONFIGURATION STATUS")
    print("=" * 70)
    
    if backend_passed == backend_total:
        print("✅ Backend service credential: working")
    else:
        print("❌ Backend service credential: issues detected")
    
    if mcp_passed > 0:
        print("✅ MCP Server: OPERATIONAL")
        if mcp_passed == mcp_total:
            print("   All MCP tools working with backend integration")
        else:
            print(f"   {mcp_passed}/{mcp_total} MCP tools working")
            print("   ⚠️  Backend service key may not be configured in MCP server")
    else:
        print("❌ MCP Server: NOT WORKING PROPERLY")
        print("   The MCP server cannot access the backend API")
    
    print("\n" + "=" * 70)
    print("REQUIRED ACTIONS")
    print("=" * 70)
    
    if mcp_passed < mcp_total:
        print("\n⚠️  Verify the server-only backend key is aligned between MCP and backend.")
        print("Redeploy both services after correcting the protected secret.")
    else:
        print("\n✅ No actions required - everything is working!")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
