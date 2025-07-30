# Changelog

All notable changes to the Luminari Wilderness Editor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2025-01-30

### Added
- 🐍 **Complete Python FastAPI Backend Migration** (by Jamie McLaughlin)
  - FastAPI application with modern async/await support
  - SQLAlchemy ORM models for direct MySQL database integration
  - Pydantic schemas for request/response validation and type safety
  - FastAPI routers with automatic OpenAPI documentation generation
  - Direct MySQL connection for LuminariMUD spatial database integration
  - Python requirements.txt with production-ready dependencies
  - Automatic API documentation at `/docs` endpoint
  - Health check endpoint for monitoring and deployment verification
- 🗄️ **MySQL Database Integration**
  - Direct connection to LuminariMUD MySQL spatial database
  - SQLAlchemy models for regions, paths, and points with spatial support
  - Production-ready database configuration with connection pooling
  - Support for MySQL spatial data types and operations
- 📚 **Comprehensive Documentation Updates**
  - Updated all setup and development guides for Python backend
  - New Python development workflow documentation
  - Updated API references and deployment instructions
  - Migration architecture decision record (ADR-002) completed
  - Environment configuration guides for MySQL integration

### Changed
- 🔄 **Complete Backend Architecture Migration**
  - Migrated from Express.js/TypeScript to Python FastAPI
  - Replaced Supabase PostgreSQL with direct MySQL integration
  - Updated API endpoints from Express routes to FastAPI routers
  - Changed authentication from Supabase JWT to configurable JWT validation
  - Updated development workflow from Node.js to Python/uvicorn
  - Changed API documentation from manual to auto-generated OpenAPI
- 🏗️ **Development Environment Updates**
  - Updated package.json scripts for Python backend workflow
  - Modified development server startup from npm to uvicorn
  - Changed API base URL from :3001 to :8000
  - Updated environment configuration for MySQL database
  - Modified CI/CD workflows for Python backend deployment
- 📝 **Documentation Overhaul**
  - Updated README.md with Python FastAPI setup instructions
  - Revised SETUP.md for MySQL database configuration
  - Modified CLAUDE.md to reflect new Python architecture
  - Updated all development guides and API references

### Removed
- ❌ **Express.js Backend Infrastructure** (Migration Complete)
  - Removed all TypeScript backend files (controllers, routes, middleware)
  - Deleted Express.js server configuration and dependencies
  - Removed Supabase integration from backend
  - Eliminated Node.js backend package.json and tsconfig.json
  - Cleaned up Express-specific middleware (auth, CORS, helmet)
  - Removed TypeScript compilation step for backend
- 🧹 **Legacy Dependencies and Configuration**
  - Removed backend ESLint configuration (no longer needed for Python)
  - Deleted TypeScript type definitions for Express backend
  - Cleaned up Supabase service key requirements
  - Removed Node.js backend development dependencies

### Security
- 🔒 **Enhanced Database Security**
  - Direct MySQL connection with proper credential management
  - Secure database URL configuration with environment variables
  - Production-ready connection pooling and timeout handling
- 🛡️ **API Security Improvements**
  - FastAPI built-in request validation with Pydantic schemas
  - Type-safe API endpoints preventing injection attacks
  - Configurable JWT authentication for production deployment

### Migration Notes
- ✅ **Express to FastAPI migration completed successfully**
- ✅ **All API endpoints maintained compatibility**
- ✅ **Database integration ready for production LuminariMUD deployment**
- ✅ **Development workflow updated and documented**
- ✅ **CI/CD pipeline compatible with Python backend**

### Added
- **🎯 Drawing System Overhaul**: Comprehensive audit and stability improvements
  - Geometric utility functions for accurate point-in-polygon selection
  - Distance-to-line algorithms for precise path selection
  - Canvas coordinate transformation validation and bounds checking
  - Real-time visual feedback for drawing validity (color-coded indicators)
  - Enhanced drawing instructions panel with keyboard shortcut guidance
  - Auto-dismiss error notifications with user-friendly messages
  - Loading overlay component for better user feedback during API operations
  - Drawing cancellation functionality with ESC key support
- **⚡ Performance Optimizations**:
  - Canvas rendering memoization with pre-computed coordinate transformations
  - Selective re-rendering to reduce computational overhead
  - Memory leak prevention with proper useEffect cleanup
- **🛡️ Input Validation & Security**:
  - Coordinate bounds validation (-1024 to +1024) across all input fields
  - Input sanitization for text fields with length limits
  - VNUM validation with proper range checking (1-99999)
  - Comprehensive form validation in Properties Panel
- Comprehensive code quality audit and improvements
- Input validation in all backend controllers
- ESLint configuration for backend with TypeScript rules
- Basic request validation for required fields in API endpoints
- Consistent error handling patterns across all model methods

### Changed
- **🎨 Enhanced User Experience**:
  - Drawing state management with proper validation and cleanup
  - Improved tool switching behavior with automatic state reset
  - Visual indicators showing drawing progress and requirements
  - Status text overlay showing real-time drawing guidance
  - Enhanced Properties Panel with instructional content and validation
- **🔧 Technical Improvements**:
  - Coordinate system accuracy improvements for all zoom levels
  - Selection logic rewritten with proper geometric algorithms
  - Drawing state race condition prevention
  - Canvas rendering optimization with zoom-aware transformations
- Improved type safety by replacing `any` types with proper TypeScript types
- Enhanced error handling in frontend with proper unknown type usage
- Optimized Region/Path identification logic in UI components
- Updated ESLint configurations to resolve compatibility issues

### Fixed
- **🚀 Netlify Deployment Issues**:
  - Added missing `test` script in root package.json to fix Netlify build failures
  - Added placeholder test scripts to all workspace packages (frontend, backend, shared)
  - Updated turbo.json configuration to include test task with proper dependencies
  - Fixed root tsconfig.json references to point to workspace directories instead of non-existent files
  - Resolved TypeScript compilation errors for `npx tsc --noEmit` command
- **🚨 Critical Drawing System Issues**:
  - **Selection Logic**: Replaced primitive hit-testing with proper point-in-polygon algorithm for regions
  - **Path Selection**: Implemented distance-to-line calculation for accurate path selection
  - **Coordinate Accuracy**: Fixed canvas-to-game coordinate conversion for all zoom levels
  - **Drawing State**: Resolved race conditions and validation gaps in drawing operations
  - **Memory Leaks**: Added proper cleanup in canvas rendering useEffect hooks
- **🎯 User Interface Bugs**:
  - Fixed coordinate transformation issues causing inaccurate mouse positioning
  - Resolved drawing state conflicts when switching tools mid-draw
  - Fixed canvas scaling issues affecting selection accuracy
  - Corrected zoom functionality coordinate mapping
- **⚠️ Stability & Performance**:
  - Eliminated excessive canvas re-renders through memoization
  - Fixed coordinate bounds checking and input sanitization
  - Resolved drawing cancellation and cleanup issues
  - Improved error handling with user-visible notifications
- **Critical Logic Bug**: Fixed incorrect Region/Path identification in PropertiesPanel and useEditor
- **Configuration Issues**: 
  - Updated turbo.json to use `tasks` instead of deprecated `pipeline` field
  - Fixed missing ESLint configuration for backend package
  - Corrected TypeScript export path in shared package (removed .js extension)
- **Backend Code Quality**:
  - Added consistent null checking for Supabase client across all model methods
  - Fixed unused parameter in error handler middleware
  - Added input validation for create/update operations
- **Frontend Code Quality**:
  - Fixed conditional React Hook calls by reordering useEffect placement
  - Removed unused imports and variables
  - Fixed missing dependencies in useCallback dependency arrays
  - Improved error handling with proper type safety
- **Linting and Type Safety**:
  - All ESLint issues resolved across frontend, backend, and shared packages
  - All TypeScript type checking issues resolved
  - Removed usage of `any` types in favor of proper type annotations

### Security
- Enhanced input validation preventing coordinate injection attacks
- Improved bounds checking for all coordinate inputs
- Added text input sanitization with length limits

## [0.2.0] - 2025-01-30

### Added
- Full-stack monorepo architecture with npm workspaces and Turborepo
- Express.js backend with TypeScript (REPLACED in v0.3.0 with Python FastAPI)
- Supabase database integration with PostgreSQL (REPLACED in v0.3.0 with MySQL)
- Temporary backend solution - migrated to Python FastAPI in v0.3.0
- JWT authentication middleware for API protection
- RESTful API endpoints for regions, paths, and points
- Shared types package for frontend-backend consistency
- API client with error handling and optimistic updates
- Database schema with indexes and Row Level Security
- Health check endpoint for monitoring
- Dotenv configuration for environment variables
- CORS and Helmet.js security middleware
- Graceful handling of missing Supabase credentials
- Database setup SQL script with tables and policies
- Frontend-backend connection with real data persistence
- Loading states and error handling in UI
- SETUP.md with quick start instructions

### Changed
- Transformed project from single React app to monorepo structure
- Replaced mock data with API-based persistence
- Updated useEditor hook to integrate with API client
- Modified authentication flow to pass JWT tokens to API
- Restructured project directories into apps/ and packages/
- Updated all import paths to use shared types
- Enhanced error handling with fallback to mock data
- Improved development workflow with parallel server startup
- Updated package.json with workspace configuration
- Modified TypeScript configs for monorepo structure
- Changed from file: to workspace: protocol for shared packages

### Fixed
- TypeScript module resolution issues in backend
- Import path extensions (.js) removed for proper builds
- useState/useEffect hooks corrected in useEditor
- Null handling for Supabase client initialization
- Backend build errors with tsconfig adjustments
- Environment variable loading with dotenv  
- API authentication token passing from frontend
- CORS configuration for local development

## [0.2.0] - 2025-01-30

### Added
- Monorepo architecture implementation
- Express backend with TypeScript
- Supabase integration
- JWT authentication
- RESTful API for all entities
- Shared types package
- API client in frontend
- Database schema and setup script
- Development environment configuration

### Changed
- Project structure to monorepo
- Frontend to use API instead of mock data
- Authentication to use JWT tokens
- Build system to Turborepo

### Removed
- Mock data from frontend (now optional fallback)
- Direct Supabase queries from frontend

## [0.1.0] - 2025-01-29

### Added
- Initial project setup with React, TypeScript, and Vite
- Basic project structure and configuration files
- Comprehensive documentation suite following GitHub best practices
- Supabase authentication integration with OAuth support
- Core wilderness editor UI components:
  - MapCanvas with coordinate tracking and drawing
  - ToolPalette with four drawing tools
  - LayerControls for visibility toggles
  - PropertiesPanel for entity editing
  - StatusBar with coordinates and zoom
- Drawing tools implementation:
  - Select tool for choosing existing features
  - Point tool for placing landmarks
  - Polygon tool for drawing regions
  - Linestring tool for creating paths
- Real-time coordinate display with zoom-adjusted precision
- Layer visibility controls for grid, regions, and paths
- Keyboard shortcuts (S, P, G, L, Escape, Enter)
- Mock data system for development
- Custom React hooks for editor state management (useEditor)
- Authentication flow with protected routes
- Environment configuration template (.env.example)
- Netlify deployment configuration with SPA routing
- CLAUDE.md file for AI assistant guidance
- TypeScript type definitions for all wilderness entities

#### Documentation Infrastructure
- Professional README.md with project overview, features, and quick start guide
- CONTRIBUTING.md with development setup, coding standards, and PR process
- LICENSE file (MIT) for open source distribution
- SECURITY.md with vulnerability reporting procedures and security policies
- ROADMAP.md with comprehensive development phases and milestones
- Complete API documentation (docs/API.md) with endpoints and examples
- User Guide (docs/USER_GUIDE.md) with tutorials and best practices
- Developer Guide (docs/DEVELOPER_GUIDE.md) with technical architecture
- Deployment Guide (docs/DEPLOYMENT.md) with production setup procedures
- Documentation index (docs/README.md) for easy navigation
- WILDERNESS_PROJECT.md with detailed project specifications

#### GitHub Templates and Automation
- Bug report template for structured issue reporting
- Feature request template for standardized enhancement requests
- Pull request template with comprehensive checklist
- GitHub Actions CI/CD workflow placeholder
- Issue and PR templates following GitHub best practices

### Changed
- Updated project metadata in package.json
- Enhanced package.json with additional npm scripts
- Configured project for LuminariMUD wilderness system integration
- Set up coordinate system matching MUD wilderness (-1024 to +1024)

### Security
- Implemented protected routes requiring authentication
- Added environment variable configuration for API keys
- Configured Supabase authentication with secure OAuth flow
- Created comprehensive security policy
- Established security best practices documentation

---

## Release Notes Template

When creating a new release, use this template:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features and functionality

### Changed
- Changes to existing functionality

### Deprecated
- Features that will be removed in future versions

### Removed
- Features that have been removed

### Fixed
- Bug fixes

### Security
- Security improvements and vulnerability fixes
```

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version when you make incompatible API changes
- **MINOR** version when you add functionality in a backwards compatible manner
- **PATCH** version when you make backwards compatible bug fixes

## Categories

### Added
For new features.

### Changed
For changes in existing functionality.

### Deprecated
For soon-to-be removed features.

### Removed
For now removed features.

### Fixed
For any bug fixes.

### Security
In case of vulnerabilities.