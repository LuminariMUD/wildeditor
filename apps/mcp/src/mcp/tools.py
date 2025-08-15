"""
MCP Tools for Wildeditor Wilderness Management

This module contains tools that AI agents can use to interact with
the wilderness system through the backend API.
"""

from typing import Dict, Any, List, Optional
import httpx
from ..config import settings


class ToolRegistry:
    """Registry for MCP tools"""
    
    def __init__(self):
        self.tools = {}
        self._register_wilderness_tools()
    
    def register_tool(self, name: str, func, description: str, parameters: Dict[str, Any]):
        """Register a tool"""
        self.tools[name] = {
            "function": func,
            "description": description,
            "parameters": parameters
        }
    
    def get_tool(self, name: str):
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [
            {
                "name": name,
                "description": tool_info["description"],
                "inputSchema": tool_info["parameters"]
            }
            for name, tool_info in self.tools.items()
        ]
    
    def _register_wilderness_tools(self):
        """Register wilderness-specific tools"""
        
        # Region analysis tool
        self.register_tool(
            "analyze_region",
            self._analyze_region,
            "Analyze a wilderness region by coordinates to get terrain, exits, and environmental data",
            {
                "type": "object",
                "properties": {
                    "region_id": {
                        "type": "integer",
                        "description": "The region ID to analyze"
                    },
                    "include_paths": {
                        "type": "boolean",
                        "description": "Whether to include connected paths",
                        "default": True
                    }
                },
                "required": ["region_id"]
            }
        )
        
        # Path finding tool
        self.register_tool(
            "find_path",
            self._find_path,
            "Find paths between two regions in the wilderness",
            {
                "type": "object",
                "properties": {
                    "from_region": {
                        "type": "integer",
                        "description": "Starting region ID"
                    },
                    "to_region": {
                        "type": "integer",
                        "description": "Destination region ID"
                    },
                    "max_distance": {
                        "type": "integer",
                        "description": "Maximum path distance to search",
                        "default": 10
                    }
                },
                "required": ["from_region", "to_region"]
            }
        )
        
        # Region search tool
        self.register_tool(
            "search_regions",
            self._search_regions,
            "Search for regions by terrain type, environmental conditions, or description",
            {
                "type": "object",
                "properties": {
                    "terrain_type": {
                        "type": "string",
                        "description": "Terrain type to search for (e.g., 'forest', 'mountain', 'desert')"
                    },
                    "environment": {
                        "type": "string",
                        "description": "Environmental condition (e.g., 'cold', 'hot', 'humid')"
                    },
                    "description_keywords": {
                        "type": "string",
                        "description": "Keywords to search in region descriptions"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 20
                    }
                },
                "required": []
            }
        )
        
        # Create region tool
        self.register_tool(
            "create_region",
            self._create_region,
            "Create a new wilderness region with specified properties",
            {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the region"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the region"
                    },
                    "terrain_type": {
                        "type": "string",
                        "description": "Primary terrain type"
                    },
                    "environment": {
                        "type": "string",
                        "description": "Environmental conditions"
                    },
                    "coordinates": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "z": {"type": "integer"}
                        },
                        "description": "3D coordinates for the region"
                    }
                },
                "required": ["name", "description", "terrain_type"]
            }
        )
        
        # Validate region connections tool
        self.register_tool(
            "validate_connections",
            self._validate_connections,
            "Validate that region connections are logical and consistent",
            {
                "type": "object",
                "properties": {
                    "region_id": {
                        "type": "integer",
                        "description": "Region ID to validate connections for"
                    },
                    "check_bidirectional": {
                        "type": "boolean",
                        "description": "Check if connections are bidirectional",
                        "default": True
                    }
                },
                "required": ["region_id"]
            }
        )
        
        # Real-time terrain analysis tool
        self.register_tool(
            "analyze_terrain_at_coordinates",
            self._analyze_terrain_at_coordinates,
            "Get real-time terrain data at specific wilderness coordinates using the game engine",
            {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate (-1024 to +1024)"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate (-1024 to +1024)"
                    }
                },
                "required": ["x", "y"]
            }
        )
        
        # Wilderness room finder tool
        self.register_tool(
            "find_wilderness_room",
            self._find_wilderness_room,
            "Find wilderness room at specific coordinates or get room details by VNUM",
            {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate (-1024 to +1024)"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate (-1024 to +1024)"
                    },
                    "vnum": {
                        "type": "integer",
                        "description": "Room VNUM to get details for (alternative to coordinates)"
                    }
                },
                "anyOf": [
                    {"required": ["x", "y"]},
                    {"required": ["vnum"]}
                ]
            }
        )
        
        # Zone entrance finder tool
        self.register_tool(
            "find_zone_entrances",
            self._find_zone_entrances,
            "Find all zone entrances in the wilderness that connect to other game areas",
            {
                "type": "object",
                "properties": {},
                "required": []
            }
        )
        
        # Generate wilderness map tool
        self.register_tool(
            "generate_wilderness_map",
            self._generate_wilderness_map,
            "Generate a detailed wilderness map for a specific area showing terrain types",
            {
                "type": "object",
                "properties": {
                    "center_x": {
                        "type": "integer",
                        "description": "Center X coordinate"
                    },
                    "center_y": {
                        "type": "integer",
                        "description": "Center Y coordinate"
                    },
                    "radius": {
                        "type": "integer",
                        "description": "Map radius (1-31)",
                        "minimum": 1,
                        "maximum": 31,
                        "default": 10
                    }
                },
                "required": ["center_x", "center_y"]
            }
        )
    
    async def _analyze_region(self, region_id: int, include_paths: bool = True) -> Dict[str, Any]:
        """Analyze a wilderness region"""
        async with httpx.AsyncClient() as client:
            try:
                # Get region data
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                response = await client.get(
                    f"{settings.backend_base_url}/regions/{region_id}",
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 404:
                    return {"error": f"Region {region_id} not found"}
                
                response.raise_for_status()
                region_data = response.json()
                
                result = {
                    "region": region_data,
                    "analysis": {
                        "terrain_features": self._extract_terrain_features(region_data),
                        "environmental_conditions": self._extract_environmental_data(region_data),
                        "accessibility": self._analyze_accessibility(region_data)
                    }
                }
                
                if include_paths:
                    # Get connected paths
                    path_response = await client.get(
                        f"{settings.backend_base_url}/regions/{region_id}/paths",
                        headers=headers,
                        timeout=30.0
                    )
                    if path_response.status_code == 200:
                        result["connected_paths"] = path_response.json()
                
                return result
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to analyze region: {str(e)}"}
    
    async def _find_path(self, from_region: int, to_region: int, max_distance: int = 10) -> Dict[str, Any]:
        """Find path between regions"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                response = await client.get(
                    f"{settings.backend_base_url}/paths/find",
                    params={
                        "from": from_region,
                        "to": to_region,
                        "max_distance": max_distance
                    },
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to find path: {str(e)}"}
    
    async def _search_regions(self, terrain_type: Optional[str] = None, 
                            environment: Optional[str] = None,
                            description_keywords: Optional[str] = None,
                            limit: int = 20) -> Dict[str, Any]:
        """Search for regions"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                params: Dict[str, Any] = {"limit": limit}
                
                if terrain_type:
                    params["terrain_type"] = terrain_type
                if environment:
                    params["environment"] = environment
                if description_keywords:
                    params["description"] = description_keywords
                
                response = await client.get(
                    f"{settings.backend_base_url}/regions/search",
                    params=params,
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to search regions: {str(e)}"}
    
    async def _create_region(self, name: str, description: str, terrain_type: str,
                           environment: Optional[str] = None, 
                           coordinates: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Create a new region"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                data: Dict[str, Any] = {
                    "name": name,
                    "description": description,
                    "terrain_type": terrain_type
                }
                
                if environment:
                    data["environment"] = environment
                if coordinates:
                    data["coordinates"] = coordinates
                
                response = await client.post(
                    f"{settings.backend_base_url}/regions",
                    json=data,
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to create region: {str(e)}"}
    
    async def _validate_connections(self, region_id: int, check_bidirectional: bool = True) -> Dict[str, Any]:
        """Validate region connections"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                response = await client.get(
                    f"{settings.backend_base_url}/regions/{region_id}/validate",
                    params={"check_bidirectional": check_bidirectional},
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to validate connections: {str(e)}"}
    
    def _extract_terrain_features(self, region_data: Dict[str, Any]) -> List[str]:
        """Extract terrain features from region data"""
        features = []
        
        # Basic terrain analysis
        if "terrain_type" in region_data:
            features.append(f"Primary terrain: {region_data['terrain_type']}")
        
        # Look for terrain keywords in description
        description = region_data.get("description", "").lower()
        terrain_keywords = ["forest", "mountain", "river", "lake", "desert", "swamp", "cave", "hill"]
        
        for keyword in terrain_keywords:
            if keyword in description:
                features.append(f"Contains {keyword}")
        
        return features
    
    def _extract_environmental_data(self, region_data: Dict[str, Any]) -> List[str]:
        """Extract environmental conditions"""
        conditions = []
        
        if "environment" in region_data:
            conditions.append(f"Climate: {region_data['environment']}")
        
        # Environmental keywords
        description = region_data.get("description", "").lower()
        env_keywords = ["cold", "hot", "humid", "dry", "windy", "calm", "dark", "bright"]
        
        for keyword in env_keywords:
            if keyword in description:
                conditions.append(f"Condition: {keyword}")
        
        return conditions
    
    def _analyze_accessibility(self, region_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze region accessibility"""
        return {
            "has_exits": len(region_data.get("exits", [])) > 0,
            "exit_count": len(region_data.get("exits", [])),
            "is_isolated": len(region_data.get("exits", [])) == 0,
            "connectivity_score": min(len(region_data.get("exits", [])), 10) / 10.0
        }
    
    async def _analyze_terrain_at_coordinates(self, x: int, y: int) -> Dict[str, Any]:
        """Analyze real-time terrain at specific coordinates"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                response = await client.get(
                    f"{settings.backend_base_url}/terrain/at-coordinates",
                    params={"x": x, "y": y},
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to analyze terrain: {str(e)}"}
    
    async def _find_wilderness_room(self, x: Optional[int] = None, y: Optional[int] = None, 
                                  vnum: Optional[int] = None) -> Dict[str, Any]:
        """Find wilderness room by coordinates or VNUM"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                
                if vnum is not None:
                    # Get room by VNUM
                    response = await client.get(
                        f"{settings.backend_base_url}/wilderness/rooms/{vnum}",
                        headers=headers,
                        timeout=30.0
                    )
                elif x is not None and y is not None:
                    # Get room by coordinates
                    response = await client.get(
                        f"{settings.backend_base_url}/wilderness/rooms/at-coordinates",
                        params={"x": x, "y": y},
                        headers=headers,
                        timeout=30.0
                    )
                else:
                    return {"error": "Must provide either coordinates (x,y) or vnum"}
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to find wilderness room: {str(e)}"}
    
    async def _find_zone_entrances(self) -> Dict[str, Any]:
        """Find all zone entrances in the wilderness"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                response = await client.get(
                    f"{settings.backend_base_url}/wilderness/navigation/entrances",
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to find zone entrances: {str(e)}"}
    
    async def _generate_wilderness_map(self, center_x: int, center_y: int, radius: int = 10) -> Dict[str, Any]:
        """Generate wilderness map for an area"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                response = await client.get(
                    f"{settings.backend_base_url}/terrain/map-data",
                    params={"center_x": center_x, "center_y": center_y, "radius": radius},
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to generate wilderness map: {str(e)}"}
