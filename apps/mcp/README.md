# MCP Server

AI-powered Model Context Protocol server for the Luminari Wilderness Editor.

## 🎯 Overview

The MCP server provides AI-enhanced capabilities for wilderness design, including:

- **Region Analysis**: AI-assisted region design and optimization
- **Path Planning**: Intelligent path network analysis and creation  
- **Spatial Analytics**: Advanced spatial analysis and conflict detection
- **Natural Language Interface**: Create wilderness features from descriptions
- **Quality Assurance**: Automated validation and improvement suggestions

## 🏗️ Architecture

```
MCP Server (Port 8001)
├── FastAPI Application
├── MCP Protocol Implementation
│   ├── Tools (Region, Path, Spatial Analysis)
│   ├── Resources (Domain Knowledge, Schema References)
│   └── Prompts (AI-Powered Generation)
├── Services (Business Logic)
├── Shared Components (Auth, Models, Database)
└── AI Integration (OpenAI/Anthropic)
```

## 🚀 Quick Start

### Development Setup
```bash
# Install dependencies
cd apps/mcp
pip install -r requirements.txt

# Set environment variables
export MYSQL_DATABASE_URL="mysql+pymysql://user:pass@host:port/database"
export WILDEDITOR_API_KEY="your-api-key"

# Run development server
python -m src.main
```

### Production Deployment
```bash
# Build and deploy with backend
docker-compose -f docker-compose.same-server.yml up -d

# Health check
curl http://localhost:8001/health
```

## 📚 Documentation

- **[Implementation Plan](../../docs/mcp/MCP_IMPLEMENTATION_PLAN.md)** - Complete project plan
- **[Architecture](../../docs/mcp/ARCHITECTURE.md)** - Technical architecture
- **[Deployment](../../docs/mcp/DEPLOYMENT.md)** - Deployment guide
- **[Development Setup](../../docs/mcp/DEVELOPMENT_SETUP.md)** - Local development
- **[API Reference](../../docs/mcp/API_REFERENCE.md)** - Tools and resources

## 🛠️ Development

### Project Structure
```
apps/mcp/
├── src/
│   ├── main.py              # FastAPI application
│   ├── server.py            # MCP server implementation
│   ├── mcp/
│   │   ├── tools/          # MCP tools (region, path, spatial)
│   │   ├── resources/      # Domain knowledge resources
│   │   └── prompts/        # AI prompt generators
│   ├── services/           # Business logic services
│   ├── utils/              # Utilities and helpers
│   └── shared/             # Shared components
└── tests/                  # Test suite
```

### Key Components

#### **MCP Tools**
- `region_tools.py` - Region analysis and creation
- `path_tools.py` - Path planning and validation
- `spatial_tools.py` - Spatial analysis and optimization

#### **MCP Resources**
- `wilderness_context.py` - Domain knowledge and references
- `schema_resources.py` - Database schema and validation rules

#### **MCP Prompts**
- `region_prompts.py` - Region creation prompts
- `path_prompts.py` - Path planning prompts

## 🔧 Configuration

### Environment Variables
```bash
# Required
MYSQL_DATABASE_URL=mysql+pymysql://user:pass@host:port/database
WILDEDITOR_API_KEY=your-secure-api-key

# Optional
NODE_ENV=development|production
MCP_PORT=8001
BACKEND_URL=http://localhost:8000
AI_SERVICE_URL=https://api.openai.com/v1
AI_API_KEY=your-ai-api-key
```

### Dependencies
- **FastAPI** - Web framework
- **MCP** - Model Context Protocol implementation
- **SQLAlchemy** - Database ORM (shared with backend)
- **GeoAlchemy2** - Spatial database support
- **OpenAI/Anthropic** - AI service integration
- **Pydantic** - Data validation

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test category
pytest tests/test_tools/
pytest tests/test_integration/
```

## 📊 Health Checks

- **Health Endpoint**: `GET /health`
- **MCP Protocol**: Available at `/mcp/`
- **API Documentation**: Available at `/docs`

## 🔒 Security

- **Authentication**: Shared API key with backend
- **Rate Limiting**: Configured at Nginx level
- **Input Validation**: Comprehensive Pydantic validation
- **AI Safety**: Input sanitization and output validation

## 🚀 Deployment

The MCP server is designed to deploy alongside the existing backend on the same server:

- **Backend**: Port 8000 (existing)
- **MCP Server**: Port 8001 (new)
- **Nginx**: Routes `/api/*` to backend, `/mcp/*` to MCP server

See [Deployment Guide](../../docs/mcp/DEPLOYMENT.md) for detailed instructions.

## 📞 Support

For issues and questions:
- Check [Troubleshooting Guide](../../docs/mcp/TROUBLESHOOTING.md)
- Review [GitHub Issues](https://github.com/LuminariMUD/wildeditor/issues)
- Create new issue with detailed information

---

**Status**: Planning Phase  
**Version**: 1.0.0  
**Last Updated**: August 15, 2025
