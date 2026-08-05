# Root integration probes

Files in this directory are historical live-service, deployment, networking, AI-provider, API-key, and credential-dependent probes. They are not a coherent hermetic test suite, are not run by the standard local test commands, and may encode stale host or protocol assumptions.

Several probes contain credential-like literal defaults. Treat any matching deployed credential as exposed and rotate it; replace literals with environment reads before a probe is reused.

Use package-local suites for routine validation:

- `packages/auth/tests/`
- `apps/backend/tests/`
- `apps/mcp/tests/`

The chat agent currently has no focused package-local suite. `npm test` invokes placeholder workspace scripts and is not meaningful coverage. The canonical commands and change-to-check matrix are in [docs/testing.md](../docs/testing.md).

## Before running a root probe

1. Read the entire file and identify its hosts, ports, credentials, provider costs, data writes, and infrastructure mutations.
2. Confirm the exact target environment is authorized and in scope.
3. Replace historical defaults with disposable development resources.
4. Use least-privileged, short-lived credentials and keep them out of command history and output.
5. Do not run write-oriented, load, network-repair, or deployment probes against production by accident.
6. Report the specific file, revision, environment, and result; do not generalize one probe into suite coverage.

Command-reference text files formerly stored here were moved to `docs/archive/2024-2025/service-notes/tests/` because they are historical operational notes rather than executable tests.
