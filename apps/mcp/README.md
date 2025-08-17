# MCP Server

AI-powered Model Context Protocol server for Wildeditor Wilderness Management.

## 🎯 Overview

The MCP server provides AI agents with comprehensive wilderness management capabilities through:

- **Real-time Terrain Analysis**: Get current terrain data at any wilderness coordinates
- **Enhanced Terrain Mapping**: Complete terrain analysis including region and path overlays
- **Wilderness Room Discovery**: Find and analyze wilderness rooms by coordinates or VNUM
- **Zone Connection Discovery**: Find all wilderness entrances that connect to static zones
- **Wilderness Map Generation**: Create detailed terrain maps for specific areas
- **Spatial Navigation**: Navigate and understand wilderness geography

## 🏗️ Architecture

```
MCP Server (Port 8001)
├── FastAPI Application
├── MCP Protocol Implementation
│   ├── Tools (Terrain, Wilderness, Navigation)
│   ├── Terrain Bridge Integration
│   └── Backend API Integration  
├── Authentication (API Key)
└── Docker Deployment
```

## 🛠️ Available MCP Tools

### Core Terrain Tools
- **`analyze_terrain_at_coordinates`** - Get real-time terrain data at specific coordinates
- **`analyze_complete_terrain_map`** - Enhanced terrain analysis with region/path overlays
- **`generate_wilderness_map`** - Generate detailed terrain maps for areas

### Wilderness Room Tools  
- **`find_static_wilderness_room`** - Find static wilderness rooms by coordinates or VNUM
- **`find_zone_entrances`** - Discover all wilderness→zone connections

### Legacy Region Tools (Planning)
- **`analyze_region`** - Analyze wilderness regions by ID
- **`find_path`** - Find paths between regions
- **`search_regions`** - Search regions by criteria
- **`create_region`** - Create new wilderness regions
- **`validate_connections`** - Validate region connections

## 🚀 Quick Start

### Development Setup
```bash
# Install dependencies
cd apps/mcp
pip install -r requirements.txt

# Set environment variables
export BACKEND_BASE_URL="http://localhost:8000"
export API_KEY="your-backend-api-key"

# Run development server
python run_dev.py
```

### Production Deployment
```bash
# Deploy with GitHub Actions (automatic)
git push origin main

# Manual deployment
docker build -t wildeditor-mcp .
docker run -d --name wildeditor-mcp --network host \
  -e BACKEND_BASE_URL="http://localhost:8000" \
  -e API_KEY="your-api-key" \
  wildeditor-mcp

# Health check
curl http://localhost:8001/health
```

## 📊 Current Implementation Status

### ✅ **Implemented & Working**
- **MCP Server Framework**: FastAPI-based MCP protocol server
- **Terrain Analysis Tools**: Real-time terrain data from game engine
- **Enhanced Terrain Analysis**: Region/path overlays with spatial queries
- **Wilderness Room Tools**: Room discovery and details
- **Zone Entrance Discovery**: Complete wilderness→zone connection mapping
- **Authentication**: API key-based security
- **Docker Deployment**: Production-ready containerization
- **GitHub Actions**: Automated deployment pipeline

### 🔄 **In Development**
- Region management tools (create, modify, validate)
- Path planning and optimization
- Advanced spatial analytics

### 📋 **Planned Features**
- AI-powered wilderness generation
- Natural language wilderness design
- Quality assurance and validation tools
curl http://localhost:8001/health
```

## 📚 Documentation

- **[Implementation Plan](../../docs/mcp/MCP_IMPLEMENTATION_PLAN.md)** - Complete project plan
- **[Architecture](../../docs/mcp/ARCHITECTURE.md)** - Technical architecture
- **[Deployment](../../docs/mcp/DEPLOYMENT.md)** - Deployment guide
- **[Development Setup](../../docs/mcp/DEVELOPMENT_SETUP.md)** - Local development
- **[API Reference](../../docs/mcp/API_REFERENCE.md)** - Tools and resources

## 🛠️ Development

### Project Structure
```
apps/mcp/
├── src/
│   ├── main.py              # FastAPI application
│   ├── server.py            # MCP server implementation
│   ├── mcp/
│   │   ├── tools/          # MCP tools (region, path, spatial)
│   │   ├── resources/      # Domain knowledge resources
│   │   └── prompts/        # AI prompt generators
│   ├── services/           # Business logic services
│   ├── utils/              # Utilities and helpers
│   └── shared/             # Shared components
└── tests/                  # Test suite
```

### Key Components

#### **MCP Tools**
- `region_tools.py` - Region analysis and creation
- `path_tools.py` - Path planning and validation
- `spatial_tools.py` - Spatial analysis and optimization

#### **MCP Resources**
- `wilderness_context.py` - Domain knowledge and references
- `schema_resources.py` - Database schema and validation rules

#### **MCP Prompts**
- `region_prompts.py` - Region creation prompts
- `path_prompts.py` - Path planning prompts

## 🔧 Configuration

### Environment Variables
```bash
# Required
BACKEND_BASE_URL=http://localhost:8000    # Backend API URL
API_KEY=your-secure-api-key               # Shared API key with backend

# Optional  
MCP_PORT=8001                             # MCP server port (default: 8001)
```

### Dependencies
- **FastAPI** - Web framework and MCP protocol
- **httpx** - HTTP client for backend integration
- **Pydantic** - Data validation and settings
- **Python 3.11+** - Runtime environment

## 🧪 Testing

### Manual Testing
```bash
# Load test script
. ./test-terrain-bridge-api.ps1

# Run quick test suite  
Test-WildernessAPI

# Test specific MCP tools
$mcpResult = Invoke-RestMethod -Uri "$MCP_URL/mcp/tools/find_zone_entrances" `
    -Method POST -Headers @{"X-API-Key" = $MCP_API_KEY; "Content-Type" = "application/json"} `
    -Body "{}"
```

### Available Test Functions
```powershell
Get-ZoneEntrances          # Test zone entrance discovery
Get-TerrainSummary         # Test terrain analysis
Get-ElevationProfile       # Test elevation queries
Test-WildernessAPI         # Complete test suite
```

## 📊 Health Checks

- **Health Endpoint**: `GET /health`
- **MCP Tools**: `POST /mcp/tools/{tool_name}`
- **Server Status**: Returns backend connectivity and tool availability

## 🔒 Security

- **Authentication**: API key-based authentication (X-API-Key header)
- **Network**: Deployed with --network host for backend connectivity
- **Input Validation**: Comprehensive parameter validation
- **Rate Limiting**: Managed at infrastructure level

## 🚀 Deployment Architecture

```
Server: luminarimud.com
├── Backend API (Port 8000)          # Existing wilderness API
├── MCP Server (Port 8001)           # New MCP tools for AI agents  
├── Terrain Bridge (Port 8182)       # Game engine integration
└── Nginx Proxy                      # Traffic routing and SSL
```

**Current Status**: ✅ **Production Ready**  
- All core MCP tools implemented and tested
- Deployed via GitHub Actions
- Full wilderness management capabilities available to AI agents

## 📞 Support

For issues and questions:
- Check server logs: `docker logs wildeditor-mcp`
- Test connectivity: `curl http://luminarimud.com:8001/health`
- Review [GitHub Issues](https://github.com/LuminariMUD/wildeditor/issues)
- Create new issue with detailed information

## 📋 MCP Tool Reference

### Terrain Analysis
```json
{
  "tool": "analyze_terrain_at_coordinates",
  "parameters": {"x": 0, "y": 0}
}
// Returns: elevation, temperature, moisture, sector info
```

### Enhanced Terrain with Overlays  
```json
{
  "tool": "analyze_complete_terrain_map", 
  "parameters": {"center_x": 0, "center_y": 0, "radius": 10}
}
// Returns: complete terrain + region overlays + path modifications
```

### Zone Connections
```json
{
  "tool": "find_zone_entrances",
  "parameters": {}
}
// Returns: all wilderness rooms that connect to static zones
```

### Static Wilderness Rooms
```json
{
  "tool": "find_static_wilderness_room",
  "parameters": {"x": 0, "y": 0}
}
// Returns: static room details if found, or terrain data if no static room exists
```

---

**Status**: ✅ **Production Deployed**  
**Version**: 1.0.0  
**Last Updated**: August 17, 2025  
**Deployment**: luminarimud.com:8001
