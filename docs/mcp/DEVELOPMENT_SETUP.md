# MCP Server Development Setup

**Project**: Luminari Wilderness Editor MCP Server  
**Document**: Development Setup Guide  
**Version**: 1.0  
**Date**: August 15, 2025  

## 🎯 Overview

This guide covers setting up a local development environment for the MCP server, including all dependencies, configuration, and testing setup.

## 📋 Prerequisites

### **System Requirements**
- **Python**: 3.11 or higher
- **Git**: Latest version
- **Docker**: 20.10+ (for containerized development)
- **MySQL**: 8.0+ (or access to existing database)

### **Development Tools (Recommended)**
- **VS Code**: With Python and Docker extensions
- **Postman/Insomnia**: For API testing
- **MySQL Workbench**: For database management
- **Git CLI or GUI**: For version control

## 🚀 Quick Start

### **1. Clone Repository**
```bash
git clone https://github.com/LuminariMUD/wildeditor.git
cd wildeditor
```

### **2. Setup Python Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Verify Python version
python --version  # Should be 3.11+
```

### **3. Install Dependencies**
```bash
# Install MCP server dependencies
cd apps/mcp
pip install -r requirements.txt

# Install shared authentication package (in development mode)
cd ../../packages/auth
pip install -e .

# Return to MCP directory
cd ../../apps/mcp
```

### **4. Environment Configuration**
```bash
# Create environment file for local development
cp .env.example .env.development

# Configure for hybrid development (local MCP + remote backend)
# Edit .env.development with your configuration:

# MCP Server Settings
NODE_ENV=development
MCP_PORT=8001
WILDEDITOR_MCP_KEY=dev-mcp-key-12345

# Remote Backend Access (for hybrid development)
BACKEND_URL=https://your-backend-domain.com  # Your production backend
WILDEDITOR_MCP_BACKEND_KEY=your-mcp-backend-access-key

# Optional: Direct database access for complex operations
# MYSQL_DATABASE_URL=mysql+pymysql://user:pass@remote-host:3306/wildeditor

# AI Service Configuration
OPENAI_API_KEY=your-openai-api-key
AI_SERVICE_PROVIDER=openai

# Development Features
LOG_LEVEL=DEBUG
ENABLE_DOCS=true
ENABLE_RELOAD=true
```

### **5. Backend Connection Setup**

#### **Option A: Hybrid Development (Recommended)**
```bash
# Test connection to remote backend
curl -H "X-API-Key: your-mcp-backend-key" \
     https://your-backend-domain.com/api/health

# Should return: {"status": "healthy", "service": "wildeditor-backend"}
```

#### **Option B: Full Local Development**
```bash
# If you want to run backend locally as well:
cd ../../apps/backend
# Follow backend setup instructions
python -m src.main  # Runs on port 8000

# Update .env.development to use local backend:
BACKEND_URL=http://localhost:8000
```

### **6. Run Development Server**
```bash
# Start MCP server
python -m src.main

# Server should start on http://localhost:8001
# Check health endpoint: curl http://localhost:8001/health
```

## 📁 Project Structure Setup

### **Create Directory Structure**
```bash
# From wildeditor root directory
mkdir -p apps/mcp/src/{config,mcp/{tools,resources,prompts},services,utils,shared}
mkdir -p apps/mcp/tests/{test_tools,test_resources,test_prompts,test_services,test_integration}
mkdir -p packages/auth/src
mkdir -p packages/auth/tests
```

### **Initialize Python Packages**
```bash
# Create __init__.py files
touch apps/mcp/src/__init__.py
touch apps/mcp/src/config/__init__.py
touch apps/mcp/src/mcp/__init__.py
touch apps/mcp/src/mcp/tools/__init__.py
touch apps/mcp/src/mcp/resources/__init__.py
touch apps/mcp/src/mcp/prompts/__init__.py
touch apps/mcp/src/services/__init__.py
touch apps/mcp/src/utils/__init__.py
touch apps/mcp/src/shared/__init__.py
touch apps/mcp/tests/__init__.py
touch packages/auth/src/__init__.py
touch packages/auth/tests/__init__.py
```

## 🔧 Configuration Files

### **MCP Server Requirements**
```python
# apps/mcp/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
sqlalchemy==2.0.23
pymysql==1.1.0
geoalchemy2==0.14.2
cryptography==41.0.7

# MCP Protocol
mcp==1.0.0

# AI Integration
openai==1.3.7
anthropic==0.7.7

# Development dependencies
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
black==23.11.0
isort==5.12.0
flake8==6.1.0
mypy==1.7.1

# Monitoring and logging
structlog==23.2.0
sentry-sdk[fastapi]==1.38.0
```

### **Environment Configuration**
```python
# apps/mcp/.env.example
# MCP Server Configuration
NODE_ENV=development
MCP_PORT=8001
WILDEDITOR_MCP_KEY=dev-mcp-key-12345

# Backend Communication (choose one)
# Option A: Remote backend (hybrid development)
BACKEND_URL=https://your-backend-domain.com
WILDEDITOR_MCP_BACKEND_KEY=your-mcp-backend-access-key

# Option B: Local backend (full local development)  
# BACKEND_URL=http://localhost:8000
# WILDEDITOR_MCP_BACKEND_KEY=dev-mcp-backend-key

# Optional: Direct database access for complex operations
# MYSQL_DATABASE_URL=mysql+pymysql://user:password@host:3306/wildeditor

# AI Service Configuration
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
AI_SERVICE_PROVIDER=openai  # or anthropic

# Logging and Development
LOG_LEVEL=DEBUG
SENTRY_DSN=your-sentry-dsn  # Optional

# Development Features
ENABLE_DOCS=true
ENABLE_RELOAD=true
```

### **Authentication Package Setup**
```python
# packages/auth/pyproject.toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "wildeditor-auth"
version = "1.0.0"
description = "Shared authentication for Wildeditor backend and MCP server"
dependencies = [
    "fastapi>=0.104.0",
    "pydantic>=2.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.25.0",
]
```

## 🧪 Testing Setup

### **Test Configuration**
```python
# apps/mcp/tests/conftest.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Provide authentication headers for testing."""
    return {"X-API-Key": "test-api-key"}

@pytest.fixture
def mock_db_session():
    """Provide a mock database session for testing."""
    # Implementation depends on testing strategy
    pass
```

### **Running Tests**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/test_tools/
pytest tests/test_integration/

# Run with verbose output
pytest -v

# Run tests in parallel (install pytest-xdist)
pytest -n auto
```

## 🐳 Docker Development Setup

### **Docker Compose for Development**
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  wildeditor-backend:
    build:
      context: .
      dockerfile: apps/backend/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=development
      - MYSQL_DATABASE_URL=${MYSQL_DATABASE_URL}
      - WILDEDITOR_API_KEY=${WILDEDITOR_API_KEY}
    volumes:
      - ./apps/backend:/app
    networks:
      - wildeditor-dev

  wildeditor-mcp:
    build:
      context: .
      dockerfile: apps/mcp/Dockerfile
    ports:
      - "8001:8001"
    environment:
      - NODE_ENV=development
      - MYSQL_DATABASE_URL=${MYSQL_DATABASE_URL}
      - WILDEDITOR_API_KEY=${WILDEDITOR_API_KEY}
      - BACKEND_URL=http://wildeditor-backend:8000
    volumes:
      - ./apps/mcp:/app
      - ./packages:/packages
    depends_on:
      - wildeditor-backend
    networks:
      - wildeditor-dev

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: wildeditor
      MYSQL_USER: wildeditor
      MYSQL_PASSWORD: password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - wildeditor-dev

volumes:
  mysql_data:

networks:
  wildeditor-dev:
    driver: bridge
```

### **Development with Docker**
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f wildeditor-mcp

# Execute commands in container
docker-compose -f docker-compose.dev.yml exec wildeditor-mcp bash

# Stop environment
docker-compose -f docker-compose.dev.yml down
```

## 🔧 Development Workflow

### **Code Quality Tools**
```bash
# Format code with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Lint code with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/

# Run all quality checks
make quality  # If Makefile is created
```

### **Git Hooks Setup**
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
EOF
```

### **Development Server with Auto-reload**
```bash
# Install development dependencies
pip install watchdog

# Run with auto-reload
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

# Or with make command
make dev  # If Makefile is created
```

## 🐛 Debugging Setup

### **VS Code Configuration**
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "MCP Server Debug",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "src.main:app",
                "--host", "0.0.0.0",
                "--port", "8001",
                "--reload"
            ],
            "cwd": "${workspaceFolder}/apps/mcp",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/apps/mcp"
            },
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

### **Logging Configuration**
```python
# src/config/logging.py
import structlog
import logging

def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(message)s"
    )
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

## 📊 Monitoring and Profiling

### **Development Monitoring**
```python
# src/middleware/monitoring.py
import time
from fastapi import Request
from structlog import get_logger

logger = get_logger()

async def monitoring_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        "request_processed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time
    )
    
    return response
```

### **Performance Profiling**
```bash
# Install profiling tools
pip install py-spy line_profiler memory_profiler

# Profile running application
py-spy record -o profile.svg --pid $(pgrep -f "uvicorn src.main:app")

# Memory profiling
mprof run python -m src.main
mprof plot
```

## 🔄 Development Best Practices

### **Code Organization**
- Follow Clean Architecture principles
- Separate concerns (MCP protocol, business logic, data access)
- Use dependency injection for testability
- Maintain consistent naming conventions

### **Testing Strategy**
- Write unit tests for all business logic
- Integration tests for MCP protocol compliance
- Performance tests for AI operations
- Mock external dependencies (AI services, database)

### **Documentation**
- Keep README files updated
- Document all public APIs
- Include code examples in docstrings
- Maintain architecture decision records (ADRs)

### **Version Control**
- Use feature branches for development
- Write descriptive commit messages
- Keep commits atomic and focused
- Use conventional commit format

## 📞 Support and Troubleshooting

### **Common Issues**
- **Import Errors**: Check PYTHONPATH and virtual environment
- **Database Connection**: Verify MySQL is running and accessible
- **Port Conflicts**: Ensure ports 8000/8001 are available
- **Environment Variables**: Check .env file configuration

### **Getting Help**
- Check [Troubleshooting Guide](./TROUBLESHOOTING.md)
- Review GitHub Issues
- Contact development team
- Check MCP protocol documentation

---

**Document Version**: 1.0  
**Last Updated**: August 15, 2025  
**Next Review**: After Phase 1 completion
