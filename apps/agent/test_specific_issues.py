#!/usr/bin/env python3
"""
Test specific MCP issues to understand the errors
"""

import os
import json
import httpx
import asyncio
from rich.console import Console
from rich.json import JSON
from dotenv import load_dotenv

load_dotenv()
console = Console()

BASE_URL = os.getenv("MCP_BASE_URL", "http://luminarimud.com:8001")
API_KEY = os.getenv("MCP_API_KEY")

async def test_find_wilderness_room_variations():
    """Test different coordinates for find_wilderness_room"""
    console.print("[bold cyan]Testing find_wilderness_room with different coordinates[/bold cyan]\n")
    
    test_coords = [
        (0, 0),      # Origin
        (5, 67),     # Known zone entrance from the data
        (-57, 89),   # Another known zone entrance
        (100, 100),  # Original test coordinate
    ]
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for x, y in test_coords:
            console.print(f"\n[yellow]Testing coordinates ({x}, {y})[/yellow]")
            try:
                response = await client.post(
                    f"{BASE_URL}/mcp/tools/find_wilderness_room",
                    headers=headers,
                    json={"x": x, "y": y}
                )
                
                data = response.json()
                if "result" in data:
                    result = data["result"]
                    if "error" in result:
                        console.print(f"[red]Error:[/red] {result['error'][:100]}...")
                    else:
                        console.print(f"[green]Success![/green] Found room data")
                        if "vnum" in result:
                            console.print(f"  VNUM: {result['vnum']}")
                        if "wilderness_room" in result:
                            room = result["wilderness_room"]
                            console.print(f"  Room VNUM: {room.get('vnum')}")
                            console.print(f"  Name: {room.get('name', 'N/A')}")
                else:
                    console.print(f"[red]Unexpected response format[/red]")
                    
            except Exception as e:
                console.print(f"[red]Exception: {e}[/red]")

async def test_generate_wilderness_map_variations():
    """Test different parameters for generate_wilderness_map"""
    console.print("\n[bold cyan]Testing generate_wilderness_map with different parameters[/bold cyan]\n")
    
    test_params = [
        {"center_x": 0, "center_y": 0, "radius": 5},  # Using radius like complete_terrain_map
        {"center_x": 0, "center_y": 0, "width": 10, "height": 10},  # Original parameters
        {"x": 0, "y": 0, "radius": 5},  # Alternative naming
        {"center_x": 0, "center_y": 0, "size": 10},  # Single size parameter
    ]
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, params in enumerate(test_params, 1):
            console.print(f"\n[yellow]Test {i}: {json.dumps(params)}[/yellow]")
            try:
                response = await client.post(
                    f"{BASE_URL}/mcp/tools/generate_wilderness_map",
                    headers=headers,
                    json=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "result" in data:
                        result = data["result"]
                        if "error" in result:
                            console.print(f"[red]Tool error:[/red] {result['error'][:100]}...")
                        elif "map" in result or "ascii_map" in result or "terrain_map" in result:
                            console.print(f"[green]Success![/green] Map generated")
                            # Show first few lines of map if available
                            if "ascii_map" in result:
                                lines = result["ascii_map"].split('\n')[:3]
                                for line in lines:
                                    console.print(f"  {line[:50]}...")
                        else:
                            console.print(f"[yellow]Response has result but no map data[/yellow]")
                            console.print(f"  Keys: {list(result.keys())}")
                else:
                    console.print(f"[red]HTTP {response.status_code}:[/red] {response.text[:100]}...")
                    
            except Exception as e:
                console.print(f"[red]Exception: {e}[/red]")

async def check_mcp_tool_list():
    """Check if there's a way to list available tools"""
    console.print("\n[bold cyan]Checking for available MCP tools list[/bold cyan]\n")
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Try to get OpenAPI docs if available
        try:
            response = await client.get(f"{BASE_URL}/openapi.json")
            if response.status_code == 200:
                console.print("[green]Found OpenAPI spec![/green]")
                spec = response.json()
                if "paths" in spec:
                    mcp_paths = [p for p in spec["paths"] if "/mcp/tools/" in p]
                    console.print(f"Available MCP tool endpoints: {len(mcp_paths)}")
                    for path in mcp_paths[:5]:  # Show first 5
                        tool_name = path.replace("/mcp/tools/", "")
                        console.print(f"  - {tool_name}")
        except:
            console.print("[yellow]OpenAPI spec not available[/yellow]")

async def main():
    await test_find_wilderness_room_variations()
    await test_generate_wilderness_map_variations()
    await check_mcp_tool_list()

if __name__ == "__main__":
    asyncio.run(main())