"""
Terrain API Router

Provides REST endpoints for wilderness terrain data using the LuminariMUD terrain bridge.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
import math
from ..middleware.auth import RequireAuth
from ..services.terrain_bridge import get_terrain_client, TerrainBridgeError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def terrain_health_check():
    """
    Check if the terrain bridge is available
    """
    client = get_terrain_client()
    is_available = await client.health_check()
    
    return {
        "terrain_bridge_available": is_available,
        "status": "healthy" if is_available else "unavailable",
        "service": "terrain-bridge"
    }


@router.get("/at-coordinates")
async def get_terrain_at_coordinates(
    x: int = Query(..., ge=-1024, le=1024, description="X coordinate"),
    y: int = Query(..., ge=-1024, le=1024, description="Y coordinate"),
    authenticated: bool = Depends(RequireAuth())
):
    """
    Get terrain data for a specific coordinate
    
    Returns elevation, temperature, moisture, and sector type information
    for the specified wilderness coordinates.
    """
    client = get_terrain_client()
    
    try:
        response = await client.get_terrain(x, y)
        terrain_data = response.get('data', {})
        
        return {
            "coordinates": {"x": x, "y": y},
            "terrain": {
                "elevation": terrain_data.get('elevation'),
                "temperature": terrain_data.get('temperature'),
                "moisture": terrain_data.get('moisture'),
                "sector_type": terrain_data.get('sector_type'),
                "sector_name": terrain_data.get('sector_name')
            },
            "source": "terrain_bridge"
        }
        
    except TerrainBridgeError as e:
        raise HTTPException(status_code=503, detail=f"Terrain bridge error: {str(e)}")


@router.get("/area")
async def get_terrain_area(
    min_x: int = Query(..., ge=-1024, le=1024, description="Minimum X coordinate"),
    max_x: int = Query(..., ge=-1024, le=1024, description="Maximum X coordinate"),
    min_y: int = Query(..., ge=-1024, le=1024, description="Minimum Y coordinate"),
    max_y: int = Query(..., ge=-1024, le=1024, description="Maximum Y coordinate"),
    authenticated: bool = Depends(RequireAuth())
):
    """
    Get terrain data for a rectangular area
    
    Returns terrain information for all coordinates in the specified area.
    Limited to 1000 coordinates maximum for performance.
    """
    # Validate area size
    area_size = (max_x - min_x + 1) * (max_y - min_y + 1)
    if area_size > 1000:
        raise HTTPException(
            status_code=400, 
            detail=f"Area too large ({area_size} coordinates). Maximum 1000 coordinates allowed."
        )
    
    client = get_terrain_client()
    
    try:
        response = await client.get_terrain_batch(min_x, min_y, max_x, max_y)
        
        return {
            "area": {
                "min_x": min_x,
                "max_x": max_x,
                "min_y": min_y,
                "max_y": max_y
            },
            "count": response.get('count', 0),
            "terrain_data": response.get('data', []),
            "source": "terrain_bridge"
        }
        
    except TerrainBridgeError as e:
        raise HTTPException(status_code=503, detail=f"Terrain bridge error: {str(e)}")


@router.get("/elevation-profile")
async def get_elevation_profile(
    from_x: int = Query(..., ge=-1024, le=1024, description="Starting X coordinate"),
    from_y: int = Query(..., ge=-1024, le=1024, description="Starting Y coordinate"),
    to_x: int = Query(..., ge=-1024, le=1024, description="Ending X coordinate"),
    to_y: int = Query(..., ge=-1024, le=1024, description="Ending Y coordinate"),
    authenticated: bool = Depends(RequireAuth())
):
    """
    Get elevation profile along a line between two points
    
    Samples elevation at regular intervals along the line from start to end coordinates.
    Useful for pathfinding and terrain analysis.
    """
    client = get_terrain_client()
    
    try:
        # Calculate sampling points along the line
        distance = math.sqrt((to_x - from_x)**2 + (to_y - from_y)**2)
        num_samples = min(int(distance) + 1, 100)  # Limit to 100 samples
        
        profile_points = []
        
        for i in range(num_samples):
            if num_samples == 1:
                t = 0
            else:
                t = i / (num_samples - 1)
            
            sample_x = int(from_x + t * (to_x - from_x))
            sample_y = int(from_y + t * (to_y - from_y))
            
            response = await client.get_terrain(sample_x, sample_y)
            terrain_data = response.get('data', {})
            
            profile_points.append({
                "x": sample_x,
                "y": sample_y,
                "distance": t * distance,
                "elevation": terrain_data.get('elevation'),
                "sector_name": terrain_data.get('sector_name')
            })
        
        return {
            "from": {"x": from_x, "y": from_y},
            "to": {"x": to_x, "y": to_y},
            "total_distance": distance,
            "sample_count": len(profile_points),
            "elevation_profile": profile_points,
            "source": "terrain_bridge"
        }
        
    except TerrainBridgeError as e:
        raise HTTPException(status_code=503, detail=f"Terrain bridge error: {str(e)}")


@router.get("/map-data")
async def generate_map_data(
    center_x: int = Query(..., ge=-1024, le=1024, description="Center X coordinate"),
    center_y: int = Query(..., ge=-1024, le=1024, description="Center Y coordinate"),
    radius: int = Query(10, ge=1, le=31, description="Map radius (max 31)"),
    authenticated: bool = Depends(RequireAuth())
):
    """
    Generate map data for a circular area around a center point
    
    Returns terrain data suitable for rendering a wilderness map.
    Limited to radius 31 to keep under 1000 coordinate limit.
    """
    client = get_terrain_client()
    
    try:
        # Calculate bounding box for the radius
        min_x = max(-1024, center_x - radius)
        max_x = min(1024, center_x + radius)
        min_y = max(-1024, center_y - radius)
        max_y = min(1024, center_y + radius)
        
        response = await client.get_terrain_batch(min_x, min_y, max_x, max_y)
        terrain_data = response.get('data', [])
        
        # Organize data into a grid format for easy map rendering
        map_grid = {}
        for point in terrain_data:
            x, y = point['x'], point['y']
            # Only include points within the circular radius
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            if distance <= radius:
                map_grid[f"{x},{y}"] = {
                    "x": x,
                    "y": y,
                    "elevation": point.get('elevation'),
                    "sector_type": point.get('sector_type'),
                    "sector_name": point.get('sector_name'),
                    "temperature": point.get('temperature'),
                    "moisture": point.get('moisture')
                }
        
        return {
            "center": {"x": center_x, "y": center_y},
            "radius": radius,
            "bounds": {
                "min_x": min_x,
                "max_x": max_x,
                "min_y": min_y,
                "max_y": max_y
            },
            "point_count": len(map_grid),
            "map_data": map_grid,
            "source": "terrain_bridge"
        }
        
    except TerrainBridgeError as e:
        raise HTTPException(status_code=503, detail=f"Terrain bridge error: {str(e)}")


@router.get("/sector-types")
async def get_sector_types(authenticated: bool = Depends(RequireAuth())):
    """
    Get the list of available sector types
    
    Returns reference information about all terrain sector types
    used by the wilderness system.
    """
    return {
        "sector_types": {
            0: {"name": "Inside", "description": "Indoor areas"},
            1: {"name": "City", "description": "Urban areas"},
            2: {"name": "Field", "description": "Open grasslands"},
            3: {"name": "Forest", "description": "Wooded areas"},
            4: {"name": "Hills", "description": "Rolling hills"},
            5: {"name": "Mountains", "description": "Mountain ranges"},
            6: {"name": "Water Swim", "description": "Shallow water"},
            7: {"name": "Water No Swim", "description": "Deep water"},
            8: {"name": "Underwater", "description": "Underwater areas"},
            9: {"name": "Flying", "description": "Aerial areas"},
            10: {"name": "Desert", "description": "Arid desert"},
            11: {"name": "Ocean", "description": "Open ocean"},
            12: {"name": "Marshland", "description": "Wetlands"},
            13: {"name": "High Mountain", "description": "Impassable peaks"},
            14: {"name": "Road", "description": "Constructed roads"},
            15: {"name": "Zone Entrance", "description": "Entrance to other zones"}
        },
        "total_types": 16,
        "source": "static_reference"
    }
