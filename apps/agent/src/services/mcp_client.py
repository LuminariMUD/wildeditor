"""MCP Server client for AI tools and terrain operations"""
import httpx
from typing import Optional, Dict, Any, List
import logging
from config import settings

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for interacting with the MCP server"""
    
    def __init__(self):
        self.base_url = settings.wilderness_mcp_url
        self.api_key = settings.mcp_api_key
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        logger.info(f"Initialized MCPClient with base URL: {self.base_url}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool with given arguments"""
        request_data = {
            "id": f"chat-agent-{tool_name}",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp/request",
                json=request_data,
                headers=self.headers,
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise Exception(f"MCP error: {result['error']}")
            
            return result.get("result", {})
    
    async def generate_description(
        self,
        region_name: Optional[str] = None,
        region_type: Optional[str] = None,
        terrain_theme: Optional[str] = None,
        description_style: str = "immersive",
        description_length: str = "medium",
        user_prompt: Optional[str] = None
    ) -> str:
        """Generate a region description using AI"""
        # Use the backend proxy for description generation
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.backend_api_url}/api/mcp/generate-description",
                json={
                    "region_name": region_name,
                    "region_type": region_type,
                    "terrain_theme": terrain_theme,
                    "description_style": description_style,
                    "description_length": description_length,
                    "user_prompt": user_prompt
                },
                headers={
                    "X-API-Key": settings.backend_api_key,
                    "Content-Type": "application/json"
                },
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("success") and result.get("result"):
                return result["result"].get("description", "")
            else:
                raise Exception(f"Failed to generate description: {result.get('error', 'Unknown error')}")
    
    async def analyze_terrain(self, x: int, y: int) -> Dict[str, Any]:
        """Analyze terrain at specific coordinates"""
        return await self.call_tool(
            "analyze_terrain_at_coordinates",
            {"x": x, "y": y}
        )
    
    async def analyze_complete_terrain(
        self,
        center_x: int,
        center_y: int,
        radius: int = 5
    ) -> Dict[str, Any]:
        """Get complete terrain analysis with overlays"""
        return await self.call_tool(
            "analyze_complete_terrain_map",
            {
                "center_x": center_x,
                "center_y": center_y,
                "radius": radius
            }
        )
    
    async def find_wilderness_room(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """Find a wilderness room at specific coordinates"""
        try:
            return await self.call_tool(
                "find_static_wilderness_room",
                {"x": x, "y": y}
            )
        except Exception as e:
            logger.warning(f"No room found at ({x}, {y}): {str(e)}")
            return None
    
    async def find_zone_entrances(self) -> List[Dict[str, Any]]:
        """Find all zone entrances in the wilderness"""
        result = await self.call_tool("find_zone_entrances", {})
        return result.get("entrances", [])
    
    async def generate_wilderness_map(
        self,
        center_x: int,
        center_y: int,
        radius: int = 10
    ) -> Dict[str, Any]:
        """Generate a wilderness map for an area"""
        return await self.call_tool(
            "generate_wilderness_map",
            {
                "center_x": center_x,
                "center_y": center_y,
                "radius": radius
            }
        )