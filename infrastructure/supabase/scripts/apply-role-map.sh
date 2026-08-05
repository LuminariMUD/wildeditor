#!/bin/sh
set -eu

cd "$(dirname "$0")/.."

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <role-map.csv>" >&2
  echo "CSV rows: user_uuid,viewer|editor|admin (no header, no emails)" >&2
  exit 2
fi

role_map=$1
if [ ! -f "$role_map" ]; then
  echo "Role map not found: $role_map" >&2
  exit 2
fi

values_file=$(mktemp)
sql_file=$(mktemp)
trap 'rm -f "$values_file" "$sql_file"' EXIT

row_count=0
while IFS=, read -r user_id role extra; do
  [ -z "$user_id$role$extra" ] && continue
  case "$user_id" in
    ????????-????-????-????-????????????) ;;
    *) echo "Invalid user UUID in role map" >&2; exit 2 ;;
  esac
  case "$user_id" in
    *[!0-9A-Fa-f-]*) echo "Invalid user UUID in role map" >&2; exit 2 ;;
  esac
  case "$role" in
    viewer|editor|admin) ;;
    *) echo "Invalid role in role map" >&2; exit 2 ;;
  esac
  if [ -n "$extra" ]; then
    echo "Unexpected extra column in role map" >&2
    exit 2
  fi
  if [ "$row_count" -gt 0 ]; then
    printf ',\n' >> "$values_file"
  fi
  printf "('%s'::uuid, '%s')" "$user_id" "$role" >> "$values_file"
  row_count=$((row_count + 1))
done < "$role_map"

if [ "$row_count" -eq 0 ]; then
  echo "Role map is empty" >&2
  exit 2
fi

{
  printf '%s\n' 'BEGIN;'
  printf '%s\n' 'CREATE TEMP TABLE wildeditor_role_map (user_id uuid PRIMARY KEY, app_role text NOT NULL);'
  printf '%s\n' 'INSERT INTO wildeditor_role_map (user_id, app_role) VALUES'
  cat "$values_file"
  printf ';\n'
  printf '%s\n' "DO \$\$ BEGIN"
  printf '%s\n' "  IF EXISTS (SELECT 1 FROM wildeditor_role_map WHERE app_role NOT IN ('viewer', 'editor', 'admin')) THEN"
  printf '%s\n' "    RAISE EXCEPTION 'invalid Wildeditor role';"
  printf '%s\n' '  END IF;'
  printf '%s\n' '  IF (SELECT count(*) FROM wildeditor_role_map) <> (SELECT count(*) FROM auth.users u JOIN wildeditor_role_map m ON m.user_id = u.id) THEN'
  printf '%s\n' "    RAISE EXCEPTION 'role map contains an unknown user UUID';"
  printf '%s\n' '  END IF;'
  printf '%s\n' 'END $$;'
  printf '%s\n' "UPDATE auth.users AS u SET raw_app_meta_data = coalesce(u.raw_app_meta_data, '{}'::jsonb) || jsonb_build_object('app_role', m.app_role) FROM wildeditor_role_map AS m WHERE u.id = m.user_id;"
  printf '%s\n' 'COMMIT;'
  printf '%s\n' 'SELECT count(*) AS roles_applied FROM wildeditor_role_map;'
} > "$sql_file"

docker compose exec -T db psql \
  --username postgres \
  --dbname "${POSTGRES_DB:-postgres}" \
  --no-psqlrc \
  --set ON_ERROR_STOP=1 < "$sql_file"
