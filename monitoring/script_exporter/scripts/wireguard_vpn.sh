#!/bin/sh
# Migrated from the native `wireguard_vpn` check (remote, on the mediaserver).
# Exits 0 when the wireguard container is running (Up), non-zero otherwise.
SSH_KEY="${SSH_KEY:-/scripts/keys/id_ed25519}"
HOST="${MEDIASERVER_SSH:-user@mediaserver.example.lan}"

status="$(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 "$HOST" -- \
  "docker ps --filter name=wireguard --format '{{.Status}}'" 2>/dev/null)"
case "$status" in
  Up*) echo "wireguard up: $status"; exit 0 ;;
  *)   echo "wireguard NOT running (status: ${status:-none})"; exit 1 ;;
esac
