# MCP Server Architecture

**Project**: Luminari Wilderness Editor MCP Server  
**Document**: Technical Architecture  
**Version**: 1.0  
**Date**: August 15, 2025  

## 🏗️ Architecture Overview

The MCP (Model Context Protocol) server extends the Luminari Wilderness Editor with AI-powered capabilities while maintaining architectural consistency with the existing backend system.

### **Design Principles**

1. **Service Separation**: MCP server as independent service with clear boundaries
2. **Shared Components**: Reuse authentication, database models, and validation logic
3. **Same-Server Deployment**: Deploy both services on same physical server with container isolation
4. **Protocol Compliance**: Full MCP protocol implementation for AI agent integration
5. **Domain Integration**: Deep integration with LuminariMUD wilderness system knowledge

## 🌐 System Architecture

### **High-Level Architecture**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Internet / External Clients                      │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────────────────────┐
│                    Same Physical Server                                      │
│                         │                                                   │
│  ┌─────────────────────┬┴──────────────────────────────┐                   │
│  │        Nginx Reverse Proxy (Port 80/443)           │                   │
│  │  ┌─────────────────┬─────────────────────────────┐  │                   │
│  │  │  /api/*         │        /mcp/*              │  │                   │
│  │  └─────────────────┴─────────────────────────────┘  │                   │
│  └─────────────────────┬─────────────────┬─────────────┘                   │
│                        │                 │                                 │
│  ┌─────────────────────┴─────────────────┴─────────────┐                   │
│  │              Docker Network (wildeditor)            │                   │
│  │                                                     │                   │
│  │  ┌──────────────────┐  ┌──────────────────────────┐ │                   │
│  │  │ Backend Container│  │   MCP Server Container   │ │                   │
│  │  │   (Port 8000)    │  │      (Port 8001)        │ │                   │
│  │  │                  │  │                         │ │                   │
│  │  │ - REST API       │  │ - MCP Protocol          │ │                   │
│  │  │ - Authentication │  │ - AI Tools              │ │                   │
│  │  │ - Database Ops   │  │ - Domain Knowledge      │ │                   │
│  │  │ - CRUD Operations│  │ - Spatial Analysis      │ │                   │
│  │  └──────────────────┘  └──────────────────────────┘ │                   │
│  │           │                        │                │                   │
│  │           └────────────┬───────────┘                │                   │
│  └─────────────────────────┼─────────────────────────────┘                   │
│                            │                                                 │
│  ┌─────────────────────────┴─────────────────────────────┐                   │
│  │                 Shared Components                     │                   │
│  │                                                       │                   │
│  │  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐ │                   │
│  │  │     Auth     │  │  Database   │  │   Models     │ │                   │
│  │  │   Package    │  │   Models    │  │ & Schemas    │ │                   │
│  │  └──────────────┘  └─────────────┘  └──────────────┘ │                   │
│  └─────────────────────────┬─────────────────────────────┘                   │
│                            │                                                 │
│  ┌─────────────────────────┴─────────────────────────────┐                   │
│  │                   MySQL Database                      │                   │
│  │                                                       │                   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │                   │
│  │  │ region_data │  │ path_data   │  │ Other Tables│   │                   │
│  │  │ (Spatial)   │  │ (Spatial)   │  │             │   │                   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘   │                   │
│  └─────────────────────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┐
```

## 🧩 Component Architecture

### **MCP Server Internal Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server (Port 8001)                   │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                FastAPI Application                      │ │
│  │                                                         │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │ │
│  │  │   Router    │  │ Middleware  │  │   Config    │     │ │
│  │  │   Layer     │  │   Layer     │  │  Management │     │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                 │
│  ┌─────────────────────────┴─────────────────────────────────┐ │
│  │                  MCP Protocol Layer                      │ │
│  │                                                         │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │ │
│  │  │    Tools    │  │  Resources  │  │   Prompts   │     │ │
│  │  │             │  │             │  │             │     │ │
│  │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │     │ │
│  │  │ │ Region  │ │  │ │Wilderness│ │  │ │ Region  │ │     │ │
│  │  │ │ Tools   │ │  │ │ Context │ │  │ │Creation │ │     │ │
│  │  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │     │ │
│  │  │             │  │             │  │             │     │ │
│  │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │     │ │
│  │  │ │  Path   │ │  │ │ Schema  │ │  │ │  Path   │ │     │ │
│  │  │ │ Tools   │ │  │ │Reference│ │  │ │Planning │ │     │ │
│  │  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │     │ │
│  │  │             │  │             │  │             │     │ │
│  │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │     │ │
│  │  │ │Spatial  │ │  │ │Examples │ │  │ │Analysis │ │     │ │
│  │  │ │Analysis │ │  │ │& Guides │ │  │ │ Prompts │ │     │ │
│  │  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │     │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                 │
│  ┌─────────────────────────┴─────────────────────────────────┐ │
│  │                    Service Layer                         │ │
│  │                                                         │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │ │
│  │  │   Region    │  │    Path     │  │   Spatial   │     │ │
│  │  │   Service   │  │   Service   │  │   Service   │     │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │ │
│  │                                                         │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │ │
│  │  │    AI       │  │ Validation  │  │ Knowledge   │     │ │
│  │  │ Integration │  │   Service   │  │   Base      │     │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                 │
│  ┌─────────────────────────┴─────────────────────────────────┐ │
│  │                   Data Access Layer                      │ │
│  │                                                         │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │ │
│  │  │ Database    │  │   Shared    │  │   Cache     │     │ │
│  │  │ Connector   │  │   Models    │  │  Manager    │     │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📂 Directory Structure

### **Project Structure**
```
wildeditor/
├── apps/
│   ├── frontend/                    # Existing React frontend
│   ├── backend/                     # Existing FastAPI backend
│   └── mcp/                        # NEW: MCP Server
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── pyproject.toml
│       ├── README.md
│       ├── src/
│       │   ├── __init__.py
│       │   ├── main.py             # FastAPI app entry point
│       │   ├── server.py           # MCP server implementation
│       │   ├── config/
│       │   │   ├── __init__.py
│       │   │   └── settings.py     # Configuration management
│       │   ├── routers/
│       │   │   ├── __init__.py
│       │   │   ├── health.py       # Health check endpoints
│       │   │   └── mcp.py          # MCP protocol endpoints
│       │   ├── mcp/
│       │   │   ├── __init__.py
│       │   │   ├── protocol.py     # MCP protocol implementation
│       │   │   ├── tools/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── base.py     # Base tool class
│       │   │   │   ├── region_tools.py
│       │   │   │   ├── path_tools.py
│       │   │   │   ├── spatial_tools.py
│       │   │   │   └── validation_tools.py
│       │   │   ├── resources/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── base.py     # Base resource class
│       │   │   │   ├── wilderness_context.py
│       │   │   │   ├── schema_resources.py
│       │   │   │   └── examples.py
│       │   │   └── prompts/
│       │   │       ├── __init__.py
│       │   │       ├── base.py     # Base prompt class
│       │   │       ├── region_prompts.py
│       │   │       ├── path_prompts.py
│       │   │       └── analysis_prompts.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── region_service.py
│       │   │   ├── path_service.py
│       │   │   ├── spatial_service.py
│       │   │   ├── ai_service.py
│       │   │   └── validation_service.py
│       │   ├── utils/
│       │   │   ├── __init__.py
│       │   │   ├── spatial.py      # Spatial calculation utilities
│       │   │   ├── ai_client.py    # AI service integration
│       │   │   └── formatters.py   # Data formatting utilities
│       │   └── shared/
│       │       ├── __init__.py
│       │       ├── database.py     # Database connection
│       │       ├── models.py       # Shared database models
│       │       └── schemas.py      # Shared Pydantic schemas
│       └── tests/
│           ├── __init__.py
│           ├── conftest.py         # Test configuration
│           ├── test_tools/
│           ├── test_resources/
│           ├── test_prompts/
│           ├── test_services/
│           └── test_integration/
│
├── packages/                       # NEW: Shared packages
│   └── auth/                      # Shared authentication
│       ├── __init__.py
│       ├── pyproject.toml
│       ├── src/
│       │   ├── __init__.py
│       │   ├── api_key.py         # API key validation
│       │   ├── middleware.py      # FastAPI middleware
│       │   ├── exceptions.py      # Authentication exceptions
│       │   └── types.py           # Type definitions
│       └── tests/
│           ├── __init__.py
│           └── test_auth.py
│
├── docs/
│   └── mcp/                       # MCP documentation
│       ├── README.md
│       ├── MCP_IMPLEMENTATION_PLAN.md
│       ├── ARCHITECTURE.md        # This document
│       ├── DEPLOYMENT.md
│       ├── API_REFERENCE.md
│       ├── DEVELOPMENT_SETUP.md
│       ├── AUTHENTICATION.md
│       ├── TESTING.md
│       ├── MONITORING.md
│       ├── TROUBLESHOOTING.md
│       └── CHANGELOG.md
│
└── deployment/                    # Deployment configurations
    ├── docker-compose.same-server.yml
    ├── nginx.conf
    └── scripts/
        ├── deploy-same-server.sh
        └── health-check.sh
```

## 🔧 Technology Stack

### **MCP Server Stack**
- **Framework**: FastAPI 0.104+ (same as backend)
- **Python**: 3.11+ (same as backend)
- **MCP Protocol**: `mcp` Python package
- **AI Integration**: OpenAI/Anthropic client libraries
- **Database**: SQLAlchemy + PyMySQL (shared with backend)
- **Spatial**: GeoAlchemy2 (shared with backend)
- **Validation**: Pydantic 2.0+ (shared with backend)
- **Testing**: pytest + pytest-asyncio

### **Shared Components Stack**
- **Authentication**: Custom API key package
- **Database Models**: SQLAlchemy models
- **Schemas**: Pydantic schemas
- **Configuration**: pydantic-settings

### **Infrastructure Stack**
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **CI/CD**: GitHub Actions
- **Monitoring**: Docker health checks + custom metrics

## 🔌 Integration Patterns

### **Database Integration**
```python
# Shared database session factory
from packages.auth import get_db_session
from apps.backend.src.models import Region, Path

# In MCP server
class RegionService:
    def __init__(self, db_session):
        self.db = db_session
    
    async def analyze_region(self, region_vnum: int):
        region = self.db.query(Region).filter(Region.vnum == region_vnum).first()
        # Analysis logic here
        return analysis_result
```

### **Authentication Integration**
```python
# Shared authentication middleware
from packages.auth import APIKeyAuth

# In both backend and MCP
auth = APIKeyAuth(valid_api_keys=set(os.getenv("API_KEYS", "").split(",")))

@app.middleware("http")
async def authenticate_request(request: Request, call_next):
    return await auth.middleware(request, call_next)
```

### **Model Sharing**
```python
# Shared models package
from apps.backend.src.models.region import Region
from apps.backend.src.models.path import Path

# Used in both services with same schema
```

## 🌊 Data Flow Architecture

### **MCP Tool Execution Flow**
```
1. AI Agent Request → MCP Server
2. Tool Authentication → Shared Auth Package  
3. Tool Execution → Service Layer
4. Database Query → Shared Models
5. Spatial Analysis → GeoAlchemy2 + MySQL
6. AI Processing → External AI Service
7. Result Validation → Shared Schemas
8. Response → MCP Protocol → AI Agent
```

### **Resource Request Flow**
```
1. AI Agent Request → MCP Server
2. Resource Lookup → Resource Registry
3. Content Generation → Knowledge Base
4. Schema Validation → Shared Schemas
5. Response → MCP Protocol → AI Agent
```

### **Prompt Generation Flow**
```
1. AI Agent Request → MCP Server
2. Context Analysis → Domain Knowledge
3. Prompt Template → Prompt Service
4. Variable Substitution → Template Engine
5. Response → MCP Protocol → AI Agent
```

## 🔒 Security Architecture

### **Authentication Flow**
```
External Request → Nginx → Service → Shared Auth → API Key Validation
```

### **Authorization Matrix**
| Operation | Backend API | MCP Server | Authentication Required |
|-----------|-------------|------------|------------------------|
| Read Operations | ✅ | ✅ | Yes |
| Write Operations | ✅ | ✅ | Yes |
| AI Tools | ❌ | ✅ | Yes |
| Health Checks | ✅ | ✅ | No |

### **Container Security**
- Services run in separate containers
- Internal Docker network communication
- No direct external access to service ports
- Environment variable for secrets

### **Rate Limiting**
- Nginx level rate limiting
- Different limits for API vs MCP endpoints
- AI operation specific throttling

## 📈 Scalability Design

### **Current Design (Same Server)**
- Suitable for MVP and medium-scale usage
- Single point of failure but low complexity
- Easy monitoring and debugging

### **Future Scaling Options**

#### **Horizontal Scaling**
```
Frontend → Load Balancer → [Backend1, Backend2, ...]
                      → [MCP1, MCP2, ...]
```

#### **Vertical Scaling**
- Increase server resources
- Optimize container resource allocation
- Database connection pooling

#### **Service Separation**
- Move MCP to dedicated servers
- Database clustering
- CDN for static resources

## 🔍 Monitoring Architecture

### **Health Check Strategy**
```
Nginx → /health        → Backend Health
      → /mcp-health    → MCP Health
      → /status        → Overall System Status
```

### **Logging Strategy**
```
Application Logs → Docker Logs → Log Aggregation
Error Tracking  → Sentry       → Alert System
Metrics         → Prometheus   → Grafana Dashboard
```

### **Performance Monitoring**
- Response time tracking
- Database query performance
- AI operation latency
- Resource utilization metrics

## 🧪 Testing Architecture

### **Testing Pyramid**
```
E2E Tests         (Integration workflows)
    ↑
Service Tests     (API + MCP protocol)
    ↑  
Unit Tests        (Tools, Resources, Prompts)
```

### **Test Environment**
- Separate test database
- Mock AI services for testing
- Docker compose for test environment
- Automated CI/CD testing

## 📋 Implementation Considerations

### **Performance Considerations**
- Connection pooling for database
- Caching for frequently accessed resources
- Async operations for AI calls
- Request/response size optimization

### **Reliability Considerations**
- Graceful degradation if AI services unavailable
- Database connection retry logic
- Health checks and automatic restarts
- Comprehensive error handling

### **Maintenance Considerations**
- Shared component versioning
- Database migration coordination
- Deployment rollback procedures
- Monitoring and alerting setup

---

**Document Version**: 1.0  
**Last Updated**: August 15, 2025  
**Next Review**: Phase 2 completion
