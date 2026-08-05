# Development setup

Run commands from the repository root unless a section explicitly changes directory. Python services are installed independently so their dependency and deployment boundaries remain visible.

## Toolchains

| Tool | Repository version |
| --- | --- |
| Node.js | `26.6.0` from `.nvmrc` |
| npm | `12.0.2` from `package.json` |
| Python | `3.14+`; service images use `3.14.6` |
| Database | MySQL/MariaDB with spatial support and the LuminariMUD wilderness schema |

## Frontend

Install the workspace exactly from `package-lock.json`:

```bash
nvm install
nvm use
npm install --global npm@12.0.2
npm ci
cp apps/frontend/.env.development.example apps/frontend/.env.local
```

For a local-only UI session, set `VITE_DISABLE_AUTH=true` in `.env.local`. This bypass is honored only by development builds. Set `VITE_API_URL=http://localhost:8000/api` and configure a non-empty development-only `VITE_WILDEDITOR_API_KEY` if you need to exercise mutation calls.

Start Vite:

```bash
npm run dev
```

The application is served at `http://localhost:5173`.

## Backend

Create a service-local environment and install the shared auth package before backend dependencies:

```bash
cd apps/backend
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ../../packages/auth
python -m pip install -r src/requirements.txt
cp .env.example .env
```

Set a usable `MYSQL_DATABASE_URL`. For isolated development you may set `REQUIRE_AUTH=false`; never use that setting on a network-accessible environment.

Start the backend from `apps/backend/` so the required import path remains `src.main:app`:

```bash
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Check `http://localhost:8000/api/health` and `http://localhost:8000/docs`.

## MCP service

MCP depends on the shared Python authentication package and a running backend:

```bash
cd apps/mcp
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ../../packages/auth
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

At minimum, set matching development values for `WILDEDITOR_MCP_KEY`, `WILDEDITOR_API_KEY`, and `WILDEDITOR_BACKEND_URL`. The public health endpoint is `http://localhost:8001/health`; MCP operations under `/mcp` require `X-API-Key`.

## Chat agent

The chat agent needs a running MCP service and at least one configured AI provider:

```bash
cd apps/agent
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8002
```

Set `WILDERNESS_MCP_URL=http://localhost:8001` and make `MCP_API_KEY` match the MCP operations key. The health endpoints are `/health/`, `/health/ready`, and `/health/live`.

The default `memory` session backend is process-local and disappears on restart. Use Redis only when a Redis service is available and `STORAGE_BACKEND=redis` is set.

## Suggested startup order

1. MySQL/MariaDB
2. Backend (`:8000`)
3. MCP (`:8001`), when AI/MCP features are needed
4. Chat agent (`:8002`), when chat is needed
5. Frontend (`:5173`)

## Development rules

- Keep editor state in `useEditor`; keep API conversion in `apps/frontend/src/services/api.ts`.
- Put reusable frontend domain types in `@wildeditor/shared`.
- Add backend routes in `routers/`, Pydantic contracts in `schemas/`, and persistence mappings in `models/`.
- Preserve the agent-to-MCP-to-backend path.
- Use Bearer authentication for backend requests and `X-API-Key` for MCP requests.
- Add new database migrations beside the datastore that owns the schema.
- Do not use root integration probes as unit tests or point them at production by default.

See [Testing](testing.md) for the supported validation commands and [Contributing](../CONTRIBUTING.md) for change and review expectations.
