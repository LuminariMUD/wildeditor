# Wildeditor self-hosted Auth

This directory vendors the official Supabase Docker snapshot recorded in
`UPSTREAM_VERSION`. The base stack is intentionally kept intact for supported
upgrades and restore compatibility. `docker-compose.wildeditor.yml` layers the
Wildeditor production boundary on top:

- only the Auth gateway binds a host port, and it binds to loopback;
- PostgreSQL and Supavisor have no host ports;
- the public gateway permits `/auth/v1/*` and health only;
- the default runtime starts only PostgreSQL, GoTrue Auth, Kong, and the Auth
  gateway;
- Studio, REST, Realtime, Storage, Functions, Meta, Imgproxy, and Supavisor are
  disabled behind the explicit `full-platform` Compose profile;
- the LuminariMUD MariaDB is not referenced, mounted, migrated, or replicated.

## First staging install

1. Copy `.env.example` to `.env` and replace every placeholder. Never commit
   `.env`.
2. Generate secrets and asymmetric Auth/API keys with
   `sh scripts/generate-secrets.sh`.
3. Configure real SMTP delivery and exact redirect URLs in `.env`.
4. Install `age`, set `AUTH_BACKUP_AGE_RECIPIENT` to an off-host public
   recipient, and keep the matching identity outside this server.
5. Run `sh scripts/validate-config.sh`.
6. Start the supported Auth runtime with `sh run.sh start`.
7. Point the TLS/Cloudflare tunnel hostname at `http://127.0.0.1:8010`.
8. Run `sh scripts/smoke.sh https://auth.wildedit.luminarimud.com`.

Do not run the legacy SQL under the repository root `supabase/migrations/`.
Wildeditor game/wilderness data remains exclusively in MariaDB.

## Credential locations

- `infrastructure/supabase/.env` is the ignored, mode-`0600` Auth runtime
  environment. SMTP delivery uses `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, and
  `SMTP_PASS` from this file.
- The repository-root `.env` is the ignored, mode-`0600` operator environment.
  `SMTP2GO_API_KEY` lives there for SMTP2GO API administration only; GoTrue
  does not use it and it must not be copied into this stack.
- The backup recovery identity lives off-host at
  `~/.config/wildeditor/auth-backup-age-identity.txt` with mode `0600` and in
  the protected `AUTH_BACKUP_AGE_IDENTITY` GitHub secret. This stack receives
  only its public `AUTH_BACKUP_AGE_RECIPIENT`.
- Values never belong in `.env.example`, documentation, Git history, Vite
  variables, or command output.

For an isolated local Auth/email rehearsal, append
`docker-compose.wildeditor-test.yml` to `COMPOSE_FILE`. That explicit test
override enables signup and adds a loopback-only Inbucket mailbox on port 9010;
it must never be used for staging or production configuration.

## Routine commands

```bash
sh run.sh start
sh run.sh logs auth
sh scripts/backup.sh
sh scripts/monitor.sh
sh scripts/smoke.sh https://auth.wildedit.luminarimud.com
```

See `docs/operations/self-hosted-auth-runbook.md` for backup restore, migration,
cutover, rollback, role administration, and key rotation procedures.
The gated production operations workflow creates a daily encrypted backup,
retains an off-host copy as a 30-day GitHub artifact, and checks health, backup
age, and disk capacity hourly once
`SELF_HOSTED_AUTH_OPERATIONS_ENABLED=true` is set as a repository variable.
Keep `SELF_HOSTED_AUTH_PRODUCTION_ENABLED` unset until the controlled cutover
has passed the Auth and application smoke gates; it enables automatic frontend
and service deployments on subsequent `main` pushes.
