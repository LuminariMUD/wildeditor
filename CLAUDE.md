# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Luminari Wilderness Editor is a full-stack monorepo application for creating and managing wilderness areas in the LuminariMUD game world. It consists of a React/TypeScript frontend and Python FastAPI backend, with shared types and utilities.

**CRITICAL ARCHITECTURE NOTES**:
- ✅ **MIGRATION COMPLETE**: Express backend has been replaced with Python FastAPI
- The backend now directly integrates with LuminariMUD's existing MySQL spatial tables
- Supabase was used for initial development but production uses direct MySQL integration
- Real-time integration with the game world through direct database access

## Common Development Commands

```bash
# Install dependencies
npm install

# Start frontend only (backend runs separately)
npm run dev:frontend  # Frontend on :5173

# Start Python backend
cd apps/backend/src
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Build frontend
npm run build:frontend

# Python backend doesn't need building (interpreted language)

# Run linting across all packages
npm run lint

# Fix linting issues across all packages
npm run lint:fix

# Type checking across all packages
npm run type-check

# Clean all build artifacts
npm run clean
```

## Architecture Overview

### Monorepo Structure
This is a monorepo using npm workspaces and Turborepo for build orchestration:

- **apps/frontend/**: React 18.3 + TypeScript 5.5 + Vite
- **apps/backend/**: Python 3.8+ + FastAPI + SQLAlchemy + MySQL integration
- **packages/shared/**: Shared TypeScript types and utilities

### Technology Stack

#### Frontend (`apps/frontend/`)
- **Framework**: React 18.3 with TypeScript 5.5
- **Build Tool**: Vite 7.0
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Authentication**: Supabase Auth (client-side)
- **API Client**: Custom fetch-based client with error handling

#### Backend (`apps/backend/`)
- **Framework**: FastAPI (Python 3.8+) with Uvicorn ASGI server
- **Database**: Direct MySQL integration with LuminariMUD spatial tables
- **ORM**: SQLAlchemy for database operations
- **Validation**: Pydantic schemas for request/response validation
- **API**: RESTful endpoints with automatic OpenAPI documentation
- **Authentication**: JWT token validation (configurable)
- **Performance**: Async support for high-performance operations

#### Shared (`packages/shared/`)
- **Types**: Shared TypeScript interfaces and types
- **Utilities**: Common functions used by both frontend and backend

### Core Application Structure

The application follows a clean separation between frontend and backend:

```
apps/frontend/src/
├── components/             # React UI components
├── hooks/                  # Custom React hooks
├── services/               # API client and external services
├── types/                  # Type definitions (re-exports from shared)
└── App.tsx                 # Main application component

apps/backend/src/
├── models/                 # SQLAlchemy database models
├── schemas/                # Pydantic request/response schemas
├── routers/                # FastAPI route handlers
├── config/                 # Database and app configuration
├── main.py                 # FastAPI application entry point
└── requirements.txt        # Python dependencies

packages/shared/src/
└── types/                  # Shared TypeScript interfaces
```

### Key Concepts

1. **Coordinate System**: The wilderness uses a coordinate grid from -1024 to +1024 on both X and Y axes, matching the LuminariMUD wilderness system.

2. **Drawing Tools**:
   - `select`: Click items to view/edit properties
   - `point`: Place single landmarks
   - `polygon`: Draw regions (requires 3+ points)
   - `linestring`: Draw paths (requires 2+ points)

3. **Data Types**:
   - **Region**: Polygonal areas with types (geographic, encounter, sector_transform, sector)
   - **Path**: Linear features with types (road, dirt_road, geographic, river, stream)
   - **Point**: Single coordinate landmarks

4. **State Management**: 
   - Frontend: React hooks with API integration
   - Backend: SQLAlchemy ORM with direct MySQL database access
   - Production: Real-time integration with LuminariMUD spatial tables
   - Real-time updates: Optimistic UI updates with API persistence

5. **API Integration**: The frontend communicates with the backend via RESTful API:
   - FastAPI automatic OpenAPI documentation at `/docs`
   - Pydantic validation for all requests and responses
   - CRUD operations for regions, paths, and points
   - Error handling and loading states
   - Optimistic updates for better UX

### Database Schema 

**Production (LuminariMUD MySQL Spatial Tables)**

The backend now directly integrates with LuminariMUD's existing MySQL spatial database:

```sql
-- Regions table (MySQL with spatial support)
CREATE TABLE regions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  vnum INT UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(100) NOT NULL,
  coordinates JSON NOT NULL,
  properties TEXT,
  color VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Paths table  
CREATE TABLE paths (
  id INT PRIMARY KEY AUTO_INCREMENT,
  vnum INT UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(100) NOT NULL,
  coordinates JSON NOT NULL,
  color VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Points table
CREATE TABLE points (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(100) NOT NULL,
  coordinate JSON NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**Production (LuminariMUD MySQL Spatial Tables)**
The core system will integrate directly with the existing LuminariMUD MySQL spatial database tables. This provides real-time integration with the game world, allowing changes made in the editor to immediately affect the game environment.

### API Endpoints

The backend provides RESTful endpoints:

```
GET    /api/health           # Health check
GET    /api/regions          # List all regions
GET    /api/regions/:id      # Get specific region
POST   /api/regions          # Create region (auth required)
PUT    /api/regions/:id      # Update region (auth required)
DELETE /api/regions/:id      # Delete region (auth required)

# Similar endpoints for /api/paths and /api/points
```

### Authentication Flow

1. User authenticates with Supabase (frontend)
2. Frontend receives JWT access token
3. API client sets Authorization header for backend requests
4. Backend middleware validates JWT with Supabase
5. Protected routes require valid authentication

### Development Workflow

1. **Frontend Development**: 
   - Current tool selection
   - Drawing state and temporary coordinates
   - Selected items for editing
   - Layer visibility toggles
   - Zoom level and mouse position
   - API integration with loading/error states

2. **Backend Development**:
   - FastAPI server with Python 3.8+
   - SQLAlchemy ORM with MySQL integration
   - Pydantic schemas for validation
   - Async/await support for performance
   - RESTful API with automatic OpenAPI docs
   - Error handling and validation

3. **Shared Development**:
   - Type definitions in packages/shared
   - Both frontend and backend import shared types
   - Consistent data structures across the stack

### Environment Configuration

The monorepo uses environment variables for configuration:

#### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api
# Authentication configuration (if needed)
VITE_JWT_SECRET=your_jwt_secret
```

#### Backend (.env)
```
# Database configuration
MYSQL_DATABASE_URL=mysql+pymysql://username:password@localhost/luminari_mudprod

# Server configuration
PORT=8000
HOST=0.0.0.0

# CORS configuration
FRONTEND_URL=http://localhost:5173

# Authentication (optional)
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
```

Production domain: `https://wildedit.luminarimud.com`

### Current Implementation Status

**Implemented**:
- ✅ Monorepo structure with npm workspaces
- ✅ **FastAPI backend with Python 3.8+**
- ✅ **Direct MySQL database integration**
- ✅ **SQLAlchemy ORM models**
- ✅ **Pydantic validation schemas**
- ✅ RESTful API endpoints for all entities
- ✅ **Automatic OpenAPI documentation**
- ✅ Frontend API client with error handling
- ✅ Optimistic UI updates
- ✅ Shared type definitions
- ✅ Development workflow with Turborepo

**In Progress**:
- Database table creation (manual setup required)
- Error boundary implementation
- Comprehensive testing
- Production deployment configuration

### Getting Started (Development)

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Set up Python backend environment**:
   ```bash
   # Install Python dependencies
   cd apps/backend/src
   pip install -r requirements.txt
   
   # Configure database connection
   cp .env.example .env
   # Edit .env with your MySQL database credentials
   ```

3. **Set up MySQL database**:
   - Configure connection to LuminariMUD MySQL database
   - Ensure spatial tables exist for regions, paths, points
   - Test database connectivity

4. **Start development servers**:
   ```bash
   # Start frontend
   npm run dev:frontend
   
   # Start Python backend (separate terminal)
   cd apps/backend/src
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000/api
   - API Documentation: http://localhost:8000/docs
   - Health check: http://localhost:8000/api/health

### Common Development Tasks

**Adding new features**:
1. Define types in `packages/shared/src/types/`
2. Add Python models in `apps/backend/src/models/`
3. Create Pydantic schemas in `apps/backend/src/schemas/`
4. Add FastAPI endpoints in `apps/backend/src/routers/`
5. Update frontend API client in `apps/frontend/src/services/api.ts`
6. Test both frontend and backend integration

**Debugging**:
- Frontend: Check browser console and React DevTools
- Backend: Check FastAPI server logs and uvicorn output
- Database: Use MySQL client or GUI tools for query debugging
- API: Use automatic OpenAPI docs at http://localhost:8000/docs
- Authentication: Verify JWT tokens and authentication flow

**Working with the monorepo**:
- Frontend: Use `npm run dev:frontend` 
- Backend: Run Python FastAPI server separately
- Use workspace-specific commands: `npm run dev --workspace=@wildeditor/frontend`
- Shared types are automatically available in frontend
- Changes to shared package require frontend restart

## 📚 Documentation Reference

For comprehensive information beyond this technical overview, refer to:

### Essential Documentation
- **[README.md](README.md)** - Project overview, quick start, and complete documentation map
- **[docs/SETUP.md](docs/SETUP.md)** - Detailed setup instructions
- **[docs/README_DOCS.md](docs/README_DOCS.md)** - Documentation index and organization guide
- **[docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)** - Full development guide and best practices
- **[docs/API.md](docs/API.md)** - Complete API reference and examples

### Architecture & Planning
- **[docs/WILDERNESS_PROJECT.md](docs/WILDERNESS_PROJECT.md)** - Detailed project specifications and milestones
- **[docs/WILDERNESS_SYSTEM.md](docs/WILDERNESS_SYSTEM.md)** - LuminariMUD wilderness system architecture
- **[docs/adr/](docs/adr/)** - Architecture Decision Records for major technical decisions

### Migration & Operations
- **[docs/MIGRATION.md](docs/MIGRATION.md)** - Express to Python FastAPI migration guide
- **[docs/INTEGRATION.md](docs/INTEGRATION.md)** - LuminariMUD game server integration procedures
- **[docs/TESTING.md](docs/TESTING.md)** - Testing strategy and implementation guide

### Current Development Status
- **[docs/TODO.md](docs/TODO.md)** - Active development tasks and known issues
- **[docs/CHANGELOG.md](docs/CHANGELOG.md)** - Recent changes and version history
- **[docs/AUDIT.md](docs/AUDIT.md)** - Code quality assessment and recommendations

All documentation is kept up-to-date and reflects the current Python FastAPI backend architecture.

## Chat Agent Integration (DEPLOYED - December 2024)

### Overview
AI-powered chat assistant for wilderness building, running on port 8002 as a separate Docker container.

### Architecture (MCP-Only Design)
- **Service**: FastAPI application with PydanticAI
- **Port**: 8002 (uses MCP on 8001 as single contact surface)
- **Location**: `/apps/agent/`
- **Status**: **DEPLOYED AND RUNNING** - MCP-only refactor complete
- **Data Flow**: Chat Agent (8002) → MCP Server (8001) → Backend (8000) → MySQL

### Key Features
- Natural language region and path creation
- AI-powered description generation via MCP
- Dynamic hint generation for weather/time variations
- Terrain analysis and map generation
- Session management for conversation history
- **MCP-only architecture** - single contact surface

### Available Tools (All via MCP)
1. **create_region** - Create regions with coordinates (integer types)
2. **create_path** - Create paths/roads/rivers
3. **generate_region_description** - AI-powered descriptions
4. **generate_hints_from_description** - Dynamic weather/time variations
5. **analyze_terrain_at_coordinates** - Real-time terrain data
6. **analyze_complete_terrain_map** - Area analysis with overlays
7. **find_zone_entrances** - Locate zone connections
8. **find_static_wilderness_room** - Find static content
9. **generate_wilderness_map** - Create area maps
10. **search_regions** - Search by location/type/name
11. **search_by_coordinates** - Find regions/paths at coordinates
12. **store_region_hints** - Save generated hints
13. **get_region_hints** - Retrieve existing hints

### API Endpoints
- `POST /api/chat/message` - Send message and get response
- `GET /api/chat/history` - Get conversation history
- `POST /api/session/` - Create new session
- `GET /health/` - Health check

### Deployment
```bash
# Test deployed agent
SESSION_ID=$(curl -X POST http://localhost:8002/api/session/ -H "Content-Type: application/json" -d '{}' | jq -r .session_id)
curl -X POST http://localhost:8002/api/chat/message \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Help me create a forest region\", \"session_id\": \"$SESSION_ID\"}" | jq .

# Docker logs
docker logs -f wildeditor-chat-agent
```

### GitHub Secrets (Reusing Existing)
- `AI_PROVIDER` - "openai" or "deepseek" (defaults to openai)
- `OPENAI_API_KEY` - OpenAI API key
- `DEEPSEEK_API_KEY` - DeepSeek API key (fallback)
- `OPENAI_MODEL` - Model name (defaults to gpt-4-turbo)
- `DEEPSEEK_MODEL` - DeepSeek model (defaults to deepseek-chat)
- `WILDEDITOR_MCP_KEY` - MCP server authentication

### Completed ✅
- [x] Deploy chat agent with Docker
- [x] Fix pydantic_ai compatibility issues
- [x] Add DeepSeek as fallback provider
- [x] **Refactor to MCP-only architecture**
- [x] Remove BackendClient entirely
- [x] Add create_path tool
- [x] Fix API endpoint paths

### TODO
- [ ] Test full MCP tool integration
- [ ] Add region type name mapping (forest→4, etc.)
- [ ] Implement WebSocket for real-time chat
- [ ] Add streaming response support
- [ ] Create frontend React components
- [ ] Configure Redis for session persistence

See `/apps/agent/TODO.md` for detailed status and next steps.

## Region Hints System

### Overview
The Region Hints system provides AI-generated dynamic descriptions for wilderness regions. Hints are categorized descriptive elements that can be combined based on weather, time of day, and season to create immersive, contextual descriptions.

### Database Tables
- **region_hints**: Stores categorized hints with weather/time/season conditions
  - Categories: atmosphere, fauna, flora, geography, weather_influence, resources, landmarks, sounds, scents, seasonal_changes, time_of_day, mystical
  - Weather conditions: MySQL SET type ('clear', 'cloudy', 'rainy', 'stormy', 'lightning')
  - Weight ranges: 0-2 (0 = never, 1 = normal, 2 = double probability)
  - **Note**: Column is `agent_id` not `ai_agent_id` in production
- **region_profiles**: Stores overall theme and mood for regions
- **hint_usage_log**: Optional analytics tracking

### API Endpoints
- `GET /api/regions/{vnum}/hints` - List all hints for a region
- `POST /api/regions/{vnum}/hints` - Create hints (batch)
- `PUT /api/regions/{vnum}/hints/{id}` - Update a specific hint
- `DELETE /api/regions/{vnum}/hints/{id}` - Delete a specific hint
- `DELETE /api/regions/{vnum}/hints` - Delete all hints for a region
- `POST /api/regions/{vnum}/hints/generate` - Generate hints from description (uses MCP)

### Frontend Components
- **RegionTabbedPanel**: Main component with Hints tab for viewing/managing hints
- **HintEditor**: Modal component for creating/editing individual hints
  - Weights displayed as percentages (0-200%) in UI
  - Converted to decimals (0.0-2.0) when saving
  - Supports seasonal and time-of-day weight multipliers

### Known Issues & Solutions

#### Weight Validation Range
- **Issue**: Database stores weights as 0-2, frontend was validating for 0-1
- **Solution**: Updated validation to accept 0-2 range in `schemas/region_hints.py`

#### Weather Conditions Format
- **Issue**: MySQL SET type needs conversion from string to array
- **Solution**: Custom validation in `RegionHintResponse.model_validate()` splits comma-separated string

#### Column Name Mismatch
- **Issue**: Model used `ai_agent_id` but database has `agent_id`
- **Solution**: Updated models and schemas to use `agent_id`

#### API Client Method Name
- **Issue**: Frontend called `getHints` but method is `getRegionHints`
- **Solution**: Fixed method name in `RegionTabbedPanel.tsx`

### MCP Integration
The system integrates with Model Context Protocol (MCP) for AI-powered hint generation:
- Endpoint: `/api/mcp/generate-hints`
- Uses DeepSeek or fallback AI models
- Generates categorized hints from region descriptions
- Validates weather conditions against allowed set

### Development Commands
```bash
# Check if hints tables exist in database
cd apps/backend/src
python3 check_hints_tables.py

# Run migrations to create tables (if needed)
mysql -h localhost -u luminari_mud -p'password' luminari_mudprod < apps/backend/migrations/002_add_region_hints_tables.sql
```

### Important Notes
1. **Always run linter before committing**: `npm run lint`
2. **Test locally first**: Backend runs on port 8000, frontend on 5173
3. **CORS errors with 500 status**: Usually means backend is crashing - check detailed error messages
4. **Weight ranges**: 0-2 throughout the system (not 0-1)