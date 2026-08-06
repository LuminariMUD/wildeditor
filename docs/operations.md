# Operations

Wildeditor defines service health checks plus dedicated monitoring, encrypted
backup, and clean-restore automation for self-hosted Auth. It does not define a
complete monitoring or disaster-recovery platform for LuminariMUD MariaDB and
the remaining application services; operators must supply and test those
controls for their environment.

## Health and readiness

| Component | Endpoint | What it proves |
| --- | --- | --- |
| Backend | `GET /api/health` | Backend process responds; also reports whether the terrain bridge is reachable |
| Backend terrain bridge | `GET /api/terrain/health` | TCP terrain bridge availability |
| MCP | `GET /health` | MCP process responds |
| MCP | `GET /health/detailed` | MCP-key authentication and backend service-principal acceptance |
| Chat agent | `GET /health/` | Agent process responds |
| Chat agent | `GET /health/ready` | Redis/storage plus authenticated MCP-to-backend readiness |
| Chat agent | `GET /health/live` | Process liveness |

Readiness proves the service-authentication chain, but it is not a database
read or model inference. Keep the deployment's authenticated data and chat
synthetics for those behaviors.

## Logs

All services primarily log to standard output/error; collect container logs centrally and attach request/deployment identifiers where available. Alert on repeated:

- database connection or spatial query failures;
- terrain bridge timeouts to `localhost:8182`;
- MCP authentication or backend upstream failures;
- AI provider initialization/rate-limit failures;
- Redis connection failures or session loss;
- HTTP `5xx` and sustained `401`/`403` changes.

Never log authorization headers, API keys, access/refresh tokens, full database
URLs, user message contents by default, or provider payloads that may contain
sensitive data. The backend validation-error handler records only the route and
issue count and omits rejected input values.

## Dependency failure behavior

| Failure | Expected impact |
| --- | --- |
| MySQL/MariaDB unavailable | Region/path/hint operations fail; basic process health may still respond |
| Terrain bridge unavailable | `/api/health` reports it unavailable; terrain/wilderness routes return failures |
| MCP unavailable | Chat tools and backend AI proxy operations fail; core region/path API remains separate |
| AI provider unavailable | MCP generation may fall back depending on configuration; chat-agent startup can fail if no model initializes |
| Redis unavailable | Redis-backed chat sessions fail; memory mode remains process-local and non-durable |
| Self-hosted Auth unavailable | Login/session refresh fails; already-issued access tokens remain usable until expiry while cached JWKS remains valid |

## Database backups

Self-hosted Auth has encrypted backup, off-host artifact retention, age, and
clean-restore drill automation in the dedicated Auth workflows and runbook.
MariaDB remains owned by LuminariMUD and requires its own provider/operator
backup controls. Before any schema or risky data change:

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

Self-hosted Auth's RPO, RTO, retention, and recovery owner are recorded in its
dedicated runbook. Define the corresponding objectives, escalation contacts,
and communication channels for MariaDB and the remaining services in the
operator's private runbook before calling an environment production-ready.

## Troubleshooting sequence

For a failing request, trace the actual path:

1. Browser network/console and configured base URL
2. Target service health and container logs
3. Authentication header type and key role
4. Upstream dependency reachability
5. Database or terrain-bridge response
6. Schema/wire conversion at the owning boundary

For chat failures, verify `browser -> agent -> MCP -> backend` in that order. Do not work around the failure by adding a direct agent-to-backend path.
