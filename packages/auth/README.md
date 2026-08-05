# `wildeditor-auth`

Shared Wildeditor authentication primitives: typed principals and asymmetric
JWT verification for human callers, plus the independent agent-to-MCP API-key
boundary.

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
| `MCP_OPERATIONS` | `WILDEDITOR_MCP_KEY` | Agent/server calls to `/mcp` |

`AuthMiddleware` reads `X-API-Key` for `/mcp` and returns `401` for a missing
or invalid key. Backend access does not use this middleware: browser callers
present a verified Auth access token, while MCP presents the separate
server-only Bearer credential through `BearerAuthenticator`.

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

Service keys are compared in constant time. JWT verification accepts only
configured asymmetric algorithms and exact issuer/audience values, refreshes a
bounded JWKS cache on key rotation, and extracts roles only from protected
claims.
