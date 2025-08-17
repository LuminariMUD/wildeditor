#!/usr/bin/env python3
"""
MCP Debug Tool - Detailed debugging of MCP server responses
"""

import os
import json
import httpx
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from dotenv import load_dotenv

load_dotenv()
console = Console()

BASE_URL = os.getenv("MCP_BASE_URL", "http://luminarimud.com:8001")
API_KEY = os.getenv("MCP_API_KEY")

async def debug_mcp_tool(tool_name: str, parameters: dict):
    """Debug a specific MCP tool call"""
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    console.print(Panel.fit(
        f"[bold cyan]Testing Tool: {tool_name}[/bold cyan]\n"
        f"Parameters: {json.dumps(parameters, indent=2)}",
        title="Request"
    ))
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/mcp/tools/{tool_name}",
                headers=headers,
                json=parameters
            )
            
            console.print(f"\n[bold]Status Code:[/bold] {response.status_code}")
            console.print(f"[bold]Headers:[/bold]")
            for key, value in response.headers.items():
                console.print(f"  {key}: {value}")
            
            console.print(f"\n[bold]Response Body:[/bold]")
            
            try:
                data = response.json()
                console.print(JSON(json.dumps(data)))
                
                # Analyze response structure
                console.print(f"\n[bold]Response Analysis:[/bold]")
                console.print(f"Type: {type(data)}")
                if isinstance(data, dict):
                    console.print(f"Keys: {list(data.keys())}")
                    for key, value in data.items():
                        if isinstance(value, (list, dict)):
                            console.print(f"  {key}: {type(value).__name__} with {len(value)} items")
                        else:
                            console.print(f"  {key}: {type(value).__name__}")
                elif isinstance(data, list):
                    console.print(f"List with {len(data)} items")
                    if data:
                        console.print(f"First item type: {type(data[0])}")
                        if isinstance(data[0], dict):
                            console.print(f"First item keys: {list(data[0].keys())}")
                
            except json.JSONDecodeError:
                console.print(f"[red]Raw text response:[/red] {response.text}")
                
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

async def main():
    """Test each MCP tool with debug output"""
    
    tests = [
        ("analyze_terrain_at_coordinates", {"x": 0, "y": 0}),
        ("analyze_complete_terrain_map", {"center_x": 0, "center_y": 0, "radius": 3}),
        ("find_wilderness_room", {"x": 100, "y": 100}),
        ("find_zone_entrances", {}),
        # Skip generate_wilderness_map for now as it has parameter issues
    ]
    
    for tool_name, params in tests:
        await debug_mcp_tool(tool_name, params)
        console.print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())