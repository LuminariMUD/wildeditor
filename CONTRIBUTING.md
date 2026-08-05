# Contributing to Wildeditor

Wildeditor is a pre-release monorepo. Keep changes focused, preserve service boundaries, and validate against source rather than historical documentation.

## Before you start

- Read the [documentation index](docs/README.md), [development setup](docs/development.md), and [testing guide](docs/testing.md).
- Use Node.js `26.6.0`, npm `12.0.2`, and Python `3.14+`. The service images currently use Python `3.14.6`.
- Install JavaScript dependencies with `npm ci`.
- Install Python services independently; install `packages/auth` editable before backend or MCP dependencies.
- Copy only the service-specific `.env.example` files you need. Use disposable development credentials and never commit secrets.

## Make a change

1. Create a short-lived branch with a descriptive name such as `fix/path-validation` or `docs/runtime-guide`.
2. Change only the files needed for the issue. Do not combine a feature or fix with broad legacy cleanup.
3. Follow the repository boundaries:
   - `useEditor` owns frontend editor state.
   - Reusable frontend domain contracts belong in `@wildeditor/shared`.
   - Backend wire-format conversion belongs in `apps/frontend/src/services/api.ts`.
   - The chat agent calls MCP, and MCP calls the backend.
   - Backend requests use Bearer authentication; MCP requests use `X-API-Key`.
   - Database changes are new migrations beside the datastore that owns them.
4. When an API shape changes, update its schema, router, frontend adapter/types, MCP caller, and focused tests together.
5. Add or update tests that demonstrate the intended behavior.
6. Update canonical documentation when setup, configuration, contracts, operations, or user behavior changes. Move superseded point-in-time material to `docs/archive/` rather than presenting it as current guidance.

## Code expectations

- Keep frontend TypeScript strict; do not weaken compiler settings to bypass an error.
- Use typed functional React components and accessible, responsive UI patterns.
- Keep FastAPI entry points importable as `src.main:app`; add routes, Pydantic schemas, and SQLAlchemy models in their established directories.
- Preserve MySQL/MariaDB spatial semantics and coordinate ordering at API boundaries.
- Never print, commit, or place real credentials in examples, fixtures, logs, URLs, or browser-exposed variables.
- Avoid unrelated formatting and generated-file churn.

## Validate

Run the smallest meaningful checks for the files changed. The standard local commands are:

```bash
npm run lint
npm run type-check
npm run build

PYTHONPATH=packages/auth/src python -m pytest -q packages/auth/tests
(cd apps/backend && PYTHONPATH=. python -m pytest tests/ -m "not integration" --tb=short)
(cd apps/mcp && PYTHONPATH=. python -m pytest tests/ --tb=short)
```

`npm test` currently invokes placeholder workspace scripts and is not meaningful coverage. Root `tests/` scripts are live-service or credential-dependent probes; run one only after reviewing its targets and obtaining authorization for the environment.

See the [testing guide](docs/testing.md) for service-specific linting, smoke checks, and the change-to-check matrix.

## Pull requests

A pull request should include:

- a concise statement of the problem and solution;
- the affected services and contracts;
- database or configuration implications;
- exact validation commands and results;
- screenshots for visible UI changes;
- known limitations or deliberately deferred work.

Keep commits reviewable. Conventional Commit-style subjects such as `fix(backend): validate path coordinates` are welcome, but clarity is more important than mechanical conformance.

Use public issues for ordinary bugs and feature requests. Report security issues privately as described in [SECURITY.md](SECURITY.md).
