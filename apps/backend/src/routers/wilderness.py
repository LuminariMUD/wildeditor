"""
Wilderness API Router

Provides REST endpoints for wilderness room data and navigation using the LuminariMUD terrain bridge.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from ..middleware.auth import RequireAuth
from ..services.terrain_bridge import get_terrain_client, TerrainBridgeError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/rooms")
async def list_wilderness_rooms(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of rooms to return"),
    authenticated: bool = RequireAuth
):
    """
    Get list of static wilderness rooms
    
    Returns summary information for wilderness rooms in zone 10000,
    including coordinates and basic details.
    """
    client = get_terrain_client()
    
    try:
        response = await client.get_static_rooms_list(limit)
        
        return {
            "total_rooms": response.get('total_rooms', 0),
            "returned_count": len(response.get('data', [])),
            "limit": limit,
            "rooms": response.get('data', []),
            "source": "terrain_bridge"
        }
        
    except TerrainBridgeError as e:
        raise HTTPException(status_code=503, detail=f"Terrain bridge error: {str(e)}")


@router.get("/rooms/{vnum}")
async def get_room_details(
    vnum: int,
    authenticated: bool = RequireAuth
):
    """
    Get detailed information for a specific wilderness room
    
    Returns complete room data including description, exits, flags,
    and coordinate information.
    """
    client = get_terrain_client()
    
    try:
        response = await client.get_room_details(vnum)
        room_data = response.get('data', {})
        
        return {
            "room": room_data,
            "source": "terrain_bridge"
        }
        
    except TerrainBridgeError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Room {vnum} not found")
        raise HTTPException(status_code=503, detail=f"Terrain bridge error: {str(e)}")


@router.get("/rooms/at-coordinates")
async def get_room_at_coordinates(
    x: int = Query(..., ge=-1024, le=1024, description="X coordinate"),
    y: int = Query(..., ge=-1024, le=1024, description="Y coordinate"),
    authenticated: bool = RequireAuth
):
    """
    Find wilderness room at specific coordinates
    
    Searches for a wilderness room at the given coordinates and returns
    room details if found.
    """
    client = get_terrain_client()
    
    try:
        # First get the list of rooms to find one at these coordinates
        response = await client.get_static_rooms_list(1000)  # Get more rooms to search
        rooms = response.get('data', [])
        
        # Find room at coordinates
        matching_room = None
        for room in rooms:
            if room.get('x') == x and room.get('y') == y:
                matching_room = room
                break
        
        if not matching_room:
            # Check if there's terrain at these coordinates
            terrain_response = await client.get_terrain(x, y)
            terrain_data = terrain_response.get('data', {})
            
            return {
                "coordinates": {"x": x, "y": y},
                "room": None,
                "terrain": terrain_data,
                "message": "No static room found at these coordinates, but terrain data is available",
                "source": "terrain_bridge"
            }
        
        # Get detailed room information
        room_details_response = await client.get_room_details(matching_room['vnum'])
        
        return {
            "coordinates": {"x": x, "y": y},
            "room": room_details_response.get('data', {}),
            "source": "terrain_bridge"
        }
        
    except TerrainBridgeError as e:
        raise HTTPException(status_code=503, detail=f"Terrain bridge error: {str(e)}")


@router.get("/navigation/entrances")
async def get_zone_entrances(
    authenticated: bool = RequireAuth
):
    """
    Get zone entrance information from wilderness rooms
    
    Returns rooms that serve as entrances/exits to other zones,
    providing navigation information for the wilderness system.
    """
    client = get_terrain_client()
    
    try:
        # Get all wilderness rooms
        response = await client.get_static_rooms_list(1000)
        rooms = response.get('data', [])
        
        entrances = []
        
        # Find rooms with zone entrance sector type or exits to other zones
        for room in rooms:
            if room.get('sector_type') == 'Zone Entrance':
                # Get detailed room info to see exits
                try:
                    details_response = await client.get_room_details(room['vnum'])
                    room_details = details_response.get('data', {})
                    
                    # Look for exits to non-wilderness zones
                    zone_exits = []
                    for exit_info in room_details.get('exits', []):
                        to_vnum = exit_info.get('to_room_vnum', 0)
                        # Wilderness rooms are 1000000-1009999
                        if not (1000000 <= to_vnum <= 1009999):
                            zone_exits.append({
                                "direction": exit_info.get('direction'),
                                "to_room_vnum": to_vnum,
                                "to_sector_type": exit_info.get('to_room_sector_type')
                            })
                    
                    if zone_exits:
                        entrances.append({
                            "wilderness_room": {
                                "vnum": room['vnum'],
                                "name": room.get('name'),
                                "x": room.get('x'),
                                "y": room.get('y')
                            },
                            "zone_exits": zone_exits
                        })
                        
                except TerrainBridgeError:
                    # Skip this room if we can't get details
                    continue
        
        return {
            "entrance_count": len(entrances),
            "entrances": entrances,
            "source": "terrain_bridge"
        }
        
    except TerrainBridgeError as e:
        raise HTTPException(status_code=503, detail=f"Terrain bridge error: {str(e)}")


@router.get("/navigation/routes")
async def find_route(
    from_x: int = Query(..., ge=-1024, le=1024, description="Starting X coordinate"),
    from_y: int = Query(..., ge=-1024, le=1024, description="Starting Y coordinate"),
    to_x: int = Query(..., ge=-1024, le=1024, description="Destination X coordinate"),
    to_y: int = Query(..., ge=-1024, le=1024, description="Destination Y coordinate"),
    authenticated: bool = RequireAuth
):
    """
    Calculate a route between two wilderness coordinates
    
    Provides basic pathfinding information and terrain analysis
    for traveling between two points in the wilderness.
    """
    client = get_terrain_client()
    
    try:
        import math
        
        # Calculate direct distance
        distance = math.sqrt((to_x - from_x)**2 + (to_y - from_y)**2)
        
        # Sample terrain along the direct route
        num_samples = min(int(distance) + 1, 50)  # Limit samples
        route_points = []
        
        for i in range(num_samples):
            if num_samples == 1:
                t = 0
            else:
                t = i / (num_samples - 1)
            
            sample_x = int(from_x + t * (to_x - from_x))
            sample_y = int(from_y + t * (to_y - from_y))
            
            terrain_response = await client.get_terrain(sample_x, sample_y)
            terrain_data = terrain_response.get('data', {})
            
            route_points.append({
                "x": sample_x,
                "y": sample_y,
                "distance_from_start": t * distance,
                "elevation": terrain_data.get('elevation'),
                "sector_name": terrain_data.get('sector_name'),
                "temperature": terrain_data.get('temperature')
            })
        
        # Analyze route difficulty
        elevation_changes = []
        difficult_terrain = []
        
        for i in range(1, len(route_points)):
            prev_elev = route_points[i-1].get('elevation', 0)
            curr_elev = route_points[i].get('elevation', 0)
            elevation_changes.append(abs(curr_elev - prev_elev))
            
            sector = route_points[i].get('sector_name', '')
            if sector in ['High Mountain', 'Water No Swim', 'Ocean']:
                difficult_terrain.append({
                    "coordinates": {"x": route_points[i]['x'], "y": route_points[i]['y']},
                    "sector": sector,
                    "distance": route_points[i]['distance_from_start']
                })
        
        avg_elevation_change = sum(elevation_changes) / len(elevation_changes) if elevation_changes else 0
        
        return {
            "from": {"x": from_x, "y": from_y},
            "to": {"x": to_x, "y": to_y},
            "route_analysis": {
                "direct_distance": distance,
                "sample_points": len(route_points),
                "average_elevation_change": avg_elevation_change,
                "difficult_terrain_count": len(difficult_terrain),
                "estimated_difficulty": "easy" if avg_elevation_change < 10 and not difficult_terrain 
                                      else "moderate" if avg_elevation_change < 25 and len(difficult_terrain) < 3
                                      else "hard"
            },
            "route_points": route_points,
            "difficult_terrain": difficult_terrain,
            "source": "terrain_bridge"
        }
        
    except TerrainBridgeError as e:
        raise HTTPException(status_code=503, detail=f"Terrain bridge error: {str(e)}")


@router.get("/config")
async def get_wilderness_config(authenticated: bool = RequireAuth):
    """
    Get wilderness system configuration information
    
    Returns basic configuration data about the wilderness system
    including coordinate ranges and room VNUM ranges.
    """
    return {
        "coordinate_system": {
            "x_range": {"min": -1024, "max": 1024},
            "y_range": {"min": -1024, "max": 1024},
            "total_coordinates": 2048 * 2048
        },
        "room_vnums": {
            "static_wilderness": {"start": 1000000, "end": 1003999},
            "dynamic_wilderness": {"start": 1004000, "end": 1009999},
            "navigation_room": 1000000
        },
        "zone_info": {
            "wilderness_zone_vnum": 10000,
            "zone_name": "Wilderness of Luminari"
        },
        "terrain_bridge": {
            "host": "localhost",
            "port": 8182,
            "protocol": "TCP JSON"
        },
        "source": "static_config"
    }
