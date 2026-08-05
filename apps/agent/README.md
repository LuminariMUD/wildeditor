# Chat agent

FastAPI chat and session service for AI-assisted wilderness editing. The service uses PydanticAI for model orchestration and calls Wildeditor application tools through MCP.

## Boundary

```text
Frontend -> Chat agent -> MCP -> Backend -> MySQL/MariaDB
```

Do not add a direct agent-to-backend or agent-to-database client.

## Run locally

```bash
cd apps/agent
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8002
```

Configure at least one AI provider, `WILDERNESS_MCP_URL`, and `MCP_API_KEY`. MCP must be running and able to reach the backend for application-data tools.

## API

- `/api/session/`: create, read, update, extend, and delete TTL-bound sessions
- `/api/chat/message`: non-streaming chat
- `/api/chat/stream`: server-sent streaming response
- `/api/chat/history`: conversation history
- `/health/`, `/health/ready`, `/health/live`: health endpoints

OpenAPI is at `http://localhost:8002/docs`.

## Session storage

`STORAGE_BACKEND=memory` is the local-development default and loses all
sessions on process restart. `remote-production` rejects memory storage and
requires `STORAGE_BACKEND=redis` plus `REDIS_URL`. `/health/ready` returns 200
only when storage responds and the authenticated MCP readiness chain reaches
the backend with its service principal.

## Security boundary

Every browser-facing session, history, message, and stream route requires an
editor/admin JWT. Sessions are keyed by opaque identifiers and remain bound to
the verified token subject; caller-supplied user IDs are rejected. Agent tool
calls use the server-only MCP key and carry request-scoped actor context.

## Validation

Run `PYTHONPATH=src python -m pytest -q tests` for JWT, authorization, ownership,
and actor-context coverage. Also validate Redis expiry, MCP authentication, and
at least one read-only tool call in an isolated deployment.

See [Architecture](../../docs/architecture.md), [Configuration](../../docs/configuration.md), and [Testing](../../docs/testing.md).
