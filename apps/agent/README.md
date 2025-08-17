# MCP Test Agent

A comprehensive testing suite for the Model Context Protocol (MCP) server, providing functional testing, stress testing, and performance monitoring capabilities.

## Features

- **Functional Testing**: Validates all MCP tools and endpoints
- **Stress Testing**: Performance and load testing with configurable concurrency
- **Rich Terminal Output**: Beautiful, informative test results using Rich library
- **Multiple Test Modes**: Terrain-focused or mixed workload testing
- **Detailed Metrics**: Response times, success rates, percentile analysis

## Installation

```bash
# Navigate to agent directory
cd apps/agent

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
```

## Configuration

Edit `.env` file with your settings:

```bash
# MCP Server Configuration
MCP_BASE_URL=http://localhost:8001  # Local development
# MCP_BASE_URL=http://luminarimud.com:8001  # Production

# Authentication
MCP_API_KEY=your-api-key-here
```

## Usage

### Basic Functional Testing

Test all MCP endpoints with detailed results:

```bash
# Test local development server
python mcp_test_agent.py

# Test production server
python mcp_test_agent.py --production

# Test custom server
python mcp_test_agent.py --url http://your-server:8001 --api-key your-key
```

### Stress Testing

Run performance and load tests:

```bash
# Basic stress test (30 seconds, 10 concurrent workers)
python mcp_stress_test.py

# High-load test
python mcp_stress_test.py --duration 60 --concurrency 50

# Terrain-focused stress test
python mcp_stress_test.py --type terrain --duration 30 --concurrency 20

# Mixed workload stress test
python mcp_stress_test.py --type mixed --duration 45 --concurrency 30

# Test production server under load
python mcp_stress_test.py --production --duration 30 --concurrency 10
```

## Test Suites

### Functional Tests (`mcp_test_agent.py`)

Tests the following MCP tools:
- **Health Check**: Server availability and status
- **Terrain Analysis**: Get terrain data at specific coordinates
- **Complete Terrain Map**: Enhanced analysis with region/path overlays
- **Find Wilderness Room**: Locate rooms by coordinates
- **Find Zone Entrances**: Discover wilderness-to-zone connections
- **Generate Wilderness Map**: Create terrain maps for areas

### Stress Tests (`mcp_stress_test.py`)

Two workload types:
- **Terrain**: Focused testing of terrain analysis endpoints
- **Mixed**: Balanced testing of all MCP tools

Provides metrics:
- Total requests and success rate
- Requests per second (throughput)
- Response time percentiles (P50, P95, P99)
- Error sampling and analysis

## Example Output

### Functional Test Results
```
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Test                 ┃ Status     ┃ Response Time┃ Details                    ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Health Check         │ ✅ PASSED  │ 0.023s       │ Server healthy: online     │
│ Terrain Analysis     │ ✅ PASSED  │ 0.145s       │ Analyzed terrain at (0, 0) │
│ Complete Terrain Map │ ✅ PASSED  │ 0.267s       │ Terrain: 121, Regions: 3   │
│ Find Wilderness Room │ ✅ PASSED  │ 0.089s       │ Found room: VNUM 12345     │
│ Find Zone Entrances  │ ✅ PASSED  │ 0.234s       │ Found 47 zone entrances    │
│ Generate Map         │ ✅ PASSED  │ 0.156s       │ Map generated successfully │
└──────────────────────┴────────────┴──────────────┴────────────────────────────┘

Tests Passed: 6/6
Average Response Time: 0.152s
```

### Stress Test Results
```
Performance Metrics
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ Metric         ┃ Value           ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ Total Requests │ 3000            │
│ Successful     │ 2976 (99.2%)    │
│ Failed         │ 24              │
│ Duration       │ 30.12s          │
│ Requests/sec   │ 99.60           │
└────────────────┴─────────────────┘

Response Time Statistics (seconds)
┏━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Percentile    ┃ Time   ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Min           │ 0.021  │
│ Median (P50)  │ 0.098  │
│ Average       │ 0.101  │
│ P95           │ 0.198  │
│ P99           │ 0.287  │
│ Max           │ 0.512  │
└───────────────┴────────┘
```

## Advanced Usage

### Custom Test Scenarios

Create your own test by extending the base classes:

```python
from mcp_test_agent import MCPTestAgent

async def custom_test():
    async with MCPTestAgent() as agent:
        # Call specific MCP tool
        result = await agent.call_mcp_tool(
            "analyze_terrain_at_coordinates",
            {"x": 100, "y": 200}
        )
        print(f"Terrain at (100, 200): {result}")
```

### Continuous Monitoring

Run periodic health checks:

```bash
# Run tests every 5 minutes
while true; do
    python mcp_test_agent.py
    sleep 300
done
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/test-mcp.yml
- name: Test MCP Server
  run: |
    cd apps/agent
    pip install -r requirements.txt
    python mcp_test_agent.py --url ${{ secrets.MCP_URL }} --api-key ${{ secrets.MCP_API_KEY }}
```

## Troubleshooting

### Connection Errors
- Verify server is running: `curl http://localhost:8001/health`
- Check firewall settings for port 8001
- Ensure API key is correct in `.env`

### Timeout Errors
- Increase timeout in stress test for slower servers
- Reduce concurrency if server is resource-constrained
- Check server logs for performance bottlenecks

### Authentication Failures
- Verify API key matches backend configuration
- Check `X-API-Key` header is being sent
- Ensure backend authentication is enabled

## Development

### Adding New Tests

1. Add test method to `MCPTestAgent` class:
```python
async def test_new_feature(self) -> TestResult:
    # Implementation
```

2. Add to test suite in `run_all_tests()`:
```python
tests = [
    # ... existing tests
    ("New Feature", self.test_new_feature),
]
```

### Customizing Output

Modify Rich console themes and styles in the agent files to customize the terminal output appearance.

## License

Part of the Wildeditor project. See main project LICENSE for details.