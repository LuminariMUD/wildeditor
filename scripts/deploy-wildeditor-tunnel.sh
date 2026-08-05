#!/usr/bin/env bash

set -euo pipefail

readonly container_name="wildeditor-cloudflared"
readonly cloudflared_image="${CLOUDFLARED_IMAGE:?CLOUDFLARED_IMAGE is required}"
readonly config_dir="${WILDEDITOR_CLOUDFLARED_CONFIG_DIR:-$HOME/.cloudflared}"
readonly credentials_file="$config_dir/wildeditor-api.json"
readonly config_file="$config_dir/wildeditor-api.yml"

for required_file in "$credentials_file" "$config_file"; do
  if [[ ! -s "$required_file" ]]; then
    echo "Required tunnel file is missing or empty: $required_file" >&2
    exit 1
  fi
done

chmod 600 "$credentials_file" "$config_file"

if groups | grep -qw docker && docker info >/dev/null 2>&1; then
  docker_cmd=(docker)
elif sudo -n docker info >/dev/null 2>&1; then
  docker_cmd=(sudo docker)
else
  echo "Docker is not available to the current user" >&2
  exit 1
fi

config_hash=$(
  sha256sum "$credentials_file" "$config_file" \
    | sha256sum \
    | awk '{print $1}'
)

"${docker_cmd[@]}" pull "$cloudflared_image" >/dev/null
desired_image_id=$("${docker_cmd[@]}" image inspect --format '{{.Id}}' "$cloudflared_image")

restart_required=true
if "${docker_cmd[@]}" container inspect "$container_name" >/dev/null 2>&1; then
  current_image_id=$("${docker_cmd[@]}" container inspect --format '{{.Image}}' "$container_name")
  current_config_hash=$(
    "${docker_cmd[@]}" container inspect \
      --format '{{index .Config.Labels "com.luminarimud.wildeditor.tunnel-config-sha256"}}' \
      "$container_name"
  )
  current_state=$("${docker_cmd[@]}" container inspect --format '{{.State.Status}}' "$container_name")

  if [[ "$current_state" == "running" \
    && "$current_image_id" == "$desired_image_id" \
    && "$current_config_hash" == "$config_hash" ]]; then
    restart_required=false
  fi
fi

if [[ "$restart_required" == "true" ]]; then
  "${docker_cmd[@]}" rm -f "$container_name" >/dev/null 2>&1 || true
  "${docker_cmd[@]}" run -d \
    --name "$container_name" \
    --restart unless-stopped \
    --network host \
    --user "$(id -u):$(id -g)" \
    --cap-drop ALL \
    --security-opt no-new-privileges:true \
    --label "com.luminarimud.wildeditor.tunnel-config-sha256=$config_hash" \
    --volume "$credentials_file:/etc/cloudflared/credentials.json:ro" \
    --volume "$config_file:/etc/cloudflared/config.yml:ro" \
    "$cloudflared_image" \
    tunnel --config /etc/cloudflared/config.yml run >/dev/null
  echo "Cloudflare tunnel container started"
else
  echo "Cloudflare tunnel container is already current"
fi

for _ in $(seq 1 30); do
  state=$("${docker_cmd[@]}" container inspect --format '{{.State.Status}}' "$container_name" 2>/dev/null || true)
  if [[ "$state" != "running" ]]; then
    echo "Cloudflare tunnel container is not running" >&2
    "${docker_cmd[@]}" logs --tail 30 "$container_name" >&2 || true
    exit 1
  fi

  registered_connections=$(
    "${docker_cmd[@]}" logs "$container_name" 2>&1 \
      | grep -c 'Registered tunnel connection' \
      || true
  )
  if (( registered_connections >= 4 )); then
    echo "Cloudflare tunnel is ready with $registered_connections registered connections"
    exit 0
  fi

  sleep 2
done

echo "Cloudflare tunnel did not establish all four edge connections" >&2
"${docker_cmd[@]}" logs --tail 50 "$container_name" >&2 || true
exit 1
