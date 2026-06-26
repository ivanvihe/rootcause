#!/usr/bin/env bash
set -euo pipefail

CERTBOT_BIN="/opt/rootcause/.venv-certbot/bin/certbot"

if [[ ! -x "$CERTBOT_BIN" ]]; then
  echo "certbot not found at $CERTBOT_BIN" >&2
  exit 1
fi

sudo "$CERTBOT_BIN" renew --quiet --deploy-hook "systemctl reload nginx"
