# Deployment

The supported deployment definitions are the service Dockerfiles and GitHub Actions workflows. Root Docker/Compose, Coolify, and Nginx files may represent older or experimental arrangements and are not authoritative without a fresh code review.

## Deployment matrix

| Component | Build definition | Workflow | Deployment behavior |
| --- | --- | --- | --- |
| Frontend | `apps/frontend/package.json`, `apps/frontend/netlify.toml` | `.github/workflows/ci.yml` | Netlify preview for pull requests; controlled production dispatch or gated `main` deployment |
| Backend | `apps/backend/Dockerfile` | `.github/workflows/backend-deploy.yml` | GHCR image, then controlled production dispatch or gated `main` deployment |
| MCP | `apps/mcp/Dockerfile` | `.github/workflows/mcp-deploy.yml` | Tests and GHCR image, then controlled production dispatch or gated `main` deployment |
| Chat agent | `apps/agent/Dockerfile` | `.github/workflows/deploy-chat-agent.yml` | Tested GHCR image plus loopback-only persistent Redis; controlled production dispatch or gated `main` deployment |

All Python images currently use Python `3.14.6-slim`, run as non-root users, expose their service port, and define a local HTTP health check.

## Workflow triggers and gates

### Frontend

`.github/workflows/ci.yml` runs for pushes and pull requests targeting `main` or `develop`. It installs with `npm ci`, runs lint and type checking, performs dependency audits, builds the frontend, and uploads the build artifact. `npm test` is invoked but currently consists of placeholder workspace scripts.

Pull requests are deployed as Netlify previews. Production can be dispatched
manually from `main`; automatic deployment on a `main` push additionally
requires `SELF_HOSTED_AUTH_PRODUCTION_ENABLED=true`.

Preview and production builds require the self-hosted Auth URL, publishable key,
callback, and recovery configuration. Authentication remains enabled. Artifact
gates reject the legacy browser backend-key variable, managed `supabase.co`
hosts, and known server credential values.

### Backend

`.github/workflows/backend-deploy.yml` is path-filtered to `apps/backend/**`. It installs backend dependencies plus `packages/auth`, runs blocking flake8 syntax/name checks, non-blocking broader flake8/mypy/Bandit checks, unit tests excluding the `integration` marker, builds a GHCR image, and deploys on `main`.

The workflow watches both backend and shared-auth changes. Its production job
uses the same manual/variable gate as the frontend. Production binds the
host-network API to loopback so only the Cloudflare tunnel reaches it.

### MCP

`.github/workflows/mcp-deploy.yml` watches both `apps/mcp/**` and `packages/auth/**`. It runs focused MCP tests and import/startup checks before building and deploying the GHCR image.
Its production job uses the same manual/variable gate.

### Chat agent

`.github/workflows/deploy-chat-agent.yml` watches agent and shared-auth changes
on `main`, supports manual dispatch, and runs the focused agent suite before
building. It provisions password-protected Redis with a named data volume and
binds both Redis and chat to production host loopback. Its production job uses
the same manual/variable gate.

## GitHub secrets

Configure secrets in the narrowest GitHub Environment/repository scope that satisfies the workflow.

| Area | Secrets read by current workflows |
| --- | --- |
| Server deployment | `PRODUCTION_HOST`, `PRODUCTION_USER`, `PRODUCTION_SSH_KEY` |
| Backend | `MYSQL_DATABASE_URL`, `WILDEDITOR_BACKEND_SERVICE_KEY`, exact Auth issuer/JWKS settings |
| MCP | `WILDEDITOR_MCP_KEY`, `WILDEDITOR_BACKEND_SERVICE_KEY`; optional provider/model settings |
| Chat agent | `WILDEDITOR_MCP_KEY`, `WILDEDITOR_REDIS_PASSWORD`, exact Auth issuer/JWKS settings, Auth smoke-test credentials; at least one provider key and its optional model setting |
| Frontend/Netlify | `NETLIFY_AUTH_TOKEN`, `NETLIFY_PROD_SITE_ID`, `PROD_API_URL`, `SELF_HOSTED_AUTH_URL`, `SELF_HOSTED_AUTH_PUBLISHABLE_KEY` |
| Notifications | `SLACK_WEBHOOK_URL` |

`GITHUB_TOKEN` is supplied by Actions. Never copy it or any other secret into generated documentation, issue comments, image labels, or shell tracing.

Production backend/chat use the self-hosted issuer by default. During a proven
managed-source migration only, the protected environment variable
`WILDEDITOR_AUTH_ISSUERS` may contain the exact comma-separated transition
issuers; deploy validation requires the self-hosted issuer to remain present.

The frontend workflow intentionally embeds `VITE_` values in its artifact.
Only public endpoint values and the Auth publishable key belong there. Human
access tokens are obtained at runtime and service credentials are prohibited.

## Container verification

Before promotion, build the same Dockerfile used by CI from repository root:

```bash
docker build --file apps/backend/Dockerfile --tag wildeditor-backend:local .
docker build --file apps/mcp/Dockerfile --tag wildeditor-mcp:local .
docker build --file apps/agent/Dockerfile --tag wildeditor-chat-agent:local .
```

After deployment, verify from inside the deployment network:

```bash
curl --fail http://127.0.0.1:8000/api/health
curl --fail http://127.0.0.1:8001/health
curl --fail http://127.0.0.1:8002/health/ready
```

Then verify the authenticated service path without printing credentials:

- MCP `/mcp/status` with the MCP `X-API-Key`
- Backend `/api/auth/status` with a designated human test access token
- One read-only MCP tool that reaches the backend
- Frontend login and a read-only map load
- Chat readiness only when an AI provider and MCP are configured

## Release checklist

1. Run the focused local checks in [Testing](testing.md).
2. Review API, migration, environment, and workflow changes together.
3. Confirm no secret or private endpoint was added to source or artifacts.
4. Back up the owning datastore and verify the backup before a database migration.
5. Build the exact service Dockerfiles and inspect health checks.
6. Deploy to a non-production environment and exercise service-to-service authentication.
7. Promote an immutable commit/SHA image, record the image digest, and observe health and logs.
8. Keep the previous known-good SHA image available. Rollback is not automated by this repository.

Do not infer a successful deployment from a green image build alone; verify the application, dependency, authentication, and data paths separately.
