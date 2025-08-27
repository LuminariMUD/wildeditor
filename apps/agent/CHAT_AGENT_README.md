# Chat Agent Service

AI-powered chat assistant for the Wilderness Editor, providing intelligent help for building wilderness regions in LuminariMUD.

## 🎯 Overview

The Chat Agent Service is a FastAPI-based application that uses PydanticAI to provide an intelligent assistant for wilderness builders. It integrates with the MCP server to access wilderness data and tools.

### Key Features
- **Natural Language Interface**: Chat with an AI assistant about wilderness building
- **Context-Aware Assistance**: Understands selected regions, viewport, and editor state
- **Session Management**: Maintains conversation history across messages
- **MCP Integration**: Access to terrain analysis and wilderness tools
- **REST & WebSocket APIs**: Support for both synchronous and real-time communication
- **Docker Deployment**: Production-ready containerized deployment

## 🏗️ Architecture

```
Chat Agent Service (Port 8002)
├── PydanticAI Agent (GPT-4/Claude)
├── Session Management (Redis/Memory)
├── FastAPI REST & WebSocket APIs
├── MCP Client Integration
└── Docker Container
```

## 🚀 Quick Start

### Development Setup

1. **Install dependencies**:
```bash
cd apps/agent
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Run development server**:
```bash
python run_dev.py
# or
python -m uvicorn src.main:app --reload --port 8002
```

4. **Access the service**:
- API Docs: http://localhost:8002/docs
- Health: http://localhost:8002/health/
- Chat API: http://localhost:8002/api/chat/message

### Docker Deployment

```bash
# Build and run with Docker Compose
cd apps/agent
docker-compose up -d

# Or build manually
docker build -t wildeditor-chat-agent .
docker run -p 8002:8002 --env-file .env wildeditor-chat-agent
```

## 📡 API Reference

### Chat Endpoints

#### Send Message
```http
POST /api/chat/message
Content-Type: application/json

{
  "message": "Help me create a forest region",
  "session_id": "user_abc123",
  "context": {
    "selected_region_id": 42,
    "viewport": {"x": 0, "y": 0, "zoom": 1},
    "active_tool": "polygon"
  }
}
```

#### Get History
```http
GET /api/chat/history?session_id=user_abc123&limit=50
```

### Session Endpoints

#### Create Session
```http
POST /api/session/
Content-Type: application/json

{
  "user_id": "user123",
  "metadata": {"project": "Northern Wilderness"}
}
```

#### Get Session Info
```http
GET /api/session/{session_id}
```

## 🔧 Configuration

### Environment Variables

```bash
# AI Model Configuration
MODEL_PROVIDER=openai              # or anthropic
OPENAI_API_KEY=sk-...             # OpenAI API key
ANTHROPIC_API_KEY=...              # Anthropic API key (if using Claude)
MODEL_NAME=gpt-4-turbo             # Model to use

# Service URLs (Docker network names in production)
WILDERNESS_MCP_URL=http://localhost:8001
BACKEND_API_URL=http://localhost:8000

# Session Storage
STORAGE_BACKEND=memory             # memory or redis
REDIS_URL=redis://localhost:6379
SESSION_TTL=86400                  # 24 hours

# Server Configuration
HOST=0.0.0.0
PORT=8002
LOG_LEVEL=INFO
```

## 🐳 Production Deployment

The service is automatically deployed via GitHub Actions when changes are pushed to the main branch.

### GitHub Secrets Required
- `VPS_HOST`: Production server hostname
- `VPS_USER`: SSH username
- `VPS_SSH_KEY`: SSH private key
- `MODEL_PROVIDER`: AI provider (openai/anthropic)
- `OPENAI_API_KEY`: OpenAI API key
- `MCP_API_KEY`: MCP server API key
- `BACKEND_API_KEY`: Backend API key

### Manual Deployment
```bash
# On production server
cd /home/luminari/wildeditor/apps/agent
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🧪 Testing

### Run Tests
```bash
cd apps/agent
pytest tests/
```

### Test Chat Functionality
```python
import httpx
import asyncio

async def test_chat():
    async with httpx.AsyncClient() as client:
        # Create session
        session_response = await client.post(
            "http://localhost:8002/api/session/",
            json={"user_id": "test_user"}
        )
        session_id = session_response.json()["session_id"]
        
        # Send message
        chat_response = await client.post(
            "http://localhost:8002/api/chat/message",
            json={
                "message": "Hello, can you help me build a forest?",
                "session_id": session_id
            }
        )
        print(chat_response.json())

asyncio.run(test_chat())
```

## 📊 Monitoring

### Health Checks
- `/health/` - Basic health check
- `/health/ready` - Readiness check (all components initialized)
- `/health/live` - Liveness check

### Logs
```bash
# View logs
docker logs wildeditor-chat-agent

# Follow logs
docker logs -f wildeditor-chat-agent
```

## 🔄 Integration with Frontend

The frontend will connect to the chat agent via WebSocket or REST API:

```typescript
// Example frontend integration
const chatAgent = new ChatAgentClient({
  baseUrl: 'http://localhost:8002',
  sessionId: 'user_session_123'
});

// Send message
const response = await chatAgent.sendMessage(
  "Create a forest region at 100,200",
  { viewport: { x: 100, y: 200, zoom: 1 } }
);
```

## 🚧 Development Status

### ✅ Completed
- Basic agent implementation with PydanticAI
- Session management (memory and Redis)
- REST API endpoints
- Docker configuration
- GitHub Actions deployment

### 🔄 In Progress
- WebSocket handler implementation
- MCP tool integration
- Frontend React components

### 📋 TODO
- Streaming response support
- Advanced context handling
- Tool execution visualization
- Error recovery and retry logic

## 📝 License

Part of the Wildeditor project. See main project LICENSE for details.