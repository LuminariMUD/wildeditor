# MCP service

FastAPI MCP/JSON-RPC facade for Wildeditor. It exposes tools, resources, and prompts while preserving the data boundary: MCP calls the backend REST API and does not connect to MySQL directly.

## Run locally

```bash
cd apps/mcp
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -e ../../packages/auth
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

Configure matching values for `WILDEDITOR_MCP_KEY`, `WILDEDITOR_API_KEY`, and the backend URL. AI provider configuration is optional for non-generation operations.

## Endpoints

- `GET /health`: public process health
- `GET /health/detailed`: authenticated dependency detail
- `POST /mcp` and `POST /mcp/request`: JSON-RPC transport
- `/mcp/tools/*`, `/mcp/resources/*`, `/mcp/prompts/*`: protocol operations
- `GET /mcp/status`: authenticated capability summary

All `/mcp` requests require `X-API-Key`. Query `tools/list`, `resources/list`, and `prompts/list` for the live registry instead of relying on a copied feature count.

## Tests

From the repository root:

```bash
(cd apps/mcp && PYTHONPATH=. python -m pytest tests/ --tb=short)
flake8 apps/mcp/src --count --select=E9,F63,F7,F82 --show-source --statistics
```

## Container

Build from repository root because the Dockerfile copies `packages/auth`:

```bash
docker build --file apps/mcp/Dockerfile --tag wildeditor-mcp:local .
```

See [API and MCP reference](../../docs/api.md), [Configuration](../../docs/configuration.md), and [Architecture](../../docs/architecture.md).
