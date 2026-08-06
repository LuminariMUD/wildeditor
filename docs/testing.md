# Testing

Use the smallest meaningful suite for the files changed. Run commands from the repository root unless parentheses change the working directory.

## JavaScript and frontend

```bash
npm run lint
npm run type-check
npm run build
```

These commands cover the frontend and shared TypeScript workspace tasks defined by Turbo. `npm test` currently prints placeholder messages for both workspaces and exits successfully; do not report it as functional coverage.

## Shared Python authentication

```bash
PYTHONPATH=packages/auth/src python -m pytest -q packages/auth/tests
```

## Backend

```bash
(cd apps/backend && PYTHONPATH=. python -m pytest tests/ -m "not integration" --tb=short)
```

The local backend suite includes import, health, schema-constant, and shallow endpoint checks. Tests marked `integration` require a real database and are excluded from the standard command.

The blocking Python lint gate used in CI is:

```bash
flake8 apps/backend/src --count --select=E9,F63,F7,F82 --show-source --statistics
```

Broader flake8, mypy, and Bandit steps in the current workflow are advisory because they are allowed to continue on failure.

## MCP

```bash
(cd apps/mcp && PYTHONPATH=. python -m pytest tests/ --tb=short)
```

The MCP workflow also imports `src.main`, starts Uvicorn briefly, checks `/health`, and runs the blocking flake8 syntax/name selection.

## Chat agent

```bash
(cd apps/agent && PYTHONPATH=src:../../packages/auth/src python -m pytest tests/ --tb=short)
```

The focused suite covers JWT/role behavior, session ownership, trusted MCP
audit context, configuration, and Redis storage. Provider behavior and the live
service chain still require an isolated startup or integration environment.
Check:

```text
GET /health/
GET /health/ready
GET /health/live
```

Do not treat a health response as proof that provider calls, MCP authentication, Redis, or session ownership work.

## Root integration probes

Root `tests/` contains live-service, production-network, Docker, API-key, AI-provider, and credential-dependent scripts. They are diagnostic probes rather than a coherent hermetic suite.

Several legacy probes contain credential-like literal defaults. Treat every such value as exposed, rotate any matching deployed credential, and replace the literal with an environment lookup before reusing the probe.

Before running one:

1. Read the file and identify every host, mutation, credential, and external dependency.
2. Confirm the target environment is explicitly in scope.
3. Prefer a development database and disposable credentials.
4. Never run write-oriented probes against production by accident.
5. Record the specific script and environment when reporting results.

## Change-to-check map

| Change | Minimum checks |
| --- | --- |
| Frontend component/hook/service | `npm run lint`, `npm run type-check`, `npm run build` |
| Shared TypeScript type | Frontend checks plus affected adapter review |
| Backend router/schema/model | Backend tests and blocking flake8 selection |
| MCP tool/resource/prompt | MCP tests, blocking flake8 selection, and a read-only protocol smoke test |
| `packages/auth` | Auth tests plus every consuming service's focused tests |
| Dockerfile/requirements | Relevant tests, `pip check`, and exact Docker build |
| Workflow | Syntax/review plus a controlled workflow run |
| MySQL migration | Backup/restore rehearsal, migration on a disposable copy, and compatibility checks |
| Documentation only | Relative-link check, command/source review, and any build required by changed examples |

## Reporting validation

State exactly which commands ran, whether they passed, and what was not runnable. A skipped external suite, placeholder `npm test`, or health-only smoke check must not be presented as broader coverage.
