# Wilderness Chat Agent

An AI-powered wilderness building assistant that provides intelligent region creation, path routing, and terrain analysis through natural language interaction. Built with PydanticAI and integrated with the Model Context Protocol (MCP) server architecture.

## Overview

The Chat Agent serves as the intelligent backend for the Wilderness Editor's chat assistant, providing:

- **Spatial Intelligence**: Analyzes terrain and finds optimal placement for new regions
- **Organic Region Creation**: Generates natural-looking borders using advanced algorithms  
- **Path Intelligence**: Creates curved, terrain-aware paths between multiple regions
- **Natural Language Processing**: Understands building requests in plain English
- **MCP Integration**: Uses Model Context Protocol for all wilderness operations

## Architecture

```
Frontend Chat UI → Chat Agent (8002) → MCP Server (8001) → Backend (8000) → MySQL
```

The agent runs as a separate FastAPI service and communicates exclusively through the MCP server, ensuring a clean separation of concerns and robust error handling.

## Core Features

### AI Agent Capabilities
- **PydanticAI Integration**: Advanced AI model support (OpenAI, DeepSeek, Anthropic)
- **Tool Function Mapping**: 15+ specialized tools for wilderness operations
- **Context Awareness**: Maintains conversation history and editor state
- **Error Recovery**: Robust fallback handling for failed operations

### Spatial Intelligence
- **Area Analysis**: Find empty space between regions or near coordinates
- **Terrain Analysis**: Understand elevation, sectors, and geographic features
- **Overlap Prevention**: Automatically prevent conflicting geographic regions
- **Organic Border Generation**: Create natural region shapes using polar algorithms

### Path Intelligence
- **Multi-Region Connection**: Connect 2+ regions with curved, natural paths
- **Terrain-Aware Routing**: Rivers follow elevation, roads avoid obstacles
- **Path Types**: Support for roads (paved/dirt), geographic features, waterways
- **Curve Generation**: Bezier-like curves with random variation for natural appearance

### Natural Language Processing
- **Intent Recognition**: Understand region creation, path building, and analysis requests
- **Parameter Extraction**: Parse coordinates, names, types from natural language
- **Context Integration**: Use editor state (selected regions, viewport) in responses
- **Suggestion Generation**: Provide next-step recommendations

## Available Tools

The agent provides these wilderness building tools through MCP integration:

### Creation Tools
- **build_new_region**: Create regions with organic borders and AI descriptions
- **build_new_path**: Create curved paths connecting multiple regions
- **generate_region_description**: AI-powered immersive region descriptions

### Analysis Tools  
- **analyze_terrain**: Get terrain data at specific coordinates
- **analyze_complete_terrain_map**: Enhanced area analysis with overlays
- **search_by_coordinates**: Find existing regions and paths near locations
- **search_regions**: Search regions by type, name, or location

### Discovery Tools
- **find_zone_entrances**: Locate wilderness-to-zone connections
- **find_static_wilderness_room**: Find static content at coordinates
- **generate_wilderness_map**: Create terrain maps for areas

### Utility Tools
- **store_region_hints**: Save AI-generated weather/time variations
- **get_region_hints**: Retrieve existing hint data
- **update_region_description**: Modify region descriptions

## Installation & Configuration

```bash
# Navigate to agent directory
cd apps/agent/src

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export OPENAI_API_KEY="your-openai-key"        # Primary AI provider
export DEEPSEEK_API_KEY="your-deepseek-key"    # Fallback provider  
export WILDEDITOR_MCP_KEY="your-mcp-key"       # MCP authentication
export MCP_BASE_URL="http://localhost:8001"    # MCP server URL

# Start the chat agent
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

### Environment Variables

```bash
# AI Model Configuration
AI_PROVIDER=openai                    # Primary: openai, deepseek, anthropic
OPENAI_API_KEY=your-openai-key       # For GPT-4 and GPT-3.5
DEEPSEEK_API_KEY=your-deepseek-key   # Fallback provider
OPENAI_MODEL=gpt-4-turbo             # Model selection
DEEPSEEK_MODEL=deepseek-chat         # DeepSeek model

# MCP Integration  
MCP_BASE_URL=http://localhost:8001   # Local: localhost, Prod: luminarimud.com
WILDEDITOR_MCP_KEY=your-mcp-key      # Authentication for MCP server

# Server Configuration
PORT=8002                            # Chat agent port
HOST=0.0.0.0                        # Listen address
```

## API Endpoints

The Chat Agent exposes these REST endpoints:

### Chat Endpoints
```bash
# Send a chat message
POST /api/chat/message
{
  "message": "Create a forest region near the lake",
  "session_id": "optional-session-id"
}

# Get conversation history  
GET /api/chat/history?session_id=session-123

# Create new session
POST /api/session/
```

### Management Endpoints
```bash
# Health check
GET /health

# Service status
GET /status
```

## Usage Examples

### Direct API Testing

```bash
# Create a new session
SESSION_ID=$(curl -X POST http://localhost:8002/api/session/ -H "Content-Type: application/json" -d '{}' | jq -r .session_id)

# Send a chat message
curl -X POST http://localhost:8002/api/chat/message \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Create a dense forest region between coordinates (100, 200) and (300, 400)\", \"session_id\": \"$SESSION_ID\"}" | jq .

# Get conversation history
curl "http://localhost:8002/api/chat/history?session_id=$SESSION_ID" | jq .
```

### Example Conversations

**Region Creation:**
```
User: "Create a forest region northeast of the village"
Agent: "I'll create a forest region with organic borders northeast of the village. Let me find a suitable location first."
→ Analyzes terrain, finds empty space
→ Generates organic forest coordinates  
→ Creates region with AI description
→ Returns frontend actions to display the region
```

**Path Building:**  
```
User: "Make a river connecting the mountain springs to the harbor"
Agent: "I'll create a river that flows naturally from the mountain springs down to the harbor."
→ Finds elevation data for mountains and harbor
→ Calculates downhill path with curves
→ Creates river path with multiple coordinate points
→ Returns actions to draw the river on map
```

**Terrain Analysis:**
```
User: "What's the terrain like around coordinates (150, 250)?"
Agent: "Let me analyze the terrain around those coordinates."
→ Calls terrain analysis tools
→ Provides elevation, sector types, existing regions
→ Suggests suitable region types for the area
```

## Advanced Features

### Organic Border Algorithm

The agent uses sophisticated spatial algorithms for natural region creation:

```python
def generate_organic_border(center_x, center_y, radius=50, points=10):
    """
    Creates natural-looking polygon borders using:
    - Polar coordinate generation around center point
    - Irregularity: varies angles for non-geometric shapes
    - Spikiness: varies radius for natural variation
    - Boundary clamping to wilderness limits (-1024 to +1024)
    """
```

### Path Intelligence

Multi-region path creation with terrain awareness:

```python  
def create_connecting_path(region_vnums, path_type="dirt_road"):
    """
    Connects multiple regions with:
    - Center point calculation for each region
    - Curved interpolation between points  
    - Terrain elevation consideration for rivers
    - Obstacle avoidance around existing regions
    """
```

### Spatial Analysis

Intelligent area analysis for optimal placement:

```python
def find_empty_space_between_regions(region1, region2):
    """
    Analyzes space between regions:
    - Calculates midpoint and search radius
    - Checks for existing regions/paths
    - Analyzes terrain suitability
    - Returns placement recommendations
    """
```

## Troubleshooting

### Common Issues

**Chat Agent not responding:**
```bash
# Check if agent is running
curl http://localhost:8002/health

# Check logs for errors
docker logs wildeditor-chat-agent

# Restart if needed
docker restart wildeditor-chat-agent
```

**MCP connection failures:**
- Verify MCP server is running on port 8001
- Check `WILDEDITOR_MCP_KEY` environment variable
- Ensure MCP server authentication is configured

**AI model errors:**
- Verify `OPENAI_API_KEY` or `DEEPSEEK_API_KEY` is set
- Check API key validity with provider
- Try switching AI provider in environment config

**Region/Path creation issues:**
- Check backend database connection (port 8000)
- Verify MySQL spatial tables exist
- Review MCP tool responses for data errors

### Performance Optimization

**Memory usage:**
- The agent loads AI models in memory (200MB+)
- Consider using smaller models for development
- Monitor memory usage with `docker stats`

**Response times:**
- First requests may be slower (model loading)
- Subsequent requests typically < 2 seconds
- Spatial analysis tools may take 3-5 seconds

### Development Workflow  

**Local Development:**
```bash
# Start all services in development mode
cd apps/agent/src
export OPENAI_API_KEY="your-key"
export MCP_BASE_URL="http://localhost:8001"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8002

# Test agent functionality
curl -X POST http://localhost:8002/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "What terrain is at coordinates (0, 0)?"}'
```

**Adding New Tools:**

1. Add tool method to `WildernessTools` class:
```python
async def your_new_tool(self, param: str) -> Dict[str, Any]:
    return await self.mcp.call_tool("mcp_tool_name", {"param": param})
```

2. Register tool with PydanticAI agent:
```python
@agent.tool
async def your_tool_wrapper(ctx: RunContext[EditorContext], param: str):
    return await self.tools.your_new_tool(param)
```

3. Update prompts to include tool usage instructions

**Testing Tools:**
```python
# Test individual MCP tool
async with MCPClient() as client:
    result = await client.call_tool("tool_name", {"param": "value"})
    print(result)
```

## Docker Deployment

The chat agent runs in production via Docker:

```dockerfile
# Dockerfile configuration
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
```

### Production Configuration

```yaml
# docker-compose.yml section
chat-agent:
  build: ./apps/agent
  ports:
    - "8002:8002"
  environment:
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}  
    - MCP_BASE_URL=http://mcp-server:8001
    - WILDEDITOR_MCP_KEY=${WILDEDITOR_MCP_KEY}
  depends_on:
    - mcp-server
```

## Future Enhancements

### Planned Features
- **WebSocket Support**: Real-time streaming responses
- **Session Persistence**: Redis-backed conversation history
- **Batch Operations**: Create multiple related features at once
- **Template System**: Pre-built region and path templates
- **Visual Planning**: ASCII art maps in chat responses

### Integration Opportunities
- **Voice Input**: Speech-to-text for hands-free building
- **Image Analysis**: Upload terrain sketches for region creation
- **3D Visualization**: Generate height maps for regions
- **Game Integration**: Real-time updates to running MUD server

## Contributing

The chat agent is actively developed. Contributions welcome:

1. **Tool Development**: Add new MCP tools for specialized functions
2. **AI Improvements**: Enhance prompts and spatial intelligence
3. **UI Integration**: Improve frontend chat experience
4. **Performance**: Optimize response times and memory usage

## License

Part of the Wildeditor project. See main project LICENSE for details.