# `wildeditor-auth`

Shared FastAPI API-key helpers used by the MCP service. The package supports distinct key roles and both dependency- and middleware-based enforcement.

## Install

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -e packages/auth
```

The package metadata requires Python `3.14+`.

## Key roles

| Role | Environment variable | Intended use |
| --- | --- | --- |
| `BACKEND_API` | `WILDEDITOR_API_KEY` | Direct/backend service access |
| `MCP_OPERATIONS` | `WILDEDITOR_MCP_KEY` | Calls to `/mcp` |
| `MCP_BACKEND_ACCESS` | `WILDEDITOR_MCP_BACKEND_KEY` | Separate MCP-to-backend role when a consumer uses it |

`AuthMiddleware` reads `X-API-Key`, selects a key role from the request path, and returns `401` for missing or invalid keys. FastAPI dependencies `verify_api_key`, `verify_mcp_key`, and `verify_backend_access_key` expose the same checks.

Example:

```python
from fastapi import Depends, FastAPI
from wildeditor_auth import verify_mcp_key

app = FastAPI()

@app.get("/mcp/example")
async def example(_: bool = Depends(verify_mcp_key)):
    return {"ok": True}
```

## Tests

```bash
PYTHONPATH=packages/auth/src python -m pytest -q packages/auth/tests
```

## Limitations

The current implementation loads keys from the environment when authentication objects are constructed and compares ordinary strings. It does not validate browser JWTs, return typed human principals, define authorization roles, or rotate keys. Those changes are proposed in the [authentication migration plan](../../docs/ongoing-projects/self-hosted-postgres-auth-migration-plan.md).
