#!/bin/sh
set -eu

cd "$(dirname "$0")/.."

if [ "$#" -ne 1 ]; then
  echo "Usage: AUTH_RESTORE_CONFIRM=restore-auth-database $0 <backup.dump>" >&2
  exit 2
fi

if [ "${AUTH_RESTORE_CONFIRM:-}" != "restore-auth-database" ]; then
  echo "Refusing destructive restore without AUTH_RESTORE_CONFIRM=restore-auth-database" >&2
  exit 2
fi

backup_path=$1
if [ ! -f "$backup_path" ]; then
  echo "Backup not found: $backup_path" >&2
  exit 2
fi

cleanup_restore_input() {
  if [ "${restore_input_is_temporary:-false}" = true ] \
    && [ -n "${restore_input:-}" ] \
    && [ -f "$restore_input" ]; then
    shred -u "$restore_input" 2>/dev/null || rm -f "$restore_input"
  fi
}

restore_input_is_temporary=false
case "$backup_path" in
  *.age)
    if [ -z "${AUTH_BACKUP_AGE_IDENTITY:-}" ]; then
      echo "AUTH_BACKUP_AGE_IDENTITY is required for an encrypted backup" >&2
      exit 2
    fi
    restore_input=$(mktemp)
    restore_input_is_temporary=true
    trap cleanup_restore_input EXIT HUP INT TERM
    age --decrypt --identity "$AUTH_BACKUP_AGE_IDENTITY" \
      --output "$restore_input" "$backup_path"
    ;;
  *)
    restore_input=$backup_path
    ;;
esac

database_name=${POSTGRES_DB:-postgres}
case "$database_name" in
  ''|template0|template1|*[!A-Za-z0-9_-]*)
    echo "Refusing unsafe POSTGRES_DB value" >&2
    exit 2
    ;;
esac

# Run only against a clean, isolated drill or an explicitly approved target.
# Stop every database client in the pinned stack so no refresh/session writes
# race the replacement. The database container itself must remain available.
non_db_services=$(docker compose config --services | sed '/^db$/d')
if [ -n "$non_db_services" ]; then
  # shellcheck disable=SC2086
  docker compose stop $non_db_services
fi

# Restoring --clean over Supabase's initialized Realtime partitions can try to
# drop inherited constraints in an invalid order. Replace the confirmed target
# database first, then restore the archive transactionally with its original
# owners and ACLs. Cluster roles come from the pinned Supabase init scripts.
docker compose exec -T db dropdb \
  --username supabase_admin \
  --maintenance-db template1 \
  --if-exists \
  --force \
  "$database_name"
docker compose exec -T db createdb \
  --username supabase_admin \
  --maintenance-db template1 \
  --owner postgres \
  --template template0 \
  "$database_name"
docker compose exec -T db pg_restore \
  --username supabase_admin \
  --dbname "$database_name" \
  --exit-on-error \
  --single-transaction < "$restore_input"

docker compose up -d --wait
echo "Auth restore completed; run scripts/smoke.sh and scripts/auth-flow-smoke.sh."
