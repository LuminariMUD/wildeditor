#!/usr/bin/env python3
"""
Test MCP server functionality after deployment
"""

import json
import os
import requests
import ast

# Configuration
MCP_URL = os.getenv("WILDEDITOR_MCP_URL", "http://127.0.0.1:8001/mcp")
MCP_KEY = os.environ["WILDEDITOR_MCP_KEY"]

def test_mcp_tool(name, tool_name, arguments):
    """Test an MCP tool"""
    print(f"\n🧪 Testing: {name}")
    
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
        
        if response.status_code == 200:
            result = response.json()
            
            if "error" in result and result["error"]:
                print(f"   ❌ Error: {result['error']}")
                return False
            
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"]
                if isinstance(content, list) and len(content) > 0:
                    text_content = content[0].get("text", "")
                    
                    # Parse the Python dict string
                    try:
                        data = ast.literal_eval(text_content)
                        if isinstance(data, dict):
                            if "error" in data:
                                print(f"   ⚠️  Tool error: {data['error']}")
                                return False
                            else:
                                # Show summary of successful response
                                if "total_found" in data:
                                    print(f"   ✅ Success: Found {data['total_found']} items")
                                elif "region" in data:
                                    print(f"   ✅ Success: Got region {data['region'].get('name', 'unknown')}")
                                elif "path" in data:
                                    print(f"   ✅ Success: Found path with {len(data.get('path', []))} steps")
                                elif "terrain_map" in data:
                                    print(f"   ✅ Success: Got terrain map")
                                elif "description" in data:
                                    print(f"   ✅ Success: Generated description")
                                else:
                                    print(f"   ✅ Success: Got response")
                                return True
                        else:
                            print(f"   ✅ Success: {text_content[:100]}")
                            return True
                    except Exception as e:
                        # Not a Python dict, might be plain text
                        print(f"   ✅ Success: {text_content[:100]}")
                        return True
            
            print(f"   ❌ Unexpected response format")
            return False
        else:
            print(f"   ❌ HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    print("=" * 70)
    print("MCP SERVER FUNCTIONALITY TEST")
    print("=" * 70)
    print(f"MCP URL: {MCP_URL}")
    print(f"MCP Key: {MCP_KEY[:10]}...{MCP_KEY[-5:]}")
    
    # Check health
    print("\n🏥 Checking server health...")
    response = requests.get(f"{MCP_URL.replace('/mcp', '')}/health")
    if response.status_code == 200:
        health = response.json()
        print(f"   ✅ Server version: {health['version']}")
        print(f"   ✅ Environment: {health['environment']}")
    
    # Check status
    print("\n🔐 Checking authenticated status...")
    response = requests.get(
        f"{MCP_URL}/status",
        headers={"X-API-Key": MCP_KEY}
    )
    if response.status_code == 200:
        status = response.json()
        print(f"   ✅ MCP Server: {status['mcp_server']['name']}")
        print(f"   ✅ Tools available: {status['mcp_server']['capabilities']['tools']}")
        print(f"   ✅ Backend: {status['backend_integration']['status']}")
    
    print("\n" + "=" * 70)
    print("TESTING MCP TOOLS")
    print("=" * 70)
    
    results = []
    
    # Test search_regions
    results.append(test_mcp_tool(
        "Search Regions",
        "search_regions",
        {"limit": 3}
    ))
    
    # Test analyze_region
    results.append(test_mcp_tool(
        "Analyze Region",
        "analyze_region",
        {"region_id": 1000004, "include_paths": False}
    ))
    
    # Test find_path (with correct parameter names)
    results.append(test_mcp_tool(
        "Find Path",
        "find_path",
        {"from_region": 1000004, "to_region": 1000003}
    ))
    
    # Test analyze_complete_terrain_map
    results.append(test_mcp_tool(
        "Analyze Terrain Map",
        "analyze_complete_terrain_map",
        {"center_x": 0, "center_y": 0, "radius": 3}
    ))
    
    # Test generate_region_description
    results.append(test_mcp_tool(
        "Generate Description",
        "generate_region_description",
        {
            "region_name": "Crystal Caves",
            "terrain_theme": "underground crystal caverns",
            "description_style": "descriptive",
            "description_length": "brief"
        }
    ))
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 SUCCESS! MCP server is fully functional!")
        print("✅ Backend API integration is working")
        print("✅ All tools are operational")
        print("✅ The API key is properly configured")
    elif passed > 0:
        print(f"\n⚠️  Partial success: {passed}/{total} tools working")
    else:
        print("\n❌ MCP tools are not working")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
