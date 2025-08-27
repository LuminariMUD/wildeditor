"""Tool definitions for the Wilderness Assistant Agent"""
from typing import Optional, Dict, Any, List, Tuple
from pydantic import BaseModel, Field
import logging
import json

logger = logging.getLogger(__name__)


class RegionCreationParams(BaseModel):
    """Parameters for creating a region"""
    name: str = Field(..., description="Name of the region")
    type: str = Field(..., description="Type of region (e.g., 'forest', 'mountain', 'plains')")
    coordinates: List[List[float]] = Field(..., description="Polygon coordinates defining the region")
    properties: Optional[Dict[str, Any]] = Field(default=None, description="Additional properties")
    color: Optional[str] = Field(default=None, description="Display color for the region")


class DescriptionGenerationParams(BaseModel):
    """Parameters for generating a description"""
    region_name: Optional[str] = Field(None, description="Name of the region")
    terrain_theme: Optional[str] = Field(None, description="Theme for the terrain")
    description_style: str = Field(default="immersive", description="Style: immersive, technical, or poetic")
    description_length: str = Field(default="medium", description="Length: short, medium, or long")
    user_prompt: Optional[str] = Field(None, description="Additional guidance for generation")


class TerrainAnalysisParams(BaseModel):
    """Parameters for terrain analysis"""
    x: int = Field(..., description="X coordinate")
    y: int = Field(..., description="Y coordinate")


class MapGenerationParams(BaseModel):
    """Parameters for map generation"""
    center_x: int = Field(..., description="Center X coordinate")
    center_y: int = Field(..., description="Center Y coordinate")
    radius: int = Field(default=10, description="Radius of the map area")


class WildernessTools:
    """Collection of tools for wilderness operations"""
    
    def __init__(self, backend_client, mcp_client):
        self.backend = backend_client
        self.mcp = mcp_client
        logger.info("Initialized WildernessTools")
    
    async def create_region(
        self,
        name: str,
        region_type: str,
        coordinates: List[List[float]],
        properties: Optional[Dict[str, Any]] = None,
        color: Optional[str] = None,
        auto_generate_description: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new wilderness region
        
        This tool creates a new region in the wilderness with the specified
        parameters and optionally generates a description for it.
        """
        try:
            # Prepare region data
            region_data = {
                "name": name,
                "type": region_type,
                "coordinates": coordinates,
                "properties": properties or {},
                "color": color or self._get_default_color(region_type)
            }
            
            # Create the region
            region = await self.backend.create_region(region_data)
            logger.info(f"Created region: {region.get('id')} - {name}")
            
            # Generate description if requested
            if auto_generate_description and region.get("vnum"):
                try:
                    description = await self.generate_region_description(
                        region_name=name,
                        terrain_theme=region_type,
                        description_style="immersive"
                    )
                    
                    # Update region with description
                    if description:
                        await self.backend.update_region(
                            region["id"],
                            {"properties": {**region.get("properties", {}), "description": description}}
                        )
                        region["properties"]["description"] = description
                        logger.info(f"Added generated description to region {region['id']}")
                except Exception as e:
                    logger.warning(f"Failed to generate description: {str(e)}")
            
            return {
                "success": True,
                "region": region,
                "message": f"Created region '{name}' successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create region: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create region: {str(e)}"
            }
    
    async def generate_region_description(
        self,
        region_name: Optional[str] = None,
        terrain_theme: Optional[str] = None,
        description_style: str = "immersive",
        description_length: str = "medium",
        user_prompt: Optional[str] = None
    ) -> str:
        """
        Generate an AI-powered description for a region
        
        This tool uses AI to generate rich, atmospheric descriptions
        for wilderness regions based on the provided parameters.
        """
        try:
            description = await self.mcp.generate_description(
                region_name=region_name,
                terrain_theme=terrain_theme,
                description_style=description_style,
                description_length=description_length,
                user_prompt=user_prompt
            )
            
            logger.info(f"Generated description for {region_name or 'unnamed region'}")
            return description
            
        except Exception as e:
            logger.error(f"Failed to generate description: {str(e)}")
            raise
    
    async def generate_region_hints(
        self,
        vnum: int,
        description: str,
        style: str = "dynamic"
    ) -> Dict[str, Any]:
        """
        Generate dynamic hints for a region based on its description
        
        This tool creates weather, time, and season-specific variations
        of the region description for dynamic storytelling.
        """
        try:
            result = await self.backend.generate_hints(vnum, description, style)
            logger.info(f"Generated hints for region {vnum}")
            return {
                "success": True,
                "hints": result.get("hints", []),
                "count": len(result.get("hints", [])),
                "message": f"Generated {len(result.get('hints', []))} hints"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate hints: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to generate hints: {str(e)}"
            }
    
    async def analyze_terrain(
        self,
        x: int,
        y: int,
        include_nearby: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze terrain at specific coordinates
        
        This tool examines the terrain type and characteristics at the
        specified wilderness coordinates.
        """
        try:
            terrain = await self.mcp.analyze_terrain(x, y)
            
            result = {
                "success": True,
                "coordinates": {"x": x, "y": y},
                "terrain": terrain,
                "message": f"Terrain at ({x}, {y}): {terrain.get('type', 'unknown')}"
            }
            
            # Optionally include nearby analysis
            if include_nearby:
                nearby = await self.mcp.analyze_complete_terrain(x, y, radius=3)
                result["nearby_terrain"] = nearby
            
            logger.info(f"Analyzed terrain at ({x}, {y})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze terrain: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to analyze terrain: {str(e)}"
            }
    
    async def find_zone_entrances_near(
        self,
        x: int,
        y: int,
        radius: int = 50
    ) -> Dict[str, Any]:
        """
        Find zone entrances near specific coordinates
        
        This tool locates all zone entrances within a specified radius
        of the given coordinates.
        """
        try:
            # Get all zone entrances
            all_entrances = await self.mcp.find_zone_entrances()
            
            # Filter by distance
            nearby_entrances = []
            for entrance in all_entrances:
                if "x" in entrance and "y" in entrance:
                    distance = ((entrance["x"] - x) ** 2 + (entrance["y"] - y) ** 2) ** 0.5
                    if distance <= radius:
                        entrance["distance"] = round(distance, 2)
                        nearby_entrances.append(entrance)
            
            # Sort by distance
            nearby_entrances.sort(key=lambda e: e.get("distance", float("inf")))
            
            return {
                "success": True,
                "center": {"x": x, "y": y},
                "radius": radius,
                "entrances": nearby_entrances,
                "count": len(nearby_entrances),
                "message": f"Found {len(nearby_entrances)} zone entrances within {radius} units"
            }
            
        except Exception as e:
            logger.error(f"Failed to find zone entrances: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to find zone entrances: {str(e)}"
            }
    
    async def generate_wilderness_map(
        self,
        center_x: int,
        center_y: int,
        radius: int = 10
    ) -> Dict[str, Any]:
        """
        Generate a map of a wilderness area
        
        This tool creates a detailed map showing terrain types, regions,
        and features within the specified area.
        """
        try:
            map_data = await self.mcp.generate_wilderness_map(center_x, center_y, radius)
            
            return {
                "success": True,
                "center": {"x": center_x, "y": center_y},
                "radius": radius,
                "map": map_data,
                "message": f"Generated map for {radius}-unit radius around ({center_x}, {center_y})"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate map: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to generate map: {str(e)}"
            }
    
    async def update_region(
        self,
        region_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing region
        
        This tool modifies properties of an existing region.
        """
        try:
            updated_region = await self.backend.update_region(region_id, updates)
            
            return {
                "success": True,
                "region": updated_region,
                "message": f"Updated region {region_id} successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to update region: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to update region: {str(e)}"
            }
    
    async def list_regions_in_area(
        self,
        min_x: int,
        min_y: int,
        max_x: int,
        max_y: int
    ) -> Dict[str, Any]:
        """
        List all regions within a bounding box
        
        This tool finds all regions that intersect with the specified area.
        """
        try:
            # Get all regions (pagination might be needed for large datasets)
            all_regions = await self.backend.get_regions(limit=1000)
            
            # Filter regions by bounding box
            regions_in_area = []
            for region in all_regions:
                # Check if region intersects with the bounding box
                # This is a simplified check - proper polygon intersection would be better
                if self._region_intersects_box(region, min_x, min_y, max_x, max_y):
                    regions_in_area.append(region)
            
            return {
                "success": True,
                "area": {
                    "min_x": min_x,
                    "min_y": min_y,
                    "max_x": max_x,
                    "max_y": max_y
                },
                "regions": regions_in_area,
                "count": len(regions_in_area),
                "message": f"Found {len(regions_in_area)} regions in the specified area"
            }
            
        except Exception as e:
            logger.error(f"Failed to list regions: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list regions: {str(e)}"
            }
    
    def _get_default_color(self, region_type: str) -> str:
        """Get default color for a region type"""
        colors = {
            "forest": "#228B22",
            "mountain": "#8B7355",
            "plains": "#DAA520",
            "desert": "#F4A460",
            "water": "#4682B4",
            "swamp": "#556B2F",
            "tundra": "#B0E0E6",
            "city": "#696969"
        }
        return colors.get(region_type.lower(), "#808080")
    
    def _region_intersects_box(
        self,
        region: Dict[str, Any],
        min_x: int,
        min_y: int,
        max_x: int,
        max_y: int
    ) -> bool:
        """Check if a region intersects with a bounding box"""
        coordinates = region.get("coordinates", [])
        if not coordinates:
            return False
        
        # Check if any point is within the box
        for coord in coordinates:
            if len(coord) >= 2:
                x, y = coord[0], coord[1]
                if min_x <= x <= max_x and min_y <= y <= max_y:
                    return True
        
        return False