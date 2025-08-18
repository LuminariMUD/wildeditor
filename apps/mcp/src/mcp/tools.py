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
        
        # Region search tool - matches backend capabilities
        self.register_tool(
            "search_regions",
            self._search_regions,
            "Search for regions by type or zone. Region types: 1=Geographic, 2=Encounter, 3=Sector Transform, 4=Sector Override",
            {
                "type": "object",
                "properties": {
                    "region_type": {
                        "type": "integer",
                        "description": "Filter by region type (1=Geographic, 2=Encounter, 3=Sector Transform, 4=Sector Override)"
                    },
                    "zone_vnum": {
                        "type": "integer", 
                        "description": "Filter by zone vnum"
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

        # Path search tool - matches backend capabilities
        self.register_tool(
            "search_paths",
            self._search_paths,
            "Search for paths by type or zone. Path types: 0=Road, 1=Paved Road, 2=Dirt Road, 3=Geographic, 4=River, 5=River, 6=Trail",
            {
                "type": "object",
                "properties": {
                    "path_type": {
                        "type": "integer",
                        "description": "Filter by path type (0=Road, 1=Paved Road, 2=Dirt Road, 3=Geographic, 4=River, 5=River, 6=Trail)"
                    },
                    "zone_vnum": {
                        "type": "integer",
                        "description": "Filter by zone vnum"
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

        # Point analysis tool - uses points endpoint to find containing regions/paths
        self.register_tool(
            "find_regions_and_paths_at_point",
            self._find_regions_and_paths_at_point,
            "Find regions and paths that contain or are near a specific coordinate point",
            {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "number",
                        "description": "X coordinate"
                    },
                    "y": {
                        "type": "number", 
                        "description": "Y coordinate"
                    },
                    "radius": {
                        "type": "number",
                        "description": "Search radius around the point (default: 0.1)",
                        "default": 0.1
                    }
                },
                "required": ["x", "y"]
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
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"}
                            },
                            "required": ["x", "y"]
                        },
                        "description": "Array of coordinates defining the region polygon boundary"
                    }
                },
                "required": ["name", "description", "terrain_type", "coordinates"]
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
        
        # Static wilderness room finder tool
        self.register_tool(
            "find_static_wilderness_room",
            self._find_static_wilderness_room,
            "Find static wilderness room at specific coordinates or get room details by VNUM. Static rooms are pre-built wilderness content.",
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
        
        # Complete terrain analysis tool (enhanced with regions/paths)
        self.register_tool(
            "analyze_complete_terrain_map",
            self._analyze_complete_terrain_map,
            "Generate complete wilderness map including base terrain PLUS region and path overlays that modify terrain properties",
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
                        "description": "Map radius (1-15 recommended for detailed analysis)",
                        "minimum": 1,
                        "maximum": 15,
                        "default": 5
                    },
                    "include_regions": {
                        "type": "boolean",
                        "description": "Include region overlay analysis",
                        "default": True
                    },
                    "include_paths": {
                        "type": "boolean",
                        "description": "Include path overlay analysis", 
                        "default": True
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
    
    async def _search_regions(self, region_type: Optional[int] = None, 
                            zone_vnum: Optional[int] = None,
                            limit: int = 20) -> Dict[str, Any]:
        """Search for regions by type or zone"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                params: Dict[str, Any] = {}
                
                if region_type is not None:
                    params["region_type"] = region_type
                if zone_vnum is not None:
                    params["zone_vnum"] = zone_vnum
                
                response = await client.get(
                    f"{settings.backend_base_url}/regions/",
                    params=params,
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Apply limit if specified
                if isinstance(data, list) and limit and len(data) > limit:
                    data = data[:limit]
                    
                return {
                    "regions": data,
                    "count": len(data) if isinstance(data, list) else 0,
                    "filters": {
                        "region_type": region_type,
                        "zone_vnum": zone_vnum
                    }
                }
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to search regions: {str(e)}"}
    
    async def _search_paths(self, path_type: Optional[int] = None,
                          zone_vnum: Optional[int] = None,
                          limit: int = 20) -> Dict[str, Any]:
        """Search for paths by type or zone"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                params: Dict[str, Any] = {}
                
                if path_type is not None:
                    params["path_type"] = path_type
                if zone_vnum is not None:
                    params["zone_vnum"] = zone_vnum
                
                response = await client.get(
                    f"{settings.backend_base_url}/paths/",
                    params=params,
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Apply limit if specified
                if isinstance(data, list) and limit and len(data) > limit:
                    data = data[:limit]
                    
                return {
                    "paths": data,
                    "count": len(data) if isinstance(data, list) else 0,
                    "filters": {
                        "path_type": path_type,
                        "zone_vnum": zone_vnum
                    }
                }
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to search paths: {str(e)}"}

    async def _find_regions_and_paths_at_point(self, x: float, y: float,
                                             radius: float = 0.1) -> Dict[str, Any]:
        """Find regions and paths at a specific coordinate point"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                params = {
                    "x": x,
                    "y": y,
                    "radius": radius
                }
                
                response = await client.get(
                    f"{settings.backend_base_url}/points/",
                    params=params,
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to find regions/paths at point: {str(e)}"}
    
    async def _create_region(self, name: str, description: str, terrain_type: str,
                           environment: Optional[str] = None,
                           coordinates: Optional[List[Dict[str, float]]] = None) -> Dict[str, Any]:
        """Create a new region"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                
                # Generate a unique vnum (using timestamp-based approach)
                import time
                vnum = int(time.time() * 1000) % 100000000  # Reasonable range
                
                # Map terrain_type to region_type and region_props
                if terrain_type.lower() in ["wetlands", "marshland", "swamp"]:
                    region_type = 4  # REGION_SECTOR (override)
                    region_props = 16  # Marshland sector type
                elif terrain_type.lower() in ["forest", "thickets", "woods"]:
                    region_type = 4  # REGION_SECTOR (override)
                    region_props = 3   # Forest sector type
                elif terrain_type.lower() in ["hills", "highlands"]:
                    region_type = 4  # REGION_SECTOR (override)
                    region_props = 4   # Hills sector type
                else:
                    # Default to geographic region for unknown terrain types
                    region_type = 1  # REGION_GEOGRAPHIC
                    region_props = 0
                
                # Validate coordinates array
                coord_list = []
                if coordinates and len(coordinates) >= 3:
                    # Use provided coordinates (minimum 3 points for polygon)
                    coord_list = coordinates
                    # Ensure polygon is closed (first point = last point)
                    if coord_list[0] != coord_list[-1]:
                        coord_list.append(coord_list[0])
                else:
                    raise ValueError("Region requires at least 3 coordinate points to form a polygon")
                
                data = {
                    "vnum": vnum,
                    "zone_vnum": 10000,  # Default wilderness zone
                    "name": name,
                    "region_type": region_type,
                    "coordinates": coord_list,
                    "region_props": region_props,
                    "region_reset_data": "",
                    "region_reset_time": None
                }
                
                response = await client.post(
                    f"{settings.backend_base_url}/regions/",
                    json=data,
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to create region: {str(e)}"}
            except ValueError as e:
                return {"error": str(e)}
    
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
    
    async def _find_static_wilderness_room(self, x: Optional[int] = None, y: Optional[int] = None, 
                                  vnum: Optional[int] = None) -> Dict[str, Any]:
        """Find static wilderness room by coordinates or VNUM"""
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

    async def _analyze_complete_terrain_map(self, center_x: int, center_y: int, radius: int = 5, 
                                          include_regions: bool = True, include_paths: bool = True) -> Dict[str, Any]:
        """Generate complete wilderness map including terrain + region/path overlays"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                
                # 1. Get base terrain data
                terrain_response = await client.get(
                    f"{settings.backend_base_url}/terrain/map-data",
                    params={"center_x": center_x, "center_y": center_y, "radius": radius},
                    headers=headers,
                    timeout=30.0
                )
                terrain_response.raise_for_status()
                base_data = terrain_response.json()
                
                # 2. Enhance terrain data with overlays using spatial queries
                enhanced_map_data = {}
                for coord_key, terrain_point in base_data.get('map_data', {}).items():
                    enhanced_point = await self._apply_terrain_overlays(terrain_point)
                    enhanced_map_data[coord_key] = enhanced_point
                
                # 3. Analyze overlay coverage
                affected_coordinates = len([p for p in enhanced_map_data.values() 
                                          if p.get('overlays', {}).get('has_overlays', False)])
                
                # 4. Collect unique regions and paths affecting the area
                all_regions = set()
                all_paths = set()
                for point in enhanced_map_data.values():
                    for region in point.get('overlays', {}).get('regions', []):
                        all_regions.add((region['vnum'], region['name'], region.get('type_name', 'Unknown')))
                    for path in point.get('overlays', {}).get('paths', []):
                        all_paths.add((path['vnum'], path['name'], path.get('type_name', 'Unknown')))
                
                return {
                    "center": {"x": center_x, "y": center_y},
                    "radius": radius,
                    "bounds": base_data.get('bounds', {}),
                    "point_count": len(enhanced_map_data),
                    "map_data": enhanced_map_data,
                    "overlay_analysis": {
                        "regions_in_area": len(all_regions),
                        "paths_in_area": len(all_paths), 
                        "coordinates_with_overlays": affected_coordinates,
                        "overlay_coverage_percent": round((affected_coordinates / len(enhanced_map_data)) * 100, 1) if enhanced_map_data else 0
                    },
                    "regions_affecting_area": [
                        {"vnum": vnum, "name": name, "type_name": type_name} 
                        for vnum, name, type_name in all_regions
                    ],
                    "paths_affecting_area": [
                        {"vnum": vnum, "name": name, "type_name": type_name}
                        for vnum, name, type_name in all_paths
                    ],
                    "source": "complete_terrain_analysis"
                }
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to analyze complete terrain: {str(e)}"}

    async def _apply_terrain_overlays(self, base_terrain: Dict[str, Any]) -> Dict[str, Any]:
        """Apply region and path overlays to base terrain point using spatial queries"""
        result = base_terrain.copy()
        result['overlays'] = {
            'has_overlays': False,
            'regions': [],
            'paths': [],
            'modifications': []
        }
        
        x, y = result.get('x'), result.get('y')
        if x is None or y is None:
            return result
        
        # Use the spatial points endpoint to find affecting regions and paths
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                spatial_response = await client.get(
                    f"{settings.backend_base_url}/points",
                    params={"x": x, "y": y, "radius": 0.1},  # Small radius for exact point
                    headers=headers,
                    timeout=30.0
                )
                spatial_response.raise_for_status()
                spatial_data = spatial_response.json()
                
                affecting_regions = spatial_data.get('regions', [])
                affecting_paths = spatial_data.get('paths', [])
                
                if affecting_regions or affecting_paths:
                    result['overlays']['has_overlays'] = True
                
                # Apply regions in priority order (1-4)
                affecting_regions.sort(key=lambda r: r.get('region_type', 1))
                
                for region in affecting_regions:
                    result['overlays']['regions'].append({
                        'name': region['name'],
                        'type': region.get('region_type'),
                        'type_name': region.get('region_type_name'),
                        'vnum': region['vnum']
                    })
                    
                    region_type = region.get('region_type')
                    
                    if region_type == 1:  # Geographic naming
                        result['geographic_name'] = region['name']
                        result['overlays']['modifications'].append(f"Named '{region['name']}'")
                        
                    elif region_type == 2:  # Encounter zone
                        result['encounter_zone'] = region['name']
                        if region.get('region_reset_data'):
                            result['overlays']['modifications'].append(f"Encounter zone: {region['name']} (spawns: {region['region_reset_data']})")
                        else:
                            result['overlays']['modifications'].append(f"Encounter zone: {region['name']}")
                        
                    elif region_type == 3:  # Transform elevation
                        result['overlays']['modifications'].append(f"Elevation affected by {region['name']}")
                        
                    elif region_type == 4:  # Sector override
                        if region.get('sector_type_name'):
                            result['sector_type'] = region.get('region_props')
                            result['sector_name'] = region['sector_type_name']
                            result['overlays']['modifications'].append(f"Sector overridden to {region['sector_type_name']} by {region['name']}")
                        else:
                            result['overlays']['modifications'].append(f"Sector overridden by {region['name']}")
                
                # Apply paths (processed after regions, highest priority)
                for path in affecting_paths:
                    result['overlays']['paths'].append({
                        'name': path['name'],
                        'type': path.get('path_type'),
                        'type_name': path.get('path_type_name'),
                        'vnum': path['vnum']
                    })
                    
                    path_type = path.get('path_type')
                    
                    # Path sector mappings from documentation
                    path_sector_map = {
                        1: {"sector_type": 17, "sector_name": "Road"},
                        2: {"sector_type": 18, "sector_name": "Dirt Road"},
                        3: {"sector_type": 7, "sector_name": "Water"},     # River
                        4: {"sector_type": 34, "sector_name": "Stream"},   # Stream  
                        5: {"sector_type": 2, "sector_name": "Field"}     # Trail
                    }
                    
                    if path_type in path_sector_map:
                        sector_info = path_sector_map[path_type]
                        result['sector_type'] = sector_info['sector_type']
                        result['sector_name'] = sector_info['sector_name']
                        result['overlays']['modifications'].append(
                            f"Sector changed to {sector_info['sector_name']} by {path['name']}"
                        )
                    else:
                        result['overlays']['modifications'].append(f"Affected by {path.get('path_type_name', 'path')}: {path['name']}")
                        
                    # Environmental effects for rivers/streams
                    if path_type in [3, 4]:  # Rivers/streams add moisture
                        original_moisture = result.get('moisture', 127)
                        result['moisture'] = min(255, original_moisture + 20)
                        result['overlays']['modifications'].append(f"Moisture increased by {path['name']}")
                    
                    # Movement bonuses for roads
                    if path_type in [1, 2]:  # Roads provide movement bonus
                        result['movement_bonus'] = 1.5 if path_type == 1 else 1.2
                        result['overlays']['modifications'].append(f"Movement bonus from {path['name']}")
                        
            except httpx.HTTPError as e:
                # Continue without overlays if spatial query fails
                result['overlays']['error'] = f"Spatial query failed: {str(e)}"
        
        return result
