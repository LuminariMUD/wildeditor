# Chat Agent API Specification

**Project**: Luminari Wilderness Editor  
**Component**: Chat Agent REST & WebSocket API  
**Version**: 1.0  
**Base URL**: `https://api.luminarimud.com/agent`  

## 🔐 Authentication

All API endpoints require authentication using the existing Wilderness Editor auth system.

```http
Authorization: Bearer <token>
X-Session-ID: <session_id>
```

## 📡 REST API Endpoints

### Chat Operations

#### Send Message
```http
POST /api/agent/chat/message

Request:
{
  "message": string,
  "session_id": string,
  "context": {
    "selected_region_id": number | null,
    "viewport": {
      "x": number,
      "y": number,
      "zoom": number
    },
    "active_tool": string,
    "recent_actions": array
  },
  "stream": boolean  // Default: true
}

Response (non-streaming):
{
  "response": {
    "message": string,
    "tool_calls": [
      {
        "tool": string,
        "arguments": object,
        "result": any
      }
    ],
    "suggestions": string[],
    "warnings": string[]
  },
  "session_id": string,
  "message_id": string,
  "timestamp": string
}

Response (streaming - Server-Sent Events):
data: {"type": "start", "message_id": "msg_123"}
data: {"type": "text", "delta": "I'll help you create"}
data: {"type": "text", "delta": " a new region"}
data: {"type": "tool_start", "tool": "create_region", "args": {...}}
data: {"type": "tool_end", "tool": "create_region", "result": {...}}
data: {"type": "suggestion", "text": "Consider adding paths"}
data: {"type": "complete", "message_id": "msg_123"}
```

#### Get Chat History
```http
GET /api/agent/chat/history?session_id={session_id}&limit={limit}&offset={offset}

Response:
{
  "messages": [
    {
      "id": string,
      "role": "user" | "assistant" | "system",
      "content": string,
      "tool_calls": array | null,
      "timestamp": string,
      "metadata": object
    }
  ],
  "total_count": number,
  "session_id": string,
  "has_more": boolean
}
```

#### Clear Chat History
```http
DELETE /api/agent/chat/history/{session_id}

Response:
{
  "message": "Chat history cleared",
  "session_id": string
}
```

### Session Management

#### Create Session
```http
POST /api/agent/session

Request:
{
  "user_id": string,
  "metadata": {
    "project_name": string,
    "initial_context": object
  }
}

Response:
{
  "session_id": string,
  "created_at": string,
  "expires_at": string
}
```

#### Get Session Info
```http
GET /api/agent/session/{session_id}

Response:
{
  "session_id": string,
  "user_id": string,
  "created_at": string,
  "last_activity": string,
  "expires_at": string,
  "message_count": number,
  "context": object,
  "metadata": object
}
```

#### Update Session Context
```http
PUT /api/agent/session/{session_id}/context

Request:
{
  "context": {
    "selected_region_id": number | null,
    "selected_path_ids": number[],
    "viewport": object,
    "active_tool": string
  }
}

Response:
{
  "session_id": string,
  "context_updated": boolean,
  "timestamp": string
}
```

#### List User Sessions
```http
GET /api/agent/session/list?user_id={user_id}

Response:
{
  "sessions": [
    {
      "session_id": string,
      "created_at": string,
      "last_activity": string,
      "message_count": number,
      "summary": string
    }
  ],
  "total_count": number
}
```

### Tool Operations

#### List Available Tools
```http
GET /api/agent/tools

Response:
{
  "tools": [
    {
      "name": string,
      "description": string,
      "category": "wilderness" | "sage" | "utility",
      "parameters": {
        "type": "object",
        "properties": object,
        "required": string[]
      },
      "examples": array
    }
  ],
  "categories": {
    "wilderness": number,
    "sage": number,
    "utility": number
  }
}
```

#### Execute Tool Directly
```http
POST /api/agent/tools/execute

Request:
{
  "tool_name": string,
  "arguments": object,
  "session_id": string,
  "validate_only": boolean  // Default: false
}

Response:
{
  "tool": string,
  "result": any,
  "execution_time_ms": number,
  "warnings": string[]
}
```

### Agent Configuration

#### Get Agent Status
```http
GET /api/agent/status

Response:
{
  "status": "healthy" | "degraded" | "unavailable",
  "model": {
    "name": string,
    "version": string,
    "available": boolean
  },
  "mcp_servers": [
    {
      "name": string,
      "url": string,
      "status": "connected" | "disconnected" | "error",
      "tools_available": number
    }
  ],
  "performance": {
    "avg_response_time_ms": number,
    "active_sessions": number,
    "messages_today": number
  }
}
```

#### Get Agent Capabilities
```http
GET /api/agent/capabilities

Response:
{
  "capabilities": {
    "region_management": boolean,
    "path_management": boolean,
    "description_generation": boolean,
    "hint_generation": boolean,
    "lore_integration": boolean,
    "validation": boolean
  },
  "limits": {
    "max_message_length": number,
    "max_context_size": number,
    "max_tool_calls_per_message": number
  },
  "features": {
    "streaming": boolean,
    "websocket": boolean,
    "file_upload": boolean
  }
}
```

## 🔄 WebSocket API

### Connection
```javascript
const ws = new WebSocket('wss://api.luminarimud.com/agent/ws');

// Authentication after connection
ws.send(JSON.stringify({
  type: 'auth',
  token: 'Bearer <token>',
  session_id: '<session_id>'
}));
```

### Message Types

#### Client -> Server

```typescript
// Send chat message
{
  type: 'message',
  content: string,
  context?: EditorContext,
  request_id?: string
}

// Update context
{
  type: 'context_update',
  context: EditorContext
}

// Request tool execution
{
  type: 'tool_execute',
  tool: string,
  arguments: object,
  request_id?: string
}

// Control messages
{
  type: 'ping'
}

{
  type: 'cancel',
  request_id: string
}
```

#### Server -> Client

```typescript
// Chat response (streaming)
{
  type: 'message_start',
  request_id: string,
  timestamp: string
}

{
  type: 'message_chunk',
  request_id: string,
  delta: string
}

{
  type: 'message_complete',
  request_id: string,
  message: AssistantMessage
}

// Tool execution
{
  type: 'tool_start',
  request_id: string,
  tool: string,
  arguments: object
}

{
  type: 'tool_progress',
  request_id: string,
  tool: string,
  progress: number,
  message?: string
}

{
  type: 'tool_complete',
  request_id: string,
  tool: string,
  result: any
}

// System messages
{
  type: 'error',
  request_id?: string,
  error: {
    code: string,
    message: string,
    details?: object
  }
}

{
  type: 'pong'
}

{
  type: 'session_expired',
  reason: string
}
```

## 🔍 Query Parameters

### Pagination
- `limit`: Maximum items to return (default: 50, max: 100)
- `offset`: Number of items to skip
- `cursor`: Cursor-based pagination token

### Filtering
- `start_date`: ISO 8601 datetime
- `end_date`: ISO 8601 datetime
- `tool_filter`: Comma-separated tool names
- `has_errors`: boolean

### Sorting
- `sort_by`: Field to sort by
- `sort_order`: `asc` | `desc`

## ⚠️ Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context"
    },
    "request_id": "req_123",
    "timestamp": "2024-12-01T12:00:00Z"
  }
}
```

### Error Codes
| Code | HTTP Status | Description |
|------|------------|-------------|
| `AUTH_REQUIRED` | 401 | Missing authentication |
| `AUTH_INVALID` | 401 | Invalid token |
| `SESSION_NOT_FOUND` | 404 | Session doesn't exist |
| `SESSION_EXPIRED` | 410 | Session has expired |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `MESSAGE_TOO_LONG` | 400 | Message exceeds limit |
| `CONTEXT_TOO_LARGE` | 400 | Context data too large |
| `TOOL_NOT_FOUND` | 404 | Requested tool doesn't exist |
| `TOOL_EXECUTION_FAILED` | 500 | Tool execution error |
| `MODEL_UNAVAILABLE` | 503 | AI model is unavailable |
| `MCP_SERVER_ERROR` | 502 | MCP server error |

## 📊 Rate Limiting

### Limits
- **Chat Messages**: 60 per minute per user
- **Tool Executions**: 30 per minute per user
- **Session Creates**: 10 per hour per user
- **History Requests**: 100 per minute per user

### Headers
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1701432000
```

## 🔄 Webhooks (Future)

### Event Types
```json
{
  "event": "session.created" | "message.sent" | "tool.executed" | "error.occurred",
  "data": {
    // Event-specific data
  },
  "timestamp": "2024-12-01T12:00:00Z",
  "session_id": "string",
  "user_id": "string"
}
```

### Webhook Configuration
```http
POST /api/agent/webhooks

Request:
{
  "url": "https://your-server.com/webhook",
  "events": ["session.created", "tool.executed"],
  "secret": "webhook_secret_key"
}
```

## 🧪 Testing Endpoints

### Test Connection
```http
GET /api/agent/test/ping

Response:
{
  "message": "pong",
  "timestamp": string
}
```

### Test Tool
```http
POST /api/agent/test/tool

Request:
{
  "tool_name": string,
  "arguments": object,
  "mock_response": any
}

Response:
{
  "validation": {
    "valid": boolean,
    "errors": string[]
  },
  "would_execute": object,
  "mock_result": any
}
```

## 📝 OpenAPI Specification

Full OpenAPI 3.0 specification available at:
```
GET /api/agent/openapi.json
```

Interactive documentation:
```
GET /api/agent/docs
```