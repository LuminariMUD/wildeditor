#!/bin/sh
set -eu

cd "$(dirname "$0")/.."

# This emits counts and a one-way aggregate over UUIDs only. It intentionally
# never selects email addresses, password hashes, tokens, or provider payloads.
docker compose exec -T db psql \
  --username postgres \
  --dbname "${POSTGRES_DB:-postgres}" \
  --no-psqlrc \
  --tuples-only \
  --field-separator '|' <<'SQL'
SELECT 'auth.users', count(*) FROM auth.users;
SELECT 'auth.identities', count(*) FROM auth.identities;
SELECT 'auth.sessions', count(*) FROM auth.sessions;
SELECT 'auth.refresh_tokens', count(*) FROM auth.refresh_tokens;
SELECT 'auth.mfa_factors', count(*) FROM auth.mfa_factors;
SELECT 'auth.users.uuid_checksum',
       md5(coalesce(string_agg(id::text, ',' ORDER BY id::text), ''))
FROM auth.users;
SELECT 'auth.users.viewer', count(*)
FROM auth.users WHERE raw_app_meta_data->>'app_role' = 'viewer';
SELECT 'auth.users.editor', count(*)
FROM auth.users WHERE raw_app_meta_data->>'app_role' = 'editor';
SELECT 'auth.users.admin', count(*)
FROM auth.users WHERE raw_app_meta_data->>'app_role' = 'admin';
SELECT 'auth.users.unmapped', count(*)
FROM auth.users
WHERE raw_app_meta_data->>'app_role' IS NULL
   OR raw_app_meta_data->>'app_role' NOT IN ('viewer', 'editor', 'admin');
SQL
