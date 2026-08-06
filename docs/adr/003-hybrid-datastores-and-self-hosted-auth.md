# ADR-003: Keep game data in MariaDB and identity in self-hosted Supabase Auth

- **Status:** Accepted and implemented
- **Decision date:** 2026-08-05

## Context

LuminariMUD creates, reads, and mutates the wilderness schema directly through
the MariaDB C API. Its schema initializers, spatial functions, stored routines,
and triggers are part of the game runtime contract. Wildeditor maps those same
tables; it does not independently own them.

Wildeditor uses Supabase only for browser identity flows. It does not use the
Supabase Data API, Storage, Realtime, or RPC for wilderness data. Authentication
still requires more than a PostgreSQL database: password handling, confirmation,
recovery, refresh-token rotation, and JWT issuance remain Auth-service concerns.

## Decision

Use a hybrid persistence architecture with one authority per concern:

| Concern | Authority |
| --- | --- |
| Wilderness regions, paths, indexes, hints, profiles, and usage | LuminariMUD MariaDB |
| Users, identities, credentials, refresh tokens, and MFA state | PostgreSQL through self-hosted Supabase Auth |
| Chat sessions | Redis in production; process memory in explicit local development |

Retain the Supabase Auth client and self-host its Auth service and dedicated
PostgreSQL database. PostgreSQL is an identity store, not a replica or
replacement for the game datastore. Do not introduce PostGIS replicas, dual
writes, cross-database foreign keys, or synchronization jobs for MariaDB game
tables.

The browser receives only the Auth publishable key and user tokens. Backend and
chat validate exact-issuer asymmetric JWTs and protected roles. MCP uses its
independent `X-API-Key` boundary, and MCP-to-backend calls use a distinct
server-only Bearer service principal. The chat agent continues to access game
data through MCP.

## Alternatives considered

- **Move all data to PostgreSQL/PostGIS:** rejected because it requires a broad
  LuminariMUD database port or creates a second source of truth.
- **Use a general OIDC provider:** deferred because it would replace the current
  client flows and migration shape without a current organization-wide SSO
  requirement.
- **Implement authentication in FastAPI:** rejected because it would recreate
  security-sensitive identity, token, email, and recovery behavior already
  supplied by the open-source Auth service.

## Consequences

- MariaDB and PostgreSQL need separate migrations, credentials, volumes,
  backups, restores, monitoring, and upgrade procedures.
- Supabase Auth owns its internal `auth` schema; application code must not
  mutate those tables directly.
- Human roles come only from protected `app_metadata.app_role` (or a protected
  top-level claim) and are `viewer`, `editor`, or `admin`. The `service` role is
  reserved for server-side credentials and cannot be asserted by a human JWT.
- Schema changes to game data must follow the LuminariMUD-owned MariaDB
  contract and its compatibility gate.
- A future organization/zone membership model requires a separate, versioned
  application schema and an explicit authorization design; it must not be added
  implicitly to the Auth internals.
- The operational details for Auth deployment, backup, recovery, role
  administration, and upgrades live in the
  [self-hosted Auth runbook](../operations/self-hosted-auth-runbook.md).
