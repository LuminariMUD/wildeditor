#!/bin/sh
set -eu

base_url=${1:-http://127.0.0.1:8010}
base_url=${base_url%/}

curl --fail --silent --show-error "${base_url}/health" >/dev/null
curl --fail --silent --show-error \
  "${base_url}/auth/v1/.well-known/jwks.json" \
  | grep -q '"keys"'

status=$(curl --silent --output /dev/null --write-out '%{http_code}' \
  "${base_url}/rest/v1/")
if [ "$status" != "404" ]; then
  echo "Non-Auth API unexpectedly exposed (HTTP $status)" >&2
  exit 1
fi

echo "Auth health/JWKS passed and non-Auth APIs are not exposed."
