# Luminari Wilderness Editor Project

## Project Overview

The Luminari Wilderness Editor is a full-stack monorepo application for creating and managing wilderness areas in the LuminariMUD game world. It consists of a React/TypeScript frontend for the visual editing interface and an Express/TypeScript backend API (temporary, to be replaced with Python). This architecture provides a modern editing experience while preparing for integration with existing game systems and spatial database operations.

**Architecture Decision**: The project uses a monorepo structure with shared types and parallel development capabilities. Frontend handles all UI/UX aspects while backend manages business logic, validation, and database operations.

**Current Status**: Phase 4 of 7 - Full-stack monorepo implemented with Express backend. Frontend connected to API with Supabase integration. Drawing tools and basic CRUD operations functional. Python backend development is the next major milestone.

## Core Requirements

### 1. Map Display and Interaction
- Display game-generated wilderness map image as base layer
- Click-to-register coordinates functionality
- Real-time coordinate display on mouse hover
- Zoom functionality (100%, 200%, etc.)
- Coordinate display adjusts to zoom level (1x1 at 100%, 2x2 at 200%)

### 2. Drawing Tools
- **Point Tool**: Place landmarks/single-room regions
- **Polygon Tool**: Draw regions (geographic, sector, encounter)
- **Linestring Tool**: Draw paths (roads, rivers, etc.)
- **Select Tool**: Click to view/edit existing features

### 3. User Interface
- Split-window design:
  - Left: Interactive map canvas
  - Right: Information/editing panel
- Tool palette for switching between drawing modes
- Layer visibility controls
- Coordinate display (current mouse position)

### 4. Editing Features
- Manual coordinate entry/modification
- Add/remove/reorder points in polygons and paths
- Automatic polygon validation (prevent self-intersecting lines)
- Support for polygon holes (interior rings)
- Bulk selection and editing

### 5. Data Management
- API-based persistence with optimistic updates
- Version control/commit system
- Mark items for deletion (soft delete)
- Lock regions from in-game editing
- Server selection (dev/prod environments)

### 6. Authentication & Security
- Supabase Auth for session management
- JWT token authentication for API calls
- User permission levels
- CORS protection and request validation

## Technical Architecture

### Architecture Overview

The application follows a monorepo structure with clear separation of concerns:

```
[React Frontend] → HTTP/REST → [Express API] → [Supabase PostgreSQL]
                                     ↓
                            (Future: Python API)
```

This architecture ensures:
- Frontend focuses purely on UI/UX concerns
- Backend handles all business logic and validation
- Shared types maintain consistency across the stack
- Easy migration path to Python backend

### Current Implementation (as of January 30, 2025)

#### Monorepo Architecture ✅ IMPLEMENTED
- **Structure**: npm workspaces with Turborepo
- **Packages**: 
  - `apps/frontend` - React application
  - `apps/backend` - Express API server
  - `packages/shared` - Shared TypeScript types
- **Development**: Unified `npm run dev` starts both services
- **Type Safety**: Shared types across frontend and backend
- **Build System**: Turborepo for optimized builds

#### Frontend Stack ✅ IMPLEMENTED
- **Framework**: React 18.3 with TypeScript 5.5
- **Build Tool**: Vite 7.0
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Authentication**: Supabase Auth with JWT tokens
- **State Management**: React hooks with API integration
- **API Client**: Custom fetch-based client with error handling
- **Features**:
  - Real-time coordinate tracking
  - Drawing tools (point, polygon, linestring, select)
  - Layer visibility controls
  - Properties panel for editing
  - Keyboard shortcuts
  - Optimistic UI updates
- **Location**: `apps/frontend/`
- **Port**: 5173
- **Deployment**: Netlify with SPA routing

#### Backend Stack ✅ IMPLEMENTED (Temporary Express)
- **Framework**: Express.js with TypeScript
- **Database**: Supabase (PostgreSQL with PostGIS)
- **Authentication**: Supabase JWT verification middleware
- **API**: RESTful endpoints for regions, paths, points
- **Security**: Helmet, CORS, request validation
- **Features**:
  - CRUD operations for all entity types
  - JWT authentication middleware
  - Error handling and validation
  - Health check endpoint
  - Graceful handling of missing Supabase config
- **Location**: `apps/backend/`
- **Port**: 8000
- **Environment**: Dotenv for configuration

#### Shared Package ✅ IMPLEMENTED
- **Purpose**: Type definitions shared between frontend and backend
- **Contents**:
  - Entity interfaces (Region, Path, Point)
  - API response types
  - Common utility types
- **Location**: `packages/shared/`
- **Import**: Via workspace protocol

#### Planned Python Backend (Next Phase)
- **Framework**: Python FastAPI
- **Database**: Same Supabase PostgreSQL
- **ORM**: SQLAlchemy with GeoAlchemy2
- **API**: Identical endpoints to Express version
- **Authentication**: Same Supabase JWT verification
- **Validation**: Pydantic models for request/response
- **Migration**: Drop-in replacement for Express backend

### Database Schema ✅ IMPLEMENTED
```sql
-- Current Supabase tables
regions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  vnum INTEGER UNIQUE NOT NULL,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  coordinates JSONB NOT NULL,
  properties TEXT,
  color TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
)

paths (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  vnum INTEGER UNIQUE NOT NULL,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  coordinates JSONB NOT NULL,
  color TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
)

points (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  coordinate JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
)

-- Indexes for performance
CREATE INDEX idx_regions_vnum ON regions(vnum);
CREATE INDEX idx_regions_type ON regions(type);
CREATE INDEX idx_paths_vnum ON paths(vnum);
CREATE INDEX idx_paths_type ON paths(type);
CREATE INDEX idx_points_type ON points(type);

-- Row Level Security enabled with policies
```

## API Endpoints ✅ IMPLEMENTED

The frontend communicates with the Express backend via these RESTful endpoints:

### Health Check
- `GET /api/health` - Service health status

### Region Management
- `GET /api/regions` - List all regions
- `GET /api/regions/{id}` - Get specific region
- `POST /api/regions` - Create new region (auth required)
- `PUT /api/regions/{id}` - Update region (auth required)
- `DELETE /api/regions/{id}` - Delete region (auth required)

### Path Management
- `GET /api/paths` - List all paths
- `GET /api/paths/{id}` - Get specific path
- `POST /api/paths` - Create new path (auth required)
- `PUT /api/paths/{id}` - Update path (auth required)
- `DELETE /api/paths/{id}` - Delete path (auth required)

### Point Management
- `GET /api/points` - List all points
- `GET /api/points/{id}` - Get specific point
- `POST /api/points` - Create new point (auth required)
- `PUT /api/points/{id}` - Update point (auth required)
- `DELETE /api/points/{id}` - Delete point (auth required)

## Development Phases

### Phase 1: Core Infrastructure ✅ COMPLETED
1. ✅ Set up React frontend with TypeScript
2. ✅ Configure Vite build system
3. ✅ Implement Supabase authentication
4. ✅ Create basic component structure
5. ✅ Set up development environment

### Phase 2: Basic Map Viewer ✅ COMPLETED
1. ✅ Create web frontend framework
2. ✅ Implement map canvas display
3. ✅ Add zoom functionality
4. ✅ Display mouse coordinates
5. ✅ Show regions/paths as overlays

### Phase 3: Drawing Tools ✅ COMPLETED
1. ✅ Implement point placement tool
2. ✅ Add polygon drawing with vertex editing
3. ✅ Create linestring drawing for paths
4. ✅ Add selection tool for existing features
5. ✅ Implement coordinate click registration

### Phase 4: Full-Stack Integration ✅ COMPLETED (January 30, 2025)
1. ✅ Transform to monorepo architecture
2. ✅ Create Express backend with TypeScript
3. ✅ Implement Supabase database integration
4. ✅ Add JWT authentication middleware
5. ✅ Connect frontend to backend API
6. ✅ Replace mock data with real persistence
7. ✅ Implement optimistic UI updates
8. ✅ Add error handling and loading states
9. ✅ Create shared types package
10. ✅ Set up development workflow with Turborepo

### Phase 5: Python Backend Migration 🎯 NEXT
1. ⏳ Set up FastAPI project structure
2. ⏳ Implement Supabase authentication
3. ⏳ Create SQLAlchemy models
4. ⏳ Build RESTful endpoints
5. ⏳ Add validation with Pydantic
6. ⏳ Document API with OpenAPI
7. ⏳ Migrate from Express to Python

### Phase 6: Advanced Features ⏳ PLANNED
1. ⏳ Add polygon hole support
2. ⏳ Implement automatic polygon fixing
3. ⏳ Create bulk editing tools
4. ⏳ Add region locking mechanism
5. ⏳ Implement collaborative editing features
6. ⏳ Add undo/redo functionality
7. ⏳ Create change history tracking

### Phase 7: Production Deployment ⏳ PLANNED
1. ✅ Set up production environment (Netlify)
2. ✅ Configure environment switching
3. ⏳ Implement backup and recovery
4. ✅ Create user documentation
5. ⏳ Integrate with game systems
6. ⏳ Performance optimization
7. ⏳ Security hardening

## Region Types (from game)
- `REGION_GEOGRAPHIC` (1) - Named geographic areas
- `REGION_ENCOUNTER` (2) - Encounter spawn zones
- `REGION_SECTOR_TRANSFORM` (3) - Terrain modification
- `REGION_SECTOR` (4) - Complete terrain override

## Path Types (from game)
- `PATH_ROAD` (1) - Paved roads
- `PATH_DIRT_ROAD` (2) - Dirt roads
- `PATH_GEOGRAPHIC` (3) - Geographic features
- `PATH_RIVER` (5) - Rivers and streams
- `PATH_STREAM` (6) - Small streams

## Coordinate System
- **Range**: -1024 to +1024 (X and Y)
- **Origin**: (0,0) at map center
- **Direction**: North (+Y), South (-Y), East (+X), West (-X)

## Security Considerations ✅ IMPLEMENTED
- ✅ JWT token validation for protected routes
- ✅ CORS configuration for frontend origin
- ✅ Helmet.js for security headers
- ✅ Request size limits (10MB)
- ✅ Environment variable protection
- ✅ Supabase Row Level Security
- ⏳ Rate limiting (planned)
- ⏳ Input sanitization (planned)

## Performance Optimizations ✅ IMPLEMENTED
- ✅ Optimistic UI updates for better UX
- ✅ Efficient API client with error handling
- ✅ React hooks for state management
- ✅ Turborepo for optimized builds
- ✅ Database indexes on key fields
- ⏳ React.memo for expensive renders (planned)
- ⏳ Debouncing for coordinate updates (planned)

## Current Implementation Details

### Working Features ✅
- **Authentication**: Supabase auth with JWT tokens
- **API Integration**: Full CRUD operations for all entities
- **Drawing Tools**: All tools functional with basic features
- **State Management**: useEditor hook with API integration
- **Coordinate System**: -1024 to +1024 grid working correctly
- **Layer Controls**: Visibility toggles functional
- **Properties Panel**: Display and edit entity properties
- **Error Handling**: Basic error states and fallbacks
- **Development Mode**: Graceful handling of missing credentials

### Known Limitations
- **Performance**: Canvas rendering could be optimized
- **Validation**: Limited input validation on frontend
- **Testing**: No test coverage yet
- **Mobile**: Not optimized for mobile devices
- **Accessibility**: Limited accessibility features
- **Offline**: No offline support

## Development Repository
- **Name**: wildeditor
- **URL**: https://wildedit.luminarimud.com
- **GitHub**: https://github.com/moshehbenavraham/wildeditor
- **Structure** (Monorepo):
  ```
  /
  ├── apps/
  │   ├── frontend/               # React application
  │   │   ├── src/
  │   │   │   ├── components/     # UI components
  │   │   │   ├── hooks/          # Custom React hooks
  │   │   │   ├── services/       # API client
  │   │   │   ├── lib/            # Supabase integration
  │   │   │   └── types/          # Type imports
  │   │   ├── .env                # Frontend environment
  │   │   └── [config files]
  │   └── backend/                # Express API
  │       ├── src/
  │       │   ├── controllers/    # Request handlers
  │       │   ├── routes/         # API routes
  │       │   ├── middleware/     # Auth & validation
  │       │   ├── models/         # Database models
  │       │   ├── config/         # Database config
  │       │   └── index.ts        # Server entry
  │       ├── .env                # Backend environment
  │       └── [config files]
  ├── packages/
  │   └── shared/                 # Shared types & utilities
  │       └── src/
  │           └── types/          # TypeScript interfaces
  ├── docs/                       # All documentation
  ├── scripts/                    # Operational and database scripts
  │   └── database-setup.sql      # Database schema
  ├── tests/                      # Repository-level integration tests
  ├── package.json                # Root workspace config
  ├── turbo.json                  # Turborepo config
  ├── CLAUDE.md                   # AI assistant guidance
  └── [other config files]
  ```

## Getting Started (Development) ✅ UPDATED

### Prerequisites
- Node.js 18+ and npm 9+
- Supabase account with project created
- Git

### Setup Instructions
1. **Clone repository**
   ```bash
   git clone https://github.com/moshehbenavraham/wildeditor.git
   cd wildeditor
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   - Create `apps/frontend/.env`:
     ```
     VITE_API_URL=http://localhost:8000/api
     VITE_SUPABASE_URL=your_supabase_url
     VITE_SUPABASE_ANON_KEY=<redacted>
     ```
   - Create `apps/backend/.env`:
     ```
     PORT=8000
     NODE_ENV=development
     SUPABASE_URL=your_supabase_url
     SUPABASE_SERVICE_KEY=<redacted>
     FRONTEND_URL=http://localhost:5173
     ```

4. **Create database tables**
   - Open Supabase dashboard
   - Go to SQL Editor
   - Run the SQL from `scripts/database-setup.sql`

5. **Start development servers**
   ```bash
   npm run dev  # Starts both frontend and backend
   ```

6. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000/api
   - Health check: http://localhost:8000/api/health

### Available Scripts
- `npm run dev` - Start all services
- `npm run dev:frontend` - Frontend only
- `npm run dev:backend` - Backend only
- `npm run build` - Build all packages
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix linting issues
- `npm run type-check` - Type checking
- `npm run clean` - Clean build artifacts

## Testing Strategy ⏳ PLANNED
- Unit tests with Vitest
- Integration tests for API endpoints
- Component testing with React Testing Library
- E2E testing with Playwright
- API testing with Supertest
- Load testing for performance

## Next Steps (Q1 2025)

### Immediate Priorities
1. **Environment Stabilization**
   - ✅ Configure Supabase credentials
   - ✅ Create database tables
   - ✅ Test full stack connectivity
   - ⏳ Add comprehensive error handling

2. **Frontend Polish**
   - ⏳ Add loading indicators
   - ⏳ Improve error messages
   - ⏳ Add success notifications
   - ⏳ Optimize canvas rendering
   - ⏳ Add keyboard shortcuts feedback

3. **Python Backend Development**
   - ⏳ Set up FastAPI project
   - ⏳ Implement identical API endpoints
   - ⏳ Add spatial query support
   - ⏳ Create migration scripts

### Short-term Goals
1. **Testing Infrastructure**
   - Set up Vitest
   - Write unit tests
   - Add integration tests
   - Implement E2E tests

2. **Performance Optimization**
   - Implement React.memo
   - Add request caching
   - Optimize re-renders
   - Add pagination

3. **User Experience**
   - Add tooltips
   - Improve accessibility
   - Add help documentation
   - Create video tutorials

## Architecture Benefits

### Why Monorepo?
1. **Code Sharing**: Shared types ensure consistency
2. **Atomic Changes**: Frontend and backend changes in one commit
3. **Simplified Development**: One command starts everything
4. **Better Refactoring**: Type safety across the stack
5. **Easier Testing**: Integration tests can cover full stack

### Why Express → Python Migration Path?
1. **Rapid Prototyping**: Express allowed quick API development
2. **Type Safety**: TypeScript provides immediate feedback
3. **Game Integration**: Python backend will integrate with game
4. **Spatial Operations**: Python has better GIS libraries
5. **Smooth Transition**: API contract remains the same

---

*Last Updated: January 30, 2025 - Full-stack monorepo implementation complete! Express backend with Supabase integration deployed. Frontend connected to API with full CRUD operations. Authentication working. Next phase: Python backend development for game integration.*
