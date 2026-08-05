# MCP Server Authentication Strategy

**Project**: Luminari Wilderness Editor MCP Server  
**Document**: Authentication Strategy  
**Version**: 1.1  
**Date**: August 15, 2025  

## 🔐 **Multi-Key Authentication Architecture**

### **Key Types and Usage**

#### **1. Backend API Key (Existing)**
```bash
WILDEDITOR_API_KEY=<redacted>
```
- **Purpose**: Direct access to backend REST API
- **Used by**: Frontend, direct API clients, testing tools
- **Permissions**: Full CRUD operations on regions, paths, points
- **Rate Limit**: Standard API rate limiting (10 req/s)

#### **2. MCP Server Key (New)**
```bash
WILDEDITOR_MCP_KEY=<redacted>
```
- **Purpose**: Access to MCP server AI operations
- **Used by**: AI agents, Claude, GPT, custom AI tools
- **Permissions**: MCP tools, resources, and prompts
- **Rate Limit**: AI-specific limiting (5 req/s, longer timeouts)

#### **3. MCP-to-Backend Key (New)**
```bash
WILDEDITOR_MCP_BACKEND_KEY=<redacted>
```
- **Purpose**: MCP server accessing backend API for data
- **Used by**: MCP server internal operations
- **Permissions**: Read-only or limited write access to backend
- **Rate Limit**: Internal service rate limiting (20 req/s)

### **Authentication Flow Diagram**
```
AI Agent/Client
    ↓ [MCP_KEY]
MCP Server → Validates MCP_KEY
    ↓ [MCP_BACKEND_KEY] 
Backend API → Validates MCP_BACKEND_KEY
    ↓
Database Operations

Frontend/API Client
    ↓ [API_KEY]
Backend API → Validates API_KEY
    ↓
Database Operations
```

## 🛠️ **Development Configuration**

### **Local MCP + Remote Backend Setup**

#### **Environment Configuration**
```bash
# apps/mcp/.env.development
# MCP Server Configuration
NODE_ENV=development
MCP_PORT=8001
WILDEDITOR_MCP_KEY=<redacted>

# Remote Backend Access
BACKEND_URL=https://your-production-backend.com
WILDEDITOR_MCP_BACKEND_KEY=<redacted>

# Database Access (for direct operations)
MYSQL_DATABASE_URL=mysql+pymysql://user:<redacted>@remote-db:3306/wildeditor

# AI Service Configuration
OPENAI_API_KEY=<redacted>
AI_SERVICE_PROVIDER=openai

# Development Features
LOG_LEVEL=DEBUG
ENABLE_DOCS=true
ENABLE_RELOAD=true
```

#### **Hybrid Development Architecture**
```
Local Development Machine:
┌─────────────────────────────────┐
│  MCP Server (Port 8001)         │
│  ├── AI Tools & Resources       │
│  ├── Local debugging            │
│  └── Hot reload enabled         │
└─────────────────┬───────────────┘
                  │ [MCP_BACKEND_KEY]
                  ↓ HTTPS
Remote Production Server:
┌─────────────────────────────────┐
│  Backend API (Port 8000)        │
│  ├── Production data            │
│  ├── Stable API endpoints       │
│  └── Real wilderness data       │
└─────────────────┬───────────────┘
                  │
                  ↓
┌─────────────────────────────────┐
│  MySQL Database                 │
│  └── Production wilderness data │
└─────────────────────────────────┘
```

## 🔧 **Implementation Details**

### **Updated Authentication Package**
```python
# packages/auth/src/auth_types.py
from enum import Enum
from typing import Set

class KeyType(Enum):
    BACKEND_API = "backend_api"
    MCP_OPERATIONS = "mcp_operations" 
    MCP_BACKEND_ACCESS = "mcp_backend_access"

class MultiKeyAuth:
    def __init__(self, key_configs: dict[KeyType, Set[str]]):
        self.key_configs = key_configs
    
    async def verify_key(self, api_key: str, required_type: KeyType) -> bool:
        """Verify API key for specific operation type"""
        if required_type not in self.key_configs:
            return False
        return api_key in self.key_configs[required_type]
    
    def get_backend_key(self) -> str:
        """Get MCP-to-backend communication key"""
        return os.getenv("WILDEDITOR_MCP_BACKEND_KEY")
```

### **MCP Server Configuration**
```python
# apps/mcp/src/config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Server Configuration
    node_env: str = "development"
    mcp_port: int = 8001
    
    # Authentication Keys
    mcp_key: str  # For MCP operations
    mcp_backend_key: str  # For accessing backend API
    
    # Backend Communication
    backend_url: str = "http://localhost:8000"
    backend_timeout: int = 30
    
    # Database (for direct access when needed)
    mysql_database_url: Optional[str] = None
    
    # AI Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ai_service_provider: str = "openai"
    
    # Development
    log_level: str = "INFO"
    enable_docs: bool = False
    enable_reload: bool = False
    
    class Config:
        env_file = ".env"
        env_prefix = "WILDEDITOR_"

settings = Settings()
```

### **Backend API Client for MCP**
```python
# apps/mcp/src/services/backend_client.py
import httpx
from typing import Dict, Any, Optional
from ..config.settings import settings

class BackendAPIClient:
    def __init__(self):
        self.base_url = settings.backend_url
        self.api_key = settings.mcp_backend_key
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def get_region(self, region_vnum: int) -> Optional[Dict[str, Any]]:
        """Get region data from backend API"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/regions/{region_vnum}",
                headers=self.headers,
                timeout=settings.backend_timeout
            )
            return response.json() if response.status_code == 200 else None
    
    async def get_paths_in_zone(self, zone_vnum: int) -> list[Dict[str, Any]]:
        """Get all paths in a zone from backend API"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/paths",
                params={"zone_vnum": zone_vnum},
                headers=self.headers,
                timeout=settings.backend_timeout
            )
            return response.json() if response.status_code == 200 else []
    
    async def create_region(self, region_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create region via backend API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/regions",
                json=region_data,
                headers=self.headers,
                timeout=settings.backend_timeout
            )
            return response.json() if response.status_code == 201 else None
```

## 🚀 **Development Workflow**

### **Setup Local MCP Development**
```bash
# 1. Clone repository
git clone https://github.com/LuminariMUD/wildeditor.git
cd wildeditor

# 2. Setup MCP development environment
cd apps/mcp
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure for remote backend access
cp .env.example .env.development
# Edit .env.development with remote backend URL and keys

# 5. Start local MCP server
python -m src.main --env-file .env.development
```

### **Environment File Template**
```bash
# apps/mcp/.env.development
# MCP Server Settings
NODE_ENV=development
MCP_PORT=8001
WILDEDITOR_MCP_KEY=<redacted>

# Remote Backend Access (CHANGE THESE)
BACKEND_URL=https://your-backend-domain.com
WILDEDITOR_MCP_BACKEND_KEY=<redacted>

# Optional: Direct database access for complex operations
# MYSQL_DATABASE_URL=mysql+pymysql://user:<redacted>@remote-host:3306/wildeditor

# AI Service Configuration
OPENAI_API_KEY=<redacted>
AI_SERVICE_PROVIDER=openai

# Development Features
LOG_LEVEL=DEBUG
ENABLE_DOCS=true
ENABLE_RELOAD=true
```

### **Testing Remote Connection**
```bash
# Test MCP server can reach remote backend
curl -H "X-API-Key: <redacted>" \
     https://your-backend-domain.com/api/health

# Test local MCP server is running
curl http://localhost:8001/health

# Test MCP server can access backend through its client
curl -H "X-API-Key: <redacted>" \
     http://localhost:8001/mcp/tools/test-backend-connection
```

## 📊 **Key Management Strategy**

### **Production Key Configuration**
```bash
# Production server environment
WILDEDITOR_API_KEY=<redacted>
WILDEDITOR_MCP_KEY=<redacted>
WILDEDITOR_MCP_BACKEND_KEY=<redacted>
```

### **Development Key Configuration**
```bash
# Local development
WILDEDITOR_API_KEY=<redacted>
WILDEDITOR_MCP_KEY=<redacted>
WILDEDITOR_MCP_BACKEND_KEY=<redacted>
```

### **Key Rotation Strategy**
1. **Regular Rotation**: Rotate keys every 90 days
2. **Immediate Rotation**: If any key is compromised
3. **Graduated Rollout**: Deploy new keys before removing old ones
4. **Monitoring**: Track key usage and detect anomalies

## 🔍 **Monitoring and Auditing**

### **Authentication Logging**
```python
# Log all authentication attempts with key type
logger.info(
    "authentication_attempt",
    key_type=key_type.value,
    success=is_valid,
    client_ip=request.client.host,
    endpoint=request.url.path
)
```

### **Usage Analytics**
- Track API usage by key type
- Monitor AI operation costs by MCP key
- Alert on unusual access patterns
- Generate usage reports for cost allocation

## 🚨 **Security Best Practices**

### **Key Security**
- Use strong, randomly generated keys (32+ characters)
- Store keys in environment variables, never in code
- Use different keys for different environments
- Implement key rotation procedures

### **Access Control**
- Principle of least privilege for each key type
- Regular audit of key permissions
- Monitor for suspicious activity
- Implement rate limiting per key type

### **Communication Security**
- Always use HTTPS for remote backend communication
- Validate SSL certificates
- Implement request timeouts
- Add retry logic with exponential backoff

---

**Document Version**: 1.1  
**Last Updated**: August 15, 2025  
**Addresses**: Separate keys + hybrid development
