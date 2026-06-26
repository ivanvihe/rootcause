#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

sudo install -m 0644 "$ROOT_DIR/deploy/rootcause-cert-renew.service" /etc/systemd/system/rootcause-cert-renew.service
sudo install -m 0644 "$ROOT_DIR/deploy/rootcause-cert-renew.timer" /etc/systemd/system/rootcause-cert-renew.timer
sudo install -m 0755 "$ROOT_DIR/deploy/rootcause-cert-renew.sh" /usr/local/bin/rootcause-cert-renew.sh

sudo systemctl daemon-reload
sudo systemctl enable --now rootcause-cert-renew.timer
