#!/usr/bin/env bash
set -euo pipefail

# Generate and install the three independent server-only credentials used by
# the production workflows. Values travel to GitHub CLI over stdin and are
# never printed or written to a plaintext file.

command -v gh >/dev/null 2>&1 || {
  echo "gh is required" >&2
  exit 1
}
command -v openssl >/dev/null 2>&1 || {
  echo "openssl is required" >&2
  exit 1
}
gh auth status >/dev/null

repo_args=()
if [[ -n "${GITHUB_REPOSITORY:-}" ]]; then
  repo_args=(--repo "$GITHUB_REPOSITORY")
fi

generate_secret() {
  openssl rand -hex 32
}

set_secret() {
  local name=$1
  local value=$2
  printf '%s' "$value" | gh secret set "$name" "${repo_args[@]}"
}

mcp_key=${WILDEDITOR_MCP_KEY:-$(generate_secret)}
backend_service_key=${WILDEDITOR_BACKEND_SERVICE_KEY:-$(generate_secret)}
redis_password=${WILDEDITOR_REDIS_PASSWORD:-$(generate_secret)}

set_secret WILDEDITOR_MCP_KEY "$mcp_key"
set_secret WILDEDITOR_BACKEND_SERVICE_KEY "$backend_service_key"
set_secret WILDEDITOR_REDIS_PASSWORD "$redis_password"

if [[ -n "${SELF_HOSTED_AUTH_PUBLISHABLE_KEY:-}" ]]; then
  set_secret SELF_HOSTED_AUTH_PUBLISHABLE_KEY "$SELF_HOSTED_AUTH_PUBLISHABLE_KEY"
fi

self_hosted_auth_url=${SELF_HOSTED_AUTH_URL:-https://auth.wildedit.luminarimud.com}
set_secret SELF_HOSTED_AUTH_URL "$self_hosted_auth_url"

echo "Installed separated MCP, backend-service, Redis, and Auth URL secrets."
if [[ -z "${SELF_HOSTED_AUTH_PUBLISHABLE_KEY:-}" ]]; then
  echo "SELF_HOSTED_AUTH_PUBLISHABLE_KEY was not changed; supply it after provisioning Auth."
fi
