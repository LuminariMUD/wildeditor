# API and MCP reference

This page is a route map, not a duplicate of generated schemas. The backend and chat agent expose OpenAPI; use their generated documentation for exact parameters and response models, and verify MCP definitions in the registries under `apps/mcp/src/mcp/`.

## Backend REST API

Base URL: `http://localhost:8000/api`

| Group | Routes | Purpose |
| --- | --- | --- |
| Health/auth | `GET /health`, `GET /auth/status` | Process health and backend-key verification |
| Regions | `/regions`, `/regions/{vnum}`, `/regions/types`, `/regions/landmarks` | Region listing, detail, type metadata, and CRUD |
| Paths | `/paths`, `/paths/{vnum}`, `/paths/types` | Path listing, detail, type metadata, and CRUD |
| Points | `GET /points?x=...&y=...` | Regions and paths intersecting a coordinate |
| Region hints | `/regions/{vnum}/hints`, `/profile`, `/hints/generate`, `/hints/analytics` | Hint/profile CRUD, generation, and analytics |
| Terrain | `/terrain/health`, `/at-coordinates`, `/area`, `/elevation-profile`, `/map-data`, `/sector-types` | Live terrain-bridge queries |
| Wilderness | `/wilderness/rooms`, `/navigation/*`, `/config` | Static room and navigation queries through the terrain bridge |
| MCP proxy | `/mcp/generate-description`, `/mcp/call-tool`, `/mcp/status` | Browser-safe proxy to MCP |

Backend OpenAPI is currently available at `/docs`, `/redoc`, and `/openapi.json`.

### Authentication

- Region/path `POST`, `PUT`, and `DELETE` routes require the backend Bearer key when `REQUIRE_AUTH=true`.
- Terrain and wilderness data routes declare the same Bearer dependency. `GET /terrain/health` is public; the wilderness router has no separate health endpoint.
- Core region/path/point reads and the current region-hint routes do not consistently enforce authentication.
- MCP proxy routes currently have no backend authentication dependency of their own.

This mixed state is a known limitation, not an authorization policy to emulate. See [Configuration](configuration.md) and the [active authentication migration plan](ongoing-projects/self-hosted-postgres-auth-migration-plan.md).

### Contract changes

For a backend payload change, update together:

1. `apps/backend/src/schemas/`
2. The owning router and model, when persistence changes
3. `packages/shared/` for reusable UI contracts
4. `apps/frontend/src/services/api.ts` for wire conversion
5. MCP callers in `apps/mcp/src/mcp/`
6. Focused backend, MCP, and frontend checks

## MCP service

Base URL: `http://localhost:8001`

Public process health is `GET /health`. Authenticated protocol endpoints live under `/mcp` and require `X-API-Key`.

Primary endpoints:

| Route | Purpose |
| --- | --- |
| `POST /mcp` or `/mcp/` | Main JSON-RPC entry point |
| `POST /mcp/request` | Raw MCP request wrapper used by the chat agent |
| `POST /mcp/initialize` | MCP session initialization response |
| `POST /mcp/tools/list`, `/tools/call` | Standard tool discovery and execution |
| `POST /mcp/resources/list`, `/resources/read` | Standard resource discovery and reading |
| `POST /mcp/prompts/list`, `/prompts/get` | Standard prompt discovery and rendering |
| `GET /mcp/status` | Authenticated capability/status summary |

Convenience REST-style routes (`GET /mcp/tools`, `/resources`, `/prompts` and per-name routes) expose the same registries for diagnostics.

The live tool registry is authoritative. It currently includes region search/creation, path creation, terrain and wilderness-room analysis, map generation, navigation discovery, description generation, hint generation/storage, and related spatial operations. Query `tools/list` rather than maintaining a copied count in documentation.

Example JSON-RPC call:

```bash
curl --request POST http://localhost:8001/mcp/request \
  --header 'Content-Type: application/json' \
  --header "X-API-Key: ${WILDEDITOR_MCP_KEY}" \
  --data '{"jsonrpc":"2.0","id":"regions","method":"tools/list"}'
```

## Chat agent

Base URL: `http://localhost:8002`

| Group | Routes |
| --- | --- |
| Health | `GET /health/`, `/health/ready`, `/health/live` |
| Sessions | `POST /api/session/`, `GET/DELETE /api/session/{session_id}`, `PUT .../context`, `POST .../extend` |
| Chat | `POST /api/chat/message`, `POST /api/chat/stream`, `GET /api/chat/history`, `DELETE /api/chat/history/{session_id}` |

The service's OpenAPI UI is at `/docs`. These routes currently have no user-authentication dependency; use only in a trusted development/network boundary until principal validation and session ownership are implemented.

## Error behavior

- Pydantic validation failures return HTTP `422`.
- Missing records generally return `404`.
- Terrain bridge failures are surfaced as `503` by terrain/wilderness routers.
- Backend-to-MCP connection failures are returned in the proxy response or as upstream errors.
- MCP JSON-RPC application failures appear in the protocol response even when the HTTP transport succeeds; clients must inspect the response body.
