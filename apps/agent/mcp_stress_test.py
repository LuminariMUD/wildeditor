#!/usr/bin/env python3
"""
MCP Stress Test - Performance and load testing for MCP server
"""

import os
import sys
import json
import time
import asyncio
import statistics
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime

import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TimeRemainingColumn, TextColumn
from rich.live import Live
from rich.layout import Layout
from rich import print as rprint
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

console = Console()


@dataclass
class PerformanceMetrics:
    """Performance metrics for a test run"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: float = 0
    
    @property
    def duration(self) -> float:
        return (self.end_time or time.time()) - self.start_time
    
    @property
    def requests_per_second(self) -> float:
        if self.duration == 0:
            return 0
        return self.total_requests / self.duration
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def avg_response_time(self) -> float:
        if not self.response_times:
            return 0
        return statistics.mean(self.response_times)
    
    @property
    def median_response_time(self) -> float:
        if not self.response_times:
            return 0
        return statistics.median(self.response_times)
    
    @property
    def p95_response_time(self) -> float:
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[min(index, len(sorted_times) - 1)]
    
    @property
    def p99_response_time(self) -> float:
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.99)
        return sorted_times[min(index, len(sorted_times) - 1)]


class MCPStressTest:
    """Stress testing for MCP server"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or os.getenv("MCP_BASE_URL", "http://localhost:8001")
        self.api_key = api_key or os.getenv("MCP_API_KEY", "test-api-key")
        self.metrics = PerformanceMetrics()
        
    async def call_mcp_tool(self, client: httpx.AsyncClient, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, float, Any]:
        """Call an MCP tool and return success status, response time, and result"""
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        start_time = time.time()
        try:
            response = await client.post(
                f"{self.base_url}/mcp/tools/{tool_name}",
                headers=headers,
                json=parameters,
                timeout=10.0
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return True, response_time, response.json()
            else:
                return False, response_time, f"HTTP {response.status_code}"
        except Exception as e:
            response_time = time.time() - start_time
            return False, response_time, str(e)
    
    async def terrain_analysis_worker(self, client: httpx.AsyncClient, num_requests: int, worker_id: int):
        """Worker for terrain analysis stress test"""
        for i in range(num_requests):
            # Generate random coordinates
            x = (i * 17 + worker_id * 31) % 2048 - 1024
            y = (i * 23 + worker_id * 37) % 2048 - 1024
            
            success, response_time, result = await self.call_mcp_tool(
                client,
                "analyze_terrain_at_coordinates",
                {"x": x, "y": y}
            )
            
            self.metrics.total_requests += 1
            self.metrics.response_times.append(response_time)
            
            if success:
                self.metrics.successful_requests += 1
            else:
                self.metrics.failed_requests += 1
                if len(self.metrics.errors) < 10:  # Keep first 10 errors
                    self.metrics.errors.append(f"Worker {worker_id}: {result}")
    
    async def mixed_workload_worker(self, client: httpx.AsyncClient, num_requests: int, worker_id: int):
        """Worker for mixed workload stress test"""
        tools = [
            ("analyze_terrain_at_coordinates", lambda i: {"x": i % 200 - 100, "y": i % 200 - 100}),
            ("find_wilderness_room", lambda i: {"x": i % 500, "y": i % 500}),
            ("analyze_complete_terrain_map", lambda i: {"center_x": 0, "center_y": 0, "radius": 3}),
            ("find_zone_entrances", lambda i: {}),
        ]
        
        for i in range(num_requests):
            tool_name, param_func = tools[i % len(tools)]
            
            success, response_time, result = await self.call_mcp_tool(
                client,
                tool_name,
                param_func(i)
            )
            
            self.metrics.total_requests += 1
            self.metrics.response_times.append(response_time)
            
            if success:
                self.metrics.successful_requests += 1
            else:
                self.metrics.failed_requests += 1
                if len(self.metrics.errors) < 10:
                    self.metrics.errors.append(f"Worker {worker_id} ({tool_name}): {result}")
    
    async def run_stress_test(self, test_type: str, duration: int, concurrency: int):
        """Run stress test with specified parameters"""
        self.metrics = PerformanceMetrics()
        
        console.print(Panel.fit(
            f"[bold cyan]MCP Stress Test[/bold cyan]\n"
            f"Server: {self.base_url}\n"
            f"Test Type: {test_type}\n"
            f"Duration: {duration}s\n"
            f"Concurrency: {concurrency} workers",
            title="Starting Stress Test"
        ))
        
        # Determine requests per worker
        target_rps = 10 * concurrency  # Aim for 10 requests per second per worker
        requests_per_worker = (duration * target_rps) // concurrency
        
        # Select worker function
        if test_type == "terrain":
            worker_func = self.terrain_analysis_worker
        elif test_type == "mixed":
            worker_func = self.mixed_workload_worker
        else:
            raise ValueError(f"Unknown test type: {test_type}")
        
        # Create progress bar
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task(
                f"Running {concurrency} workers...",
                total=concurrency * requests_per_worker
            )
            
            # Create HTTP clients and workers
            async with httpx.AsyncClient(timeout=30.0) as client:
                workers = []
                for i in range(concurrency):
                    worker = asyncio.create_task(
                        worker_func(client, requests_per_worker, i)
                    )
                    workers.append(worker)
                
                # Monitor progress
                last_count = 0
                while not all(w.done() for w in workers):
                    await asyncio.sleep(0.5)
                    current_count = self.metrics.total_requests
                    progress.update(task, completed=current_count)
                    last_count = current_count
                
                # Wait for all workers to complete
                await asyncio.gather(*workers)
                progress.update(task, completed=concurrency * requests_per_worker)
        
        self.metrics.end_time = time.time()
        return self.metrics
    
    def print_results(self, metrics: PerformanceMetrics):
        """Print stress test results"""
        
        # Main metrics table
        table = Table(title="Performance Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold yellow")
        
        table.add_row("Total Requests", str(metrics.total_requests))
        table.add_row("Successful", f"{metrics.successful_requests} ({metrics.success_rate:.1f}%)")
        table.add_row("Failed", str(metrics.failed_requests))
        table.add_row("Duration", f"{metrics.duration:.2f}s")
        table.add_row("Requests/sec", f"{metrics.requests_per_second:.2f}")
        
        console.print(table)
        
        # Response time statistics
        if metrics.response_times:
            rt_table = Table(title="Response Time Statistics (seconds)")
            rt_table.add_column("Percentile", style="cyan")
            rt_table.add_column("Time", style="bold yellow")
            
            rt_table.add_row("Min", f"{min(metrics.response_times):.3f}")
            rt_table.add_row("Median (P50)", f"{metrics.median_response_time:.3f}")
            rt_table.add_row("Average", f"{metrics.avg_response_time:.3f}")
            rt_table.add_row("P95", f"{metrics.p95_response_time:.3f}")
            rt_table.add_row("P99", f"{metrics.p99_response_time:.3f}")
            rt_table.add_row("Max", f"{max(metrics.response_times):.3f}")
            
            console.print(rt_table)
        
        # Errors if any
        if metrics.errors:
            console.print(Panel.fit(
                "\n".join(metrics.errors[:5]),
                title=f"[red]Sample Errors (showing {min(5, len(metrics.errors))} of {len(metrics.errors)})[/red]"
            ))
        
        # Summary
        status_color = "green" if metrics.success_rate > 95 else "yellow" if metrics.success_rate > 80 else "red"
        console.print(Panel.fit(
            f"[{status_color}]Success Rate: {metrics.success_rate:.1f}%[/{status_color}]\n"
            f"Throughput: {metrics.requests_per_second:.1f} req/s\n"
            f"P95 Response Time: {metrics.p95_response_time:.3f}s",
            title="Summary"
        ))


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Stress Test")
    parser.add_argument("--url", default=None, help="MCP server URL")
    parser.add_argument("--api-key", default=None, help="API key for authentication")
    parser.add_argument("--production", action="store_true", help="Test production server")
    parser.add_argument("--type", choices=["terrain", "mixed"], default="mixed", help="Test type")
    parser.add_argument("--duration", type=int, default=30, help="Test duration in seconds")
    parser.add_argument("--concurrency", type=int, default=10, help="Number of concurrent workers")
    
    args = parser.parse_args()
    
    # Determine server URL
    if args.production:
        base_url = "http://luminarimud.com:8001"
    else:
        base_url = args.url or os.getenv("MCP_BASE_URL", "http://localhost:8001")
    
    tester = MCPStressTest(base_url=base_url, api_key=args.api_key)
    
    try:
        metrics = await tester.run_stress_test(
            test_type=args.type,
            duration=args.duration,
            concurrency=args.concurrency
        )
        tester.print_results(metrics)
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
        if tester.metrics.total_requests > 0:
            tester.metrics.end_time = time.time()
            tester.print_results(tester.metrics)
    except Exception as e:
        console.print(f"\n[red]Error running stress test: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())