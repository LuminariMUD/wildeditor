"""
Core MCP protocol implementation
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
import json


class MCPMethodType(str, Enum):
    """MCP method types"""
    INITIALIZE = "initialize"
    LIST_TOOLS = "tools/list"
    CALL_TOOL = "tools/call"
    LIST_RESOURCES = "resources/list"
    READ_RESOURCE = "resources/read"
    LIST_PROMPTS = "prompts/list"
    GET_PROMPT = "prompts/get"


class MCPRequest(BaseModel):
    """MCP request message"""
    jsonrpc: str = "2.0"
    id: Union[str, int]
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPNotification(BaseModel):
    """MCP notification message (no id field)"""
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPResponse(BaseModel):
    """MCP response message"""
    jsonrpc: str = "2.0"
    id: Union[str, int]
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class MCPError(BaseModel):
    """MCP error object"""
    code: int
    message: str
    data: Optional[Any] = None


class MCPCapabilities(BaseModel):
    """MCP server capabilities"""
    tools: Dict[str, Any] = Field(default_factory=dict)
    resources: Dict[str, Any] = Field(default_factory=dict)
    prompts: Dict[str, Any] = Field(default_factory=dict)


class MCPServerInfo(BaseModel):
    """MCP server information"""
    name: str
    version: str
    protocol_version: str = "2024-11-05"


class MCPServer:
    """
    MCP Server implementation for Wildeditor
    
    Handles MCP protocol messages and coordinates between tools,
    resources, and prompts.
    """
    
    def __init__(self, name: str = "wildeditor-mcp-server", version: str = "1.0.0"):
        self.server_info = MCPServerInfo(name=name, version=version)
        self.capabilities = MCPCapabilities()
        self.tools = {}
        self.resources = {}
        self.prompts = {}
        
    def register_tool(self, name: str, tool_func, description: str, parameters: Dict[str, Any]):
        """Register a tool with the MCP server"""
        self.tools[name] = {
            "function": tool_func,
            "description": description,
            "parameters": parameters
        }
        
    def register_resource(self, uri: str, resource_func, name: str, description: str):
        """Register a resource with the MCP server"""
        self.resources[uri] = {
            "function": resource_func,
            "name": name,
            "description": description
        }
        
    def register_prompt(self, name: str, prompt_func, description: str, arguments: List[Dict[str, Any]]):
        """Register a prompt with the MCP server"""
        self.prompts[name] = {
            "function": prompt_func,
            "description": description,
            "arguments": arguments
        }
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle an MCP request"""
        try:
            if request.method == MCPMethodType.INITIALIZE:
                return await self._handle_initialize(request)
            elif request.method == MCPMethodType.LIST_TOOLS:
                return await self._handle_list_tools(request)
            elif request.method == MCPMethodType.CALL_TOOL:
                return await self._handle_call_tool(request)
            elif request.method == MCPMethodType.LIST_RESOURCES:
                return await self._handle_list_resources(request)
            elif request.method == MCPMethodType.READ_RESOURCE:
                return await self._handle_read_resource(request)
            elif request.method == MCPMethodType.LIST_PROMPTS:
                return await self._handle_list_prompts(request)
            elif request.method == MCPMethodType.GET_PROMPT:
                return await self._handle_get_prompt(request)
            else:
                return MCPResponse(
                    id=request.id,
                    error={"code": -32601, "message": f"Method not found: {request.method}"}
                )
        except Exception as e:
            return MCPResponse(
                id=request.id,
                error={"code": -32603, "message": f"Internal error: {str(e)}"}
            )
    
    async def _handle_initialize(self, request: MCPRequest) -> MCPResponse:
        """Handle initialize request"""
        return MCPResponse(
            id=request.id,
            result={
                "protocolVersion": self.server_info.protocol_version,
                "capabilities": self.capabilities.model_dump(),
                "serverInfo": self.server_info.model_dump()
            }
        )
    
    async def _handle_list_tools(self, request: MCPRequest) -> MCPResponse:
        """Handle list tools request"""
        tools = []
        for name, tool_info in self.tools.items():
            tools.append({
                "name": name,
                "description": tool_info["description"],
                "inputSchema": tool_info["parameters"]
            })
        
        return MCPResponse(
            id=request.id,
            result={"tools": tools}
        )
    
    async def _handle_call_tool(self, request: MCPRequest) -> MCPResponse:
        """Handle call tool request"""
        if not request.params or "name" not in request.params:
            return MCPResponse(
                id=request.id,
                error={"code": -32602, "message": "Missing tool name"}
            )
        
        tool_name = request.params["name"]
        if tool_name not in self.tools:
            return MCPResponse(
                id=request.id,
                error={"code": -32602, "message": f"Unknown tool: {tool_name}"}
            )
        
        tool_func = self.tools[tool_name]["function"]
        arguments = request.params.get("arguments", {})
        
        try:
            result = await tool_func(**arguments)
            return MCPResponse(
                id=request.id,
                result={"content": [{"type": "text", "text": str(result)}]}
            )
        except Exception as e:
            return MCPResponse(
                id=request.id,
                error={"code": -32603, "message": f"Tool execution error: {str(e)}"}
            )
    
    async def _handle_list_resources(self, request: MCPRequest) -> MCPResponse:
        """Handle list resources request"""
        resources = []
        for uri, resource_info in self.resources.items():
            resources.append({
                "uri": uri,
                "name": resource_info["name"],
                "description": resource_info["description"],
                "mimeType": "application/json"
            })
        
        return MCPResponse(
            id=request.id,
            result={"resources": resources}
        )
    
    async def _handle_read_resource(self, request: MCPRequest) -> MCPResponse:
        """Handle read resource request"""
        if not request.params or "uri" not in request.params:
            return MCPResponse(
                id=request.id,
                error={"code": -32602, "message": "Missing resource URI"}
            )
        
        uri = request.params["uri"]
        if uri not in self.resources:
            return MCPResponse(
                id=request.id,
                error={"code": -32602, "message": f"Unknown resource: {uri}"}
            )
        
        resource_func = self.resources[uri]["function"]
        
        try:
            result = await resource_func()
            return MCPResponse(
                id=request.id,
                result={
                    "contents": [{
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(result, indent=2)
                    }]
                }
            )
        except Exception as e:
            return MCPResponse(
                id=request.id,
                error={"code": -32603, "message": f"Resource read error: {str(e)}"}
            )
    
    async def _handle_list_prompts(self, request: MCPRequest) -> MCPResponse:
        """Handle list prompts request"""
        prompts = []
        for name, prompt_info in self.prompts.items():
            prompts.append({
                "name": name,
                "description": prompt_info["description"],
                "arguments": prompt_info["arguments"]
            })
        
        return MCPResponse(
            id=request.id,
            result={"prompts": prompts}
        )
    
    async def _handle_get_prompt(self, request: MCPRequest) -> MCPResponse:
        """Handle get prompt request"""
        if not request.params or "name" not in request.params:
            return MCPResponse(
                id=request.id,
                error={"code": -32602, "message": "Missing prompt name"}
            )
        
        prompt_name = request.params["name"]
        if prompt_name not in self.prompts:
            return MCPResponse(
                id=request.id,
                error={"code": -32602, "message": f"Unknown prompt: {prompt_name}"}
            )
        
        prompt_func = self.prompts[prompt_name]["function"]
        arguments = request.params.get("arguments", {})
        
        try:
            result = await prompt_func(**arguments)
            return MCPResponse(
                id=request.id,
                result={
                    "description": result.get("description", ""),
                    "messages": result.get("messages", [])
                }
            )
        except Exception as e:
            return MCPResponse(
                id=request.id,
                error={"code": -32603, "message": f"Prompt execution error: {str(e)}"}
            )
