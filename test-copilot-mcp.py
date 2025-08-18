"""
Test script to verify MCP server connectivity and GitHub Copilot integration
"""

import os
import requests
import json
from typing import Dict, Any


def test_mcp_server_health() -> bool:
    """Test if MCP server is accessible"""
    try:
        response = requests.get("http://luminarimud.com:8001/health", timeout=10)
        if response.status_code == 200:
            print("✅ MCP server health check passed")
            return True
        else:
            print(f"⚠️  MCP server returned status {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Cannot reach MCP server: {e}")
        return False


def test_mcp_authentication() -> bool:
    """Test MCP server authentication"""
    mcp_key = os.getenv("WILDEDITOR_MCP_KEY")
    if not mcp_key:
        print("❌ WILDEDITOR_MCP_KEY environment variable not set")
        return False
    
    try:
        headers = {"X-API-Key": mcp_key}
        response = requests.get(
            "http://luminarimud.com:8001/health", 
            headers=headers, 
            timeout=10
        )
        if response.status_code == 200:
            print("✅ MCP server authentication successful")
            return True
        else:
            print(f"❌ MCP authentication failed with status {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ MCP authentication test failed: {e}")
        return False


def test_mcp_tools() -> bool:
    """Test if MCP tools are available"""
    mcp_key = os.getenv("WILDEDITOR_MCP_KEY")
    if not mcp_key:
        print("❌ WILDEDITOR_MCP_KEY environment variable not set")
        return False
    
    try:
        headers = {"X-API-Key": mcp_key, "Content-Type": "application/json"}
        # Test tools endpoint
        response = requests.get(
            "http://luminarimud.com:8001/mcp/tools", 
            headers=headers, 
            timeout=10
        )
        if response.status_code == 200:
            tools = response.json()
            print(f"✅ MCP tools available: {len(tools.get('tools', []))} tools found")
            for tool in tools.get('tools', []):
                print(f"   • {tool.get('name', 'unknown')}: {tool.get('description', 'no description')}")
            return True
        else:
            print(f"⚠️  MCP tools endpoint returned status {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ MCP tools test failed: {e}")
        return False


def test_environment_variables() -> bool:
    """Test if required environment variables are set"""
    required_vars = [
        "WILDEDITOR_MCP_KEY",
        "WILDEDITOR_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("   Run the setup script or set them manually:")
        print("   $env:WILDEDITOR_MCP_KEY='your-mcp-key'")
        print("   $env:WILDEDITOR_API_KEY='your-api-key'")
        return False
    else:
        print("✅ All required environment variables are set")
        return True


def main():
    """Run all MCP integration tests"""
    print("🧪 Testing Wildeditor MCP Integration")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("MCP Server Health", test_mcp_server_health),
        ("MCP Authentication", test_mcp_authentication),
        ("MCP Tools", test_mcp_tools),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 All tests passed! GitHub Copilot MCP integration is ready.")
        print("\nNext steps:")
        print("1. Open VS Code in the wildeditor workspace")
        print("2. Start GitHub Copilot Chat")
        print("3. Try asking: 'What wilderness management tools are available?'")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")
        print("Run the setup script: .\\setup-copilot-mcp.ps1")


if __name__ == "__main__":
    main()
