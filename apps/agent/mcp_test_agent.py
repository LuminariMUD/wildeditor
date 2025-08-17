#!/usr/bin/env python3
"""
MCP Test Agent - Simple agent to test MCP server functionality
"""

import os
import sys
import json
import time
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

console = Console()


class TestStatus(Enum):
    PASSED = "✅ PASSED"
    FAILED = "❌ FAILED"
    SKIPPED = "⏭️ SKIPPED"
    RUNNING = "🔄 RUNNING"


@dataclass
class TestResult:
    name: str
    status: TestStatus
    response_time: float
    details: Optional[str] = None
    error: Optional[str] = None


class MCPTestAgent:
    """Agent for testing MCP server functionality"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or os.getenv("MCP_BASE_URL", "http://localhost:8001")
        self.api_key = api_key or os.getenv("MCP_API_KEY", "test-api-key")
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results: List[TestResult] = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
        
    async def test_health(self) -> TestResult:
        """Test server health endpoint"""
        start_time = time.time()
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return TestResult(
                    name="Health Check",
                    status=TestStatus.PASSED,
                    response_time=response_time,
                    details=f"Server healthy: {data.get('status', 'unknown')}"
                )
            else:
                return TestResult(
                    name="Health Check",
                    status=TestStatus.FAILED,
                    response_time=response_time,
                    error=f"HTTP {response.status_code}"
                )
        except Exception as e:
            return TestResult(
                name="Health Check",
                status=TestStatus.FAILED,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def call_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool with parameters"""
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        response = await self.client.post(
            f"{self.base_url}/mcp/tools/{tool_name}",
            headers=headers,
            json=parameters
        )
        
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
            
        return response.json()
    
    async def test_terrain_analysis(self) -> TestResult:
        """Test terrain analysis at coordinates"""
        start_time = time.time()
        try:
            result = await self.call_mcp_tool(
                "analyze_terrain_at_coordinates",
                {"x": 0, "y": 0}
            )
            response_time = time.time() - start_time
            
            # Handle wrapped response format
            if "result" in result:
                terrain_data = result["result"]
                if "terrain" in terrain_data:
                    sector = terrain_data["terrain"].get("sector_name", "unknown")
                    return TestResult(
                        name="Terrain Analysis",
                        status=TestStatus.PASSED,
                        response_time=response_time,
                        details=f"Analyzed terrain at (0, 0): {sector}"
                    )
            
            return TestResult(
                name="Terrain Analysis",
                status=TestStatus.FAILED,
                response_time=response_time,
                error="Invalid response format"
            )
        except Exception as e:
            return TestResult(
                name="Terrain Analysis",
                status=TestStatus.FAILED,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def test_complete_terrain_map(self) -> TestResult:
        """Test enhanced terrain analysis with overlays"""
        start_time = time.time()
        try:
            result = await self.call_mcp_tool(
                "analyze_complete_terrain_map",
                {"center_x": 0, "center_y": 0, "radius": 5}
            )
            response_time = time.time() - start_time
            
            # Handle wrapped response format
            if "result" in result:
                map_data = result["result"]
                details = []
                if "map_data" in map_data:
                    details.append(f"Terrain points: {len(map_data.get('map_data', {}))}")
                if "regions_affecting_area" in map_data:
                    details.append(f"Regions: {len(map_data.get('regions_affecting_area', []))}")
                if "paths_affecting_area" in map_data:
                    details.append(f"Paths: {len(map_data.get('paths_affecting_area', []))}")
                    
                if details:
                    return TestResult(
                        name="Complete Terrain Map",
                        status=TestStatus.PASSED,
                        response_time=response_time,
                        details=", ".join(details)
                    )
            
            return TestResult(
                name="Complete Terrain Map",
                status=TestStatus.FAILED,
                response_time=response_time,
                error="Invalid response format"
            )
        except Exception as e:
            return TestResult(
                name="Complete Terrain Map",
                status=TestStatus.FAILED,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def test_find_wilderness_room(self) -> TestResult:
        """Test finding wilderness room by coordinates"""
        start_time = time.time()
        try:
            # Use coordinates that exist
            result = await self.call_mcp_tool(
                "find_wilderness_room",
                {"x": 0, "y": 0}
            )
            response_time = time.time() - start_time
            
            # Handle wrapped response format
            if "result" in result:
                room_data = result["result"]
                if "error" in room_data:
                    return TestResult(
                        name="Find Wilderness Room",
                        status=TestStatus.FAILED,
                        response_time=response_time,
                        error=room_data["error"][:50] + "..."
                    )
                elif "vnum" in room_data or "room" in room_data:
                    vnum = room_data.get("vnum", room_data.get("room", {}).get("vnum", "unknown"))
                    return TestResult(
                        name="Find Wilderness Room",
                        status=TestStatus.PASSED,
                        response_time=response_time,
                        details=f"Found room at coordinates: VNUM {vnum}"
                    )
            
            return TestResult(
                name="Find Wilderness Room",
                status=TestStatus.FAILED,
                response_time=response_time,
                error="Invalid response format"
            )
        except Exception as e:
            return TestResult(
                name="Find Wilderness Room",
                status=TestStatus.FAILED,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def test_find_zone_entrances(self) -> TestResult:
        """Test finding zone entrances from wilderness"""
        start_time = time.time()
        try:
            result = await self.call_mcp_tool(
                "find_zone_entrances",
                {}
            )
            response_time = time.time() - start_time
            
            # Handle wrapped response format
            if "result" in result:
                entrance_data = result["result"]
                if "entrances" in entrance_data:
                    count = len(entrance_data["entrances"])
                    return TestResult(
                        name="Find Zone Entrances",
                        status=TestStatus.PASSED,
                        response_time=response_time,
                        details=f"Found {count} zone entrances"
                    )
                elif "entrance_count" in entrance_data:
                    count = entrance_data["entrance_count"]
                    return TestResult(
                        name="Find Zone Entrances",
                        status=TestStatus.PASSED,
                        response_time=response_time,
                        details=f"Found {count} zone entrances"
                    )
            
            return TestResult(
                name="Find Zone Entrances",
                status=TestStatus.FAILED,
                response_time=response_time,
                error="Invalid response format"
            )
        except Exception as e:
            return TestResult(
                name="Find Zone Entrances",
                status=TestStatus.FAILED,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def test_generate_wilderness_map(self) -> TestResult:
        """Test wilderness map generation"""
        start_time = time.time()
        try:
            # Use correct parameter names
            result = await self.call_mcp_tool(
                "generate_wilderness_map",
                {"center_x": 0, "center_y": 0, "radius": 5}
            )
            response_time = time.time() - start_time
            
            # Handle wrapped response format
            if "result" in result:
                map_result = result["result"]
                if "error" in map_result:
                    return TestResult(
                        name="Generate Wilderness Map",
                        status=TestStatus.FAILED,
                        response_time=response_time,
                        error=map_result["error"][:50] + "..."
                    )
                elif "map" in map_result or "ascii_map" in map_result or "terrain_map" in map_result or "map_data" in map_result:
                    return TestResult(
                        name="Generate Wilderness Map",
                        status=TestStatus.PASSED,
                        response_time=response_time,
                        details="Map generated successfully"
                    )
            
            return TestResult(
                name="Generate Wilderness Map",
                status=TestStatus.FAILED,
                response_time=response_time,
                error="Invalid response format"
            )
        except Exception as e:
            return TestResult(
                name="Generate Wilderness Map",
                status=TestStatus.FAILED,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def run_all_tests(self) -> List[TestResult]:
        """Run all MCP tests"""
        tests = [
            ("Health Check", self.test_health),
            ("Terrain Analysis", self.test_terrain_analysis),
            ("Complete Terrain Map", self.test_complete_terrain_map),
            ("Find Wilderness Room", self.test_find_wilderness_room),
            ("Find Zone Entrances", self.test_find_zone_entrances),
            ("Generate Wilderness Map", self.test_generate_wilderness_map),
        ]
        
        console.print(Panel.fit(
            f"[bold cyan]MCP Test Agent[/bold cyan]\n"
            f"Testing server at: {self.base_url}",
            title="Starting Tests"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            for test_name, test_func in tests:
                task = progress.add_task(f"Running {test_name}...", total=None)
                result = await test_func()
                self.results.append(result)
                progress.update(task, completed=True)
        
        return self.results
    
    def print_results(self):
        """Print test results in a formatted table"""
        table = Table(title="MCP Test Results")
        table.add_column("Test", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Response Time", style="yellow")
        table.add_column("Details", style="white")
        
        for result in self.results:
            status_color = "green" if result.status == TestStatus.PASSED else "red"
            status_text = f"[{status_color}]{result.status.value}[/{status_color}]"
            
            details = result.details if result.details else ""
            if result.error:
                details = f"[red]{result.error}[/red]"
            
            table.add_row(
                result.name,
                status_text,
                f"{result.response_time:.3f}s",
                details
            )
        
        console.print(table)
        
        # Summary
        passed = sum(1 for r in self.results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        total = len(self.results)
        
        summary_color = "green" if failed == 0 else "red" if passed == 0 else "yellow"
        console.print(Panel.fit(
            f"[{summary_color}]Tests Passed: {passed}/{total}[/{summary_color}]\n"
            f"Average Response Time: {sum(r.response_time for r in self.results)/total:.3f}s",
            title="Summary"
        ))


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Test Agent")
    parser.add_argument("--url", default=None, help="MCP server URL")
    parser.add_argument("--api-key", default=None, help="API key for authentication")
    parser.add_argument("--production", action="store_true", help="Test production server")
    
    args = parser.parse_args()
    
    # Determine server URL
    if args.production:
        base_url = "http://luminarimud.com:8001"
    else:
        base_url = args.url or os.getenv("MCP_BASE_URL", "http://localhost:8001")
    
    async with MCPTestAgent(base_url=base_url, api_key=args.api_key) as agent:
        try:
            await agent.run_all_tests()
            agent.print_results()
        except KeyboardInterrupt:
            console.print("\n[yellow]Tests interrupted by user[/yellow]")
        except Exception as e:
            console.print(f"\n[red]Error running tests: {e}[/red]")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())