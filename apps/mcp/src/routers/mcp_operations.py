"""
MCP operations endpoints

This router implements the core MCP protocol with tools, resources, and prompts
for wilderness management.
"""

from typing import Dict, Any, List, Optional
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from wildeditor_auth import verify_mcp_key
from ..config import settings
from ..mcp import MCPServer, MCPRequest, MCPResponse, MCPNotification
from ..mcp.tools import ToolRegistry
from ..mcp.resources import ResourceRegistry  
from ..mcp.prompts import PromptRegistry

router = APIRouter()

# Initialize MCP components
mcp_server = MCPServer("wildeditor-mcp-server", "1.0.0")
tool_registry = ToolRegistry()
resource_registry = ResourceRegistry()
prompt_registry = PromptRegistry()

# Register tools, resources, and prompts with MCP server
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


@router.post("/")
async def handle_jsonrpc(
    data: dict,
    authenticated: bool = Depends(verify_mcp_key)
):
    """
    Main JSON-RPC endpoint for GitHub Copilot MCP integration
    
    This endpoint handles standard MCP JSON-RPC requests and notifications
    that GitHub Copilot sends.
    """
    # Check if this is a notification (no id field) or request (has id field)
    if "id" in data:
        # This is a request - convert to MCPRequest
        request = MCPRequest(**data)
        response = await mcp_server.handle_request(request)
        return response.model_dump()
    else:
        # This is a notification - handle specially
        if data.get("method") == "notifications/initialized":
            # GitHub Copilot sends this after connecting
            return {"status": "acknowledged"}
        else:
            # For other notifications, just acknowledge
            return {"status": "acknowledged"}


@router.get("/status")
async def mcp_status(authenticated: bool = Depends(verify_mcp_key)):
    """
    MCP server status endpoint
    
    Returns the current status of MCP operations and available capabilities.
    """
    return {
        "mcp_server": {
            "name": "wildeditor-mcp-server",
            "version": "1.0.0",
            "protocol_version": "2024-11-05",
            "capabilities": {
                "tools": len(tool_registry.tools),
                "resources": len(resource_registry.resources),
                "prompts": len(prompt_registry.prompts)
            },
            "status": "ready"
        },
        "backend_integration": {
            "url": settings.backend_base_url,
            "status": "configured"
        },
        "authenticated": True
    }

@router.post("/initialize")
async def initialize_mcp(authenticated: bool = Depends(verify_mcp_key)):
    """
    Initialize MCP server session
    
    This endpoint handles MCP client initialization.
    """
    # Create mock initialization request
    init_request = MCPRequest(
        id="init-1",
        method="initialize",
        params={"protocolVersion": "2024-11-05"}
    )
    
    response = await mcp_server.handle_request(init_request)
    return response.model_dump()

@router.post("/request")
async def handle_mcp_request(request: MCPRequest, authenticated: bool = Depends(verify_mcp_key)):
    """
    Handle raw MCP protocol requests
    
    This is the main MCP protocol endpoint for handling JSON-RPC requests.
    """
    response = await mcp_server.handle_request(request)
    return response.model_dump()

# Individual endpoint implementations for easier testing
@router.get("/tools")
async def list_tools(authenticated: bool = Depends(verify_mcp_key)):
    """List available MCP tools"""
    return {"tools": tool_registry.list_tools()}

@router.get("/resources")
async def list_resources(authenticated: bool = Depends(verify_mcp_key)):
    """List available MCP resources"""
    return {"resources": resource_registry.list_resources()}

@router.get("/prompts")
async def list_prompts(authenticated: bool = Depends(verify_mcp_key)):
    """List available MCP prompts"""
    return {"prompts": prompt_registry.list_prompts()}

@router.get("/resources/{uri:path}")
async def read_resource(uri: str, authenticated: bool = Depends(verify_mcp_key)):
    """Read a specific resource"""
    # Convert path to URI format
    full_uri = f"wildeditor://{uri}" if not uri.startswith("wildeditor://") else uri
    
    resource = resource_registry.get_resource(full_uri)
    if not resource:
        raise HTTPException(status_code=404, detail=f"Resource not found: {full_uri}")
    
    try:
        result = await resource["function"]()
        return {
            "uri": full_uri,
            "name": resource["name"],
            "description": resource["description"],
            "content": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading resource: {str(e)}")

@router.post("/tools/{tool_name}")
async def call_tool(tool_name: str, arguments: dict = None, authenticated: bool = Depends(verify_mcp_key)):
    """Call a specific tool"""
    tool = tool_registry.get_tool(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")
    
    try:
        result = await tool["function"](**(arguments or {}))
        return {
            "tool": tool_name,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution error: {str(e)}")

@router.post("/prompts/{prompt_name}")
async def get_prompt(prompt_name: str, arguments: dict = None, authenticated: bool = Depends(verify_mcp_key)):
    """Get a specific prompt"""
    prompt = prompt_registry.get_prompt(prompt_name)
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Prompt not found: {prompt_name}")
    
    try:
        result = await prompt["function"]**(arguments or {})
        return {
            "prompt": prompt_name,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prompt execution error: {str(e)}")
