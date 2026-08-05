# Repository scripts

This directory contains manual setup, diagnostic, credential, and SQL utilities accumulated across several deployment approaches. These files are not a supported installer or migration framework. Read an entire script, resolve every target and environment variable, and test it in a disposable environment before running it.

The authoritative deployment definitions are the service Dockerfiles and `.github/workflows/`. The authoritative application schema is the owning datastore plus new migrations under `apps/backend/migrations/` or `supabase/migrations/`.

## Inventory

| Files | Intended use | Required review |
| --- | --- | --- |
| `setup-server.sh`, `debug-path.sh` | One-off Linux host setup and path diagnostics | Package-manager, firewall, filesystem, and privilege assumptions |
| `diagnose_production_ai.sh`, `fix_ollama_network.sh`, `setup_openai_from_luminari.sh` | AI-provider and container-network troubleshooting | Production hosts, container names, network mutations, provider secrets |
| `setup_github_secrets.sh`, `generate-mcp-keys.ps1`, `validate-secrets.ps1`, `setup-copilot-mcp.ps1` | Secret generation/checks and local MCP client setup | Values written to GitHub, local files, process output, or clipboard |
| `database-setup*.sql` | Historical database bootstrap snapshots | Current MySQL/MariaDB schema, spatial support, ownership, destructive statements |
| `setup-supabase-schema.sql` | Historical Supabase application-data design | This is not the current MySQL application schema or the proposed auth-only Supabase design |
| `fix_region_hints_table.sql`, `path_data_queries.sql` | Targeted repair and diagnostic SQL | Live table definitions, backup, transaction/rollback plan, production authorization |

Command-reference text files formerly stored here were moved to `docs/archive/2024-2025/service-notes/scripts/` because they describe point-in-time infrastructure.

## Safe use

1. Run from the repository root unless the script explicitly says otherwise.
2. Inspect the file for hard-coded hosts, account names, ports, container names, and mutations.
3. Supply credentials through the intended secret mechanism; never paste them into the script.
4. Prefer a disposable environment and a least-privileged account.
5. Back up and rehearse restoration before database or host changes.
6. Record the exact script revision, target, and result for an operational change.

Do not infer current production topology from these utilities. See [deployment](../docs/deployment.md), [operations](../docs/operations.md), and [backend migration guidance](../apps/backend/migrations/README.md).

When adding a reusable script, make it non-interactive where practical, fail safely, validate its resolved targets, document required privileges and side effects, and add a dry-run mode for consequential changes.
