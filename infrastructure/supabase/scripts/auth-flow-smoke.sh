#!/bin/sh
set -eu

cd "$(dirname "$0")/.."

base_url=${1:-http://127.0.0.1:8010}
base_url=${base_url%/}

if [ -z "${AUTH_TEST_EMAIL:-}" ] || [ -z "${AUTH_TEST_PASSWORD:-}" ]; then
  echo "AUTH_TEST_EMAIL and AUTH_TEST_PASSWORD are required" >&2
  exit 2
fi

publishable_key=$(sed -n 's/^SUPABASE_PUBLISHABLE_KEY=//p' .env | tail -n 1)
if [ -z "$publishable_key" ]; then
  echo "SUPABASE_PUBLISHABLE_KEY is missing from .env" >&2
  exit 2
fi

umask 077
response_file=$(mktemp)
refresh_file=$(mktemp)
trap 'rm -f "$response_file" "$refresh_file"' EXIT

login_body=$(jq -nc \
  --arg email "$AUTH_TEST_EMAIL" \
  --arg password "$AUTH_TEST_PASSWORD" \
  '{email:$email,password:$password}')

curl --fail --silent --show-error \
  --request POST \
  --header "apikey: $publishable_key" \
  --header 'Content-Type: application/json' \
  --data "$login_body" \
  "$base_url/auth/v1/token?grant_type=password" > "$response_file"

access_token=$(jq -er '.access_token' "$response_file")
refresh_token=$(jq -er '.refresh_token' "$response_file")
expected_role=${AUTH_TEST_ROLE:-editor}
jq -e --arg expected_role "$expected_role" \
  '.user.id and .user.aud == "authenticated" and .user.app_metadata.app_role == $expected_role' \
  "$response_file" >/dev/null

curl --fail --silent --show-error \
  --header "apikey: $publishable_key" \
  --header "Authorization: Bearer $access_token" \
  "$base_url/auth/v1/user" \
  | jq -e '.id' >/dev/null

refresh_body=$(jq -nc --arg refresh_token "$refresh_token" \
  '{refresh_token:$refresh_token}')
curl --fail --silent --show-error \
  --request POST \
  --header "apikey: $publishable_key" \
  --header 'Content-Type: application/json' \
  --data "$refresh_body" \
  "$base_url/auth/v1/token?grant_type=refresh_token" > "$refresh_file"

refreshed_access_token=$(jq -er '.access_token' "$refresh_file")
refreshed_refresh_token=$(jq -er '.refresh_token' "$refresh_file")

curl --fail --silent --show-error \
  --request POST \
  --header "apikey: $publishable_key" \
  --header "Authorization: Bearer $refreshed_access_token" \
  "$base_url/auth/v1/logout" >/dev/null

logout_refresh_body=$(jq -nc --arg refresh_token "$refreshed_refresh_token" \
  '{refresh_token:$refresh_token}')
status=$(curl --silent --output /dev/null --write-out '%{http_code}' \
  --request POST \
  --header "apikey: $publishable_key" \
  --header 'Content-Type: application/json' \
  --data "$logout_refresh_body" \
  "$base_url/auth/v1/token?grant_type=refresh_token")
case "$status" in
  400|401) ;;
  *) echo "Logged-out refresh token was accepted (HTTP $status)" >&2; exit 1 ;;
esac

if [ "${AUTH_TEST_RECOVERY:-false}" = "true" ]; then
  recovery_body=$(jq -nc \
    --arg email "$AUTH_TEST_EMAIL" \
    --arg redirect_to "${AUTH_TEST_RECOVERY_REDIRECT:-https://wildedit.luminarimud.com/reset-password}" \
    '{email:$email,gotrue_meta_security:{captcha_token:null}}')
  curl --fail --silent --show-error \
    --request POST \
    --header "apikey: $publishable_key" \
    --header 'Content-Type: application/json' \
    --data "$recovery_body" \
    "$base_url/auth/v1/recover?redirect_to=${AUTH_TEST_RECOVERY_REDIRECT:-https://wildedit.luminarimud.com/reset-password}" >/dev/null
fi

echo "Password login, user lookup, refresh, logout, and refresh revocation passed."
