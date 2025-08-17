"""
LuminariMUD Terrain Bridge Client

Provides real-time access to wilderness terrain data through TCP socket connection
to the game engine's terrain bridge API running on localhost:8182.
"""

import socket
import json
import asyncio
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)


class TerrainBridgeError(Exception):
    """Exception raised when terrain bridge operations fail"""
    pass


class TerrainBridgeClient:
    """
    Async client for LuminariMUD terrain bridge API
    
    Connects to localhost:8182 TCP socket and provides methods for:
    - Real-time terrain calculations (elevation, temperature, moisture, sector)
    - Wilderness room data
    - Batch terrain queries for efficient mapping
    """
    
    def __init__(self, host: str = 'localhost', port: int = 8182, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout
    
    async def _send_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a JSON request to the terrain bridge and return the response
        
        Args:
            request_data: Dictionary to send as JSON
            
        Returns:
            Dictionary response from terrain bridge
            
        Raises:
            TerrainBridgeError: If connection fails or invalid response
        """
        try:
            # Create connection
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout
            )
            
            # Send request
            request_json = json.dumps(request_data) + '\n'
            writer.write(request_json.encode('utf-8'))
            await writer.drain()
            
            # Read response (wait for newline terminator)
            response_data = await asyncio.wait_for(
                reader.readuntil(b'\n'),
                timeout=self.timeout
            )
            
            # Clean up connection
            writer.close()
            await writer.wait_closed()
            
            # Parse response
            response_json = response_data.decode('utf-8').strip()
            response = json.loads(response_json)
            
            # Check for error
            if not response.get('success', False):
                error_msg = response.get('error', 'Unknown terrain bridge error')
                raise TerrainBridgeError(f"Terrain bridge error: {error_msg}")
            
            return response
            
        except asyncio.TimeoutError:
            raise TerrainBridgeError("Terrain bridge connection timeout")
        except json.JSONDecodeError as e:
            raise TerrainBridgeError(f"Invalid JSON response from terrain bridge: {e}")
        except Exception as e:
            raise TerrainBridgeError(f"Terrain bridge connection failed: {e}")
    
    async def ping(self) -> Dict[str, Any]:
        """
        Test connectivity and get server status
        
        Returns:
            Server status including uptime and server time
        """
        return await self._send_request({"command": "ping"})
    
    async def get_terrain(self, x: int, y: int) -> Dict[str, Any]:
        """
        Get terrain data for a single coordinate
        
        Args:
            x: X coordinate (-1024 to +1024)
            y: Y coordinate (-1024 to +1024)
            
        Returns:
            Dictionary with elevation, temperature, moisture, sector_type, sector_name
        """
        if not (-1024 <= x <= 1024) or not (-1024 <= y <= 1024):
            raise TerrainBridgeError("Coordinates must be within -1024 to +1024 range")
        
        return await self._send_request({
            "command": "get_terrain",
            "x": x,
            "y": y
        })
    
    async def get_terrain_batch(self, x_min: int, y_min: int, x_max: int, y_max: int) -> Dict[str, Any]:
        """
        Get terrain data for a rectangular area (batch request)
        
        Args:
            x_min: Minimum X coordinate
            y_min: Minimum Y coordinate
            x_max: Maximum X coordinate
            y_max: Maximum Y coordinate
            
        Returns:
            Dictionary with count and array of terrain data points
        """
        # Validate coordinates
        for coord in [x_min, y_min, x_max, y_max]:
            if not (-1024 <= coord <= 1024):
                raise TerrainBridgeError("Coordinates must be within -1024 to +1024 range")
        
        # Validate batch size (max 1000 coordinates)
        area_size = (x_max - x_min + 1) * (y_max - y_min + 1)
        if area_size > 1000:
            raise TerrainBridgeError("Batch too large (max 1000 coordinates)")
        
        return await self._send_request({
            "command": "get_terrain_batch",
            "params": {
                "x_min": x_min,
                "y_min": y_min,
                "x_max": x_max,
                "y_max": y_max
            }
        })
    
    async def get_static_rooms_list(self, limit: int = 100) -> Dict[str, Any]:
        """
        Get list of static wilderness rooms
        
        Args:
            limit: Maximum number of rooms to return
            
        Returns:
            Dictionary with total_rooms count and array of room summaries
        """
        return await self._send_request({
            "command": "get_static_rooms_list",
            "limit": limit
        })
    
    async def get_room_details(self, vnum: int) -> Dict[str, Any]:
        """
        Get detailed information for a specific room
        
        Args:
            vnum: Room VNUM to query
            
        Returns:
            Dictionary with complete room information including exits
        """
        return await self._send_request({
            "command": "get_room_details",
            "vnum": vnum
        })
    
    async def get_static_room_by_coordinates(self, x: int, y: int) -> Dict[str, Any]:
        """
        Find static wilderness room at specific coordinates using efficient KD-tree lookup
        
        Args:
            x: X coordinate (-1024 to +1024)
            y: Y coordinate (-1024 to +1024)
            
        Returns:
            Dictionary with room data if found, or null data if no static room exists
        """
        if not (-1024 <= x <= 1024) or not (-1024 <= y <= 1024):
            raise TerrainBridgeError("Coordinates must be within -1024 to +1024 range")
        
        return await self._send_request({
            "command": "get_static_room_by_coordinates",
            "x": x,
            "y": y
        })
    
    async def get_wilderness_exits(self) -> Dict[str, Any]:
        """
        Get all wilderness rooms that have exits leading to non-wilderness zones
        
        Returns:
            Dictionary with wilderness rooms that connect to static zones
        """
        return await self._send_request({
            "command": "get_wilderness_exits"
        })
    
    async def health_check(self) -> bool:
        """
        Quick health check - returns True if terrain bridge is accessible
        
        Returns:
            True if terrain bridge responds to ping, False otherwise
        """
        try:
            await self.ping()
            return True
        except TerrainBridgeError:
            return False


# Global terrain bridge client instance
_terrain_client: Optional[TerrainBridgeClient] = None


def get_terrain_client() -> TerrainBridgeClient:
    """
    Get the global terrain bridge client instance
    
    Returns:
        TerrainBridgeClient instance
    """
    global _terrain_client
    if _terrain_client is None:
        _terrain_client = TerrainBridgeClient()
    return _terrain_client


async def is_terrain_bridge_available() -> bool:
    """
    Check if the terrain bridge is currently available
    
    Returns:
        True if terrain bridge is accessible, False otherwise
    """
    client = get_terrain_client()
    return await client.health_check()
