#!/bin/sh
set -eu

cd "$(dirname "$0")/.."

backup_dir=${AUTH_BACKUP_DIR:-./backups}
retention_days=${AUTH_BACKUP_RETENTION_DAYS:-30}
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
backup_path="${backup_dir}/wildeditor-auth-${timestamp}.dump"
mkdir -p "$backup_dir"

umask 077
docker compose exec -T db pg_dump \
  --username supabase_admin \
  --dbname "${POSTGRES_DB:-postgres}" \
  --format custom \
  --compress 9 > "$backup_path"

if [ -n "${AUTH_BACKUP_AGE_RECIPIENT:-}" ]; then
  encrypted_path="${backup_path}.age"
  cleanup_plaintext() {
    if [ -f "$backup_path" ]; then
      shred -u "$backup_path" 2>/dev/null || rm -f "$backup_path"
    fi
  }
  trap cleanup_plaintext EXIT HUP INT TERM
  age --recipient "$AUTH_BACKUP_AGE_RECIPIENT" \
    --output "$encrypted_path" "$backup_path"
  cleanup_plaintext
  trap - EXIT HUP INT TERM
  backup_path=$encrypted_path
fi

find "$backup_dir" -type f \
  \( -name 'wildeditor-auth-*.dump' -o -name 'wildeditor-auth-*.dump.age' \) \
  -mtime "+$retention_days" -delete

echo "Auth backup created: $backup_path"
