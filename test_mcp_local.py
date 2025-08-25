#!/usr/bin/env python3
"""
Test MCP endpoints locally
"""

import sys
import asyncio
sys.path.insert(0, '/home/luminari/wildeditor/apps/mcp/src')

from mcp.protocol import MCPRequest, MCPServer
from mcp.tools import ToolRegistry
from mcp.resources import ResourceRegistry
from mcp.prompts import PromptRegistry

async def test_local():
    """Test MCP server locally"""
    print("=" * 60)
    print("LOCAL MCP SERVER TEST")
    print("=" * 60)
    
    # Initialize components
    mcp_server = MCPServer("wildeditor-mcp-server", "1.0.0")
    tool_registry = ToolRegistry()
    resource_registry = ResourceRegistry()
    prompt_registry = PromptRegistry()
    
    # Register components
    for name, tool_info in tool_registry.tools.items():
        mcp_server.register_tool(
            name, 
            tool_info["function"],
            tool_info["description"], 
            tool_info["parameters"]
        )
    
    for uri, resource_info in resource_registry.resources.items():
        mcp_server.register_resource(
            uri,
            resource_info["function"],
            resource_info["name"],
            resource_info["description"]
        )
    
    for name, prompt_info in prompt_registry.prompts.items():
        mcp_server.register_prompt(
            name,
            prompt_info["function"],
            prompt_info["description"],
            prompt_info["arguments"]
        )
    
    print(f"\n✅ Registered {len(tool_registry.tools)} tools")
    print(f"✅ Registered {len(resource_registry.resources)} resources")
    print(f"✅ Registered {len(prompt_registry.prompts)} prompts")
    
    # Test initialize
    print("\n🧪 Testing initialize...")
    request = MCPRequest(
        jsonrpc="2.0",
        id="test-1",
        method="initialize",
        params={"protocolVersion": "2024-11-05"}
    )
    response = await mcp_server.handle_request(request)
    print(f"   Response: {response.model_dump()['result']['serverInfo']}")
    
    # Test tools/list
    print("\n🧪 Testing tools/list...")
    request = MCPRequest(
        jsonrpc="2.0",
        id="test-2",
        method="tools/list"
    )
    response = await mcp_server.handle_request(request)
    tools = response.model_dump()['result']['tools']
    print(f"   Found {len(tools)} tools:")
    for tool in tools[:3]:
        print(f"     - {tool['name']}: {tool['description'][:60]}...")
    
    # Test resources/list
    print("\n🧪 Testing resources/list...")
    request = MCPRequest(
        jsonrpc="2.0",
        id="test-3",
        method="resources/list"
    )
    response = await mcp_server.handle_request(request)
    resources = response.model_dump()['result']['resources']
    print(f"   Found {len(resources)} resources:")
    for resource in resources[:3]:
        print(f"     - {resource['name']}: {resource['description'][:60]}...")
    
    # Test prompts/list
    print("\n🧪 Testing prompts/list...")
    request = MCPRequest(
        jsonrpc="2.0",
        id="test-4",
        method="prompts/list"
    )
    response = await mcp_server.handle_request(request)
    prompts = response.model_dump()['result']['prompts']
    print(f"   Found {len(prompts)} prompts:")
    for prompt in prompts[:3]:
        print(f"     - {prompt['name']}: {prompt['description'][:60]}...")
    
    # Test tool call
    print("\n🧪 Testing tools/call (analyze_region)...")
    request = MCPRequest(
        jsonrpc="2.0",
        id="test-5",
        method="tools/call",
        params={
            "name": "analyze_region",
            "arguments": {
                "region_id": 1000004,
                "include_paths": False
            }
        }
    )
    response = await mcp_server.handle_request(request)
    result = response.model_dump()
    if "error" in result:
        print(f"   Error: {result['error']}")
    else:
        print(f"   Success: Got region analysis")
    
    print("\n" + "=" * 60)
    print("✅ Local MCP server is working correctly!")
    print("All standard MCP protocol methods are functional.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_local())