#!/usr/bin/env python3
"""
Test the backend API directly to understand the 422 error
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

# Test both the backend directly and through MCP
BACKEND_URL = "http://luminarimud.com:8000"
API_KEY = os.getenv("MCP_API_KEY")

async def test_backend_wilderness_endpoints():
    """Test backend wilderness endpoints directly"""
    console.print("[bold cyan]Testing Backend Wilderness Endpoints Directly[/bold cyan]\n")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "X-API-Key": API_KEY,  # Try both
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Check if the endpoint exists
        console.print("[yellow]Test 1: Checking wilderness/rooms endpoints[/yellow]")
        try:
            # Try the base wilderness endpoint
            response = await client.get(
                f"{BACKEND_URL}/api/wilderness/rooms",
                headers=headers
            )
            console.print(f"GET /api/wilderness/rooms: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                console.print(f"  Found {len(data) if isinstance(data, list) else 'data'}")
        except Exception as e:
            console.print(f"  Error: {e}")
        
        # Test 2: Try different URL patterns for at-coordinates
        console.print("\n[yellow]Test 2: Testing coordinate-based room lookup[/yellow]")
        test_urls = [
            (f"{BACKEND_URL}/api/wilderness/rooms/at-coordinates?x=0&y=0", "with /api prefix"),
            (f"{BACKEND_URL}/wilderness/rooms/at-coordinates?x=0&y=0", "without /api prefix"),
            (f"{BACKEND_URL}/api/wilderness/room?x=0&y=0", "singular 'room'"),
            (f"{BACKEND_URL}/api/wilderness/at-coordinates?x=0&y=0", "simplified path"),
        ]
        
        for url, description in test_urls:
            try:
                console.print(f"\n  Testing: {description}")
                console.print(f"  URL: {url}")
                response = await client.get(url, headers=headers)
                console.print(f"  Status: {response.status_code}")
                if response.status_code == 200:
                    console.print(f"  [green]SUCCESS![/green]")
                    data = response.json()
                    console.print(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else 'list'}")
                elif response.status_code == 422:
                    console.print(f"  [red]422 Error:[/red] {response.text[:100]}")
                elif response.status_code == 404:
                    console.print(f"  [yellow]404: Endpoint not found[/yellow]")
                else:
                    console.print(f"  [red]Error:[/red] {response.text[:100]}")
            except Exception as e:
                console.print(f"  [red]Exception:[/red] {str(e)[:100]}")
        
        # Test 3: Check OpenAPI spec for correct endpoint
        console.print("\n[yellow]Test 3: Checking OpenAPI spec for correct endpoints[/yellow]")
        try:
            response = await client.get(f"{BACKEND_URL}/openapi.json")
            if response.status_code == 200:
                spec = response.json()
                wilderness_paths = [p for p in spec.get("paths", {}) if "wilderness" in p.lower()]
                console.print(f"Found {len(wilderness_paths)} wilderness endpoints:")
                for path in wilderness_paths[:10]:  # Show first 10
                    methods = list(spec["paths"][path].keys())
                    console.print(f"  {path} [{', '.join(methods)}]")
            else:
                console.print(f"  OpenAPI spec not available: {response.status_code}")
        except Exception as e:
            console.print(f"  Error fetching OpenAPI: {e}")
        
        # Test 4: Try terrain bridge endpoint which we know works
        console.print("\n[yellow]Test 4: Testing working terrain endpoint for comparison[/yellow]")
        try:
            response = await client.get(
                f"{BACKEND_URL}/api/terrain?x=0&y=0",
                headers=headers
            )
            console.print(f"GET /api/terrain?x=0&y=0: {response.status_code}")
            if response.status_code == 200:
                console.print("  [green]Terrain endpoint works![/green]")
        except Exception as e:
            console.print(f"  Error: {e}")

async def main():
    await test_backend_wilderness_endpoints()

if __name__ == "__main__":
    asyncio.run(main())