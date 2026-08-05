# Backend MySQL migrations

This directory contains Wildeditor-owned changes to the LuminariMUD MySQL/MariaDB datastore. The game project's owning schema remains authoritative for shared tables.

## Current migration

`002_add_region_hints_tables.sql` creates `region_hints`, `region_profiles`, and `hint_usage_log` with foreign keys to `region_data`. There is no `001` file in this directory; do not infer an initial schema from the numbering.

The migration is dated historical SQL and may differ from current model validation. In particular, compare hint categories and column names against `src/models/region_hints.py`, `src/schemas/region_hints.py`, and the owning live schema before applying it to a new environment.

## Safe application process

1. Confirm this repository owns the intended schema change.
2. Back up the target database and restore the backup in isolation.
3. Review the SQL against the target MySQL/MariaDB version and live table definitions.
4. Apply it to the restored/development copy first.
5. Run `src/check_hints_tables.py` and focused backend/API compatibility checks.
6. Schedule and record the production migration with an explicit rollback plan.

Example against a disposable database:

```bash
mysql -h "$DB_HOST" -u "$DB_USER" -p "$DB_NAME" \
  < apps/backend/migrations/002_add_region_hints_tables.sql
```

The command prompts for the password. Do not put credentials in shell history.

To inspect table presence after setting `MYSQL_DATABASE_URL`:

```bash
python apps/backend/src/check_hints_tables.py
```

Add future changes as new migration files. Never rewrite a migration that may already have been applied, and never mix these MySQL changes with `supabase/migrations/`.
