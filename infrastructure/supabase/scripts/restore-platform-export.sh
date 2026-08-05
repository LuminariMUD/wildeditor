#!/bin/sh
set -eu

cd "$(dirname "$0")/.."

if [ "$#" -ne 1 ]; then
  echo "Usage: AUTH_RESTORE_CONFIRM=restore-platform-export $0 <export-directory>" >&2
  exit 2
fi

if [ "${AUTH_RESTORE_CONFIRM:-}" != "restore-platform-export" ]; then
  echo "Refusing restore without AUTH_RESTORE_CONFIRM=restore-platform-export" >&2
  exit 2
fi

export_dir=$1
for name in roles.sql schema.sql data.sql SHA256SUMS; do
  if [ ! -f "$export_dir/$name" ]; then
    echo "Missing managed export file: $name" >&2
    exit 2
  fi
done

(cd "$export_dir" && sha256sum --check SHA256SUMS)

docker compose stop studio kong auth rest realtime storage imgproxy meta functions supavisor

{
  cat "$export_dir/roles.sql"
  cat "$export_dir/schema.sql"
  printf '%s\n' 'SET session_replication_role = replica;'
  cat "$export_dir/data.sql"
} | docker compose exec -T db psql \
  --username postgres \
  --dbname "${POSTGRES_DB:-postgres}" \
  --no-psqlrc \
  --single-transaction \
  --set ON_ERROR_STOP=1

docker compose up -d --wait
echo "Managed export restored; apply the reviewed role map and reconcile inventory."
