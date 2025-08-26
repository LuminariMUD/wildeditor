"""
MCP Tools for Wildeditor Wilderness Management

This module contains tools that AI agents can use to interact with
the wilderness system through the backend API.
"""

from typing import Dict, Any, List, Optional
import httpx
import logging

logger = logging.getLogger(__name__)

try:
    # Try relative import (when run as module)
    from ..config import settings
except ImportError:
    # Fall back to absolute import (when run directly)
    from config import settings


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
        
        # Path finding tool - REMOVED: Use spatial search instead
        # Spatial search with search_by_coordinates provides better path discovery
        
        # Region search tool (enhanced with spatial and description support)
        self.register_tool(
            "search_regions",
            self._search_regions,
            "Search for regions by coordinates/radius, type, zone, or descriptions",
            {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "number",
                        "description": "X coordinate for spatial search"
                    },
                    "y": {
                        "type": "number",
                        "description": "Y coordinate for spatial search"
                    },
                    "radius": {
                        "type": "number",
                        "description": "Search radius for spatial search (default 10)"
                    },
                    "region_type": {
                        "type": "integer",
                        "description": "Filter by region type: 1=Geographic, 2=Encounter, 3=Sector Transform, 4=Sector Override"
                    },
                    "zone_vnum": {
                        "type": "integer",
                        "description": "Filter by zone VNUM"
                    },
                    "include_descriptions": {
                        "type": "string",
                        "enum": ["false", "true", "summary"],
                        "description": "Include descriptions: false (default), true (full), summary (first 200 chars)",
                        "default": "false"
                    },
                    "has_description": {
                        "type": "boolean",
                        "description": "Filter to only regions that have descriptions"
                    },
                    "is_approved": {
                        "type": "boolean",
                        "description": "Filter by approval status"
                    },
                    "requires_review": {
                        "type": "boolean",
                        "description": "Filter to regions requiring review"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return"
                    }
                },
                "required": []
            }
        )
        
        # Create region tool (updated with description fields)
        self.register_tool(
            "create_region",
            self._create_region,
            "Create a new wilderness region with comprehensive description and metadata",
            {
                "type": "object",
                "properties": {
                    "vnum": {
                        "type": "integer",
                        "description": "Unique region VNUM identifier (1-99999999)"
                    },
                    "zone_vnum": {
                        "type": "integer",
                        "description": "Zone VNUM this region belongs to",
                        "default": 1
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the region (max 50 chars)"
                    },
                    "region_type": {
                        "type": "integer",
                        "description": "Region type: 1=Geographic, 2=Encounter, 3=Sector Transform, 4=Sector Override"
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
                        "description": "Array of x,y coordinates defining the region boundary (min 3 points for polygon)"
                    },
                    "region_props": {
                        "type": "integer",
                        "description": "Properties value: sector type (0-36) for type 4, elevation adjustment for type 3",
                        "default": 0
                    },
                    "region_description": {
                        "type": "string",
                        "description": "Comprehensive description of the region (can be very detailed)"
                    },
                    "description_style": {
                        "type": "string",
                        "enum": ["poetic", "practical", "mysterious", "dramatic", "pastoral"],
                        "description": "Writing style for the description",
                        "default": "poetic"
                    },
                    "description_length": {
                        "type": "string",
                        "enum": ["brief", "moderate", "detailed", "extensive"],
                        "description": "Target length for the description",
                        "default": "moderate"
                    },
                    "has_historical_context": {
                        "type": "boolean",
                        "description": "Whether description includes historical information",
                        "default": False
                    },
                    "has_resource_info": {
                        "type": "boolean",
                        "description": "Whether description mentions available resources",
                        "default": False
                    },
                    "has_wildlife_info": {
                        "type": "boolean",
                        "description": "Whether description includes wildlife details",
                        "default": False
                    },
                    "has_geological_info": {
                        "type": "boolean",
                        "description": "Whether description contains geological information",
                        "default": False
                    },
                    "has_cultural_info": {
                        "type": "boolean",
                        "description": "Whether description includes cultural elements",
                        "default": False
                    },
                    "ai_agent_source": {
                        "type": "string",
                        "description": "Identifier of the AI agent that generated the description"
                    },
                    "description_quality_score": {
                        "type": "number",
                        "description": "Quality score for the description (0.00-9.99)",
                        "minimum": 0,
                        "maximum": 9.99
                    },
                    "requires_review": {
                        "type": "boolean",
                        "description": "Whether the description needs human review",
                        "default": False
                    },
                    "is_approved": {
                        "type": "boolean",
                        "description": "Whether the description has been approved",
                        "default": False
                    }
                },
                "required": ["vnum", "zone_vnum", "name", "region_type", "coordinates"]
            }
        )
        
        # Create path tool
        self.register_tool(
            "create_path",
            self._create_path,
            "Create a new wilderness path with specified route and properties",
            {
                "type": "object",
                "properties": {
                    "vnum": {
                        "type": "integer",
                        "description": "Unique path VNUM identifier"
                    },
                    "zone_vnum": {
                        "type": "integer",
                        "description": "Zone VNUM this path belongs to"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the path (max 50 characters)"
                    },
                    "path_type": {
                        "type": "integer",
                        "description": "Path type: 1=Paved Road, 2=Dirt Road, 3=Geographic, 5=River, 6=Stream"
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
                        "description": "Array of x,y coordinates defining the path route"
                    },
                    "path_props": {
                        "type": "integer",
                        "description": "Sector type to apply along path (0-36), optional",
                        "default": 0
                    }
                },
                "required": ["vnum", "zone_vnum", "name", "path_type", "coordinates"]
            }
        )
        
        # Validate region connections tool - DISABLED: Backend endpoint not implemented
        # self.register_tool(
        #     "validate_connections",
        #     self._validate_connections,
        #     "Validate that region connections are logical and consistent",
        #     {
        #         "type": "object",
        #         "properties": {
        #             "region_id": {
        #                 "type": "integer",
        #                 "description": "Region ID to validate connections for"
        #             },
        #             "check_bidirectional": {
        #                 "type": "boolean",
        #                 "description": "Check if connections are bidirectional",
        #                 "default": True
        #             }
        #         },
        #         "required": ["region_id"]
        #     }
        # )
        
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
                "properties": {
                    "zone_vnum": {
                        "type": "integer",
                        "description": "Optional zone VNUM to filter entrances for specific zone"
                    }
                },
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
                    },
                    "width": {
                        "type": "integer",
                        "description": "Map width (alternative to radius)",
                        "minimum": 2,
                        "maximum": 62
                    },
                    "height": {
                        "type": "integer",
                        "description": "Map height (alternative to radius)",
                        "minimum": 2,
                        "maximum": 62
                    },
                    "show_regions": {
                        "type": "boolean",
                        "description": "Whether to show region overlays on map",
                        "default": True
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
        
        # Generate region description tool
        self.register_tool(
            "generate_region_description",
            self._generate_region_description,
            "Generate a comprehensive description for a region based on its properties",
            {
                "type": "object",
                "properties": {
                    "region_vnum": {
                        "type": "integer",
                        "description": "VNUM of existing region to generate description for"
                    },
                    "region_name": {
                        "type": "string",
                        "description": "Name of the region (used if vnum not provided)"
                    },
                    "region_type": {
                        "type": "integer",
                        "description": "Region type (1-4) to inform description generation"
                    },
                    "terrain_theme": {
                        "type": "string",
                        "description": "Primary terrain theme (forest, mountain, desert, etc.)"
                    },
                    "description_style": {
                        "type": "string",
                        "enum": ["poetic", "practical", "mysterious", "dramatic", "pastoral"],
                        "description": "Writing style for the description",
                        "default": "poetic"
                    },
                    "description_length": {
                        "type": "string",
                        "enum": ["brief", "moderate", "detailed", "extensive"],
                        "description": "Target length for the description",
                        "default": "moderate"
                    },
                    "include_sections": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["overview", "geography", "vegetation", "wildlife", "atmosphere", "seasons", "resources", "history", "culture"]
                        },
                        "description": "Specific sections to include in the description"
                    },
                    "user_prompt": {
                        "type": "string",
                        "description": "Optional user guidance or specific requirements for the description"
                    }
                },
                "required": []
            }
        )
        
        # Update region description tool
        self.register_tool(
            "update_region_description",
            self._update_region_description,
            "Update the description and metadata for an existing region",
            {
                "type": "object",
                "properties": {
                    "vnum": {
                        "type": "integer",
                        "description": "VNUM of the region to update"
                    },
                    "region_description": {
                        "type": "string",
                        "description": "New or updated description text"
                    },
                    "description_style": {
                        "type": "string",
                        "enum": ["poetic", "practical", "mysterious", "dramatic", "pastoral"],
                        "description": "Writing style"
                    },
                    "description_length": {
                        "type": "string",
                        "enum": ["brief", "moderate", "detailed", "extensive"],
                        "description": "Length category"
                    },
                    "has_historical_context": {"type": "boolean"},
                    "has_resource_info": {"type": "boolean"},
                    "has_wildlife_info": {"type": "boolean"},
                    "has_geological_info": {"type": "boolean"},
                    "has_cultural_info": {"type": "boolean"},
                    "description_quality_score": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 9.99
                    },
                    "requires_review": {"type": "boolean"},
                    "is_approved": {"type": "boolean"}
                },
                "required": ["vnum"]
            }
        )
        
        # Analyze description quality tool
        self.register_tool(
            "analyze_description_quality",
            self._analyze_description_quality,
            "Analyze the quality and completeness of a region's description",
            {
                "type": "object",
                "properties": {
                    "vnum": {
                        "type": "integer",
                        "description": "VNUM of the region to analyze"
                    },
                    "suggest_improvements": {
                        "type": "boolean",
                        "description": "Whether to generate improvement suggestions",
                        "default": True
                    }
                },
                "required": ["vnum"]
            }
        )
        
        # Generate hints from description tool
        self.register_tool(
            "generate_hints_from_description",
            self._generate_hints_from_description,
            "Analyze a region description and generate categorized hints for the dynamic description engine",
            {
                "type": "object",
                "properties": {
                    "region_vnum": {
                        "type": "integer",
                        "description": "VNUM of the region (for fetching existing description)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Region description to analyze (if not using vnum)"
                    },
                    "region_name": {
                        "type": "string",
                        "description": "Name of the region"
                    },
                    "target_hint_count": {
                        "type": "integer",
                        "description": "Target number of hints to generate (5-30)",
                        "default": 15
                    },
                    "include_profile": {
                        "type": "boolean",
                        "description": "Also generate a region personality profile",
                        "default": True
                    }
                },
                "required": []
            }
        )
        
        # Store generated hints tool
        self.register_tool(
            "store_region_hints",
            self._store_region_hints,
            "Store generated hints in the database for a region",
            {
                "type": "object",
                "properties": {
                    "region_vnum": {
                        "type": "integer",
                        "description": "VNUM of the region"
                    },
                    "hints": {
                        "type": "array",
                        "description": "Array of hint objects to store",
                        "items": {
                            "type": "object",
                            "properties": {
                                "category": {"type": "string"},
                                "text": {"type": "string"},
                                "priority": {"type": "integer"},
                                "seasonal_weight": {"type": "object"},
                                "weather_conditions": {"type": "array"},
                                "time_of_day_weight": {"type": "object"}
                            },
                            "required": ["category", "text"]
                        }
                    },
                    "profile": {
                        "type": "object",
                        "description": "Optional region profile to store",
                        "properties": {
                            "overall_theme": {"type": "string"},
                            "dominant_mood": {"type": "string"},
                            "key_characteristics": {"type": "array"},
                            "description_style": {"type": "string"},
                            "complexity_level": {"type": "integer"}
                        }
                    }
                },
                "required": ["region_vnum", "hints"]
            }
        )
        
        # Get existing hints tool
        self.register_tool(
            "get_region_hints",
            self._get_region_hints,
            "Retrieve existing hints for a region from the database",
            {
                "type": "object",
                "properties": {
                    "region_vnum": {
                        "type": "integer",
                        "description": "VNUM of the region"
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter",
                        "enum": ["atmosphere", "fauna", "flora", "geography", "weather_influence", 
                                "resources", "landmarks", "sounds", "scents", "seasonal_changes", 
                                "time_of_day", "mystical"]
                    },
                    "active_only": {
                        "type": "boolean",
                        "description": "Only return active hints",
                        "default": True
                    }
                },
                "required": ["region_vnum"]
            }
        )
        
        # Spatial search tool - searches for regions and paths by coordinates
        self.register_tool(
            "search_by_coordinates",
            self._search_by_coordinates,
            "Search for regions and paths at or near specific coordinates",
            {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "number",
                        "description": "X coordinate to search from"
                    },
                    "y": {
                        "type": "number",
                        "description": "Y coordinate to search from"
                    },
                    "radius": {
                        "type": "number",
                        "description": "Search radius (default 10)",
                        "default": 10
                    }
                },
                "required": ["x", "y"]
            }
        )
    
    async def _search_by_coordinates(self, x: float, y: float, radius: float = 10) -> Dict[str, Any]:
        """Search for regions and paths at or near specific coordinates"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                
                # Use the /points endpoint which does spatial queries
                response = await client.get(
                    f"{settings.backend_base_url}/points",
                    params={"x": x, "y": y, "radius": radius},
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Enhance the response with additional analysis
                result = {
                    "coordinate": data["coordinate"],
                    "radius": data["radius"],
                    "regions": data["regions"],
                    "paths": data["paths"],
                    "summary": {
                        "region_count": data["summary"]["region_count"],
                        "path_count": data["summary"]["path_count"],
                        "total_features": data["summary"]["region_count"] + data["summary"]["path_count"]
                    }
                }
                
                # Add analysis of what was found
                if data["regions"]:
                    result["analysis"] = {
                        "regions_at_point": [r for r in data["regions"] if self._contains_point(r, x, y)],
                        "regions_nearby": [r for r in data["regions"] if not self._contains_point(r, x, y)],
                        "region_types": list(set(r["region_type_name"] for r in data["regions"]))
                    }
                
                if data["paths"]:
                    result["analysis"]["path_types"] = list(set(p["path_type_name"] for p in data["paths"]))
                
                return result
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to search by coordinates: {str(e)}"}
    
    def _contains_point(self, region: Dict[str, Any], x: float, y: float) -> bool:
        """Check if a region contains a point (simplified check)"""
        # This is a simplified check - the actual containment is done by the database
        # We're just categorizing the results here
        return True  # For now, assume regions returned are at the point
    
    async def _analyze_region(self, region_id: int, include_paths: bool = True) -> Dict[str, Any]:
        """Analyze a wilderness region including its description"""
        async with httpx.AsyncClient() as client:
            try:
                # Get region data with full description
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
                
                # Analyze description if present
                description_analysis = self._analyze_region_description(region_data)
                
                result = {
                    "region": region_data,
                    "analysis": {
                        "terrain_features": self._extract_terrain_features(region_data),
                        "environmental_conditions": self._extract_environmental_data(region_data),
                        "accessibility": self._analyze_accessibility(region_data),
                        "description_analysis": description_analysis
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
    
    # _find_path function removed - use spatial search instead
    
    async def _search_regions(self, **kwargs) -> Dict[str, Any]:
        """Search for regions with optional filters including spatial search"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                
                # Check if this is a spatial search
                if "x" in kwargs and "y" in kwargs:
                    # Use the spatial search endpoint
                    params = {
                        "x": kwargs["x"],
                        "y": kwargs["y"],
                        "radius": kwargs.get("radius", 10)
                    }
                    
                    response = await client.get(
                        f"{settings.backend_base_url}/points",
                        params=params,
                        headers=headers,
                        timeout=30.0
                    )
                    
                    response.raise_for_status()
                    spatial_data = response.json()
                    
                    # Return regions from spatial search
                    regions = spatial_data["regions"]
                    
                    # Apply additional filters if provided
                    if "region_type" in kwargs:
                        regions = [r for r in regions if r.get("region_type") == kwargs["region_type"]]
                    
                else:
                    # Traditional search by filters
                    params: Dict[str, Any] = {}
                    
                    # Add filters if provided
                    if "region_type" in kwargs:
                        params["region_type"] = kwargs["region_type"]
                    if "zone_vnum" in kwargs:
                        params["zone_vnum"] = kwargs["zone_vnum"]
                    if "include_descriptions" in kwargs:
                        params["include_descriptions"] = kwargs["include_descriptions"]
                    else:
                        params["include_descriptions"] = "false"  # Default to no descriptions for performance
                    
                    # Get all regions with specified filters
                    response = await client.get(
                        f"{settings.backend_base_url}/regions",
                        params=params,
                        headers=headers,
                        timeout=30.0
                    )
                    
                    response.raise_for_status()
                    regions = response.json()
                
                # Client-side filtering for description-based filters
                if kwargs.get("has_description"):
                    regions = [r for r in regions if r.get("region_description") or r.get("has_description")]
                if kwargs.get("is_approved") is not None:
                    regions = [r for r in regions if r.get("is_approved") == kwargs["is_approved"]]
                if kwargs.get("requires_review") is not None:
                    regions = [r for r in regions if r.get("requires_review") == kwargs["requires_review"]]
                
                # Analyze results
                result = {
                    "total_found": len(regions),
                    "regions": regions,
                    "summary": {
                        "by_type": {},
                        "with_descriptions": 0,
                        "approved": 0,
                        "requiring_review": 0
                    }
                }
                
                # Generate summary statistics
                for region in regions:
                    region_type = region.get("region_type_name", "Unknown")
                    result["summary"]["by_type"][region_type] = result["summary"]["by_type"].get(region_type, 0) + 1
                    
                    if region.get("region_description") or region.get("has_description"):
                        result["summary"]["with_descriptions"] += 1
                    if region.get("is_approved"):
                        result["summary"]["approved"] += 1
                    if region.get("requires_review"):
                        result["summary"]["requiring_review"] += 1
                
                return result
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to search regions: {str(e)}"}
    
    async def _create_region(self, vnum: int, zone_vnum: int, name: str, region_type: int,
                           coordinates: List[Dict[str, float]], **kwargs) -> Dict[str, Any]:
        """Create a new region with comprehensive description"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                
                # Build the region data with all fields
                data: Dict[str, Any] = {
                    "vnum": vnum,
                    "zone_vnum": zone_vnum,
                    "name": name,
                    "region_type": region_type,
                    "coordinates": coordinates
                }
                
                # Add optional fields from kwargs
                optional_fields = [
                    "region_props", "region_reset_data", "region_reset_time",
                    "region_description", "description_style", "description_length",
                    "has_historical_context", "has_resource_info", "has_wildlife_info",
                    "has_geological_info", "has_cultural_info",
                    "ai_agent_source", "description_quality_score", 
                    "requires_review", "is_approved"
                ]
                
                for field in optional_fields:
                    if field in kwargs and kwargs[field] is not None:
                        data[field] = kwargs[field]
                
                # Set AI agent source if not provided
                if "ai_agent_source" not in data and "region_description" in data:
                    data["ai_agent_source"] = "mcp_server"
                
                response = await client.post(
                    f"{settings.backend_base_url}/regions/",
                    json=data,
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                error_detail = str(e)
                try:
                    # Try to extract more detailed error information
                    if hasattr(e, 'response') and e.response:
                        if hasattr(e.response, 'text'):
                            error_detail = f"{str(e)} - Response: {e.response.text()}"
                        elif hasattr(e.response, 'json'):
                            error_detail = f"{str(e)} - Detail: {e.response.json().get('detail', 'No details')}"
                except:
                    pass  # Use original error if parsing fails
                return {"error": f"Failed to create region: {error_detail}"}
    
    async def _create_path(self, vnum: int, zone_vnum: int, name: str, 
                          path_type: int, coordinates: List[Dict[str, float]],
                          path_props: int = 0) -> Dict[str, Any]:
        """Create a new path"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                data: Dict[str, Any] = {
                    "vnum": vnum,
                    "zone_vnum": zone_vnum,
                    "name": name,
                    "path_type": path_type,
                    "coordinates": coordinates,
                    "path_props": path_props
                }
                
                response = await client.post(
                    f"{settings.backend_base_url}/paths/",
                    json=data,
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to create path: {str(e)}"}
    
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
    
    def _analyze_region_description(self, region_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze region description and metadata"""
        description = region_data.get("region_description", "")
        
        analysis = {
            "has_description": bool(description),
            "description_length": len(description) if description else 0,
            "description_style": region_data.get("description_style"),
            "description_length_category": region_data.get("description_length"),
            "quality_score": region_data.get("description_quality_score"),
            "is_approved": region_data.get("is_approved", False),
            "requires_review": region_data.get("requires_review", False),
            "ai_source": region_data.get("ai_agent_source"),
            "content_flags": {
                "historical": region_data.get("has_historical_context", False),
                "resources": region_data.get("has_resource_info", False),
                "wildlife": region_data.get("has_wildlife_info", False),
                "geological": region_data.get("has_geological_info", False),
                "cultural": region_data.get("has_cultural_info", False)
            }
        }
        
        if description:
            # Analyze description content
            analysis["word_count"] = len(description.split())
            analysis["paragraph_count"] = len([p for p in description.split('\n\n') if p.strip()])
            
            # Check for key sections
            description_lower = description.lower()
            analysis["has_sections"] = {
                "overview": "overview" in description_lower,
                "geography": any(word in description_lower for word in ["geography", "terrain", "landscape"]),
                "vegetation": any(word in description_lower for word in ["vegetation", "flora", "trees", "plants"]),
                "wildlife": any(word in description_lower for word in ["wildlife", "fauna", "animals", "creatures"]),
                "atmosphere": any(word in description_lower for word in ["atmosphere", "mood", "feeling"]),
                "resources": any(word in description_lower for word in ["resources", "materials", "minerals"]),
                "seasonal": any(word in description_lower for word in ["season", "spring", "summer", "autumn", "winter"])
            }
            
            # Calculate completeness score
            content_count = sum(analysis["content_flags"].values())
            section_count = sum(analysis["has_sections"].values())
            analysis["completeness_score"] = (content_count + section_count) / 12.0 * 10  # Scale to 0-10
            
        return analysis
    
    def _extract_terrain_features(self, region_data: Dict[str, Any]) -> List[str]:
        """Extract terrain features from region data"""
        features = []
        
        # Basic terrain analysis from region type
        region_type_name = region_data.get("region_type_name", "")
        if region_type_name:
            features.append(f"Type: {region_type_name}")
        
        # Look for terrain keywords in description
        description = region_data.get("region_description", "").lower()
        terrain_keywords = ["forest", "mountain", "river", "lake", "desert", "swamp", "cave", "hill"]
        
        for keyword in terrain_keywords:
            if keyword in description:
                features.append(f"Contains {keyword}")
        
        return features
    
    def _extract_environmental_data(self, region_data: Dict[str, Any]) -> List[str]:
        """Extract environmental conditions"""
        conditions = []
        
        # Check description metadata
        if region_data.get("has_geological_info"):
            conditions.append("Contains geological information")
        if region_data.get("has_wildlife_info"):
            conditions.append("Contains wildlife information")
        
        # Environmental keywords in description
        description = region_data.get("region_description", "").lower()
        env_keywords = ["cold", "hot", "humid", "dry", "windy", "calm", "dark", "bright", "mist", "fog"]
        
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
    
    async def _find_zone_entrances(self, zone_vnum: Optional[int] = None) -> Dict[str, Any]:
        """Find all zone entrances in the wilderness, optionally filtered by zone"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                params = {}
                if zone_vnum is not None:
                    params["zone_vnum"] = zone_vnum
                
                response = await client.get(
                    f"{settings.backend_base_url}/wilderness/navigation/entrances",
                    params=params,
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                # If zone filtering was requested but backend doesn't support it, filter client-side
                if zone_vnum is not None and "entrances" in data:
                    filtered_entrances = [e for e in data["entrances"] if e.get("zone_vnum") == zone_vnum]
                    data["entrances"] = filtered_entrances
                    data["total_found"] = len(filtered_entrances)
                    data["note"] = f"Filtered for zone {zone_vnum}"
                
                return data
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to find zone entrances: {str(e)}"}
    
    async def _generate_wilderness_map(self, center_x: int, center_y: int, radius: Optional[int] = None, 
                                      width: Optional[int] = None, height: Optional[int] = None,
                                      show_regions: bool = True) -> Dict[str, Any]:
        """Generate wilderness map for an area"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                
                # Convert width/height to radius if provided
                if width is not None and height is not None:
                    # Use the larger dimension and convert to radius
                    actual_radius = max(width, height) // 2
                elif width is not None:
                    actual_radius = width // 2
                elif height is not None:
                    actual_radius = height // 2
                else:
                    actual_radius = radius or 10
                
                params = {
                    "center_x": center_x, 
                    "center_y": center_y, 
                    "radius": actual_radius
                }
                
                # Add show_regions if supported by backend
                if show_regions:
                    params["include_regions"] = True
                
                response = await client.get(
                    f"{settings.backend_base_url}/terrain/map-data",
                    params=params,
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
    
    async def _generate_region_description(self, **kwargs) -> Dict[str, Any]:
        """Generate a comprehensive description for a region"""
        try:
            # Import AI service dynamically to avoid circular imports
            try:
                from ..services.ai_service import get_ai_service
            except ImportError:
                # Fallback for different import contexts
                import sys
                import os
                sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
                from services.ai_service import get_ai_service
            
            # If vnum provided, fetch existing region data
            region_data = None
            if "region_vnum" in kwargs:
                async with httpx.AsyncClient() as client:
                    headers = {"Authorization": f"Bearer {settings.api_key}"}
                    response = await client.get(
                        f"{settings.backend_base_url}/regions/{kwargs['region_vnum']}",
                        headers=headers,
                        timeout=30.0
                    )
                    if response.status_code == 200:
                        region_data = response.json()
            
            # Build description generation parameters
            region_name = kwargs.get("region_name") or (region_data["name"] if region_data else "Unnamed Region")
            region_type = kwargs.get("region_type") or (region_data["region_type"] if region_data else 1)
            terrain_theme = kwargs.get("terrain_theme", "wilderness")
            style = kwargs.get("description_style", "poetic")
            length = kwargs.get("description_length", "moderate")
            sections = kwargs.get("include_sections", ["overview", "geography", "vegetation", "atmosphere"])
            user_prompt = kwargs.get("user_prompt", "")
            
            # Try AI generation first
            ai_service = get_ai_service()
            ai_result = None
            
            if ai_service.is_available():
                ai_result = await ai_service.generate_description(
                    region_name=region_name,
                    terrain_theme=terrain_theme,
                    style=style,
                    length=length,
                    sections=sections,
                    user_prompt=user_prompt
                )
            
            # If AI generation succeeded, use that result
            if ai_result:
                return ai_result
            
            # Fall back to template-based generation
            description = self._compose_region_description(
                name=region_name,
                region_type=region_type,
                terrain_theme=terrain_theme,
                style=style,
                length=length,
                sections=sections,
                user_prompt=user_prompt
            )
            
            # Analyze generated description for metadata
            metadata = self._analyze_description_content(description)
            
            return {
                "generated_description": description,
                "metadata": metadata,
                "word_count": len(description.split()),
                "character_count": len(description),
                "suggested_quality_score": metadata.get("quality_score", 7.0),
                "region_vnum": kwargs.get("region_vnum"),
                "region_name": region_name,
                "ai_provider": "template"  # Mark as template-generated
            }
            
        except Exception as e:
            return {"error": f"Failed to generate description: {str(e)}"}
    
    async def _update_region_description(self, vnum: int, **kwargs) -> Dict[str, Any]:
        """Update region description and metadata"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                
                # Build update data
                update_data = {}
                for field in ["region_description", "description_style", "description_length",
                             "has_historical_context", "has_resource_info", "has_wildlife_info",
                             "has_geological_info", "has_cultural_info", "description_quality_score",
                             "requires_review", "is_approved"]:
                    if field in kwargs:
                        update_data[field] = kwargs[field]
                
                # Set AI agent source
                if "region_description" in update_data:
                    update_data["ai_agent_source"] = "mcp_server_update"
                
                response = await client.put(
                    f"{settings.backend_base_url}/regions/{vnum}",
                    json=update_data,
                    headers=headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                error_detail = str(e)
                try:
                    # Try to extract more detailed error information
                    if hasattr(e, 'response') and e.response:
                        if hasattr(e.response, 'text'):
                            error_detail = f"{str(e)} - Response: {e.response.text()}"
                        elif hasattr(e.response, 'json'):
                            error_detail = f"{str(e)} - Detail: {e.response.json().get('detail', 'No details')}"
                except:
                    pass  # Use original error if parsing fails
                return {"error": f"Failed to update region description: {error_detail}"}
    
    async def _analyze_description_quality(self, vnum: int, suggest_improvements: bool = True) -> Dict[str, Any]:
        """Analyze description quality and suggest improvements"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                response = await client.get(
                    f"{settings.backend_base_url}/regions/{vnum}",
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 404:
                    return {"error": f"Region {vnum} not found"}
                
                response.raise_for_status()
                region_data = response.json()
                
                # Perform quality analysis
                analysis = self._analyze_region_description(region_data)
                
                result = {
                    "vnum": vnum,
                    "name": region_data.get("name"),
                    "current_quality_score": region_data.get("description_quality_score"),
                    "analysis": analysis
                }
                
                if suggest_improvements and region_data.get("region_description"):
                    result["improvements"] = self._suggest_description_improvements(
                        region_data.get("region_description", ""),
                        analysis
                    )
                
                return result
                
            except httpx.HTTPError as e:
                return {"error": f"Failed to analyze description quality: {str(e)}"}
    
    def _compose_region_description(self, name: str, region_type: int, terrain_theme: str,
                                   style: str, length: str, sections: List[str], user_prompt: str = "") -> str:
        """Compose a region description based on parameters"""
        # Length guidelines
        length_targets = {
            "brief": 100,
            "moderate": 300,
            "detailed": 600,
            "extensive": 1000
        }
        target_words = length_targets.get(length, 300)
        
        # Style templates
        style_intros = {
            "poetic": f"The {name} unfolds before you like a living canvas of {terrain_theme} beauty.",
            "practical": f"{name} is a {terrain_theme} region with distinct geographical features.",
            "mysterious": f"An air of ancient mystery permeates {name}, where the {terrain_theme} holds secrets untold.",
            "dramatic": f"The {name} rises dramatically from the surrounding lands, a testament to nature's raw power.",
            "pastoral": f"The gentle contours of {name} create a peaceful {terrain_theme} sanctuary."
        }
        
        description_parts = []
        description_parts.append(f"{name.upper()} COMPREHENSIVE DESCRIPTION\n")
        
        # Add sections based on request
        if "overview" in sections:
            description_parts.append(f"\nOVERVIEW:\n{style_intros.get(style, style_intros['poetic'])}")
            
        if "geography" in sections:
            description_parts.append(f"\nGEOGRAPHY:\nThe terrain here is characterized by {terrain_theme} features, "
                                    f"with natural formations that have developed over countless ages.")
            
        if "vegetation" in sections:
            description_parts.append(f"\nVEGETATION:\nThe plant life adapts remarkably to the {terrain_theme} environment, "
                                    f"creating a unique ecosystem of hardy flora.")
            
        if "wildlife" in sections:
            description_parts.append(f"\nWILDLIFE:\nCreatures both common and rare make their home in this {terrain_theme}, "
                                    f"each adapted to the specific challenges of the environment.")
            
        if "atmosphere" in sections:
            description_parts.append(f"\nATMOSPHERE:\nThe ambiance of {name} shifts with the time of day, "
                                    f"from misty mornings to sun-drenched afternoons.")
            
        if "seasons" in sections:
            description_parts.append(f"\nSEASONAL CHANGES:\nEach season transforms {name} in unique ways, "
                                    f"bringing different colors, sounds, and experiences.")
            
        if "resources" in sections:
            description_parts.append(f"\nRESOURCES:\nThe {terrain_theme} provides various natural resources, "
                                    f"from minerals to medicinal plants.")
            
        if "history" in sections:
            description_parts.append(f"\nHISTORICAL CONTEXT:\nLegends speak of ancient times when {name} "
                                    f"played a crucial role in the region's history.")
            
        if "culture" in sections:
            description_parts.append(f"\nCULTURAL SIGNIFICANCE:\nLocal traditions and folklore are deeply connected "
                                    f"to the {terrain_theme} landscape of {name}.")
        
        return "\n".join(description_parts)
    
    def _analyze_description_content(self, description: str) -> Dict[str, Any]:
        """Analyze description content to determine metadata flags"""
        desc_lower = description.lower()
        
        return {
            "has_historical_context": any(word in desc_lower for word in ["history", "ancient", "legend", "past"]),
            "has_resource_info": any(word in desc_lower for word in ["resource", "mineral", "material", "harvest"]),
            "has_wildlife_info": any(word in desc_lower for word in ["wildlife", "animal", "creature", "fauna"]),
            "has_geological_info": any(word in desc_lower for word in ["geological", "rock", "stone", "mineral", "formation"]),
            "has_cultural_info": any(word in desc_lower for word in ["culture", "tradition", "folklore", "people"]),
            "quality_score": min(9.0, 5.0 + len(description) / 500)  # Simple quality estimate
        }
    
    def _suggest_description_improvements(self, description: str, analysis: Dict[str, Any]) -> List[str]:
        """Suggest improvements for a description"""
        suggestions = []
        
        # Check completeness
        if analysis.get("word_count", 0) < 100:
            suggestions.append("Expand the description to provide more detail (currently very brief)")
        
        if not analysis.get("has_sections", {}).get("overview"):
            suggestions.append("Add an overview section to introduce the region")
            
        if not analysis.get("has_sections", {}).get("geography"):
            suggestions.append("Include geographical details about the terrain")
            
        if not analysis.get("content_flags", {}).get("wildlife"):
            suggestions.append("Add information about local wildlife and creatures")
            
        if not analysis.get("content_flags", {}).get("resources"):
            suggestions.append("Mention available resources or materials in the area")
            
        if analysis.get("completeness_score", 0) < 5:
            suggestions.append("Add more comprehensive sections to improve completeness")
            
        if not analysis.get("has_sections", {}).get("atmosphere"):
            suggestions.append("Describe the atmospheric qualities and mood of the region")
        
        return suggestions
    
    async def _generate_hints_from_description(self, **kwargs) -> Dict[str, Any]:
        """Generate categorized hints from a region description"""
        try:
            # Get description either from vnum or directly
            description = kwargs.get("description", "")
            region_vnum = kwargs.get("region_vnum")
            region_name = kwargs.get("region_name", "Unknown Region")
            target_count = kwargs.get("target_hint_count", 15)
            include_profile = kwargs.get("include_profile", True)
            
            logger.info(f"Generating hints - vnum: {region_vnum}, description length: {len(description) if description else 0}")
            
            # If vnum provided but no description, fetch it
            if region_vnum and not description:
                async with httpx.AsyncClient() as client:
                    headers = {"Authorization": f"Bearer {settings.api_key}"}
                    response = await client.get(
                        f"{settings.backend_base_url}/regions/{region_vnum}",
                        headers=headers
                    )
                    if response.status_code == 200:
                        region_data = response.json()
                        description = region_data.get("region_description", "")
                        region_name = region_data.get("name", region_name)
            
            if not description:
                return {"error": "No description provided or found for region"}
            
            # Analyze description and extract hints
            logger.info(f"Calling AI service with description: {description[:100]}...")
            hints = await self._extract_hints_from_description(description, region_name)
            logger.info(f"AI service returned {len(hints)} hints")
            
            # Generate profile if requested
            profile = None
            if include_profile:
                profile = self._generate_profile_from_description(description, region_name)
            
            return {
                "hints": hints[:target_count],  # Limit to target count
                "profile": profile,
                "total_hints_found": len(hints),
                "region_name": region_name,
                "description_length": len(description)
            }
            
        except Exception as e:
            return {"error": f"Failed to generate hints: {str(e)}"}
    
    async def _extract_hints_from_description(self, description: str, region_name: str = "") -> List[Dict[str, Any]]:
        """Extract categorized hints from description text using AI"""
        try:
            # Import AI service dynamically to avoid circular imports
            try:
                from ..services.ai_service import get_ai_service
            except ImportError:
                # Fallback for different import contexts
                import sys
                import os
                sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
                from services.ai_service import get_ai_service
            
            # Try AI generation first
            ai_service = get_ai_service()
            ai_result = None
            
            # Check if hint agent specifically is available
            if hasattr(ai_service, 'is_hint_agent_available') and ai_service.is_hint_agent_available():
                logger.info("Hint agent is available, generating hints")
                logger.info(f"Description preview: {description[:200]}...")
                ai_result = await ai_service.generate_hints_from_description(
                    description=description,
                    region_name=region_name
                )
                logger.info(f"AI service returned: {type(ai_result)}, has error: {ai_result.get('error') if ai_result else 'N/A'}")
                if ai_result and 'hints' in ai_result:
                    logger.info(f"Hints in result: {len(ai_result.get('hints', []))}")
            elif ai_service.is_available():
                # Fallback to checking general availability
                logger.warning("Using general AI availability check (hint agent might not be available)")
                logger.info(f"Description preview: {description[:200]}...")
                ai_result = await ai_service.generate_hints_from_description(
                    description=description,
                    region_name=region_name
                )
                logger.info(f"AI service returned: {type(ai_result)}, has error: {ai_result.get('error') if ai_result else 'N/A'}")
                if ai_result and 'hints' in ai_result:
                    logger.info(f"Hints in result: {len(ai_result.get('hints', []))}")
            else:
                logger.error("AI service not available for hint generation")
                ai_result = None
            
            # If AI generation successful, return hints directly
            # The AI agent should already have set appropriate weights
            if ai_result and not ai_result.get("error"):
                hints = ai_result.get("hints", [])
                logger.info(f"AI generation successful: {len(hints)} hints generated")
                return hints
            
            # If we get here, AI failed or wasn't available
            if not ai_result:
                logger.error("No AI result obtained - service unavailable")
            return []
            
        except Exception as e:
            logger.error(f"AI hint extraction failed: {e}")
            # Return error instead of fallback to templates
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return []

    # REMOVED: _extract_hints_fallback - We only use AI agents for hint generation
    
    # REMOVED: _calculate_hint_priority, _determine_weather_conditions - Only used by fallback
    
    def _calculate_seasonal_weight(self, text: str) -> Dict[str, float]:
        """Calculate seasonal weights based on text content - LOGICAL weights"""
        # Default: hint is generally applicable year-round
        weights = {"spring": 1.0, "summer": 1.0, "autumn": 1.0, "winter": 1.0}
        
        # Spring-specific hints
        if "spring" in text or "bloom" in text or "blossom" in text or "flower" in text or "budding" in text:
            weights = {"spring": 2.0, "summer": 0.5, "autumn": 0.2, "winter": 0.0}
        # Summer-specific hints
        elif "summer" in text or "hot" in text or "scorching" in text or "sultry" in text:
            weights = {"spring": 0.5, "summer": 2.0, "autumn": 0.5, "winter": 0.0}
        # Autumn-specific hints
        elif "autumn" in text or "fall" in text or "harvest" in text or "falling leaves" in text:
            weights = {"spring": 0.2, "summer": 0.5, "autumn": 2.0, "winter": 0.5}
        # Winter-specific hints
        elif "winter" in text or "snow" in text or "frost" in text or "frozen" in text or "ice" in text:
            weights = {"spring": 0.0, "summer": 0.0, "autumn": 0.2, "winter": 2.0}
            
        return weights
    
    def _calculate_time_weight(self, text: str) -> Dict[str, float]:
        """Calculate time of day weights based on text content - LOGICAL weights"""
        # Default: hint is applicable throughout the day
        weights = {"dawn": 1.0, "morning": 1.0, "midday": 1.0, "afternoon": 1.0, "evening": 1.0, "night": 1.0}
        
        # Dawn-specific hints
        if "dawn" in text or "sunrise" in text or "first light" in text:
            weights = {"dawn": 2.0, "morning": 1.2, "midday": 0.5, "afternoon": 0.5, "evening": 0.8, "night": 0.6}
        # Morning-specific hints
        elif "morning" in text and not "dawn" in text:
            weights = {"dawn": 1.2, "morning": 2.0, "midday": 1.0, "afternoon": 0.8, "evening": 0.6, "night": 0.5}
        # Midday-specific hints
        elif "noon" in text or "midday" in text or "zenith" in text:
            weights = {"dawn": 0.5, "morning": 0.8, "midday": 2.0, "afternoon": 1.5, "evening": 0.6, "night": 0.3}
        # Afternoon-specific hints
        elif "afternoon" in text:
            weights = {"dawn": 0.5, "morning": 0.8, "midday": 1.5, "afternoon": 2.0, "evening": 1.0, "night": 0.5}
        # Evening-specific hints  
        elif "evening" in text or "dusk" in text or "sunset" in text or "twilight" in text:
            weights = {"dawn": 0.8, "morning": 0.6, "midday": 0.6, "afternoon": 1.0, "evening": 2.0, "night": 1.2}
        # Night-specific hints
        elif "night" in text or "darkness" in text or "moonlight" in text or "nocturnal" in text or "stars" in text:
            weights = {"dawn": 0.6, "morning": 0.3, "midday": 0.0, "afternoon": 0.3, "evening": 1.2, "night": 2.0}
            
        return weights
    
    def _generate_profile_from_description(self, description: str, region_name: str) -> Dict[str, Any]:
        """Generate a region personality profile from description"""
        desc_lower = description.lower()
        
        # Determine overall theme (first 200 chars of description as summary)
        theme = description[:200].strip()
        if not theme.endswith('.'):
            theme = theme.rsplit('.', 1)[0] + '.' if '.' in theme else theme + '...'
        
        # Determine dominant mood
        mood_keywords = {
            "serene": ["peaceful", "calm", "tranquil", "quiet"],
            "mysterious": ["mysterious", "enigmatic", "strange", "unknown"],
            "vibrant": ["vibrant", "lively", "bustling", "active"],
            "ancient": ["ancient", "old", "timeless", "primordial"],
            "magical": ["magical", "enchanted", "mystical", "ethereal"]
        }
        
        dominant_mood = "neutral"
        for mood, keywords in mood_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                dominant_mood = mood
                break
        
        # Extract key characteristics
        characteristics = []
        if "forest" in desc_lower: characteristics.append("forested")
        if "mountain" in desc_lower: characteristics.append("mountainous")
        if "river" in desc_lower or "stream" in desc_lower: characteristics.append("water_features")
        if "ancient" in desc_lower: characteristics.append("ancient_features")
        if "magical" in desc_lower: characteristics.append("magical_elements")
        if "wildlife" in desc_lower: characteristics.append("rich_wildlife")
        if "ruin" in desc_lower: characteristics.append("ruins")
        
        # Determine style
        style = "poetic"  # Default
        if len(description) < 500:
            style = "practical"
        elif any(word in desc_lower for word in ["mysterious", "strange", "unknown"]):
            style = "mysterious"
        elif any(word in desc_lower for word in ["dramatic", "magnificent", "spectacular"]):
            style = "dramatic"
        
        return {
            "overall_theme": theme,
            "dominant_mood": dominant_mood,
            "key_characteristics": characteristics[:10],  # Limit to 10
            "description_style": style,
            "complexity_level": min(5, max(1, len(description) // 200)),  # Based on length
            "ai_agent_id": "mcp_profile_generator"
        }
    
    async def _store_region_hints(self, **kwargs) -> Dict[str, Any]:
        """Store hints and profile in the database"""
        try:
            region_vnum = kwargs.get("region_vnum")
            hints = kwargs.get("hints", [])
            profile = kwargs.get("profile")
            
            if not region_vnum:
                return {"error": "region_vnum is required"}
            
            if not hints:
                return {"error": "No hints provided to store"}
            
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                
                # Store hints
                hints_payload = {
                    "hints": hints
                }
                
                response = await client.post(
                    f"{settings.backend_base_url}/regions/{region_vnum}/hints",
                    headers=headers,
                    json=hints_payload,
                    timeout=30.0
                )
                
                if response.status_code not in [200, 201]:
                    return {"error": f"Failed to store hints: {response.status_code}"}
                
                stored_hints = response.json()
                
                # Store profile if provided
                stored_profile = None
                if profile:
                    profile_response = await client.post(
                        f"{settings.backend_base_url}/regions/{region_vnum}/profile",
                        headers=headers,
                        json=profile,
                        timeout=30.0
                    )
                    
                    if profile_response.status_code in [200, 201]:
                        stored_profile = profile_response.json()
                
                return {
                    "success": True,
                    "hints_stored": len(stored_hints) if isinstance(stored_hints, list) else 1,
                    "profile_stored": stored_profile is not None,
                    "region_vnum": region_vnum
                }
                
        except Exception as e:
            return {"error": f"Failed to store hints: {str(e)}"}
    
    async def _get_region_hints(self, **kwargs) -> Dict[str, Any]:
        """Retrieve existing hints for a region"""
        try:
            region_vnum = kwargs.get("region_vnum")
            category = kwargs.get("category")
            active_only = kwargs.get("active_only", True)
            
            if not region_vnum:
                return {"error": "region_vnum is required"}
            
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {settings.api_key}"}
                
                # Build query parameters
                params = {}
                if category:
                    params["category"] = category
                if active_only:
                    params["is_active"] = "true"
                
                response = await client.get(
                    f"{settings.backend_base_url}/regions/{region_vnum}/hints",
                    headers=headers,
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 404:
                    return {"hints": [], "message": "No hints found for this region"}
                
                if response.status_code != 200:
                    return {"error": f"Failed to retrieve hints: {response.status_code}"}
                
                data = response.json()
                
                return {
                    "hints": data.get("hints", []),
                    "total_count": data.get("total_count", 0),
                    "active_count": data.get("active_count", 0),
                    "categories": data.get("categories", {}),
                    "region_vnum": region_vnum
                }
                
        except Exception as e:
            return {"error": f"Failed to retrieve hints: {str(e)}"}
