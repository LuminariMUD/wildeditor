# MCP Test Agent - TODO & Status

## Current Status (August 17, 2025)

###  Completed
- Created comprehensive MCP test agent (`mcp_test_agent.py`)
- Created stress testing tool (`mcp_stress_test.py`) 
- Created debugging utilities (`mcp_debug.py`, `test_specific_issues.py`)
- Set up environment configuration with production MCP server
- Fixed test parameter issues (Generate Wilderness Map now uses `radius` correctly)
- Successfully connected to production MCP server at `luminarimud.com:8001`

### =Ê Test Results Summary

**5 out of 6 tests passing (83% functional)**

| Test | Status | Details |
|------|--------|---------|
| Health Check |  PASSED | Server online and healthy |
| Terrain Analysis |  PASSED | Returns terrain data correctly |
| Complete Terrain Map |  PASSED | Returns 81 terrain points with overlays |
| Find Zone Entrances |  PASSED | Found 116 zone entrances |
| Generate Wilderness Map |  PASSED | Works with `radius` parameter |
| Find Wilderness Room | L FAILED | Server configuration issue |

### =' Known Issues

#### 1. Find Wilderness Room - Server Configuration Issue
- **Problem**: MCP server returns 422 error when trying to find wilderness rooms
- **Root Cause**: MCP server on production doesn't have the correct `WILDEDITOR_API_KEY` to authenticate with the backend
- **Evidence**: Backend returns "Invalid API key" when MCP server tries to call `/api/wilderness/rooms/at-coordinates`
- **Fix Required**: Update environment variable on production server:
  - The MCP server needs `WILDEDITOR_API_KEY` set to match what the backend expects
  - This is NOT the MCP API key we use to call the MCP server
  - It's the backend's API key that MCP uses internally
- **Workaround**: None available from client side

### =€ Performance Metrics

Stress test results (10 workers, terrain analysis):
- **Success Rate**: 100%
- **Throughput**: 8.5 requests/second
- **P95 Response Time**: 0.685 seconds
- **Average Response Time**: 0.571 seconds

### =Ý Next Steps

1. **Server-side fix needed**: 
   - SSH into production server
   - Update MCP server's `WILDEDITOR_API_KEY` environment variable
   - Restart MCP server container
   - Verify `find_wilderness_room` works

2. **Optional enhancements**:
   - Add automated monitoring/alerting
   - Create CI/CD integration tests
   - Add more comprehensive error handling
   - Create dashboard for monitoring MCP health

### = Configuration

Current `.env` configuration:
```
MCP_BASE_URL=http://luminarimud.com:8001
MCP_API_KEY=xJO/3aCmd5SBx0xxyPwvVOSSFkCR6BYVVl+RH+PMww0=
BACKEND_BASE_URL=http://luminarimud.com:8000
```

### =Ú Usage

```bash
# Run functional tests
cd apps/agent
source venv/bin/activate
python mcp_test_agent.py

# Run stress tests
python mcp_stress_test.py --duration 30 --concurrency 10

# Debug specific issues
python mcp_debug.py
python test_specific_issues.py
```

### <× Architecture Notes

The MCP server uses a two-key authentication system:
1. **MCP Key** (`mcp_key`): What AI agents use to authenticate with MCP server (we have this)
2. **Backend API Key** (`api_key`): What MCP server uses to authenticate with backend (missing/incorrect on production)

The failing test is due to #2 being misconfigured on the production server.