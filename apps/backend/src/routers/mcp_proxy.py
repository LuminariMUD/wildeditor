"""
MCP Proxy Router for AI Services

This module provides a proxy endpoint for the frontend to call MCP services,
avoiding CORS issues with direct browser-to-MCP communication.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import httpx
import os
import json

router = APIRouter()

# MCP Server Configuration
MCP_URL = os.getenv("MCP_URL", "http://luminarimud.com:8001/mcp")
MCP_API_KEY = os.getenv("MCP_API_KEY", "xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0=")


class MCPRequest(BaseModel):
    """Request model for MCP proxy calls."""
    tool_name: str = Field(..., description="Name of the MCP tool to call")
    arguments: Dict[str, Any] = Field(..., description="Arguments for the tool")
    request_id: Optional[str] = Field(None, description="Optional request ID for tracking")


class MCPResponse(BaseModel):
    """Response model for MCP proxy calls."""
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class GenerateDescriptionRequest(BaseModel):
    """Request model for generating region descriptions."""
    region_vnum: Optional[int] = None
    region_name: Optional[str] = None
    region_type: Optional[int] = None
    terrain_theme: Optional[str] = None
    description_style: Optional[str] = None
    description_length: Optional[str] = None
    include_sections: Optional[list[str]] = None
    user_prompt: Optional[str] = None


@router.post("/generate-description", response_model=MCPResponse)
async def generate_region_description(request: GenerateDescriptionRequest):
    """
    Generate a region description using the MCP AI service.
    
    This endpoint proxies the request to the MCP server, avoiding CORS issues
    when the frontend tries to call MCP directly.
    
    Args:
        request: GenerateDescriptionRequest with region details and generation parameters
    
    Returns:
        MCPResponse with the generated description
    """
    try:
        # Prepare MCP request
        mcp_request = {
            "id": f"generate-desc-{request.region_vnum or 'new'}",
            "method": "tools/call",
            "params": {
                "name": "generate_region_description",
                "arguments": {
                    "region_vnum": request.region_vnum,
                    "region_name": request.region_name,
                    "region_type": request.region_type,
                    "terrain_theme": request.terrain_theme,
                    "description_style": request.description_style,
                    "description_length": request.description_length,
                    "include_sections": request.include_sections,
                    "user_prompt": request.user_prompt
                }
            }
        }
        
        # Remove None values from arguments
        mcp_request["params"]["arguments"] = {
            k: v for k, v in mcp_request["params"]["arguments"].items() 
            if v is not None
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_URL}/request",
                json=mcp_request,
                headers={
                    "X-API-Key": MCP_API_KEY,
                    "Content-Type": "application/json"
                },
                timeout=60.0  # Longer timeout for AI generation
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"MCP server returned status {response.status_code}"
                )
            
            data = response.json()
            
            # Extract result from MCP response
            if "result" in data and "content" in data["result"]:
                result_text = data["result"]["content"][0]["text"]
                try:
                    # Try to parse as JSON
                    result = json.loads(result_text)
                except json.JSONDecodeError:
                    # Return as plain text if not JSON
                    result = {
                        "generated_description": result_text,
                        "ai_provider": "mcp"
                    }
                
                return MCPResponse(success=True, result=result)
            elif "error" in data:
                return MCPResponse(success=False, error=data["error"].get("message", "Unknown error"))
            else:
                return MCPResponse(success=False, error="Invalid response from MCP server")
                
    except httpx.RequestError as e:
        return MCPResponse(success=False, error=f"Failed to connect to MCP server: {str(e)}")
    except Exception as e:
        return MCPResponse(success=False, error=f"Internal error: {str(e)}")


@router.post("/call-tool", response_model=MCPResponse)
async def call_mcp_tool(request: MCPRequest):
    """
    Generic proxy endpoint for calling any MCP tool.
    
    Args:
        request: MCPRequest with tool name and arguments
    
    Returns:
        MCPResponse with the tool result
    """
    try:
        # Prepare MCP request
        mcp_request = {
            "id": request.request_id or f"proxy-{request.tool_name}",
            "method": "tools/call",
            "params": {
                "name": request.tool_name,
                "arguments": request.arguments
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_URL}/request",
                json=mcp_request,
                headers={
                    "X-API-Key": MCP_API_KEY,
                    "Content-Type": "application/json"
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"MCP server returned status {response.status_code}"
                )
            
            data = response.json()
            
            # Extract result from MCP response
            if "result" in data and "content" in data["result"]:
                result_text = data["result"]["content"][0]["text"]
                try:
                    # Try to parse as JSON first
                    result = json.loads(result_text)
                except json.JSONDecodeError:
                    # If not JSON, try to parse Python dict format
                    try:
                        import ast
                        result = ast.literal_eval(result_text)
                    except (ValueError, SyntaxError):
                        # If that fails too, return as plain text
                        result = {"text": result_text}
                
                return MCPResponse(success=True, result=result)
            elif "error" in data:
                return MCPResponse(success=False, error=data["error"].get("message", "Unknown error"))
            else:
                return MCPResponse(success=False, error="Invalid response from MCP server")
                
    except httpx.RequestError as e:
        return MCPResponse(success=False, error=f"Failed to connect to MCP server: {str(e)}")
    except Exception as e:
        return MCPResponse(success=False, error=f"Internal error: {str(e)}")


@router.get("/status")
async def get_mcp_status():
    """
    Check if the MCP server is accessible and running.
    
    Returns:
        Status information about MCP server connectivity
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MCP_URL}/status",
                headers={"X-API-Key": MCP_API_KEY},
                timeout=5.0
            )
            
            if response.status_code == 200:
                return {
                    "mcp_available": True,
                    "mcp_url": MCP_URL,
                    "status": response.json()
                }
            else:
                return {
                    "mcp_available": False,
                    "mcp_url": MCP_URL,
                    "error": f"MCP server returned status {response.status_code}"
                }
                
    except Exception as e:
        return {
            "mcp_available": False,
            "mcp_url": MCP_URL,
            "error": str(e)
        }