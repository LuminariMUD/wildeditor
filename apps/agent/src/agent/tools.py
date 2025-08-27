"""Tool definitions for the Wilderness Assistant Agent - MCP Only Version"""
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class WildernessTools:
    """Collection of tools for wilderness operations using MCP server exclusively"""
    
    def __init__(self, mcp_client):
        """Initialize with only MCP client - single contact surface"""
        self.mcp = mcp_client
        # Track tool calls for frontend action conversion
        self.captured_tool_calls = []
        logger.info("Initialized WildernessTools with MCP-only architecture")
    
    async def create_region(
        self,
        name: str,
        region_type: int,  # MCP uses integers for types
        coordinates: List[Dict[str, float]],
        vnum: Optional[int] = None,
        zone_vnum: int = 10000,  # Default zone
        properties: Optional[Dict[str, Any]] = None,
        auto_generate_description: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new wilderness region via MCP
        
        This tool creates a new region using the MCP server's create_region tool,
        which handles both database operations and optional AI description generation.
        """
        try:
            # Capture this tool call for frontend action conversion
            self.captured_tool_calls.append({
                "tool_name": "create_region",
                "args": {
                    "name": name,
                    "region_type": region_type,
                    "coordinates": coordinates,
                    "zone_vnum": zone_vnum,
                    "auto_generate_description": auto_generate_description
                }
            })
            logger.info(f"Captured create_region call for: {name}")
            
            # Generate a vnum if not provided (simple auto-increment logic)
            if vnum is None:
                import random
                vnum = 1000000 + random.randint(1, 99999)
            
            # Call MCP create_region tool
            result = await self.mcp.call_tool(
                "create_region",
                {
                    "vnum": vnum,
                    "zone_vnum": zone_vnum,
                    "name": name,
                    "region_type": region_type,
                    "coordinates": coordinates,
                    **(properties or {})
                }
            )
            
            # Generate description if requested and creation succeeded
            if auto_generate_description and not result.get("error"):
                try:
                    desc_result = await self.generate_region_description(
                        region_vnum=vnum,
                        region_name=name,
                        region_type=region_type
                    )
                    if desc_result.get("generated_description"):
                        # Update the region with the description
                        await self.mcp.call_tool(
                            "update_region_description",
                            {
                                "vnum": vnum,
                                "region_description": desc_result["generated_description"]
                            }
                        )
                        result["description"] = desc_result["generated_description"]
                except Exception as e:
                    logger.warning(f"Failed to generate description: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create region: {str(e)}")
            return {
                "error": str(e),
                "message": f"Failed to create region: {str(e)}"
            }
    
    async def create_path(
        self,
        name: str,
        path_type: int,  # 1=Paved, 2=Dirt, 3=Geographic, 5=River, 6=Stream
        coordinates: List[Dict[str, float]],
        vnum: Optional[int] = None,
        zone_vnum: int = 10000,
        path_props: int = 0
    ) -> Dict[str, Any]:
        """
        Create a new wilderness path via MCP
        
        Path types: 1=Paved Road, 2=Dirt Road, 3=Geographic, 5=River, 6=Stream
        """
        try:
            # Generate a vnum if not provided
            if vnum is None:
                import random
                vnum = 2000000 + random.randint(1, 99999)
            
            # Call MCP create_path tool
            result = await self.mcp.call_tool(
                "create_path",
                {
                    "vnum": vnum,
                    "zone_vnum": zone_vnum,
                    "name": name,
                    "path_type": path_type,
                    "coordinates": coordinates,
                    "path_props": path_props
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create path: {str(e)}")
            return {
                "error": str(e),
                "message": f"Failed to create path: {str(e)}"
            }
    
    async def generate_region_description(
        self,
        region_vnum: Optional[int] = None,
        region_name: Optional[str] = None,
        region_type: Optional[int] = None,
        terrain_theme: Optional[str] = None,
        description_style: str = "immersive",
        description_length: str = "medium",
        user_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an AI-powered description for a region via MCP
        """
        try:
            result = await self.mcp.call_tool(
                "generate_region_description",
                {
                    "region_vnum": region_vnum,
                    "region_name": region_name,
                    "region_type": region_type,
                    "terrain_theme": terrain_theme,
                    "description_style": description_style,
                    "description_length": description_length,
                    "user_prompt": user_prompt
                }
            )
            
            logger.info(f"Generated description for {region_name or f'region {region_vnum}'}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate description: {str(e)}")
            return {"error": str(e)}
    
    async def generate_region_hints(
        self,
        region_vnum: Optional[int] = None,
        description: Optional[str] = None,
        region_name: Optional[str] = None,
        target_hint_count: int = 15
    ) -> Dict[str, Any]:
        """
        Generate dynamic hints for a region based on its description via MCP
        """
        try:
            result = await self.mcp.call_tool(
                "generate_hints_from_description",
                {
                    "region_vnum": region_vnum,
                    "description": description,
                    "region_name": region_name,
                    "target_hint_count": target_hint_count,
                    "include_profile": True
                }
            )
            
            logger.info(f"Generated {result.get('total_hints_found', 0)} hints")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate hints: {str(e)}")
            return {"error": str(e)}
    
    async def analyze_terrain(
        self,
        x: int,
        y: int
    ) -> Dict[str, Any]:
        """
        Analyze terrain at specific coordinates via MCP
        """
        try:
            result = await self.mcp.call_tool(
                "analyze_terrain_at_coordinates",
                {"x": x, "y": y}
            )
            
            logger.info(f"Analyzed terrain at ({x}, {y})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze terrain: {str(e)}")
            return {"error": str(e)}
    
    async def analyze_complete_terrain(
        self,
        center_x: int,
        center_y: int,
        radius: int = 5,
        include_regions: bool = True,
        include_paths: bool = True
    ) -> Dict[str, Any]:
        """
        Get complete terrain analysis with overlays via MCP
        """
        try:
            result = await self.mcp.call_tool(
                "analyze_complete_terrain_map",
                {
                    "center_x": center_x,
                    "center_y": center_y,
                    "radius": radius,
                    "include_regions": include_regions,
                    "include_paths": include_paths
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze complete terrain: {str(e)}")
            return {"error": str(e)}
    
    async def search_regions(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None,
        radius: Optional[float] = None,
        region_type: Optional[int] = None,
        zone_vnum: Optional[int] = None,
        name_pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for regions with various filters via MCP
        """
        try:
            params = {}
            if x is not None:
                params["x"] = x
            if y is not None:
                params["y"] = y
            if radius is not None:
                params["radius"] = radius
            if region_type is not None:
                params["region_type"] = region_type
            if zone_vnum is not None:
                params["zone_vnum"] = zone_vnum
            if name_pattern is not None:
                params["name_pattern"] = name_pattern
            
            result = await self.mcp.call_tool("search_regions", params)
            return result
            
        except Exception as e:
            logger.error(f"Failed to search regions: {str(e)}")
            return {"error": str(e)}
    
    async def search_by_coordinates(
        self,
        x: float,
        y: float,
        radius: float = 10
    ) -> Dict[str, Any]:
        """
        Search for regions and paths near coordinates via MCP
        """
        try:
            result = await self.mcp.call_tool(
                "search_by_coordinates",
                {
                    "x": x,
                    "y": y,
                    "radius": radius
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to search by coordinates: {str(e)}")
            return {"error": str(e)}
    
    async def find_zone_entrances(
        self,
        zone_vnum: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Find zone entrances in the wilderness via MCP
        """
        try:
            params = {}
            if zone_vnum is not None:
                params["zone_vnum"] = zone_vnum
            
            result = await self.mcp.call_tool("find_zone_entrances", params)
            return result
            
        except Exception as e:
            logger.error(f"Failed to find zone entrances: {str(e)}")
            return {"error": str(e)}
    
    async def find_zone_entrances_near(
        self,
        x: int,
        y: int,
        radius: int = 50
    ) -> Dict[str, Any]:
        """
        Find zone entrances near specific coordinates
        
        This is a convenience method that gets all entrances and filters by distance.
        """
        try:
            # Get all zone entrances
            result = await self.find_zone_entrances()
            
            if "error" in result:
                return result
            
            # Filter by distance
            all_entrances = result.get("entrances", [])
            nearby_entrances = []
            
            for entrance in all_entrances:
                if "coordinates" in entrance:
                    coord = entrance["coordinates"]
                    ex = coord.get("x", 0)
                    ey = coord.get("y", 0)
                    distance = ((ex - x) ** 2 + (ey - y) ** 2) ** 0.5
                    if distance <= radius:
                        entrance["distance"] = round(distance, 2)
                        nearby_entrances.append(entrance)
            
            # Sort by distance
            nearby_entrances.sort(key=lambda e: e.get("distance", float("inf")))
            
            return {
                "center": {"x": x, "y": y},
                "radius": radius,
                "entrances": nearby_entrances,
                "count": len(nearby_entrances),
                "message": f"Found {len(nearby_entrances)} zone entrances within {radius} units"
            }
            
        except Exception as e:
            logger.error(f"Failed to find nearby zone entrances: {str(e)}")
            return {"error": str(e)}
    
    async def generate_wilderness_map(
        self,
        center_x: int,
        center_y: int,
        radius: int = 10
    ) -> Dict[str, Any]:
        """
        Generate a wilderness map via MCP
        """
        try:
            result = await self.mcp.call_tool(
                "generate_wilderness_map",
                {
                    "center_x": center_x,
                    "center_y": center_y,
                    "radius": radius
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate map: {str(e)}")
            return {"error": str(e)}
    
    async def find_static_wilderness_room(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        vnum: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Find static wilderness room at coordinates or by VNUM via MCP
        """
        try:
            params = {}
            if x is not None:
                params["x"] = x
            if y is not None:
                params["y"] = y
            if vnum is not None:
                params["vnum"] = vnum
            
            result = await self.mcp.call_tool("find_static_wilderness_room", params)
            return result
            
        except Exception as e:
            logger.error(f"Failed to find static room: {str(e)}")
            return {"error": str(e)}
    
    async def analyze_region(
        self,
        region_id: int,
        include_paths: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a wilderness region via MCP
        """
        try:
            result = await self.mcp.call_tool(
                "analyze_region",
                {
                    "region_id": region_id,
                    "include_paths": include_paths
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze region: {str(e)}")
            return {"error": str(e)}
    
    async def update_region_description(
        self,
        vnum: int,
        region_description: str,
        **metadata
    ) -> Dict[str, Any]:
        """
        Update region description and metadata via MCP
        """
        try:
            params = {
                "vnum": vnum,
                "region_description": region_description,
                **metadata
            }
            
            result = await self.mcp.call_tool("update_region_description", params)
            return result
            
        except Exception as e:
            logger.error(f"Failed to update region description: {str(e)}")
            return {"error": str(e)}
    
    async def store_region_hints(
        self,
        region_vnum: int,
        hints: List[Dict[str, Any]],
        profile: Optional[Dict[str, Any]] = None,
        clear_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Store generated hints in the database via MCP
        """
        try:
            result = await self.mcp.call_tool(
                "store_region_hints",
                {
                    "region_vnum": region_vnum,
                    "hints": hints,
                    "profile": profile,
                    "clear_existing": clear_existing
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to store hints: {str(e)}")
            return {"error": str(e)}
    
    async def get_region_hints(
        self,
        region_vnum: int,
        category: Optional[str] = None,
        weather_conditions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get existing hints for a region via MCP
        """
        try:
            params = {"region_vnum": region_vnum}
            if category:
                params["category"] = category
            if weather_conditions:
                params["weather_conditions"] = weather_conditions
            
            result = await self.mcp.call_tool("get_region_hints", params)
            return result
            
        except Exception as e:
            logger.error(f"Failed to get hints: {str(e)}")
            return {"error": str(e)}