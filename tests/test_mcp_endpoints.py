#!/usr/bin/env python3
"""
Test all standard MCP endpoints
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

def test_endpoint(name: str, method: str, url: str, data: Dict[str, Any] = None) -> bool:
    """Test a single endpoint"""
    print(f"\n🧪 Testing {name}...")
    print(f"   Method: {method}")
    print(f"   URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS)
        else:
            response = requests.post(url, headers=HEADERS, json=data or {})
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success (Status: {response.status_code})")
            
            # Show sample of response
            result_str = json.dumps(result, indent=2)
            lines = result_str.split('\n')
            if len(lines) > 10:
                print(f"   Response preview:")
                for line in lines[:10]:
                    print(f"     {line}")
                print(f"     ... ({len(lines) - 10} more lines)")
            else:
                print(f"   Response: {result_str}")
            return True
        else:
            print(f"   ❌ Failed (Status: {response.status_code})")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("MCP STANDARD ENDPOINTS TEST")
    print("=" * 60)
    
    results = []
    
    # Test root endpoint
    results.append(test_endpoint(
        "Root MCP endpoint (/mcp)",
        "POST",
        MCP_URL,
        {
            "jsonrpc": "2.0",
            "id": "test-1",
            "method": "tools/list"
        }
    ))
    
    # Test /mcp/request endpoint
    results.append(test_endpoint(
        "Request endpoint (/mcp/request)",
        "POST",
        f"{MCP_URL}/request",
        {
            "jsonrpc": "2.0",
            "id": "test-2",
            "method": "resources/list"
        }
    ))
    
    # Test standard method endpoints
    results.append(test_endpoint(
        "Tools list (/mcp/tools/list)",
        "POST",
        f"{MCP_URL}/tools/list",
        {}
    ))
    
    results.append(test_endpoint(
        "Resources list (/mcp/resources/list)",
        "POST",
        f"{MCP_URL}/resources/list",
        {}
    ))
    
    results.append(test_endpoint(
        "Prompts list (/mcp/prompts/list)",
        "POST",
        f"{MCP_URL}/prompts/list",
        {}
    ))
    
    # Test tool call
    results.append(test_endpoint(
        "Tool call (/mcp/tools/call)",
        "POST",
        f"{MCP_URL}/tools/call",
        {
            "jsonrpc": "2.0",
            "id": "test-call",
            "params": {
                "name": "analyze_region",
                "arguments": {
                    "region_id": 1000004,
                    "include_paths": False
                }
            }
        }
    ))
    
    # Test GET endpoints (backward compatibility)
    results.append(test_endpoint(
        "GET tools (/mcp/tools)",
        "GET",
        f"{MCP_URL}/tools"
    ))
    
    results.append(test_endpoint(
        "GET status (/mcp/status)",
        "GET",
        f"{MCP_URL}/status"
    ))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! MCP server has all standard endpoints.")
    else:
        print(f"⚠️  {total - passed} tests failed. Check the errors above.")
    
    print("\n" + "=" * 60)
    print("ENDPOINT COMPATIBILITY")
    print("=" * 60)
    
    print("\n✅ Standard MCP Protocol Endpoints:")
    print("  POST /mcp                - Root JSON-RPC endpoint")
    print("  POST /mcp/request        - Alternative JSON-RPC endpoint")
    print("  POST /mcp/tools/list     - List available tools")
    print("  POST /mcp/tools/call     - Call a tool")
    print("  POST /mcp/resources/list - List available resources")
    print("  POST /mcp/resources/read - Read a resource")
    print("  POST /mcp/prompts/list   - List available prompts")
    print("  POST /mcp/prompts/get    - Get a prompt")
    
    print("\n✅ Additional Convenience Endpoints:")
    print("  GET  /mcp/status         - Server status")
    print("  GET  /mcp/tools          - List tools (simple)")
    print("  GET  /mcp/resources      - List resources (simple)")
    print("  GET  /mcp/prompts        - List prompts (simple)")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)