#!/bin/sh
set -eu

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "Missing infrastructure/supabase/.env" >&2
  exit 1
fi

required='POSTGRES_PASSWORD JWT_SECRET SUPABASE_PUBLISHABLE_KEY SUPABASE_SECRET_KEY JWT_KEYS JWT_JWKS DASHBOARD_PASSWORD SECRET_KEY_BASE VAULT_ENC_KEY PG_META_CRYPTO_KEY SMTP_ADMIN_EMAIL SMTP_HOST SMTP_USER SMTP_PASS SITE_URL API_EXTERNAL_URL SUPABASE_PUBLIC_URL ADDITIONAL_REDIRECT_URLS'
for name in $required; do
  value=$(sed -n "s/^${name}=//p" .env | tail -n 1)
  if [ -z "$value" ]; then
    echo "Missing required value: $name" >&2
    exit 1
  fi
  case "$value" in
    *replace*|*your-*|*fake_*|*example.com*|*xxxxxxxx*)
      echo "Placeholder value remains: $name" >&2
      exit 1
      ;;
  esac
done

compose_files=$(sed -n 's/^COMPOSE_FILE=//p' .env | tail -n 1)
case ":${compose_files}:" in
  *:docker-compose.wildeditor.yml:*) ;;
  *)
    echo "COMPOSE_FILE must include docker-compose.wildeditor.yml" >&2
    exit 1
    ;;
esac

case "$(sed -n 's/^API_EXTERNAL_URL=//p' .env | tail -n 1)" in
  */auth/v1) ;;
  *)
    echo "API_EXTERNAL_URL must end in /auth/v1" >&2
    exit 1
    ;;
esac

case "$(sed -n 's/^DISABLE_SIGNUP=//p' .env | tail -n 1)" in
  true) ;;
  *)
    echo "Production signup must remain invite-only (DISABLE_SIGNUP=true)" >&2
    exit 1
    ;;
esac

docker compose --env-file .env config --quiet

active_services=$(docker compose --env-file .env config --services)
for service in db auth kong auth-gateway; do
  if ! printf '%s\n' "$active_services" | grep -qx "$service"; then
    echo "Required Auth runtime service is disabled: $service" >&2
    exit 1
  fi
done

for service in studio rest realtime storage imgproxy meta functions supavisor; do
  if printf '%s\n' "$active_services" | grep -qx "$service"; then
    echo "Non-Auth service is active in the default runtime: $service" >&2
    exit 1
  fi
done

echo "Self-hosted Auth configuration is structurally valid."
