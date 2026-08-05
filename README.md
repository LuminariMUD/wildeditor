# Wildeditor

Wildeditor is a browser-based editor for LuminariMUD wilderness data. It combines a React map editor, a FastAPI REST API, an MCP/JSON-RPC facade, and an optional AI chat service in one repository.

> **Project status:** pre-release and under active development. The current browser-to-API authentication design has known security gaps; do not expose a deployment to untrusted users until the [authentication migration plan](docs/ongoing-projects/self-hosted-postgres-auth-migration-plan.md) is complete.

## What it does

- Draws, edits, and deletes wilderness regions and paths in the `-1024..1024` coordinate space.
- Maps API payloads to strict shared TypeScript domain types.
- Stores regions and paths as MySQL spatial `POLYGON` and `LINESTRING` values.
- Manages region descriptions, hints, profiles, and review metadata.
- Exposes wilderness operations as MCP tools, resources, and prompts.
- Provides an optional chat assistant whose application-data access goes through MCP.

## Architecture

```text
React frontend (:5173) ────────────────> Backend API (:8000) ──> MySQL/MariaDB
        │                                      │
        │                                      └───────────────> MCP (:8001)
        └────> Chat agent (:8002) ─────────────> MCP (:8001) ──> Backend API
                  │
                  └────> memory or Redis session storage

React frontend ──> Supabase Auth (browser authentication)
```

The service boundary is intentional: the chat agent calls MCP, and MCP calls the backend. See [Architecture](docs/architecture.md) for ownership, trust boundaries, and data flow.

## Repository layout

| Path | Responsibility |
| --- | --- |
| `apps/frontend/` | React 19, Vite, Tailwind CSS, and strict TypeScript UI |
| `apps/backend/` | FastAPI REST API and SQLAlchemy/GeoAlchemy MySQL access |
| `apps/mcp/` | FastAPI MCP/JSON-RPC facade and AI-assisted wilderness tools |
| `apps/agent/` | FastAPI chat/session service backed by MCP |
| `packages/shared/` | Shared frontend domain contracts |
| `packages/auth/` | Shared Python API-key authentication used by MCP |
| `docs/` | Current documentation, ADRs, active plans, and archive |

## Quick start

### Prerequisites

- Node.js `26.6.0` and npm `12.0.2` (the versions pinned by `.nvmrc` and `package.json`)
- Python `3.14` (service images currently use `3.14.6`)
- A MySQL-compatible LuminariMUD database with the expected wilderness tables

Install the JavaScript workspace and start the frontend:

```bash
nvm install
nvm use
npm install --global npm@12.0.2
npm ci
cp apps/frontend/.env.development.example apps/frontend/.env.local
npm run dev
```

The frontend expects a backend at `http://localhost:8000/api`. Configure the service-specific environment files and start the Python services separately; the complete commands are in [Development setup](docs/development.md).

Local service URLs:

| Service | URL |
| --- | --- |
| Frontend | `http://localhost:5173` |
| Backend | `http://localhost:8000` |
| Backend OpenAPI | `http://localhost:8000/docs` |
| MCP | `http://localhost:8001` |
| Chat agent | `http://localhost:8002` |

## Validation

Run the smallest checks relevant to a change. The standard repository checks are:

```bash
npm run lint
npm run type-check
npm run build

PYTHONPATH=packages/auth/src python -m pytest -q packages/auth/tests
(cd apps/backend && PYTHONPATH=. python -m pytest tests/ -m "not integration" --tb=short)
(cd apps/mcp && PYTHONPATH=. python -m pytest tests/ --tb=short)
```

`npm test` currently invokes placeholder workspace scripts and is not meaningful test coverage. Root `tests/` contains live-service and credential-dependent probes; run those only when their dependencies are explicitly in scope.

## Documentation

- [Documentation index](docs/README.md)
- [Development setup](docs/development.md)
- [Configuration and authentication](docs/configuration.md)
- [API and MCP reference](docs/api.md)
- [Deployment](docs/deployment.md)
- [Testing](docs/testing.md)
- [Operations](docs/operations.md)
- [User guide](docs/user-guide.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

Historical plans, completed migrations, incident notes, superseded deployment guides, and earlier status reports are retained under [`docs/archive/`](docs/archive/README.md). They are not operational instructions.

## License

[MIT](LICENSE)
