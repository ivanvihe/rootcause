#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${1:-rootcause.example.com}"
EMAIL="${2:-}"

if [[ -z "$EMAIL" ]]; then
  echo "Usage: $0 <domain> <email>"
  echo "Example: $0 rootcause.example.com you@example.com"
  exit 1
fi

if ! command -v certbot >/dev/null 2>&1; then
  echo "certbot is not installed"
  exit 1
fi

cat <<'NOTE'
Let's Encrypt will not validate on port 8443.
Before running this script, make sure one of these is true:
1. Port 80 from the Internet reaches this machine for HTTP-01, or
2. Port 443 from the Internet reaches this machine for TLS-ALPN-01, or
3. You switch to a DNS-01 workflow instead of this script.
NOTE

sudo certbot certonly \
  --standalone \
  --preferred-challenges http \
  -d "$DOMAIN" \
  -m "$EMAIL" \
  --agree-tos \
  --non-interactive
