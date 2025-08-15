# Wildeditor Authentication Package

Shared authentication package providing multi-key API authentication for both the Wildeditor backend and MCP server.

## 🎯 Overview

This package provides consistent API key authentication across both the FastAPI backend and MCP server, ensuring security and maintaining a single source of truth for authentication logic.

## Features

- **Multi-Key Support**: Three distinct API key types for different services
- **FastAPI Integration**: Built-in dependencies and middleware
- **Type Safety**: Full typing support with Pydantic
- **Comprehensive Testing**: Full test coverage with pytest

## Key Types

- `BACKEND_API`: Direct backend API access
- `MCP_OPERATIONS`: MCP server operations  
- `MCP_BACKEND_ACCESS`: MCP server accessing backend

## Quick Start

```python
from wildeditor_auth import MultiKeyAuth, RequireBackendKey
from fastapi import FastAPI, Depends

app = FastAPI()

@app.get("/protected")
async def protected_endpoint(authenticated: bool = RequireBackendKey):
    return {"message": "Access granted"}
```

## Environment Variables

```bash
WILDEDITOR_API_KEY=your-backend-api-key
WILDEDITOR_MCP_KEY=your-mcp-operations-key  
WILDEDITOR_MCP_BACKEND_KEY=your-mcp-backend-access-key
```

## Installation

```bash
pip install -e .
```

## Testing

```bash
pytest
```

## 🏗️ Architecture

```
packages/auth/
├── src/
│   ├── __init__.py
│   ├── api_key.py          # Core API key validation
│   ├── middleware.py       # FastAPI middleware
│   ├── exceptions.py       # Authentication exceptions
│   └── types.py           # Type definitions
└── tests/
    └── test_auth.py       # Authentication tests
```

## 🚀 Usage

### Basic API Key Authentication
```python
from packages.auth import APIKeyAuth

# Initialize with valid API keys
auth = APIKeyAuth(valid_api_keys={"your-api-key-1", "your-api-key-2"})

# In FastAPI dependency
from fastapi import Depends

async def protected_endpoint(authenticated: bool = Depends(auth.verify_api_key)):
    return {"message": "Access granted"}
```

### FastAPI Middleware Integration
```python
from fastapi import FastAPI
from packages.auth import AuthMiddleware

app = FastAPI()

# Add authentication middleware
app.add_middleware(
    AuthMiddleware,
    api_keys={"your-api-key"},
    exclude_paths={"/health", "/docs"}  # Public endpoints
)
```

### Environment Configuration
```python
import os
from packages.auth import APIKeyAuth

# Load API keys from environment
api_keys = set(os.getenv("WILDEDITOR_API_KEY", "").split(","))
auth = APIKeyAuth(valid_api_keys=api_keys)
```

## 🔧 Configuration

### Environment Variables
```bash
# Single API key
WILDEDITOR_API_KEY=your-secure-api-key

# Multiple API keys (comma-separated)
WILDEDITOR_API_KEY=key1,key2,key3
```

### Security Best Practices
- Use strong, randomly generated API keys
- Rotate API keys regularly
- Store API keys securely (environment variables, not in code)
- Use HTTPS in production
- Implement rate limiting

## 🧪 Testing

```bash
# Run authentication tests
cd packages/auth
pytest tests/

# Test with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📚 API Reference

### `APIKeyAuth`
Core authentication class for API key validation.

```python
class APIKeyAuth:
    def __init__(self, valid_api_keys: set[str])
    async def verify_api_key(self, x_api_key: Optional[str] = Header(None)) -> bool
    def is_valid_key(self, api_key: str) -> bool
```

### `AuthMiddleware`
FastAPI middleware for automatic authentication.

```python
class AuthMiddleware:
    def __init__(self, api_keys: set[str], exclude_paths: set[str] = None)
    async def __call__(self, request: Request, call_next)
```

### Exceptions
```python
class AuthenticationError(HTTPException)
class InvalidAPIKeyError(AuthenticationError)
class MissingAPIKeyError(AuthenticationError)
```

## 🔒 Security Features

- **API Key Validation**: Secure comparison of provided keys
- **Header-based Authentication**: Uses `X-API-Key` header
- **Path Exclusion**: Exclude public endpoints from authentication
- **Error Handling**: Consistent error responses
- **Type Safety**: Full type hints and validation

## 🚀 Integration Examples

### Backend Integration
```python
# apps/backend/src/main.py
from fastapi import FastAPI
from packages.auth import APIKeyAuth
import os

app = FastAPI()

# Setup authentication
api_keys = set(os.getenv("WILDEDITOR_API_KEY", "").split(","))
auth = APIKeyAuth(valid_api_keys=api_keys)

# Use in protected endpoints
@app.get("/api/protected")
async def protected_endpoint(authenticated: bool = Depends(auth.verify_api_key)):
    return {"message": "Access granted"}
```

### MCP Server Integration
```python
# apps/mcp/src/main.py
from fastapi import FastAPI
from packages.auth import APIKeyAuth
import os

app = FastAPI()

# Same authentication setup
api_keys = set(os.getenv("WILDEDITOR_API_KEY", "").split(","))
auth = APIKeyAuth(valid_api_keys=api_keys)

# Use in MCP endpoints
@app.post("/mcp/tools/analyze-region")
async def analyze_region(authenticated: bool = Depends(auth.verify_api_key)):
    return {"analysis": "AI-powered region analysis"}
```

---

**Status**: Planning Phase  
**Version**: 1.0.0  
**Last Updated**: August 15, 2025
