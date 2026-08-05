# ADR-002: Replace the prototype Express backend with FastAPI

- **Status:** Accepted and implemented
- **Decision date:** 2025-01-30

## Context

The initial backend prototype used Express and TypeScript. The production integration needed direct access to LuminariMUD's MySQL/MariaDB spatial tables, explicit request/response validation, and a Python-compatible path for the project's terrain and AI integrations.

## Decision

Use a Python FastAPI backend with:

- Pydantic request and response schemas;
- SQLAlchemy and GeoAlchemy compatibility mappings;
- PyMySQL access to the existing LuminariMUD datastore;
- Uvicorn entry point `src.main:app`;
- generated OpenAPI documentation.

The browser remains React/TypeScript. Wire-format conversion stays in the frontend API adapter rather than sharing Python persistence models with the UI.

## Alternatives considered

- **Keep Express:** would retain one language for browser and API code but offered no decisive benefit for the existing Python/MySQL integration path.
- **Move all data to PostgreSQL:** rejected because LuminariMUD's game datastore and spatial routines remain MySQL/MariaDB contracts.

## Consequences

- Python services have independent dependency installation and test suites.
- API-shape changes require coordinated Pydantic, frontend, MCP, and test updates.
- MySQL-specific geometry behavior must be tested against the owning schema.
- The repository no longer maintains an Express backend; Express migration instructions belong in the documentation archive.
