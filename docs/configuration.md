# Configuration and authentication

Each application loads its own environment. Copy the example beside the service you are running; do not place real credentials in version control. Root environment examples are reference indexes, not a shared runtime configuration file.

## Frontend

Vite embeds every `VITE_` value into public browser assets at build time.

| Variable | Purpose | Notes |
| --- | --- | --- |
| `VITE_API_URL` | Backend base URL including `/api` | Defaults in code to the production API; set it explicitly for local and preview builds |
| `VITE_CHAT_API_URL` | Chat-agent base URL | Set explicitly per environment |
| `VITE_SUPABASE_URL` | Browser authentication service URL | Required unless using the development-only bypass |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | Self-hosted Auth publishable key | Public by design; never substitute a secret/service-role key |
| `VITE_AUTH_CALLBACK_URL` | Exact post-confirmation callback | Must be present in the Auth redirect allow-list |
| `VITE_PASSWORD_RECOVERY_URL` | Exact password-recovery route | Must be present in the Auth redirect allow-list |
| `VITE_AUTH_SIGNUP_ENABLED` | Shows public signup UI | Keep `false` for invite-only production |
| `VITE_DISABLE_AUTH` | Development login bypass | Use only with a Vite development build; never use for a deployed environment |

`VITE_MCP_URL` and `VITE_MCP_API_KEY` appeared in older templates but are not read by the current frontend. Browser AI requests use the backend MCP proxy or chat-agent API instead.

Production accepts the configured self-hosted HTTPS URL. Placeholder hosts and
non-HTTPS production Auth URLs fail closed. One `AuthProvider` owns the session
subscription and propagates the current user access token to backend and chat
adapters.

## Backend

| Variable | Purpose | Required |
| --- | --- | --- |
| `MYSQL_DATABASE_URL` | SQLAlchemy MySQL URL, normally `mysql+pymysql://...` | Preferred |
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Fallback database components when no explicit URL is supplied | As a complete set |
| `WILDEDITOR_AUTH_ISSUERS` | Exact comma-separated Auth issuer allow-list | Yes when auth is enabled |
| `WILDEDITOR_AUTH_JWKS_URLS` | Optional comma-aligned JWKS URL list | Optional; derived from each issuer by default |
| `WILDEDITOR_AUTH_AUDIENCE` | Required JWT audience | Defaults to `authenticated` |
| `WILDEDITOR_AUTH_ALLOWED_ALGORITHMS` | Asymmetric JWT algorithm allow-list | Production default is `ES256` |
| `WILDEDITOR_AUTH_JWKS_CACHE_TTL` | Bounded JWKS cache lifetime | Defaults to 300 seconds |
| `WILDEDITOR_BACKEND_SERVICE_KEY` | Server-only MCP-to-backend Bearer credential | Required for MCP calls; never expose to Vite |
| `REQUIRE_AUTH` | Enables JWT/service Bearer validation; defaults to `true` | Yes in any shared environment |
| `CORS_ORIGINS` | Comma-separated browser origins | Set explicitly outside local development |
| `ENVIRONMENT` | Selects database-host fallback behavior | Recommended |
| `MCP_URL` | Base URL used by `/api/mcp/*` proxy routes | Required for proxy features |
| `MCP_API_KEY` | MCP operations key sent by the human-only backend proxy | Required for proxy features; no literal fallback exists |
| `TESTING` | Enables test-only database fallback behavior | Tests only |

The Docker image defaults Uvicorn to `0.0.0.0:8000`; the production workflow
overrides that command to bind host loopback only. Workflow variables such as
`PORT`, `HOST`, `WORKERS`, `LOG_LEVEL`, and `ENABLE_DOCS` are not all consumed
by the current application code. Backend OpenAPI routes are currently enabled
unconditionally in `apps/backend/src/main.py`.

## MCP service

Pydantic settings use the `WILDEDITOR_` prefix:

| Variable | Purpose |
| --- | --- |
| `WILDEDITOR_NODE_ENV` | `development` enables OpenAPI routes |
| `WILDEDITOR_MCP_PORT` | Application port, normally `8001` |
| `WILDEDITOR_HOST` | Bind host |
| `WILDEDITOR_LOG_LEVEL` | Python log level |
| `WILDEDITOR_MCP_KEY` | `X-API-Key` accepted for MCP operations |
| `WILDEDITOR_BACKEND_SERVICE_KEY` | Server-only Bearer key used for MCP-to-backend calls |
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
| `WILDEDITOR_AUTH_ISSUERS`, `WILDEDITOR_AUTH_JWKS_URLS` | Exact human JWT trust configuration |
| `WILDEDITOR_AUTH_AUDIENCE`, `WILDEDITOR_AUTH_ALLOWED_ALGORITHMS`, `WILDEDITOR_AUTH_JWKS_CACHE_TTL` | JWT claim, algorithm, and key-cache policy |
| `REQUIRE_AUTH` | Must be `true` outside explicit local development |
| `WILDEDITOR_ENVIRONMENT` | `local-development` or `remote-production`; production enforces Redis sessions |
| `STORAGE_BACKEND` | `memory` or `redis` |
| `REDIS_URL` | Redis connection string when Redis storage is selected |
| `SESSION_TTL` | Session lifetime in seconds |
| `FRONTEND_URL` | Compatibility setting used by deployment files; current CORS middleware does not read it |
| `CORS_ORIGINS` | JSON list of browser origins parsed by Pydantic settings |

There is no supported direct agent-to-backend variable; application data must flow through MCP.
The production workflow provisions a pinned, loopback-only Redis container and
constructs `REDIS_URL` from the URL-safe `WILDEDITOR_REDIS_PASSWORD` GitHub
secret. The password must contain at least 32 characters.

## Current authentication flows

### Backend

Protected backend routes expect:

```http
Authorization: Bearer <user-access-token>
```

All application-data routes require a typed principal. Viewer/editor/admin users
may read; editor/admin users may mutate; a service principal is accepted only
where MCP-to-backend operation is intended. The backend MCP proxy requires a
human editor/admin.

### MCP

All `/mcp` operations expect:

```http
X-API-Key: <mcp-operations-key>
```

MCP then calls protected backend routes with the independent server-only
`WILDEDITOR_BACKEND_SERVICE_KEY` as a Bearer credential and propagates only
server-derived audit actor/request context.

### Browser and chat

Self-hosted Supabase Auth protects the UI and issues human access tokens.
Backend and chat validate those JWTs; chat requires editor/admin and enforces
session ownership by token subject. The browser never receives a backend or
MCP service credential.

## Secret handling

- Generate independent high-entropy values for backend and MCP service credentials.
- Store deployment credentials in GitHub Environments/Actions secrets or the deployment platform's secret store.
- Never put server credentials in a `VITE_` variable.
- Do not log credentials, complete database URLs, tokens, or request authorization headers.
- Rotate a value immediately if it appears in source, documentation, build artifacts, CI output, or browser assets.
- Keep `.env` files local; only placeholder-only `.env*.example` files belong in Git.
