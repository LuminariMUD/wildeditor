# Deployment

The supported deployment definitions are the service Dockerfiles and GitHub Actions workflows. Root Docker/Compose, Coolify, and Nginx files may represent older or experimental arrangements and are not authoritative without a fresh code review.

## Deployment matrix

| Component | Build definition | Workflow | Deployment behavior |
| --- | --- | --- | --- |
| Frontend | `apps/frontend/package.json`, `apps/frontend/netlify.toml` | `.github/workflows/ci.yml` | Netlify preview for pull requests and production on `main` |
| Backend | `apps/backend/Dockerfile` | `.github/workflows/backend-deploy.yml` | GHCR image, then SSH/Docker deployment on `main` |
| MCP | `apps/mcp/Dockerfile` | `.github/workflows/mcp-deploy.yml` | Tests, GHCR image, then SSH/Docker deployment on `main` |
| Chat agent | `apps/agent/Dockerfile` | `.github/workflows/deploy-chat-agent.yml` | GHCR image and SSH/Docker deployment on `main` |

All Python images currently use Python `3.14.6-slim`, run as non-root users, expose their service port, and define a local HTTP health check.

## Workflow triggers and gates

### Frontend

`.github/workflows/ci.yml` runs for pushes and pull requests targeting `main` or `develop`. It installs with `npm ci`, runs lint and type checking, performs dependency audits, builds the frontend, and uploads the build artifact. `npm test` is invoked but currently consists of placeholder workspace scripts.

Pull requests are deployed as Netlify previews. A push to `main` deploys production after the build job succeeds.

The preview and production jobs currently write `VITE_DISABLE_AUTH=true`, while `useAuth` honors the bypass only in non-production Vite builds. Remove that contradictory workflow input rather than relying on it as an access-control setting. Both jobs also have fallback API targets; configure `PROD_API_URL` explicitly so a deployment never silently selects a historical target.

### Backend

`.github/workflows/backend-deploy.yml` is path-filtered to `apps/backend/**`. It installs backend dependencies plus `packages/auth`, runs blocking flake8 syntax/name checks, non-blocking broader flake8/mypy/Bandit checks, unit tests excluding the `integration` marker, builds a GHCR image, and deploys on `main`.

The workflow's environment is currently named `development` even though it uses production-named host secrets. Treat that name as workflow behavior, not proof of a separate environment.

The path filter does not include `packages/auth/**` even though the Docker image copies that package. A shared-auth-only change will not trigger the backend workflow; resolve or deliberately account for that before release.

### MCP

`.github/workflows/mcp-deploy.yml` watches both `apps/mcp/**` and `packages/auth/**`. It runs focused MCP tests and import/startup checks before building and deploying the GHCR image.

### Chat agent

`.github/workflows/deploy-chat-agent.yml` watches `apps/agent/**` on `main` and supports manual dispatch. It builds and deploys the image but currently has no independent test job. Validate agent imports and health behavior before merging a release-affecting change.

## GitHub secrets

Configure secrets in the narrowest GitHub Environment/repository scope that satisfies the workflow.

| Area | Secrets read by current workflows |
| --- | --- |
| Server deployment | `PRODUCTION_HOST`, `PRODUCTION_USER`, `PRODUCTION_SSH_KEY` |
| Backend | `MYSQL_DATABASE_URL`, `WILDEDITOR_API_KEY` |
| MCP | `WILDEDITOR_MCP_KEY`, `WILDEDITOR_API_KEY`; optional provider/model settings |
| Chat agent | `WILDEDITOR_MCP_KEY`; at least one provider key and its optional model setting |
| Frontend/Netlify | `NETLIFY_AUTH_TOKEN`, `NETLIFY_PROD_SITE_ID`, `PROD_API_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY` |
| Notifications | `SLACK_WEBHOOK_URL` |

`GITHUB_TOKEN` is supplied by Actions. Never copy it or any other secret into generated documentation, issue comments, image labels, or shell tracing.

The frontend workflow intentionally embeds `VITE_` values in its artifact. Only publishable values belong there. Frontend source still supports a browser-side `VITE_WILDEDITOR_API_KEY`, although the current workflow does not supply it; do not add it to a production build. Without the transitional key, current browser mutations are unavailable until user-token authorization is implemented. See [Configuration](configuration.md).

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
curl --fail http://127.0.0.1:8002/health/
```

Then verify the authenticated service path without printing credentials:

- MCP `/mcp/status` with the MCP `X-API-Key`
- Backend `/api/auth/status` with the backend Bearer key
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
