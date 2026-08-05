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

`STORAGE_BACKEND=memory` is the default and loses all sessions on process restart. `STORAGE_BACKEND=redis` uses `REDIS_URL` and is the intended durable-across-process option, while still enforcing `SESSION_TTL`.

## Security status

Chat routes currently have no user-authentication dependency and do not enforce session ownership. Run the service only inside a trusted development/network boundary until the active authentication plan is implemented.

## Validation

There is no focused agent test suite yet. Validate import/startup, all three health endpoints, session expiry/storage behavior, MCP authentication, and at least one read-only tool call in a non-production environment.

See [Architecture](../../docs/architecture.md), [Configuration](../../docs/configuration.md), and [Testing](../../docs/testing.md).
