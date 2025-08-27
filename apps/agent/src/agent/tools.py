"""Tool definitions for the Wilderness Assistant Agent - MCP Only Version"""
from typing import Optional, Dict, Any, List, Tuple
import logging
import math
import random
import json

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

    # ========================================
    # SPATIAL INTELLIGENCE HELPER METHODS  
    # ========================================

    def generate_organic_border(
        self, 
        center_x: float, 
        center_y: float, 
        base_radius: float = 50.0, 
        num_points: int = 10,
        irregularity: float = 0.3,
        spikiness: float = 0.2
    ) -> List[Dict[str, float]]:
        """
        Generate natural-looking organic border coordinates for regions.
        
        Args:
            center_x, center_y: Center point of the region
            base_radius: Base radius for the shape
            num_points: Number of points in the polygon (8-12 recommended)
            irregularity: How irregular the shape is (0.0-1.0)
            spikiness: How spiky the shape is (0.0-1.0)
            
        Returns:
            List of coordinate dictionaries for organic border
        """
        logger.info(f"Generating organic border: center=({center_x}, {center_y}), radius={base_radius}")
        
        # Ensure minimum points for valid polygon
        num_points = max(3, min(20, num_points))
        
        # Generate angles
        angles = []
        for i in range(num_points):
            # Base angle
            base_angle = (2 * math.pi * i) / num_points
            
            # Add irregularity  
            angle_variance = irregularity * (random.random() - 0.5) * (2 * math.pi / num_points)
            angles.append(base_angle + angle_variance)
        
        # Sort angles to maintain proper polygon order
        angles.sort()
        
        # Generate coordinates
        coordinates = []
        for angle in angles:
            # Vary the radius for spikiness
            radius_variance = spikiness * (random.random() - 0.5) * base_radius
            current_radius = base_radius + radius_variance
            
            # Ensure radius stays positive and within bounds
            current_radius = max(5.0, min(100.0, current_radius))
            
            # Calculate point
            x = center_x + current_radius * math.cos(angle)
            y = center_y + current_radius * math.sin(angle)
            
            # Clamp to wilderness bounds
            x = max(-1024, min(1024, round(x)))
            y = max(-1024, min(1024, round(y)))
            
            coordinates.append({"x": float(x), "y": float(y)})
        
        logger.info(f"Generated {len(coordinates)} organic border points")
        return coordinates

    async def find_empty_space_between_regions(
        self, 
        region1_vnum: int, 
        region2_vnum: int,
        min_distance: float = 20.0
    ) -> Dict[str, Any]:
        """
        Find suitable empty space between two regions for placing a new region.
        
        Args:
            region1_vnum: First region's vnum
            region2_vnum: Second region's vnum
            min_distance: Minimum distance from existing regions
            
        Returns:
            Dict with suggested coordinates and analysis
        """
        try:
            logger.info(f"Finding space between regions {region1_vnum} and {region2_vnum}")
            
            # Search for both regions first
            region1_result = await self.mcp.call_tool("search_regions", {
                "region_type": None,
                "vnum": region1_vnum
            })
            
            region2_result = await self.mcp.call_tool("search_regions", {
                "region_type": None, 
                "vnum": region2_vnum
            })
            
            if not region1_result.get("regions") or not region2_result.get("regions"):
                return {"error": "One or both regions not found"}
            
            region1 = region1_result["regions"][0]
            region2 = region2_result["regions"][0]
            
            # Calculate center points
            def get_region_center(region):
                coords = region.get("coordinates", [])
                if not coords:
                    return None
                x_avg = sum(c["x"] for c in coords) / len(coords)
                y_avg = sum(c["y"] for c in coords) / len(coords)
                return {"x": x_avg, "y": y_avg}
            
            center1 = get_region_center(region1)
            center2 = get_region_center(region2)
            
            if not center1 or not center2:
                return {"error": "Could not calculate region centers"}
            
            # Find midpoint
            mid_x = (center1["x"] + center2["x"]) / 2
            mid_y = (center1["y"] + center2["y"]) / 2
            
            # Search for existing regions in the middle area
            search_radius = max(30.0, min_distance * 2)
            existing_check = await self.mcp.call_tool("search_by_coordinates", {
                "x": mid_x,
                "y": mid_y,
                "radius": search_radius
            })
            
            # Analyze terrain in the area
            terrain_analysis = await self.mcp.call_tool("analyze_complete_terrain_map", {
                "center_x": int(mid_x),
                "center_y": int(mid_y), 
                "radius": int(search_radius / 2),
                "include_regions": True,
                "include_paths": True
            })
            
            return {
                "success": True,
                "suggested_center": {"x": mid_x, "y": mid_y},
                "region1_center": center1,
                "region2_center": center2,
                "distance_between": math.sqrt((center2["x"] - center1["x"])**2 + (center2["y"] - center1["y"])**2),
                "existing_regions": existing_check.get("regions", []),
                "existing_paths": existing_check.get("paths", []),
                "terrain_analysis": terrain_analysis,
                "recommended_radius": max(15.0, min_distance),
                "is_clear": len(existing_check.get("regions", [])) == 0
            }
            
        except Exception as e:
            logger.error(f"Failed to find space between regions: {str(e)}")
            return {"error": str(e)}

    async def create_path_connecting_regions(
        self,
        region_vnums: List[int],
        path_type: int = 2,  # Default to dirt road
        path_name: str = "Connecting Path"
    ) -> Dict[str, Any]:
        """
        Create a path that connects multiple regions in sequence.
        
        Args:
            region_vnums: List of region vnums to connect
            path_type: Type of path (1=Paved, 2=Dirt, 3=Geographic, 5=River, 6=Stream)
            path_name: Name for the path
            
        Returns:
            Dict with path coordinates and creation result
        """
        try:
            logger.info(f"Creating path connecting regions: {region_vnums}")
            
            if len(region_vnums) < 2:
                return {"error": "Need at least 2 regions to connect"}
            
            # Get all region centers
            region_centers = []
            for vnum in region_vnums:
                result = await self.mcp.call_tool("search_regions", {
                    "region_type": None,
                    "vnum": vnum
                })
                
                if not result.get("regions"):
                    return {"error": f"Region {vnum} not found"}
                
                region = result["regions"][0]
                coords = region.get("coordinates", [])
                if not coords:
                    return {"error": f"Region {vnum} has no coordinates"}
                
                center_x = sum(c["x"] for c in coords) / len(coords)
                center_y = sum(c["y"] for c in coords) / len(coords)
                region_centers.append({"x": center_x, "y": center_y, "vnum": vnum})
            
            # Generate path coordinates with curves between centers
            path_coordinates = []
            
            for i in range(len(region_centers)):
                center = region_centers[i]
                
                if i == 0:
                    # Starting point
                    path_coordinates.append({"x": center["x"], "y": center["y"]})
                else:
                    prev_center = region_centers[i-1]
                    
                    # Add curved path between centers
                    curved_points = self._generate_curved_path(
                        prev_center["x"], prev_center["y"],
                        center["x"], center["y"],
                        num_intermediate_points=2
                    )
                    
                    # Skip the first point (already added) and add the rest
                    path_coordinates.extend(curved_points[1:])
            
            # Create the path using MCP
            result = await self.mcp.call_tool("create_path", {
                "name": path_name,
                "path_type": path_type,
                "coordinates": path_coordinates,
                "zone_vnum": 10000
            })
            
            return {
                "success": True,
                "path_coordinates": path_coordinates,
                "connected_regions": region_vnums,
                "creation_result": result
            }
            
        except Exception as e:
            logger.error(f"Failed to create connecting path: {str(e)}")
            return {"error": str(e)}

    def _generate_curved_path(
        self, 
        start_x: float, start_y: float,
        end_x: float, end_y: float,
        num_intermediate_points: int = 2
    ) -> List[Dict[str, float]]:
        """
        Generate a curved path between two points using Bezier-like interpolation.
        
        Returns:
            List of coordinate points forming a curved path
        """
        points = []
        
        # Add start point
        points.append({"x": start_x, "y": start_y})
        
        # Calculate distance and perpendicular offset for curve
        distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        curve_offset = min(30.0, distance * 0.3)  # Curve strength based on distance
        
        # Calculate perpendicular direction for curve
        if distance > 0:
            # Unit vector from start to end
            dir_x = (end_x - start_x) / distance  
            dir_y = (end_y - start_y) / distance
            
            # Perpendicular vector (90 degree rotation)
            perp_x = -dir_y
            perp_y = dir_x
        else:
            perp_x = perp_y = 0
        
        # Generate intermediate points
        for i in range(1, num_intermediate_points + 1):
            t = i / (num_intermediate_points + 1)
            
            # Linear interpolation
            x = start_x + t * (end_x - start_x)
            y = start_y + t * (end_y - start_y)
            
            # Add curve offset (sin wave for smooth curve)
            curve_factor = math.sin(t * math.pi) * curve_offset
            x += curve_factor * perp_x
            y += curve_factor * perp_y
            
            # Clamp to bounds and add some randomness
            x += (random.random() - 0.5) * 10  # Small random offset
            y += (random.random() - 0.5) * 10
            
            x = max(-1024, min(1024, round(x)))
            y = max(-1024, min(1024, round(y)))
            
            points.append({"x": float(x), "y": float(y)})
        
        # Add end point
        points.append({"x": end_x, "y": end_y})
        
        return points

    async def check_region_overlap(
        self,
        coordinates: List[Dict[str, float]],
        region_type: int = 1,  # Default to Geographic
        exclude_vnum: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Check if proposed region coordinates would overlap with existing geographic regions.
        
        Args:
            coordinates: Proposed region coordinates
            region_type: Type of region being checked
            exclude_vnum: Region vnum to exclude from overlap check (for editing)
            
        Returns:
            Dict with overlap analysis and suggestions
        """
        try:
            logger.info(f"Checking region overlap for {len(coordinates)} coordinates")
            
            if not coordinates:
                return {"error": "No coordinates provided"}
            
            # Calculate center point and bounding box
            center_x = sum(c["x"] for c in coordinates) / len(coordinates)
            center_y = sum(c["y"] for c in coordinates) / len(coordinates)
            
            min_x = min(c["x"] for c in coordinates)
            max_x = max(c["x"] for c in coordinates) 
            min_y = min(c["y"] for c in coordinates)
            max_y = max(c["y"] for c in coordinates)
            
            # Search radius should cover the bounding box plus some margin
            search_radius = max(
                abs(max_x - min_x) / 2,
                abs(max_y - min_y) / 2
            ) + 20
            
            # Search for existing regions in the area
            search_result = await self.mcp.call_tool("search_by_coordinates", {
                "x": center_x,
                "y": center_y,
                "radius": search_radius
            })
            
            existing_regions = search_result.get("regions", [])
            
            # Filter out non-geographic regions and excluded region
            geographic_regions = [
                r for r in existing_regions 
                if r.get("region_type") == 1  # Geographic regions only
                and (exclude_vnum is None or r.get("vnum") != exclude_vnum)
            ]
            
            overlap_warnings = []
            
            # Check for potential overlaps (simplified bounding box check)
            for region in geographic_regions:
                region_coords = region.get("coordinates", [])
                if not region_coords:
                    continue
                
                # Calculate existing region bounding box
                existing_min_x = min(c["x"] for c in region_coords)
                existing_max_x = max(c["x"] for c in region_coords)
                existing_min_y = min(c["y"] for c in region_coords)
                existing_max_y = max(c["y"] for c in region_coords)
                
                # Check bounding box overlap
                if (max_x >= existing_min_x and min_x <= existing_max_x and
                    max_y >= existing_min_y and min_y <= existing_max_y):
                    overlap_warnings.append({
                        "region_name": region.get("name", f"Region {region.get('vnum')}"),
                        "region_vnum": region.get("vnum"),
                        "overlap_severity": "possible"  # Could do more precise polygon intersection
                    })
            
            # Only warn for geographic regions (type 1) overlapping with other geographic regions
            should_warn = region_type == 1 and len(overlap_warnings) > 0
            
            return {
                "success": True,
                "center": {"x": center_x, "y": center_y},
                "bounding_box": {
                    "min_x": min_x, "max_x": max_x,
                    "min_y": min_y, "max_y": max_y
                },
                "existing_regions": existing_regions,
                "geographic_overlaps": overlap_warnings,
                "has_overlap_risk": should_warn,
                "recommendation": (
                    "WARNING: Potential geographic region overlap detected. Consider adjusting coordinates." 
                    if should_warn else "Area appears clear for new region."
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to check region overlap: {str(e)}")
            return {"error": str(e)}