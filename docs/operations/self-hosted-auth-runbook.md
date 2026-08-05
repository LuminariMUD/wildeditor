# Wildeditor self-hosted Auth runbook

This runbook is the operational contract for moving Wildeditor identity from
managed Supabase to the pinned self-hosted stack in
`infrastructure/supabase/`. It does not move game data: LuminariMUD MariaDB
remains the sole authority for wilderness regions, paths, points, hints,
profiles, and usage logs.

## Recorded decisions and open gates

| Item | Recorded value | State |
| --- | --- | --- |
| Production Auth hostname | `wildedit-auth.luminarimud.com` | Selected |
| Auth API/issuer | `https://wildedit-auth.luminarimud.com/auth/v1` | Selected |
| Hosting | Existing Wildeditor production host; gateway loopback port `8010` | Selected |
| Signup | Invite-only (`DISABLE_SIGNUP=true`) | Selected |
| Roles | `viewer`, `editor`, `admin`; the initial operational account was explicitly assigned `editor` and its claim and application access were verified on 2026-08-06 | Passed |
| Stack | Official Docker snapshot `self-hosted/v0.7.2`; exact commit in `UPSTREAM_VERSION`; PostgreSQL 17 and GoTrue versions are pinned in Compose | Selected |
| SMTP | Dedicated SMTP2GO SMTP credentials are stored in the protected local Auth environment; live invite/confirmation and recovery/password-reset messages were delivered and post-reset login passed on 2026-08-06 | Passed |
| Backup policy | Daily encrypted database dump; 30-day online retention; GitHub Actions artifact is the off-host destination; the exact production artifact was checksum-verified and clean-restored off production | Passed |
| Recovery objective | RPO 24 hours and RTO 4 hours | Selected |
| Rollback window | Seven days | Selected |
| Rollback owner | GitHub operator `moshehbenavraham` | Selected |
| Managed source | Owner confirmed on 2026-08-06 that the former free-tier hosted Supabase database was deleted; no source data or credentials remain to export | Resolved as an explicit clean start; prior users must create new accounts |

The clean-start role assignment, live SMTP delivery, encrypted off-host backup,
clean recovery, application deployment, and authenticated browser gates all
passed on 2026-08-06. No migration gate remains open.

## Automated controls

- `.github/workflows/self-hosted-auth-drill.yml` runs the destructive full Auth
  and clean-restore drill only against a disposable stack with the explicit
  Inbucket test override.
- `.github/workflows/self-hosted-auth-deploy.yml` validates every change but
  deploys only from a manual run whose input is exactly `deploy-auth`, through
  the protected `production-auth` environment and only from `main`. Production
  Auth deployments are serialized. The workflow preserves the remote `.env`
  and database volume, refuses the test override, requires `age`, takes
  encrypted pre/post-deploy backups, checks the loopback/private-port boundary,
  and configures/verifies the Auth-only Cloudflare ingress.
- `.github/workflows/self-hosted-auth-operations.yml` creates a daily encrypted
  backup, copies it off-host into a 30-day GitHub artifact with its SHA-256
  checksum, and checks public Auth health, backup age, and capacity hourly. Its
  scheduled job is enabled only when the repository variable
  `SELF_HOSTED_AUTH_OPERATIONS_ENABLED` is `true`; manual runs are always
  allowed. The variable was enabled after the production cutover passed.
- `.github/workflows/ci.yml` builds the pinned LuminariMUD source, performs real
  schema-initialization and fixture-load boots against MariaDB 10.11, and gates
  deployment on Wildeditor spatial, hint, profile, and cleanup compatibility.
- Frontend, backend, MCP, and chat production jobs can be dispatched manually
  from `main` during the controlled cutover. Automatic production deployment
  on later `main` pushes is controlled by the repository variable
  `SELF_HOSTED_AUTH_PRODUCTION_ENABLED`. It was enabled only after the
  self-hosted Auth readiness and application smoke gates passed.

Required protected GitHub inputs are `PRODUCTION_SSH_KEY`, `PRODUCTION_HOST`,
`PRODUCTION_USER`, `SELF_HOSTED_AUTH_ENV_B64` (first install only), and
`CLOUDFLARE_TUNNEL_CREDENTIALS_B64`, plus the existing
`CLOUDFLARE_TUNNEL_ID` repository variable. The base64 values are transport
encoding inside GitHub Secrets, not encryption. Production `.env` must include
the real SMTP values and `AUTH_BACKUP_AGE_RECIPIENT`; the matching age identity
must remain off-host.

As of 2026-08-06, `SELF_HOSTED_AUTH_URL`, the backend service credential, and
the Redis credential are populated in GitHub by name-only verification.
`SELF_HOSTED_AUTH_PRODUCTION_ENABLED` and
`SELF_HOSTED_AUTH_OPERATIONS_ENABLED` are `true` after the controlled cutover
passed. The generated values were not printed or copied into this repository.

As of 2026-08-06, the complete initial Auth environment, publishable key, test
account inputs, and backup recovery identity are present as protected GitHub
secrets by name-only verification. `age` v1.3.1 is installed in the production
operator's `$HOME/bin`; workflows prepend that directory to `PATH`.

SMTP credential locations are deliberately split:

- `infrastructure/supabase/.env` (ignored, mode `0600`) contains the SMTP host,
  port, username, password, and SMTP2GO-verified From address consumed by
  GoTrue.
- The repository-root `.env` (ignored, mode `0600`) contains
  `SMTP2GO_API_KEY` for operator API access only. It is not an Auth runtime
  input and must not be deployed with the stack.
- `~/.config/wildeditor/auth-backup-age-identity.txt` (mode `0600`) is the
  off-production-host recovery identity. The same identity is retained as the
  protected `AUTH_BACKUP_AGE_IDENTITY` GitHub secret; production receives only
  its public `age1…` recipient.

Record locations and variable names only. Never record either credential value
in this runbook, examples, issues, commits, or workflow output.

Backend and chat default to the self-hosted issuer only. If a real managed
source exists, set the protected production variable `WILDEDITOR_AUTH_ISSUERS`
to the exact comma-separated managed and self-hosted issuers for the rollback
window. The deploy jobs reject an override that omits the self-hosted issuer.
Remove the override after the observation window.

## Trust and network boundary

- Cloudflare terminates public TLS and routes only the Auth hostname to
  `http://127.0.0.1:8010`.
- The loopback nginx gateway permits `/auth/v1/*` and `/health`; it returns 404
  for Studio, REST, Storage, Realtime, Functions, and other paths.
- The default Compose runtime contains only PostgreSQL, GoTrue Auth, Kong, and
  the Auth gateway. Supavisor and every non-Auth product service require the
  explicit `full-platform` profile and are not part of production.
- PostgreSQL publishes no host port in the Wildeditor override.
- Frontend code receives only the public Auth base URL and
  `sb_publishable_*` key. Signing keys, secret/service keys, database
  credentials, backend service keys, and SMTP credentials stay server-side.
- Backend and chat trust only exact configured issuers. The production issuer
  includes `/auth/v1`; its JWKS endpoint is
  `/auth/v1/.well-known/jwks.json`.

## Provisioning or rebuilding an isolated target

1. Copy `infrastructure/supabase/` to a clean host directory. Keep the official
   base Compose file and `docker-compose.wildeditor.yml` together.
2. Copy `.env.example` to `.env` with mode 600.
3. Generate secrets without capturing stdout in shared logs:

   ```sh
   sh scripts/generate-secrets.sh
   ```

4. Set the SMTP provider, off-host backup encryption recipient, and every
   remaining placeholder. Do not reuse MariaDB credentials or volumes.
5. Validate and start:

   ```sh
   sh scripts/validate-config.sh
   sh run.sh start
   sh scripts/smoke.sh http://127.0.0.1:8010
   ```

6. Add TLS/tunnel routing only after the loopback smoke passes. Confirm from an
   external network that the Auth endpoint works and ports 5432/6543 are
   unreachable.

## Managed-source inventory and export

Before the maintenance freeze, record only non-personal facts: source project
reference, PostgreSQL/Auth versions, enabled providers, signup and confirmation
policies, token lifetime, redirects, hooks, templates, extensions, and counts
for Auth users, identities, sessions, refresh tokens, and MFA factors. Also
record whether any public/custom schemas, Data API, Storage, Realtime, or Edge
Functions are actually used.

With the platform database URL held only in the operator environment:

```sh
SOURCE_DATABASE_URL='postgresql://…' \
  sh infrastructure/supabase/scripts/export-platform.sh /secure/export/path
```

The pinned script uses Supabase CLI dumps for roles, schema, and COPY-format
data and records checksums. Never substitute raw `pg_dump` for a platform
export: it includes reserved internals that the supported Supabase export
filters out.

## Rehearsal restore and reconciliation

Use a clean isolated stack, not production. Save the empty target snapshot
first, then restore the platform export:

```sh
AUTH_RESTORE_CONFIRM=restore-platform-export \
  sh scripts/restore-platform-export.sh /secure/export/path
sh scripts/apply-role-map.sh /secure/role-map.csv
sh scripts/inventory.sh > /secure/rehearsal-inventory.txt
sh scripts/smoke.sh http://127.0.0.1:8010
```

The role map contains UUID and role only, no email address. Compare source and
target table counts and UUID checksum. Designated users must then prove password
login, confirmation state, identity provider linkage, refresh, logout,
recovery, and roles. Run `auth-flow-smoke.sh` with credentials supplied through
the operator environment; enable `AUTH_TEST_RECOVERY=true` only while watching
the test mailbox.

Complete two clean restores from the same checked export. Record elapsed time,
versions, checksums, tests, operator, and outcome in the drill table below.

## Production cutover

Decision point A: abort unless source inventory, two rehearsals, SMTP delivery,
external network isolation, encrypted off-host backup, reviewed role map, and
application suites are green.

Keep `SELF_HOSTED_AUTH_PRODUCTION_ENABLED` unset during the cutover. Run the
reviewed workflows manually from `main` in dependency order: self-hosted Auth,
backend, MCP, chat, then frontend. This prevents a merge from switching the
browser or protected APIs before Auth is actually reachable.

1. If a real managed source exists, configure the protected exact dual-issuer
   list and deploy backend/chat for the observation window. Each issuer has its
   own derived or explicitly aligned JWKS URL. With an explicitly empty source,
   retain the self-hosted-only default.
2. Rotate to a new server-only `WILDEDITOR_BACKEND_SERVICE_KEY`; deploy the same
   value to backend and MCP. Keep the independent agent-to-MCP key.
3. Enter the announced maintenance window. Disable source signup/account
   changes and prevent identity divergence.
4. Run the final managed export and verify its checksums.
5. Restore to the clean production target, apply the reviewed UUID role map,
   and compare counts/checksum.
6. Point Cloudflare DNS/tunnel at loopback port 8010 and verify TLS, health,
   JWKS, rate limiting, and the non-Auth 404 boundary.
7. Set GitHub/Netlify public build values to the self-hosted Auth URL and its
   publishable key. Deploy the exact reviewed frontend artifact.
8. Require all users to sign in again; old managed access and refresh tokens
   are intentionally invalid under the new signing keys.
9. Prove login, refresh, logout, recovery, editor reads/writes, hint mutations,
   chat ownership, agent-to-MCP, MCP-to-backend, and MariaDB region/path loads.
10. End maintenance only after all smoke and reconciliation gates pass.
11. Set `SELF_HOSTED_AUTH_PRODUCTION_ENABLED=true` only after decision point B
    has passed, so future reviewed `main` pushes may deploy automatically.

Decision point B: roll back on failed reconciliation, broken password/recovery,
SMTP delivery failure, repeated Auth 5xx, unexpected public PostgreSQL access,
or an application authorization regression.

## Rollback during the observation window

1. Freeze account changes again.
2. Redeploy the recorded pre-cutover frontend artifact and managed public
   Auth URL/key.
3. Keep exact dual-issuer validation active in backend/chat.
4. Restore prior backend/MCP/chat artifacts only if the new service boundary is
   itself faulty; never re-expose a backend key to the browser.
5. Reconcile or explicitly discard target-only identity changes. Never
   dual-write Auth state.
6. Record the decision and preserve target backups for diagnosis. MariaDB needs
   no restore because this migration never changes it.

After the approved healthy window, remove the managed issuer, old public
secrets, and old artifacts; take a final managed export before project
decommissioning.

## Backups, restore drills, and monitoring

Configure an `age` recipient and off-host synchronization before production:

```sh
AUTH_BACKUP_AGE_RECIPIENT='age1…' sh scripts/backup.sh
AUTH_PUBLIC_URL='https://wildedit-auth.luminarimud.com' sh scripts/monitor.sh
```

Schedule backup daily and monitoring at least hourly (use a five-minute
external probe when available). Alert on
non-zero exit, Auth/DB container health, public smoke failure, backup age over
25 hours, less than 10 GiB free, SMTP failures, sustained login failures, and
API 401/403/5xx changes. A backup is not accepted until an isolated clean
restore passes:

```sh
AUTH_BACKUP_AGE_IDENTITY=/secure/identity.txt \
AUTH_RESTORE_CONFIRM=restore-auth-database \
  sh scripts/restore.sh /secure/wildeditor-auth-TIMESTAMP.dump.age
```

Never point the restore script at a serving instance. Stop at its explicit
confirmation and independently verify the target directory/host first.
The scripts connect inside the pinned database container as the Supabase-owned
`supabase_admin` superuser. Restore stops every stack database client, replaces
only the explicitly confirmed target database, then transactionally restores
original owners and ACLs. This avoids invalid drop ordering among initialized
Realtime partitions and event triggers. PostgreSQL is never exposed on the
host.

## User and role administration

Use the Auth admin API only from a protected operator environment with the
server-side secret key. Invite rather than enabling public signup. Set
`app_metadata.app_role` to one of `viewer`, `editor`, or `admin`; never use
`user_metadata` for authorization. After a role change, revoke sessions or ask
the user to refresh/sign in again, then inspect the new token through the API
tests without logging it. Suspending or deleting a user requires a backup and a
ticket/record identifying the approving operator.

## Key rotation

- Signing keys: add a new ES256 key, recreate Auth, prove new tokens and old-key
  overlap through JWKS, wait at least the maximum token lifetime plus cache
  TTL, then remove the old key. Never rotate by silently copying the managed
  signing secret.
- Publishable/secret Auth keys: use the pinned upstream rotation utilities,
  deploy consumers, verify, then revoke old keys.
- Backend service key: generate a random replacement, deploy backend and MCP
  together, verify MCP calls/audit context, then revoke the prior value.
- MCP ingress key: deploy MCP and agent together, verify agent tools, then
  revoke the prior value.

Record key identifiers and times, never key material.

## Upgrade procedure

Read `UPSTREAM_VERSION`, upstream changelog, image diffs, and PostgreSQL/Auth
compatibility notes. Pin a new official snapshot in a branch, restore the latest
production backup into isolated staging, and run the entire Auth/application
suite. Take a fresh production backup, deploy exact rehearsed artifacts, and
retain the prior images/config until the observation window closes. Never run a
PostgreSQL major-version image against an existing older data directory.

## Incident response

- Auth unavailable: preserve logs without response bodies/tokens, check DB and
  gateway health, capacity, and recent config/key changes; restore or roll back
  only from a verified artifact.
- SMTP failure: keep signup invite-only, do not autoconfirm users to mask the
  problem, inspect provider delivery/bounce telemetry and sender DNS, then
  repeat confirmation/recovery tests.
- Suspected key exposure: identify key class, rotate only that boundary, revoke
  it, inspect access/audit logs, invalidate sessions when signing material may
  be affected, and document scope.

## Drill and cutover record

| Date UTC | Environment | Export/backup checksum | Source/target counts matched | Auth flow | Restore elapsed | Operator | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-08-05 | Disposable local pinned stack | Matched by full drill | Yes, including UUID aggregate and owners/ACLs | Confirmation, role, login, refresh, logout/revocation, recovery/update, post-restore login, and real-token backend/chat ownership passed | Completed; timing not yet accepted as production rehearsal | Codex/local operator | Passed; engineering proof only, not a source-data rehearsal |
| 2026-08-05 | Clean-start rehearsal 1, disposable pinned stack | Generated backup checksum verified | Yes, including UUID aggregate and database owners/ACLs | Full confirmation, recovery, role, login, refresh, logout/revocation, restore, and post-restore login passed | Completed within the 4-hour RTO | Codex/GitHub Actions | Passed |
| 2026-08-05 | Clean-start rehearsal 2, independent disposable pinned stack | Generated backup checksum verified | Yes, including UUID aggregate and database owners/ACLs | Full confirmation, recovery, role, login, refresh, logout/revocation, restore, and post-restore login passed | Completed within the 4-hour RTO | Codex/GitHub Actions | Passed |
| 2026-08-05 | Production backup restored into an isolated clean stack | Exact encrypted artifact SHA-256 verified before decryption | Yes: one user, one identity, `editor` role, UUID aggregate, schema/table owners, and no sessions/tokens matched production | Restored Auth health, JWKS, and Auth-only public-boundary checks passed | Completed within the 4-hour RTO | Codex/production operator | Passed; disposable target and decrypted dump removed after verification |
| 2026-08-05 | Production cutover | Encrypted production backup retained off-host by workflow run `31050863086` | MariaDB authority loaded 42 regions and 7 paths through the authenticated editor | Live SMTP invite/confirmation and recovery/password update passed; login, refresh, logout/revocation, backend reads, chat opening, and desktop/mobile browser smoke passed without runtime errors | Not applicable | Codex/production operator | Passed; Auth run `31050821366` and application run `31051862257` |
