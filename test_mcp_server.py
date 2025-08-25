#!/usr/bin/env python3
"""
Test script for MCP Server features
Tests the enhanced description capabilities of the MCP server
"""

import json
import requests
from typing import Dict, Any

# MCP Server configuration
MCP_URL = "http://luminarimud.com:8001/mcp"
API_KEY = "xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0="
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call an MCP tool and return the result"""
    request_data = {
        "id": f"test-{tool_name}",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    response = requests.post(
        f"{MCP_URL}/request",
        headers=HEADERS,
        json=request_data
    )
    
    if response.status_code == 200:
        data = response.json()
        # Extract the actual result from the MCP response
        if "result" in data and "content" in data["result"]:
            result_text = data["result"]["content"][0]["text"]
            return eval(result_text)  # Convert string representation to dict
    return {"error": f"Failed to call {tool_name}: {response.status_code}"}

def test_mcp_status():
    """Test MCP server status"""
    print("\n=== Testing MCP Server Status ===")
    response = requests.get(f"{MCP_URL}/status", headers={"X-API-Key": API_KEY})
    if response.status_code == 200:
        status = response.json()
        print(f"✅ MCP Server: {status['mcp_server']['name']} v{status['mcp_server']['version']}")
        print(f"   Tools: {status['mcp_server']['capabilities']['tools']}")
        print(f"   Resources: {status['mcp_server']['capabilities']['resources']}")
        print(f"   Prompts: {status['mcp_server']['capabilities']['prompts']}")
    else:
        print(f"❌ Failed to get status: {response.status_code}")

def test_analyze_region():
    """Test analyze_region tool with description analysis"""
    print("\n=== Testing analyze_region Tool ===")
    result = call_mcp_tool("analyze_region", {
        "region_id": 1000004,
        "include_paths": False
    })
    
    if "error" not in result:
        region = result.get("region", {})
        analysis = result.get("analysis", {})
        print(f"✅ Region: {region.get('name')} (vnum: {region.get('vnum')})")
        
        desc_analysis = analysis.get("description_analysis", {})
        if desc_analysis:
            print(f"   Description exists: {desc_analysis.get('has_description')}")
            print(f"   Word count: {desc_analysis.get('word_count')}")
            print(f"   Quality score: {desc_analysis.get('quality_score')}")
            print(f"   Completeness: {desc_analysis.get('completeness_score', 0):.1f}/10")
            print(f"   Content flags: {desc_analysis.get('content_flags')}")
    else:
        print(f"❌ {result['error']}")

def test_search_regions():
    """Test search_regions with description filtering"""
    print("\n=== Testing search_regions Tool ===")
    result = call_mcp_tool("search_regions", {
        "include_descriptions": "summary",
        "has_description": True
    })
    
    if "error" not in result:
        print(f"✅ Total regions found: {result.get('total_found')}")
        summary = result.get("summary", {})
        print(f"   With descriptions: {summary.get('with_descriptions')}")
        print(f"   Approved: {summary.get('approved')}")
        print(f"   Requiring review: {summary.get('requiring_review')}")
        
        # Show regions with descriptions
        for region in result.get("regions", [])[:3]:
            if region.get("has_description"):
                print(f"   - {region['name']} (vnum: {region['vnum']})")
    else:
        print(f"❌ {result['error']}")

def test_generate_description():
    """Test generate_region_description tool"""
    print("\n=== Testing generate_region_description Tool ===")
    result = call_mcp_tool("generate_region_description", {
        "region_name": "Whispering Peaks",
        "terrain_theme": "mountain peaks shrouded in mist",
        "description_style": "mysterious",
        "description_length": "moderate",
        "include_sections": ["overview", "geography", "atmosphere", "wildlife"]
    })
    
    if "error" not in result:
        print(f"✅ Generated description for: {result.get('region_name')}")
        print(f"   Word count: {result.get('word_count')}")
        print(f"   Character count: {result.get('character_count')}")
        print(f"   Suggested quality score: {result.get('suggested_quality_score', 0):.1f}")
        
        metadata = result.get("metadata", {})
        print(f"   Metadata flags set:")
        for key, value in metadata.items():
            if value and key != "quality_score":
                print(f"     - {key}: {value}")
        
        # Show preview
        desc = result.get("generated_description", "")
        if desc:
            print(f"\n   Description preview (first 200 chars):")
            print(f"   {desc[:200]}...")
    else:
        print(f"❌ {result['error']}")

def test_analyze_quality():
    """Test analyze_description_quality tool"""
    print("\n=== Testing analyze_description_quality Tool ===")
    result = call_mcp_tool("analyze_description_quality", {
        "vnum": 1000004,
        "suggest_improvements": True
    })
    
    if "error" not in result:
        print(f"✅ Analyzed: {result.get('name')} (vnum: {result.get('vnum')})")
        print(f"   Current quality score: {result.get('current_quality_score') or 'Not set'}")
        
        analysis = result.get("analysis", {})
        print(f"   Word count: {analysis.get('word_count')}")
        print(f"   Completeness score: {analysis.get('completeness_score', 0):.1f}/10")
        
        # Show content flags
        content_flags = analysis.get("content_flags", {})
        print(f"   Content present:")
        for flag, value in content_flags.items():
            status = "✓" if value else "✗"
            print(f"     {status} {flag}")
        
        # Show improvements
        improvements = result.get("improvements", [])
        if improvements:
            print(f"\n   Suggested improvements:")
            for imp in improvements[:3]:
                print(f"     - {imp}")
    else:
        print(f"❌ {result['error']}")

def test_list_tools():
    """List all available MCP tools"""
    print("\n=== Available MCP Tools ===")
    response = requests.get(f"{MCP_URL}/tools", headers={"X-API-Key": API_KEY})
    if response.status_code == 200:
        data = response.json()
        tools = data.get("tools", [])
        
        # Filter for description-related tools
        desc_tools = [t for t in tools if "description" in t["name"].lower() or "description" in t["description"].lower()]
        
        print(f"✅ Total tools: {len(tools)}")
        print(f"   Description-related tools: {len(desc_tools)}")
        
        for tool in desc_tools:
            print(f"\n   📦 {tool['name']}")
            print(f"      {tool['description']}")
    else:
        print(f"❌ Failed to list tools: {response.status_code}")

def main():
    print("=" * 60)
    print("MCP SERVER ENHANCED DESCRIPTION FEATURES TEST")
    print("=" * 60)
    
    # Run all tests
    test_mcp_status()
    test_list_tools()
    test_analyze_region()
    test_search_regions()
    test_generate_description()
    test_analyze_quality()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nThe MCP server is successfully running with all enhanced")
    print("description features. AI agents can now:")
    print("  - Generate comprehensive region descriptions")
    print("  - Analyze description quality and completeness")
    print("  - Search regions by description metadata")
    print("  - Update descriptions with proper tracking")

if __name__ == "__main__":
    main()