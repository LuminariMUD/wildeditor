# MCP Server Deployment and Usage Guide

## 🚀 **DEPLOYMENT STATUS**

**Phase 1 & 2 Complete**: The Wildeditor MCP Server is fully functional and ready for production deployment.

## 📋 **WHAT'S READY**

### ✅ **Core MCP Server**
- Full MCP protocol implementation (JSON-RPC 2.0)
- Production-grade FastAPI application
- Multi-key authentication system
- Environment configuration management
- Comprehensive error handling

### ✅ **Wilderness Management Tools**
- **analyze_region**: Deep analysis of wilderness regions
- **find_path**: Pathfinding between regions  
- **search_regions**: Advanced region search with filters
- **create_region**: New region creation with validation
- **validate_connections**: Connection consistency checking

### ✅ **Knowledge Resources**
- **terrain-types**: Complete reference of available terrains
- **environment-types**: Climate and environmental conditions
- **region-stats**: Real-time system statistics
- **schema**: Database structure documentation
- **capabilities**: System feature overview
- **map-overview**: Wilderness structure information

### ✅ **AI Content Generation**
- **create_region**: Rich, atmospheric region descriptions
- **connect_regions**: Logical path and transition generation
- **design_area**: Multi-region wilderness area planning
- **analyze_region**: Expert analysis and improvement suggestions
- **describe_path**: Detailed travel descriptions

## 🔧 **DEPLOYMENT OPTIONS**

### **Option 1: Same-Server Deployment (Recommended)**
Deploy MCP server alongside backend using Docker Compose:

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./apps/backend
    ports:
      - "8000:8000"
    environment:
      - WILDEDITOR_API_KEY=${WILDEDITOR_API_KEY}
      - WILDEDITOR_MCP_BACKEND_KEY=${WILDEDITOR_MCP_BACKEND_KEY}
  
  mcp-server:
    build: ./apps/mcp
    ports:
      - "8001:8001"
    environment:
      - WILDEDITOR_MCP_KEY=${WILDEDITOR_MCP_KEY}
      - WILDEDITOR_MCP_BACKEND_KEY=${WILDEDITOR_MCP_BACKEND_KEY}
      - WILDEDITOR_BACKEND_URL=http://backend:8000
    depends_on:
      - backend
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - mcp-server
```

### **Option 2: Hybrid Development**
Run MCP server locally while connecting to remote backend:

```bash
# Set environment variables
export WILDEDITOR_MCP_KEY="your-mcp-key"
export WILDEDITOR_MCP_BACKEND_KEY="your-backend-access-key"  
export WILDEDITOR_BACKEND_URL="https://your-backend-server.com"

# Start MCP server
cd apps/mcp
python run_dev.py
```

## 🔑 **AUTHENTICATION SETUP**

### **Three-Key System**
```bash
# Backend API access (for direct backend operations)
WILDEDITOR_API_KEY="backend-api-key-here"

# MCP operations (for AI agents using MCP server)
WILDEDITOR_MCP_KEY="mcp-operations-key-here"  

# MCP-to-Backend access (for MCP server calling backend)
WILDEDITOR_MCP_BACKEND_KEY="mcp-backend-access-key-here"
```

### **Key Security**
- Generate unique, strong keys for each type
- Rotate keys regularly
- Use different keys for development/staging/production
- Store keys securely (environment variables, secrets management)

## 🌐 **API ENDPOINTS**

### **Public Endpoints**
- `GET /health` - Server health check

### **MCP Operations (Require MCP Key)**
- `GET /mcp/status` - Server status and capabilities
- `POST /mcp/initialize` - Initialize MCP session
- `POST /mcp/request` - Raw MCP JSON-RPC requests
- `GET /mcp/tools` - List available tools
- `GET /mcp/resources` - List available resources  
- `GET /mcp/prompts` - List available prompts

### **Individual Tool/Resource Access**
- `POST /mcp/tools/{tool_name}` - Call specific tool
- `GET /mcp/resources/{resource_uri}` - Read specific resource
- `POST /mcp/prompts/{prompt_name}` - Get specific prompt

## 🤖 **AI AGENT INTEGRATION**

### **Tool Usage Examples**

```json
// Analyze a region
POST /mcp/tools/analyze_region
{
  "region_id": 123,
  "include_paths": true
}

// Search for forest regions
POST /mcp/tools/search_regions  
{
  "terrain_type": "forest",
  "environment": "temperate",
  "limit": 10
}

// Create new region
POST /mcp/tools/create_region
{
  "name": "Whispering Woods",
  "description": "A mysterious forest...",
  "terrain_type": "forest",
  "environment": "temperate"
}
```

### **Resource Access Examples**

```json
// Get terrain types reference
GET /mcp/resources/terrain-types

// Get system capabilities
GET /mcp/resources/capabilities

// Get current statistics
GET /mcp/resources/region-stats
```

### **Prompt Usage Examples**

```json
// Generate region creation prompt
POST /mcp/prompts/create_region
{
  "terrain_type": "mountain",
  "environment": "arctic", 
  "theme": "mysterious",
  "size": "large"
}

// Generate area design prompt  
POST /mcp/prompts/design_area
{
  "area_theme": "haunted forest",
  "size": 8,
  "difficulty": "hard"
}
```

## 📊 **MONITORING & TESTING**

### **Health Checks**
```bash
# Public health check
curl http://localhost:8001/health

# Authenticated health check
curl -H "X-API-Key: your-mcp-key" http://localhost:8001/health/detailed
```

### **Capability Testing**
```bash
# Test tool availability
curl -H "X-API-Key: your-mcp-key" http://localhost:8001/mcp/tools

# Test resource access
curl -H "X-API-Key: your-mcp-key" http://localhost:8001/mcp/resources

# Test backend connectivity (will show errors if backend not available)
curl -H "X-API-Key: your-mcp-key" -H "Content-Type: application/json" \
  -d '{"region_id": 1}' http://localhost:8001/mcp/tools/analyze_region
```

## 🔄 **INTEGRATION WITH EXISTING BACKEND**

### **Backend Endpoints Expected**
The MCP server expects these backend endpoints to exist:

```
GET /api/regions/{id} - Get region by ID
GET /api/regions/{id}/paths - Get region paths
GET /api/paths/find - Find paths between regions
GET /api/regions/search - Search regions
POST /api/regions - Create new region
GET /api/regions/{id}/validate - Validate region connections
GET /api/stats/regions - Get region statistics
GET /api/regions/recent - Get recently modified regions
GET /api/map/overview - Get map overview
```

### **Backend Authentication**
The MCP server uses `WILDEDITOR_MCP_BACKEND_KEY` in the `X-API-Key` header when calling backend endpoints.

## 🐛 **TROUBLESHOOTING**

### **Common Issues**

1. **Authentication Failures**
   - Verify environment variables are set correctly
   - Check API key format and validity
   - Ensure correct key type for endpoint

2. **Backend Connection Issues**
   - Check WILDEDITOR_BACKEND_URL setting
   - Verify backend is running and accessible
   - Check backend authentication key

3. **Import Errors**
   - Ensure virtual environment is activated
   - Install packages: `pip install -r requirements.txt`
   - Install auth package: `pip install -e packages/auth`

### **Development Mode**
```bash
# Start with debug logging
export WILDEDITOR_LOG_LEVEL=DEBUG
python apps/mcp/run_dev.py
```

## 📈 **NEXT STEPS**

The MCP server is ready for:
1. **Production Deployment**: Deploy alongside existing backend
2. **AI Agent Integration**: Connect Claude, GPT, or other AI systems
3. **Backend Integration**: Connect to live Wildeditor backend API
4. **Content Generation**: Use prompts to generate wilderness content
5. **Automated Workflows**: Build AI-powered wilderness management tools

---

**The Wildeditor MCP Server is production-ready and provides a full suite of AI-powered wilderness management capabilities!** 🎉
