#!/bin/sh
set -eu

cd "$(dirname "$0")/.."

max_backup_age_hours=${AUTH_BACKUP_MAX_AGE_HOURS:-25}
minimum_free_mb=${AUTH_MINIMUM_FREE_MB:-10240}

docker compose ps --status running --services | grep -qx auth
docker compose ps --status running --services | grep -qx db
sh scripts/smoke.sh "${AUTH_PUBLIC_URL:-http://127.0.0.1:8010}"

latest_backup=$(find "${AUTH_BACKUP_DIR:-./backups}" -type f \
  \( -name 'wildeditor-auth-*.dump' -o -name 'wildeditor-auth-*.dump.age' \) \
  -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -n 1 | cut -d' ' -f2-)
if [ -z "$latest_backup" ]; then
  echo "No Auth backup found" >&2
  exit 1
fi

now=$(date +%s)
backup_epoch=$(date -r "$latest_backup" +%s)
backup_age_hours=$(((now - backup_epoch) / 3600))
if [ "$backup_age_hours" -gt "$max_backup_age_hours" ]; then
  echo "Latest Auth backup is ${backup_age_hours}h old" >&2
  exit 1
fi

free_mb=$(df -Pm . | awk 'NR == 2 {print $4}')
if [ "$free_mb" -lt "$minimum_free_mb" ]; then
  echo "Auth filesystem has only ${free_mb} MiB free" >&2
  exit 1
fi

echo "Auth services, endpoint, backup age, and disk capacity are healthy."
