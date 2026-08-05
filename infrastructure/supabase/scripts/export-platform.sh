#!/bin/sh
set -eu

cd "$(dirname "$0")/.."

if [ -z "${SOURCE_DATABASE_URL:-}" ]; then
  echo "SOURCE_DATABASE_URL is required in the operator environment" >&2
  exit 2
fi

case "$SOURCE_DATABASE_URL" in
  *your-project*|*example.com*)
    echo "SOURCE_DATABASE_URL is still a placeholder" >&2
    exit 2
    ;;
esac

export_dir=${1:-./migration-export}
cli_version=${SUPABASE_CLI_VERSION:-2.111.0}
mkdir -p "$export_dir"
chmod 700 "$export_dir"
umask 077

npx --yes "supabase@${cli_version}" db dump \
  --db-url "$SOURCE_DATABASE_URL" \
  --file "$export_dir/roles.sql" \
  --role-only
npx --yes "supabase@${cli_version}" db dump \
  --db-url "$SOURCE_DATABASE_URL" \
  --file "$export_dir/schema.sql"
npx --yes "supabase@${cli_version}" db dump \
  --db-url "$SOURCE_DATABASE_URL" \
  --file "$export_dir/data.sql" \
  --use-copy \
  --data-only

sha256sum \
  "$export_dir/roles.sql" \
  "$export_dir/schema.sql" \
  "$export_dir/data.sql" > "$export_dir/SHA256SUMS"

echo "Managed export created in $export_dir; no source credentials were written."
