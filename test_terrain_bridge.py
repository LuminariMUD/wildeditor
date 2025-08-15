#!/usr/bin/env python3
"""Quick test of terrain bridge connectivity"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'apps', 'backend', 'src'))

from services.terrain_bridge import TerrainBridgeClient

async def test_terrain_bridge():
    """Test terrain bridge connectivity"""
    client = TerrainBridgeClient()
    
    try:
        # Test ping
        print("Testing terrain bridge ping...")
        ping_result = await client.ping()
        print(f"Ping result: {ping_result}")
        
        # Test terrain query
        print("\nTesting terrain at coordinates (0, 0)...")
        terrain_result = await client.get_terrain_at_coordinates(0, 0)
        print(f"Terrain result: {terrain_result}")
        
        # Test room query
        print("\nTesting room at coordinates (0, 0)...")
        room_result = await client.get_room_at_coordinates(0, 0)
        print(f"Room result: {room_result}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_terrain_bridge())
