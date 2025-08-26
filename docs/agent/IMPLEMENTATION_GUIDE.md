# Chat Agent Implementation Guide

**Project**: Luminari Wilderness Editor  
**Component**: AI Chat Assistant Implementation  
**Version**: 1.0  
**Status**: Planning/Documentation  

## 🚀 Implementation Roadmap

### Phase 1: Core Infrastructure (Week 1)

#### 1.1 Project Setup
```bash
# Create agent application structure
cd apps/
mkdir -p agent/src/{agent,session,routers,schemas,services,utils}
mkdir -p agent/tests

# Initialize Python environment
cd agent/
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi pydantic-ai redis httpx pytest
```

#### 1.2 Basic Agent Implementation

```python
# src/agent/chat_agent.py
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic import BaseModel
from typing import Optional

class AssistantResponse(BaseModel):
    """Structured response from the assistant"""
    message: str
    tool_calls: list[dict] = []
    suggestions: list[str] = []
    warnings: list[str] = []

class WildernessAssistantAgent:
    def __init__(self):
        self.model = OpenAIModel('gpt-4-turbo')
        
        # Start with simple agent, no MCP yet
        self.agent = Agent(
            model=self.model,
            output_type=AssistantResponse,
            instructions="""
            You are an expert wilderness builder assistant for LuminariMUD.
            Help users create and manage wilderness regions with rich descriptions.
            """
        )
    
    async def chat(self, message: str) -> AssistantResponse:
        """Simple chat without session management"""
        result = await self.agent.run(message)
        return result.data
```

### Phase 2: Session Management (Week 2)

#### 2.1 Session Storage Implementation

```python
# src/session/storage.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import json
import redis.asyncio as redis

class SessionStorage(ABC):
    @abstractmethod
    async def save(self, key: str, data: Dict[str, Any], ttl: int):
        pass
    
    @abstractmethod
    async def load(self, key: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def delete(self, key: str):
        pass

class RedisStorage(SessionStorage):
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    async def save(self, key: str, data: Dict[str, Any], ttl: int):
        await self.redis.setex(
            key, 
            ttl, 
            json.dumps(data)
        )
    
    async def load(self, key: str) -> Optional[Dict[str, Any]]:
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def delete(self, key: str):
        await self.redis.delete(key)

class InMemoryStorage(SessionStorage):
    """For development/testing"""
    def __init__(self):
        self.store = {}
    
    async def save(self, key: str, data: Dict[str, Any], ttl: int):
        self.store[key] = data
    
    async def load(self, key: str) -> Optional[Dict[str, Any]]:
        return self.store.get(key)
    
    async def delete(self, key: str):
        self.store.pop(key, None)
```

#### 2.2 Session Manager

```python
# src/session/manager.py
from pydantic_ai.messages import (
    ModelMessage, 
    ModelMessagesTypeAdapter,
    UserMessage,
    AssistantMessage
)
from pydantic_core import to_jsonable_python
from datetime import datetime
from typing import List, Optional
import uuid

class SessionManager:
    def __init__(self, storage: SessionStorage):
        self.storage = storage
        self.ttl = 86400  # 24 hours
    
    async def create_session(self, user_id: str) -> str:
        """Create new session"""
        session_id = f"{user_id}_{uuid.uuid4().hex[:8]}"
        await self.storage.save(
            f"session:{session_id}",
            {
                "created_at": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "messages": []
            },
            self.ttl
        )
        return session_id
    
    async def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str
    ):
        """Add message to session history"""
        data = await self.storage.load(f"session:{session_id}")
        if not data:
            return
        
        data["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        await self.storage.save(
            f"session:{session_id}",
            data,
            self.ttl
        )
    
    async def get_history(
        self, 
        session_id: str
    ) -> List[ModelMessage]:
        """Get message history as PydanticAI messages"""
        data = await self.storage.load(f"session:{session_id}")
        if not data:
            return []
        
        messages = []
        for msg in data["messages"]:
            if msg["role"] == "user":
                messages.append(UserMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AssistantMessage(content=msg["content"]))
        
        return messages
```

### Phase 3: MCP Integration (Week 3)

#### 3.1 MCP Client Setup

```python
# src/services/mcp_client.py
from pydantic_ai.mcp import MCPServerHTTP, MCPServerStdio
from typing import Optional
import os

class MCPManager:
    """Manages connections to MCP servers"""
    
    def __init__(self):
        self.wilderness_mcp = None
        self.sage_mcp = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize MCP connections"""
        if self._initialized:
            return
        
        # Connect to Wilderness MCP
        if os.getenv("WILDERNESS_MCP_URL"):
            self.wilderness_mcp = MCPServerHTTP(
                url=os.getenv("WILDERNESS_MCP_URL"),
                headers={"X-API-Key": os.getenv("MCP_API_KEY")}
            )
        
        # Connect to Sage MCP (when available)
        if os.getenv("SAGE_MCP_URL"):
            self.sage_mcp = MCPServerHTTP(
                url=os.getenv("SAGE_MCP_URL"),
                headers={"X-API-Key": os.getenv("SAGE_API_KEY")}
            )
        
        self._initialized = True
    
    def get_toolsets(self):
        """Get list of available MCP toolsets"""
        toolsets = []
        if self.wilderness_mcp:
            toolsets.append(self.wilderness_mcp)
        if self.sage_mcp:
            toolsets.append(self.sage_mcp)
        return toolsets
```

#### 3.2 Enhanced Agent with MCP

```python
# src/agent/enhanced_agent.py
class EnhancedWildernessAgent:
    def __init__(self, mcp_manager: MCPManager):
        self.model = OpenAIModel('gpt-4-turbo')
        self.mcp = mcp_manager
        
    async def create_agent(self):
        """Create agent with MCP toolsets"""
        await self.mcp.initialize()
        
        self.agent = Agent(
            model=self.model,
            toolsets=self.mcp.get_toolsets(),
            output_type=AssistantResponse,
            instructions=self._get_enhanced_prompt()
        )
    
    def _get_enhanced_prompt(self) -> str:
        return """
        You are an expert wilderness builder assistant for LuminariMUD.
        
        You have access to:
        - Wilderness MCP: Create, read, update regions and paths
        - Sage MCP: Query lore and ensure consistency
        
        Guidelines:
        1. Always check existing regions before creating new ones
        2. Ensure lore consistency when referencing game history
        3. Use appropriate terrain types and properties
        4. Generate rich, immersive descriptions
        5. Consider connections to neighboring regions
        """
    
    async def chat_with_tools(
        self, 
        message: str,
        history: List[ModelMessage],
        context: dict
    ) -> AssistantResponse:
        """Chat with full tool access"""
        async with self.agent:
            result = await self.agent.run(
                message,
                message_history=history,
                context=context
            )
        return result.data
```

### Phase 4: Frontend Integration (Week 4)

#### 4.1 React Chat Component

```typescript
// src/components/ChatAssistant/ChatAssistant.tsx
import React, { useState, useEffect, useRef } from 'react';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { useWebSocket } from '../../hooks/useWebSocket';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  toolCalls?: ToolCall[];
  timestamp: string;
}

export const ChatAssistant: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  
  const ws = useWebSocket({
    url: `${process.env.VITE_AGENT_WS_URL}/chat`,
    onMessage: handleMessage,
    onConnect: () => setIsConnected(true),
    onDisconnect: () => setIsConnected(false)
  });
  
  const handleMessage = (event: MessageEvent) => {
    const data = JSON.parse(event.data);
    
    switch (data.type) {
      case 'message':
        setMessages(prev => [...prev, data.message]);
        break;
      case 'typing':
        setIsTyping(data.isTyping);
        break;
      case 'tool_call':
        // Handle tool visualization
        break;
    }
  };
  
  const sendMessage = (content: string) => {
    ws.send(JSON.stringify({
      type: 'message',
      content,
      sessionId: getSessionId(),
      context: getEditorContext()
    }));
  };
  
  return (
    <div className="chat-assistant">
      <div className="chat-header">
        <h3>Wilderness Assistant</h3>
        <StatusIndicator connected={isConnected} />
      </div>
      
      <MessageList 
        messages={messages}
        isTyping={isTyping}
      />
      
      <MessageInput
        onSend={sendMessage}
        disabled={!isConnected}
      />
    </div>
  );
};
```

#### 4.2 WebSocket Handler

```python
# src/routers/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
    
    async def send_message(self, client_id: str, message: dict):
        if websocket := self.active_connections.get(client_id):
            await websocket.send_json(message)

manager = ConnectionManager()

@router.websocket("/chat")
async def websocket_endpoint(
    websocket: WebSocket,
    agent: EnhancedWildernessAgent = Depends(get_agent),
    session_mgr: SessionManager = Depends(get_session_manager)
):
    client_id = str(uuid.uuid4())
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Process message
            if data["type"] == "message":
                # Get session history
                history = await session_mgr.get_history(data["sessionId"])
                
                # Send typing indicator
                await manager.send_message(client_id, {
                    "type": "typing",
                    "isTyping": True
                })
                
                # Process with agent
                response = await agent.chat_with_tools(
                    data["content"],
                    history,
                    data.get("context", {})
                )
                
                # Save to history
                await session_mgr.add_message(
                    data["sessionId"],
                    "user",
                    data["content"]
                )
                await session_mgr.add_message(
                    data["sessionId"],
                    "assistant",
                    response.message
                )
                
                # Send response
                await manager.send_message(client_id, {
                    "type": "message",
                    "message": {
                        "role": "assistant",
                        "content": response.message,
                        "toolCalls": response.tool_calls
                    }
                })
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
```

## 🧪 Testing Strategy

### Unit Tests

```python
# tests/test_agent.py
import pytest
from src.agent.chat_agent import WildernessAssistantAgent

@pytest.mark.asyncio
async def test_basic_chat():
    agent = WildernessAssistantAgent()
    response = await agent.chat("Hello, can you help me?")
    assert response.message
    assert "help" in response.message.lower()

@pytest.mark.asyncio
async def test_region_creation_intent():
    agent = WildernessAssistantAgent()
    response = await agent.chat(
        "Create a forest region at 100,200"
    )
    assert response.message
    # Should recognize region creation intent
```

### Integration Tests

```python
# tests/test_integration.py
@pytest.mark.asyncio
async def test_mcp_integration():
    mcp_manager = MCPManager()
    await mcp_manager.initialize()
    
    agent = EnhancedWildernessAgent(mcp_manager)
    await agent.create_agent()
    
    response = await agent.chat_with_tools(
        "List all regions near 0,0",
        [],
        {}
    )
    
    assert response.tool_calls
    assert any(tc["tool"] == "list_regions" for tc in response.tool_calls)
```

## 🚀 Deployment

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8003"]
```

### Environment Variables

```bash
# .env.production
OPENAI_API_KEY=sk-...
REDIS_URL=redis://localhost:6379
WILDERNESS_MCP_URL=http://localhost:8001/mcp
SAGE_MCP_URL=http://localhost:8002/mcp
MCP_API_KEY=...
SAGE_API_KEY=...
LOG_LEVEL=INFO
```

## 📈 Performance Considerations

### 1. Response Streaming
- Use Server-Sent Events (SSE) for real-time streaming
- Chunk responses for better perceived performance
- Show tool calls as they happen

### 2. Session Optimization
- Limit message history to last 50 messages
- Summarize older conversations
- Cache frequently accessed data

### 3. MCP Connection Pooling
- Maintain persistent connections to MCP servers
- Implement connection retry logic
- Use circuit breakers for failing services

## 🔒 Security Considerations

### 1. Authentication
- Integrate with existing auth system
- Validate session tokens
- Rate limit per user

### 2. Input Validation
- Sanitize user messages
- Prevent prompt injection
- Validate tool parameters

### 3. Data Protection
- Encrypt session data at rest
- Use secure WebSocket connections
- Audit tool usage

## 📊 Monitoring & Observability

### Metrics to Track
- Message processing time
- Tool call frequency
- Session duration
- Error rates
- Token usage

### Logging Strategy
```python
import structlog

logger = structlog.get_logger()

logger.info("chat_message_received",
    session_id=session_id,
    message_length=len(message),
    has_context=bool(context)
)

logger.info("tool_called",
    tool_name=tool_name,
    duration_ms=duration,
    success=success
)
```

## 🎯 Success Criteria

1. **Response Time**: < 2 seconds for simple queries
2. **Tool Success Rate**: > 95% successful tool calls
3. **Context Retention**: Maintains context for 24 hours
4. **Concurrent Users**: Support 100+ concurrent sessions
5. **Uptime**: 99.9% availability