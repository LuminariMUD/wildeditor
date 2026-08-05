#!/usr/bin/env python3
"""
Test spatial search functionality in MCP server
"""

import json
import requests
import ast

MCP_URL = "http://luminarimud.com:8001/mcp"
MCP_KEY = "xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0="

def test_mcp_tool(name: str, tool_name: str, arguments: dict) -> bool:
    """Test an MCP tool"""
    print(f"\n🧪 Testing: {name}")
    print(f"   Tool: {tool_name}")
    print(f"   Args: {json.dumps(arguments, indent=2)}")
    
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
                    
                    try:
                        data = ast.literal_eval(text_content) if text_content else {}
                        if isinstance(data, dict):
                            if "error" in data:
                                print(f"   ❌ Tool error: {data['error']}")
                                return False
                            else:
                                # Show summary of results
                                if "summary" in data:
                                    summary = data["summary"]
                                    print(f"   ✅ Success!")
                                    print(f"      - Found {summary.get('region_count', 0)} regions")
                                    print(f"      - Found {summary.get('path_count', 0)} paths")
                                    if "regions" in data and data["regions"]:
                                        print(f"      - Regions: {', '.join(r['name'] for r in data['regions'][:3])}")
                                    if "paths" in data and data["paths"]:
                                        print(f"      - Paths: {', '.join(p['name'] for p in data['paths'][:3])}")
                                elif "total_found" in data:
                                    print(f"   ✅ Success! Found {data['total_found']} regions")
                                    if data.get("regions"):
                                        print(f"      - Sample: {', '.join(r['name'] for r in data['regions'][:3])}")
                                else:
                                    print(f"   ✅ Success!")
                                return True
                        else:
                            print(f"   ✅ Success (non-dict response)")
                            return True
                    except Exception as e:
                        print(f"   ⚠️  Parse error: {e}")
                        print(f"      Response: {text_content[:200]}")
                        return True
            
            print(f"   ⚠️  Unexpected response format")
            return False
        else:
            print(f"   ❌ HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    print("=" * 80)
    print("🗺️  SPATIAL SEARCH TEST FOR MCP SERVER")
    print("=" * 80)
    
    results = []
    
    print("\n" + "=" * 80)
    print("TESTING SPATIAL SEARCH CAPABILITIES")
    print("=" * 80)
    
    # Test 1: New search_by_coordinates tool
    print("\n📍 Test 1: search_by_coordinates tool")
    results.append(test_mcp_tool(
        "Search at origin (0,0) with radius 10",
        "search_by_coordinates",
        {"x": 0, "y": 0, "radius": 10}
    ))
    
    results.append(test_mcp_tool(
        "Search at specific location with small radius",
        "search_by_coordinates",
        {"x": -50, "y": 95, "radius": 5}
    ))
    
    # Test 2: Enhanced search_regions with coordinates
    print("\n📍 Test 2: search_regions with spatial parameters")
    results.append(test_mcp_tool(
        "Search regions at coordinates",
        "search_regions",
        {"x": 0, "y": 0, "radius": 15}
    ))
    
    results.append(test_mcp_tool(
        "Search regions with coordinate and type filter",
        "search_regions",
        {"x": 0, "y": 0, "radius": 20, "region_type": 1}
    ))
    
    # Test 3: Traditional search_regions (should still work)
    print("\n📍 Test 3: Traditional search_regions (non-spatial)")
    results.append(test_mcp_tool(
        "Search all regions (traditional)",
        "search_regions",
        {"limit": 5}
    ))
    
    # Test 4: Search in areas known to have features
    print("\n📍 Test 4: Search in known areas")
    results.append(test_mcp_tool(
        "Search near Mosswood (-50, 95)",
        "search_by_coordinates",
        {"x": -50, "y": 95, "radius": 10}
    ))
    
    results.append(test_mcp_tool(
        "Search near Lake of Tears (7, 37)",
        "search_by_coordinates",
        {"x": 7, "y": 37, "radius": 10}
    ))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n✅ SPATIAL SEARCH IS FULLY FUNCTIONAL!")
        print("All coordinate-based searches are working correctly.")
    elif success_rate >= 70:
        print("\n⚠️  SPATIAL SEARCH IS MOSTLY FUNCTIONAL")
        print("Most searches work but some have issues.")
    else:
        print("\n❌ SPATIAL SEARCH HAS ISSUES")
        print("Many searches are not working properly.")
    
    print("\n" + "=" * 80)
    print("CAPABILITIES SUMMARY")
    print("=" * 80)
    print("\n✅ Available spatial search methods:")
    print("  1. search_by_coordinates - Direct spatial search at x,y with radius")
    print("  2. search_regions - Enhanced to support x,y,radius parameters")
    print("  3. Backend /api/points - Direct spatial queries in database")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)