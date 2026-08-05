# Operations

Wildeditor has basic service health checks and container restart behavior, but the repository does not currently define a complete monitoring, backup, or disaster-recovery platform. Operators must supply and test those controls for their environment.

## Health and readiness

| Component | Endpoint | What it proves |
| --- | --- | --- |
| Backend | `GET /api/health` | Backend process responds; also reports whether the terrain bridge is reachable |
| Backend terrain bridge | `GET /api/terrain/health` | TCP terrain bridge availability |
| MCP | `GET /health` | MCP process responds |
| MCP | `GET /health/detailed` | Authenticated dependency details |
| Chat agent | `GET /health/` | Agent process responds |
| Chat agent | `GET /health/ready` | Storage, session manager, and agent objects initialized |
| Chat agent | `GET /health/live` | Process liveness |

Health checks are not end-to-end transactions. Add synthetic checks for backend/database reads, authenticated MCP-to-backend calls, and chat-provider/MCP calls where those features are operationally required.

## Logs

All services primarily log to standard output/error; collect container logs centrally and attach request/deployment identifiers where available. Alert on repeated:

- database connection or spatial query failures;
- terrain bridge timeouts to `localhost:8182`;
- MCP authentication or backend upstream failures;
- AI provider initialization/rate-limit failures;
- Redis connection failures or session loss;
- HTTP `5xx` and sustained `401`/`403` changes.

Never log authorization headers, API keys, access/refresh tokens, full database URLs, user message contents by default, or provider payloads that may contain sensitive data. The current backend validation-error handler logs rejected request bodies; restrict log access and replace that behavior with structured redaction before accepting sensitive or untrusted payloads.

## Dependency failure behavior

| Failure | Expected impact |
| --- | --- |
| MySQL/MariaDB unavailable | Region/path/hint operations fail; basic process health may still respond |
| Terrain bridge unavailable | `/api/health` reports it unavailable; terrain/wilderness routes return failures |
| MCP unavailable | Chat tools and backend AI proxy operations fail; core region/path API remains separate |
| AI provider unavailable | MCP generation may fall back depending on configuration; chat-agent startup can fail if no model initializes |
| Redis unavailable | Redis-backed chat sessions fail; memory mode remains process-local and non-durable |
| Supabase Auth unavailable | Login/session refresh fails; existing backend API-key behavior is independent |

## Database backups

No workflow in this repository creates or verifies database backups. Before any schema or risky data change:

1. Identify the datastore owner: LuminariMUD MySQL/MariaDB versus Supabase/PostgreSQL.
2. Create a provider-native, encrypted backup with credentials supplied outside the command history where possible.
3. Record engine version, schema version, time, size, checksum, retention, and owner.
4. Restore into an isolated environment.
5. Run representative read and spatial-geometry checks against the restore.
6. Only then apply the migration to the intended environment.

Do not use a Supabase migration or PostgreSQL restore procedure for MySQL wilderness tables, or vice versa.

## Recovery priorities

1. Stop or disable writes when data integrity is uncertain.
2. Preserve logs, image digests, migration output, and the failing database state.
3. Restore the database into isolation and verify it before replacing any live datastore.
4. Redeploy a known-good immutable service image compatible with that schema.
5. Verify health, authentication, read paths, then controlled writes.
6. Re-enable traffic and monitor for recurrence.

RPO, RTO, backup retention, escalation contacts, and communication channels are deployment decisions not defined in the repository. Record them in the operator's private runbook before calling an environment production-ready.

## Troubleshooting sequence

For a failing request, trace the actual path:

1. Browser network/console and configured base URL
2. Target service health and container logs
3. Authentication header type and key role
4. Upstream dependency reachability
5. Database or terrain-bridge response
6. Schema/wire conversion at the owning boundary

For chat failures, verify `browser -> agent -> MCP -> backend` in that order. Do not work around the failure by adding a direct agent-to-backend path.
