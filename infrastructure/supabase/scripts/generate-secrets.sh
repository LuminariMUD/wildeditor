#!/bin/sh
set -eu

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "Copy .env.example to .env before generating secrets" >&2
  exit 2
fi

umask 077
base_compose=$(mktemp)
base_environment=$(mktemp)
cp docker-compose.yml "$base_compose"
cp .env "$base_environment"
generation_succeeded=false

restore_inputs() {
  [ -f "$base_compose" ] || return 0
  cp "$base_compose" docker-compose.yml
  if [ "$generation_succeeded" != true ]; then
    cp "$base_environment" .env
  fi
  rm -f "$base_compose" .env.old docker-compose.yml.old
  if [ -f "$base_environment" ]; then
    shred -u "$base_environment" 2>/dev/null || rm -f "$base_environment"
  fi
}
trap restore_inputs EXIT HUP INT TERM

# The upstream asymmetric-key helper also uncomments entries in its base
# Compose file. Wildeditor carries those entries in its override, so restore
# the exact vendored base after the official key generation completes.
sh utils/generate-keys.sh --update-env >/dev/null
sh utils/add-new-auth-keys.sh --update-env >/dev/null
generation_succeeded=true
chmod 600 .env

echo "Generated Supabase secrets and ES256 keys in the protected .env file."
