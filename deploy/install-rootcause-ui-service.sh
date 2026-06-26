#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_SRC="$ROOT_DIR/deploy/rootcause-ui.service"
SERVICE_DST="/etc/systemd/system/rootcause-ui.service"

if [[ ! -f "$SERVICE_SRC" ]]; then
  echo "Missing $SERVICE_SRC"
  exit 1
fi

sudo install -m 0644 "$SERVICE_SRC" "$SERVICE_DST"
sudo systemctl daemon-reload
sudo systemctl enable rootcause-ui.service

cat <<'NOTE'
Service installed but not started automatically by this script.
Start it when DNS and certificate files are ready:
  sudo systemctl start rootcause-ui.service
  sudo systemctl status rootcause-ui.service
NOTE
