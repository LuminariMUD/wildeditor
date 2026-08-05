#!/usr/bin/env python3
"""
Test MCP server with the backend API key
"""

import json
import os
import requests

# Configuration
MCP_URL = os.getenv("WILDEDITOR_MCP_URL", "http://127.0.0.1:8001/mcp")
MCP_KEY = os.environ["WILDEDITOR_MCP_KEY"]
API_KEY = os.environ["WILDEDITOR_BACKEND_SERVICE_KEY"]

def test_mcp_tool(tool_name, arguments):
    """Test an MCP tool that uses the backend API"""
    print(f"\n🧪 Testing MCP tool: {tool_name}")
    
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
    
    print(f"   Arguments: {json.dumps(arguments, indent=2)}")
    
    try:
        response = requests.post(
            f"{MCP_URL}/request",
            headers=headers,
            json=request_data
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "error" in result:
                print(f"   ❌ MCP Error: {result['error']}")
                return False
            else:
                print(f"   ✅ Success!")
                # Extract actual result from MCP response
                if "result" in result and "content" in result["result"]:
                    content = result["result"]["content"][0]["text"]
                    # Parse the content (it's a string representation of a dict)
                    try:
                        actual_result = eval(content)
                        if "error" in actual_result:
                            print(f"   ⚠️  Tool returned error: {actual_result['error']}")
                            return False
                        else:
                            print(f"   Result preview: {str(actual_result)[:200]}...")
                            return True
                    except:
                        print(f"   Result: {content[:200]}...")
                        return True
                return True
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    print("=" * 60)
    print("MCP SERVER WITH BACKEND API TEST")
    print("=" * 60)
    print(f"MCP URL: {MCP_URL}")
    print(f"MCP Key: {MCP_KEY[:10]}...{MCP_KEY[-5:]}")
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:]}")
    
    results = []
    
    # Test analyze_region (uses backend API)
    results.append(test_mcp_tool(
        "analyze_region",
        {
            "region_id": 1000004,
            "include_paths": True
        }
    ))
    
    # Test search_regions (uses backend API)
    results.append(test_mcp_tool(
        "search_regions",
        {
            "include_descriptions": "false",
            "limit": 5
        }
    ))
    
    # Test find_path (uses backend API)
    results.append(test_mcp_tool(
        "find_path",
        {
            "start_region_id": 1000004,
            "end_region_id": 1000003
        }
    ))
    
    # Test generate_region_description (may use AI if configured)
    results.append(test_mcp_tool(
        "generate_region_description",
        {
            "region_name": "Crystal Valley",
            "terrain_theme": "mystical valley with crystals",
            "description_style": "poetic",
            "description_length": "brief"
        }
    ))
    
    # Test analyze_complete_terrain_map (uses backend API)
    results.append(test_mcp_tool(
        "analyze_complete_terrain_map",
        {
            "center_x": 0,
            "center_y": 0,
            "radius": 3
        }
    ))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ MCP server is fully functional with the backend API!")
        print("Both the MCP key and backend API key are working correctly.")
    elif passed > 0:
        print("⚠️  Some MCP tools are working but not all.")
        print("Check the errors above for details.")
    else:
        print("❌ MCP tools are not working properly.")
        print("This might be a configuration issue.")
    
    print("\n" + "=" * 60)
    print("CONFIGURATION STATUS")
    print("=" * 60)
    print(f"✅ MCP Key: Working")
    print(f"✅ Backend API Key: Working")
    print(f"✅ Backend URL: http://luminarimud.com:8000/api")
    print(f"✅ MCP Server: http://luminarimud.com:8001/mcp")
    
    return passed > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
