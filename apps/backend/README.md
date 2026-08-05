# Backend

FastAPI REST API for Wildeditor's LuminariMUD MySQL/MariaDB data. It maps spatial regions and paths with SQLAlchemy/GeoAlchemy and exposes terrain-bridge, hint/profile, and MCP-proxy routes.

## Run locally

```bash
cd apps/backend
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -e ../../packages/auth
python -m pip install -r src/requirements.txt
cp .env.example .env
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Set `MYSQL_DATABASE_URL` before starting. Use `REQUIRE_AUTH=false` only for isolated local development.

## Route groups

- `/api/regions` and `/api/paths`: spatial CRUD and type metadata
- `/api/points`: coordinate intersection queries
- `/api/regions/{vnum}/hints` and `/profile`: dynamic narrative data
- `/api/terrain` and `/api/wilderness`: LuminariMUD terrain bridge on TCP `localhost:8182`
- `/api/mcp`: MCP proxy used by browser AI features
- `/api/health` and `/api/auth/status`: health and backend-key verification

OpenAPI is at `http://localhost:8000/docs`.

## Authentication

Protected routes use `Authorization: Bearer <user-access-token>` when
`REQUIRE_AUTH=true`. MCP uses the distinct server-only backend service key.
Read routes accept viewer/editor/admin principals, mutations require editor or
admin, and the backend MCP proxy requires a human editor/admin. See the
[configuration guide](../../docs/configuration.md).

## Tests

From the repository root:

```bash
(cd apps/backend && PYTHONPATH=. python -m pytest tests/ -m "not integration" --tb=short)
flake8 apps/backend/src --count --select=E9,F63,F7,F82 --show-source --statistics
```

Integration tests need an explicitly scoped database.

## Database changes

Models are compatibility mappings for an existing game datastore. Add Wildeditor-owned changes as new files under `migrations/`, test them on a restored copy, and never rewrite an applied migration. See [migrations/README.md](migrations/README.md) and the [domain model](../../docs/domain-model.md).

## Container

Build from repository root because the Dockerfile copies `packages/auth`:

```bash
docker build --file apps/backend/Dockerfile --tag wildeditor-backend:local .
```
