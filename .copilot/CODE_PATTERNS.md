# Code Patterns and Examples for MCP Implementation

**For AI assistants implementing the MCP server**

## 🏗️ **EXISTING CODE PATTERNS TO FOLLOW**

### **FastAPI Application Structure**
```python
# Follow this pattern from apps/backend/src/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Wildeditor MCP Server",
    description="AI-powered Model Context Protocol server",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, tags=["Health"])
```

### **Authentication Middleware Pattern**
```python
# Current backend pattern in apps/backend/src/middleware/auth.py
from fastapi import HTTPException, status, Depends, Header
from typing import Optional

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key or x_api_key != os.getenv("WILDEDITOR_API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return True

# Use in protected endpoints
@app.get("/api/protected")
async def protected_endpoint(authenticated: bool = Depends(verify_api_key)):
    return {"message": "Access granted"}
```

### **Configuration Pattern**
```python
# Follow this pattern from backend configuration
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Server settings
    node_env: str = "development"
    port: int = 8001
    
    # Authentication
    api_key: str
    mcp_key: str
    mcp_backend_key: str
    
    # External services
    backend_url: str = "http://localhost:8000"
    mysql_database_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_prefix = "WILDEDITOR_"

settings = Settings()
```

## 🔐 **AUTHENTICATION IMPLEMENTATION**

### **Multi-Key Authentication Class**
```python
# packages/auth/src/api_key.py
from enum import Enum
from typing import Set, Optional
from fastapi import HTTPException, status, Header
import os

class KeyType(Enum):
    BACKEND_API = "backend_api"
    MCP_OPERATIONS = "mcp_operations"
    MCP_BACKEND_ACCESS = "mcp_backend_access"

class MultiKeyAuth:
    def __init__(self):
        self.keys = {
            KeyType.BACKEND_API: {os.getenv("WILDEDITOR_API_KEY", "")},
            KeyType.MCP_OPERATIONS: {os.getenv("WILDEDITOR_MCP_KEY", "")},
            KeyType.MCP_BACKEND_ACCESS: {os.getenv("WILDEDITOR_MCP_BACKEND_KEY", "")}
        }
    
    async def verify_key(self, api_key: str, key_type: KeyType) -> bool:
        if not api_key or api_key not in self.keys.get(key_type, set()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid or missing {key_type.value} API key"
            )
        return True
    
    # Dependency functions
    async def verify_mcp_key(self, x_api_key: Optional[str] = Header(None)):
        return await self.verify_key(x_api_key, KeyType.MCP_OPERATIONS)
    
    async def verify_backend_key(self, x_api_key: Optional[str] = Header(None)):
        return await self.verify_key(x_api_key, KeyType.BACKEND_API)
```

### **FastAPI Middleware Implementation**
```python
# packages/auth/src/middleware.py
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from .api_key import MultiKeyAuth, KeyType

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exclude_paths: set = None):
        super().__init__(app)
        self.auth = MultiKeyAuth()
        self.exclude_paths = exclude_paths or {"/health", "/docs", "/redoc", "/openapi.json"}
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        api_key = request.headers.get("X-API-Key")
        
        # Determine key type based on path
        if request.url.path.startswith("/mcp/"):
            key_type = KeyType.MCP_OPERATIONS
        else:
            key_type = KeyType.BACKEND_API
        
        try:
            await self.auth.verify_key(api_key, key_type)
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        
        return await call_next(request)
```

## 🔧 **MCP SERVER PATTERNS**

### **Health Check Router**
```python
# apps/mcp/src/routers/health.py
from fastapi import APIRouter, Depends
from ..auth import MultiKeyAuth

router = APIRouter()
auth = MultiKeyAuth()

@router.get("/health")
async def health_check():
    """Public health check endpoint"""
    return {
        "status": "healthy",
        "service": "wildeditor-mcp",
        "version": "1.0.0"
    }

@router.get("/mcp-health")
async def mcp_health_check(authenticated: bool = Depends(auth.verify_mcp_key)):
    """Authenticated health check for MCP operations"""
    return {
        "status": "healthy",
        "service": "wildeditor-mcp",
        "version": "1.0.0",
        "authenticated": True
    }
```

### **Backend API Client Pattern**
```python
# apps/mcp/src/services/backend_client.py
import httpx
from typing import Dict, Any, Optional
from ..config.settings import settings

class BackendAPIClient:
    def __init__(self):
        self.base_url = settings.backend_url
        self.headers = {
            "X-API-Key": settings.mcp_backend_key,
            "Content-Type": "application/json"
        }
        self.timeout = 30.0
    
    async def get(self, endpoint: str) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Backend API error: {e}")
                return None
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}{endpoint}",
                    json=data,
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Backend API error: {e}")
                return None
```

## 🧪 **TESTING PATTERNS**

### **Test Configuration**
```python
# apps/mcp/tests/conftest.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    return {"X-API-Key": "test-mcp-key"}

@pytest.fixture
def backend_auth_headers():
    return {"X-API-Key": "test-backend-key"}
```

### **Authentication Tests**
```python
# packages/auth/tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends
from src.api_key import MultiKeyAuth, KeyType

def test_valid_mcp_key():
    auth = MultiKeyAuth()
    # Test implementation here

def test_invalid_mcp_key():
    # Test invalid key handling

def test_missing_api_key():
    # Test missing key handling
```

## 📦 **DOCKER PATTERNS**

### **Dockerfile Pattern**
```dockerfile
# apps/mcp/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    MCP_PORT=8001

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy shared packages first
COPY packages/auth/ ./packages/auth/
RUN pip install -e ./packages/auth/

# Copy and install MCP requirements
COPY apps/mcp/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP application
COPY apps/mcp/src/ ./src/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## 🚀 **DEVELOPMENT SCRIPT PATTERNS**

### **Development Server**
```python
# apps/mcp/run_dev.py
import uvicorn
import os
from pathlib import Path

if __name__ == "__main__":
    # Load development environment
    env_file = Path(__file__).parent / ".env.development"
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=int(os.getenv("MCP_PORT", 8001)),
        reload=True,
        env_file=str(env_file) if env_file.exists() else None,
        log_level="debug"
    )
```

## 📋 **ERROR HANDLING PATTERNS**

### **Custom Exceptions**
```python
# packages/auth/src/exceptions.py
from fastapi import HTTPException, status

class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class InvalidAPIKeyError(AuthenticationError):
    def __init__(self, key_type: str = "API"):
        super().__init__(detail=f"Invalid {key_type} key")

class MissingAPIKeyError(AuthenticationError):
    def __init__(self):
        super().__init__(detail="Missing API key in X-API-Key header")
```

---

**Use these patterns to maintain consistency with the existing codebase and follow established conventions.**
