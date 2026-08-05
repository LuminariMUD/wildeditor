# Configuration and authentication

Each application loads its own environment. Copy the example beside the service you are running; do not place real credentials in version control. Root environment examples are reference indexes, not a shared runtime configuration file.

## Frontend

Vite embeds every `VITE_` value into public browser assets at build time.

| Variable | Purpose | Notes |
| --- | --- | --- |
| `VITE_API_URL` | Backend base URL including `/api` | Defaults in code to the production API; set it explicitly for local and preview builds |
| `VITE_SUPABASE_URL` | Browser authentication service URL | Required unless using the development-only bypass |
| `VITE_SUPABASE_ANON_KEY` | Supabase publishable/anonymous key | Public by design; never substitute a service-role key |
| `VITE_DISABLE_AUTH` | Development login bypass | Use only with a Vite development build; never use for a deployed environment |
| `VITE_WILDEDITOR_API_KEY` | Current mutation credential | Transitional and insecure for production because it is compiled into the bundle |
| `VITE_CHAT_API_URL` | Chat-agent base URL | Defaults to the deployed `/chat` endpoint |

`VITE_MCP_URL` and `VITE_MCP_API_KEY` appeared in older templates but are not read by the current frontend. Browser AI requests use the backend MCP proxy or chat-agent API instead.

Current frontend validation flags a `VITE_SUPABASE_URL` that does not contain `supabase.co` as a configuration error. The self-hosted Auth migration therefore requires a code change as well as a URL change; a self-hosted hostname is not supported by the current validation path.

## Backend

| Variable | Purpose | Required |
| --- | --- | --- |
| `MYSQL_DATABASE_URL` | SQLAlchemy MySQL URL, normally `mysql+pymysql://...` | Preferred |
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Fallback database components when no explicit URL is supplied | As a complete set |
| `WILDEDITOR_API_KEY` | Bearer key checked by protected backend routes | Yes when auth is enabled |
| `REQUIRE_AUTH` | Enables Bearer-key validation; defaults to `true` | Yes in any shared environment |
| `CORS_ORIGINS` | Comma-separated browser origins | Set explicitly outside local development |
| `ENVIRONMENT` | Selects database-host fallback behavior | Recommended |
| `MCP_URL` | Base URL used by `/api/mcp/*` proxy routes | Required for proxy features |
| `MCP_API_KEY` | MCP operations key sent by the proxy | Required for proxy features; the current proxy source contains a legacy literal fallback, so override it and treat the fallback as exposed pending removal |
| `TESTING` | Enables test-only database fallback behavior | Tests only |

The Docker image fixes Uvicorn to `0.0.0.0:8000`; workflow variables such as `PORT`, `HOST`, `WORKERS`, `LOG_LEVEL`, and `ENABLE_DOCS` are not all consumed by the current application code. Backend OpenAPI routes are currently enabled unconditionally in `apps/backend/src/main.py`.

## MCP service

Pydantic settings use the `WILDEDITOR_` prefix:

| Variable | Purpose |
| --- | --- |
| `WILDEDITOR_NODE_ENV` | `development` enables OpenAPI routes |
| `WILDEDITOR_MCP_PORT` | Application port, normally `8001` |
| `WILDEDITOR_HOST` | Bind host |
| `WILDEDITOR_LOG_LEVEL` | Python log level |
| `WILDEDITOR_MCP_KEY` | `X-API-Key` accepted for MCP operations |
| `WILDEDITOR_API_KEY` | Bearer key used for MCP-to-backend calls |
| `WILDEDITOR_BACKEND_URL` | Backend origin, normally `http://localhost:8000` |
| `WILDEDITOR_BACKEND_API_BASE` | Backend prefix, normally `/api` |
| `WILDEDITOR_CORS_ORIGINS` | Comma-separated allowed origins |

AI provider settings are intentionally unprefixed:

| Variable | Purpose |
| --- | --- |
| `AI_PROVIDER` | `openai`, `anthropic`, `deepseek`, `ollama`, or `none`; keys are auto-detected when unset/unknown |
| `OPENAI_API_KEY`, `OPENAI_MODEL` | OpenAI-compatible configuration |
| `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` | Anthropic configuration |
| `DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL` | DeepSeek configuration |
| `OLLAMA_BASE_URL`, `OLLAMA_MODEL` | Local Ollama endpoint and model |

Provider/model availability changes independently of this repository. Select a model supported by the installed client and your provider account rather than copying an old model name from archived documentation.

## Chat agent

| Variable | Purpose |
| --- | --- |
| `HOST`, `PORT`, `DEBUG`, `LOG_LEVEL` | FastAPI runtime settings |
| `MODEL_PROVIDER` | `openai`, `anthropic`, or `deepseek` |
| `MODEL_NAME` | OpenAI model name |
| `ANTHROPIC_MODEL` | Anthropic model name |
| `DEEPSEEK_MODEL` | DeepSeek model name |
| `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY` | Provider credentials; at least one must initialize successfully |
| `WILDERNESS_MCP_URL` | MCP service origin, without `/mcp` |
| `MCP_API_KEY` | MCP `X-API-Key` used by the agent |
| `STORAGE_BACKEND` | `memory` or `redis` |
| `REDIS_URL` | Redis connection string when Redis storage is selected |
| `SESSION_TTL` | Session lifetime in seconds |
| `FRONTEND_URL` | Compatibility setting used by deployment files; current CORS middleware does not read it |
| `CORS_ORIGINS` | JSON list of browser origins parsed by Pydantic settings |

There is no supported direct agent-to-backend variable; application data must flow through MCP.

## Current authentication flows

### Backend

Protected backend routes expect:

```http
Authorization: Bearer <backend-api-key>
```

Region and path mutations are protected. Terrain and wilderness routes also use the same dependency, while several read and region-hint routes remain public. Check the route dependency before treating an endpoint as protected.

### MCP

All `/mcp` operations expect:

```http
X-API-Key: <mcp-operations-key>
```

MCP then calls protected backend routes with the backend Bearer key. Use separate randomly generated values for the two roles even where existing workflows use the same named backend key across services.

### Browser and chat

Supabase currently protects the frontend UI, but the backend does not validate the user's Supabase access token. Chat routes are also unauthenticated. Do not describe the current setup as end-to-end user authorization. The [active authentication migration plan](ongoing-projects/self-hosted-postgres-auth-migration-plan.md) defines the proposed principal and role model.

## Secret handling

- Generate independent high-entropy values for backend and MCP service credentials.
- Store deployment credentials in GitHub Environments/Actions secrets or the deployment platform's secret store.
- Never put server credentials in a `VITE_` variable.
- Do not log credentials, complete database URLs, tokens, or request authorization headers.
- Rotate a value immediately if it appears in source, documentation, build artifacts, CI output, or browser assets.
- Do not rely on the legacy MCP proxy fallback credential. Replace it with required configuration and rotate any matching deployed key before exposing proxy routes.
- Keep `.env` files local; only placeholder-only `.env*.example` files belong in Git.
