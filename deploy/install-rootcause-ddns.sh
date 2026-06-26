#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <desec-token>"
  exit 1
fi

TOKEN="$1"

sudo install -m 0644 "$ROOT_DIR/deploy/rootcause-ddns.service" /etc/systemd/system/rootcause-ddns.service
sudo install -m 0644 "$ROOT_DIR/deploy/rootcause-ddns.timer" /etc/systemd/system/rootcause-ddns.timer
printf 'DESEC_TOKEN=%s\n' "$TOKEN" | sudo tee /etc/rootcause-ddns.env >/dev/null
sudo chmod 600 /etc/rootcause-ddns.env
sudo systemctl daemon-reload
sudo systemctl enable --now rootcause-ddns.timer
sudo systemctl start rootcause-ddns.service
