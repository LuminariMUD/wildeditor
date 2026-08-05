# ADR-001: Use a monorepo

- **Status:** Accepted
- **Decision date:** 2025-01-30

## Context

Wildeditor contains a browser client, multiple Python services, and contracts shared within each language ecosystem. Changes to an API often span the backend schema/router, frontend adapter/types, MCP caller, tests, and deployment configuration. Separate repositories would make those changes harder to review and release atomically.

## Decision

Keep the applications and shared packages in one repository:

- npm workspaces and Turbo coordinate the frontend and shared TypeScript package;
- Python services remain independently installable and deployable;
- `packages/shared` owns reusable TypeScript domain contracts;
- `packages/auth` owns reusable Python service authentication;
- service Dockerfiles and workflows preserve independent release boundaries.

## Alternatives considered

- **Separate repository per service:** stronger repository isolation, but more cross-repository versioning and coordination for contract changes.
- **Single deployable application:** simpler deployment, but it would collapse trust boundaries and couple chat/MCP availability to core editing.

## Consequences

- Cross-service contract changes can be reviewed atomically.
- JavaScript dependencies share one lockfile; Python dependency sets remain service-specific.
- Path-filtered CI must include shared packages consumed by an image.
- Root-level files can become ambiguous, so application source, service manifests, Dockerfiles, migrations, and workflows take precedence over legacy root deployment artifacts.
