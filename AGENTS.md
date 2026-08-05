# Wildeditor Agent Guide

Context is important whether this is local dev vs remote production, check `.env` for that detail and ssh-access when needed.

## Ground truth

- Treat source, manifests, migrations, service Dockerfiles, and `.github/workflows/` as authoritative.
- Do not assume `README*`, `docs/`, root deployment files, or root `tests/` describe the current runtime. Verify behavior in code before changing it.
- Keep work scoped and preserve unrelated working-tree changes.

## Repository map

- `apps/frontend/`: React 19, Vite, Tailwind, and strict TypeScript. `useEditor` owns editor state; `services/` adapts backend/chat wire formats; Supabase is used for browser authentication.
- `apps/backend/`: FastAPI API on port 8000. Routers use Pydantic schemas plus SQLAlchemy/GeoAlchemy models backed by MySQL.
- `apps/mcp/`: FastAPI MCP/JSON-RPC facade on port 8001. Tools, resources, and prompts call the backend and use `packages/auth`.
- `apps/agent/`: FastAPI chat/session service on port 8002. It reaches application data through the MCP client and stores sessions in memory or Redis.
- `packages/shared/`: shared frontend domain types. `packages/auth/`: shared Python API-key authentication.
- `apps/*/tests/` and `packages/auth/tests/` are local suites. Root `tests/` and most `apps/agent/test_*.py` files are live-service or credential-dependent probes.

## Change rules

- Keep frontend code strict and typed. Put reusable domain contracts in `@wildeditor/shared`; keep API-to-UI conversion in `apps/frontend/src/services/api.ts`.
- Keep FastAPI entry points importable as `src.main:app`. Add routes in `routers/`, request/response shapes in `schemas/`, and persistence shapes in `models/`.
- When an API shape changes, update its schema, router, frontend adapter/types, MCP caller, and focused tests together.
- Preserve the service boundary: the chat agent calls MCP; MCP calls the backend. Do not add a direct agent-to-backend path.
- Preserve authentication conventions: backend requests use Bearer auth; MCP requests use `X-API-Key`. Never commit or print credentials.
- Add database changes as new migrations beside the owning datastore. Do not silently rewrite existing migrations or mix MySQL backend schema with Supabase schema.
- Avoid broad cleanup while fixing a feature. There is substantial legacy/debug code; change only what the task requires.

## Setup and validation

Use Node 26.6.0 with npm 12.0.2 and Python 3.14+; the service images currently pin Python 3.14.6. Install JavaScript dependencies with `npm ci`. Python services are installed independently; install `packages/auth` editable before backend or MCP work.

Run the smallest relevant checks from the repository root:

```bash
npm run lint
npm run type-check
npm run build

PYTHONPATH=packages/auth/src python -m pytest -q packages/auth/tests
(cd apps/backend && PYTHONPATH=. python -m pytest tests/ -m "not integration" --tb=short)
(cd apps/mcp && PYTHONPATH=. python -m pytest tests/ --tb=short)
```

For Python source, CI treats `flake8 --select=E9,F63,F7,F82` as blocking; broader lint and mypy output are advisory. `npm test` currently runs placeholder workspace scripts, so do not report it as meaningful coverage. Run root integration probes only when their external services and credentials are explicitly in scope.
