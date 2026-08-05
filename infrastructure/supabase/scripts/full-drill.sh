#!/bin/sh
set -eu

cd "$(dirname "$0")/.."

if [ "${AUTH_FULL_DRILL_CONFIRM:-}" != "destroy-test-auth-database" ]; then
  echo "Refusing full drill without AUTH_FULL_DRILL_CONFIRM=destroy-test-auth-database" >&2
  exit 2
fi

if ! docker compose config --services | grep -qx inbucket; then
  echo "Full drill requires the explicit Inbucket test override" >&2
  exit 2
fi

for command in curl jq openssl docker; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "Required command is unavailable: $command" >&2
    exit 2
  }
done

base_url=${AUTH_PUBLIC_URL:-http://127.0.0.1:8010}
base_url=${base_url%/}
mail_url=${AUTH_TEST_MAIL_URL:-http://127.0.0.1:9010}
mail_url=${mail_url%/}
publishable_key=$(sed -n 's/^SUPABASE_PUBLISHABLE_KEY=//p' .env | tail -n 1)
secret_key=$(sed -n 's/^SUPABASE_SECRET_KEY=//p' .env | tail -n 1)
if [ -z "$publishable_key" ] || [ -z "$secret_key" ]; then
  echo "Generated publishable and secret Auth keys are required" >&2
  exit 2
fi

umask 077
work_dir=$(mktemp -d)
cleanup() {
  rm -r -- "$work_dir"
}
trap cleanup EXIT HUP INT TERM

test_email="wildeditor-drill-$(date -u +%Y%m%d%H%M%S)-$$@example.test"
initial_password=$(openssl rand -hex 24)
replacement_password=$(openssl rand -hex 24)
email_uri=$(printf '%s' "$test_email" | jq -sRr @uri)

wait_for_message() {
  subject_pattern=$1
  output_file=$2
  attempt=1
  while [ "$attempt" -le 20 ]; do
    curl --fail --silent --show-error \
      "$mail_url/api/v1/mailbox/$email_uri" > "$work_dir/mailbox.json"
    message_id=$(jq -er \
      --arg pattern "$subject_pattern" \
      'map(select(.subject | test($pattern; "i")))[0].id' \
      "$work_dir/mailbox.json" 2>/dev/null || true)
    if [ -n "$message_id" ]; then
      curl --fail --silent --show-error \
        "$mail_url/api/v1/mailbox/$email_uri/$message_id" > "$output_file"
      return 0
    fi
    sleep 1
    attempt=$((attempt + 1))
  done
  echo "Expected Auth email was not delivered to the test mailbox" >&2
  return 1
}

extract_verification_url() {
  message_file=$1
  jq -r '.body.html' "$message_file" \
    | grep -Eo 'href="[^"]+"' \
    | head -n 1 \
    | cut -d '"' -f 2 \
    | sed 's/&amp;/\&/g'
}

use_local_auth_origin() {
  external_url=$1
  case "$external_url" in
    "$base_url"/auth/v1/verify\?*) printf '%s' "$external_url" ;;
    https://auth.wildedit.luminarimud.com/auth/v1/verify\?*)
      printf '%s%s' "$base_url" "${external_url#https://auth.wildedit.luminarimud.com}"
      ;;
    *)
      echo "Auth email contained an unexpected verification origin" >&2
      return 1
      ;;
  esac
}

signup_body=$(jq -nc \
  --arg email "$test_email" \
  --arg password "$initial_password" \
  '{email:$email,password:$password}')
signup_status=$(curl --silent --show-error \
  --output "$work_dir/signup.json" \
  --write-out '%{http_code}' \
  --request POST \
  --header "apikey: $publishable_key" \
  --header 'Content-Type: application/json' \
  --data "$signup_body" \
  "$base_url/auth/v1/signup")
test "$signup_status" = 200
user_id=$(jq -er '.id' "$work_dir/signup.json")
jq -e '.confirmation_sent_at != null and .email_confirmed_at == null' \
  "$work_dir/signup.json" >/dev/null

wait_for_message 'Confirm' "$work_dir/confirmation-message.json"
confirmation_url=$(extract_verification_url "$work_dir/confirmation-message.json")
local_confirmation_url=$(use_local_auth_origin "$confirmation_url")
confirmation_status=$(curl --silent --show-error \
  --output "$work_dir/confirmation-body" \
  --dump-header "$work_dir/confirmation-headers" \
  --write-out '%{http_code}' \
  "$local_confirmation_url")
case "$confirmation_status" in 302|303) ;; *) exit 1 ;; esac

role_body=$(jq -nc '{app_metadata:{app_role:"editor"}}')
role_status=$(curl --silent --show-error \
  --output "$work_dir/role.json" \
  --write-out '%{http_code}' \
  --request PUT \
  --header "apikey: $secret_key" \
  --header 'Content-Type: application/json' \
  --data "$role_body" \
  "$base_url/auth/v1/admin/users/$user_id")
test "$role_status" = 200
jq -e '.email_confirmed_at != null and .app_metadata.app_role == "editor"' \
  "$work_dir/role.json" >/dev/null

AUTH_TEST_EMAIL=$test_email \
AUTH_TEST_PASSWORD=$initial_password \
AUTH_TEST_ROLE=editor \
  sh scripts/auth-flow-smoke.sh "$base_url"

recovery_body=$(jq -nc --arg email "$test_email" '{email:$email}')
curl --fail --silent --show-error \
  --request POST \
  --header "apikey: $publishable_key" \
  --header 'Content-Type: application/json' \
  --data "$recovery_body" \
  "$base_url/auth/v1/recover?redirect_to=http://localhost:5173/reset-password" \
  >/dev/null

wait_for_message 'Reset|Password|Recovery' "$work_dir/recovery-message.json"
recovery_url=$(extract_verification_url "$work_dir/recovery-message.json")
local_recovery_url=$(use_local_auth_origin "$recovery_url")
recovery_status=$(curl --silent --show-error \
  --output "$work_dir/recovery-body" \
  --dump-header "$work_dir/recovery-headers" \
  --write-out '%{http_code}' \
  "$local_recovery_url")
case "$recovery_status" in 302|303) ;; *) exit 1 ;; esac

recovery_location=$(sed -n 's/^location: //Ip' "$work_dir/recovery-headers" \
  | tr -d '\r' \
  | tail -n 1)
recovery_fragment=${recovery_location#*#}
recovery_access_token=$(printf '%s' "$recovery_fragment" \
  | tr '&' '\n' \
  | sed -n 's/^access_token=//p' \
  | tail -n 1)
recovery_type=$(printf '%s' "$recovery_fragment" \
  | tr '&' '\n' \
  | sed -n 's/^type=//p' \
  | tail -n 1)
test -n "$recovery_access_token"
test "$recovery_type" = recovery

password_body=$(jq -nc --arg password "$replacement_password" '{password:$password}')
password_status=$(curl --silent --show-error \
  --output "$work_dir/password-update.json" \
  --write-out '%{http_code}' \
  --request PUT \
  --header "apikey: $publishable_key" \
  --header "Authorization: Bearer $recovery_access_token" \
  --header 'Content-Type: application/json' \
  --data "$password_body" \
  "$base_url/auth/v1/user")
test "$password_status" = 200
jq -e '.id != null and .app_metadata.app_role == "editor"' \
  "$work_dir/password-update.json" >/dev/null

AUTH_TEST_EMAIL=$test_email \
AUTH_TEST_PASSWORD=$replacement_password \
AUTH_TEST_ROLE=editor \
  sh scripts/auth-flow-smoke.sh "$base_url"

sh scripts/inventory.sh | sed 's/^ *//;s/ *$//' > "$work_dir/inventory-before.txt"
AUTH_BACKUP_DIR="$work_dir/backups" \
AUTH_BACKUP_RETENTION_DAYS=1 \
  sh scripts/backup.sh
backup_path=$(find "$work_dir/backups" -maxdepth 1 -type f \
  -name 'wildeditor-auth-*.dump' -print | sort | tail -n 1)
test -n "$backup_path"

AUTH_RESTORE_CONFIRM=restore-auth-database \
  sh scripts/restore.sh "$backup_path"
sh scripts/smoke.sh "$base_url"
sh scripts/inventory.sh | sed 's/^ *//;s/ *$//' > "$work_dir/inventory-after.txt"
diff -u "$work_dir/inventory-before.txt" "$work_dir/inventory-after.txt"

ownership=$(docker compose exec -T db psql \
  --username supabase_admin \
  --dbname "${POSTGRES_DB:-postgres}" \
  --no-psqlrc \
  --tuples-only \
  --field-separator '|' \
  --command "SELECT pg_get_userbyid(n.nspowner), pg_get_userbyid(c.relowner) FROM pg_namespace n JOIN pg_class c ON c.relnamespace = n.oid WHERE n.nspname = 'auth' AND c.relname = 'users';" \
  | tr -d ' \n\r')
test "$ownership" = 'supabase_admin|supabase_auth_admin'

AUTH_TEST_EMAIL=$test_email \
AUTH_TEST_PASSWORD=$replacement_password \
AUTH_TEST_ROLE=editor \
  sh scripts/auth-flow-smoke.sh "$base_url"

echo "Full Auth confirmation, role, reset, JWT/session, backup, and clean restore drill passed."
