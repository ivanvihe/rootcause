#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NGINX_MAIN_SRC="$ROOT_DIR/deploy/nginx.conf"
CONF_SRC="$ROOT_DIR/deploy/nginx-rootcause.conf"
NGINX_MAIN_DST="/etc/nginx/nginx.conf"
CONF_DST="/etc/nginx/conf.d/rootcause.conf"

sudo install -d -m 0755 /var/lib/letsencrypt
sudo install -d -m 0755 /etc/nginx/certs
sudo install -d -m 0755 /etc/nginx/conf.d
sudo install -m 0644 "$NGINX_MAIN_SRC" "$NGINX_MAIN_DST"
sudo install -m 0644 "$CONF_SRC" "$CONF_DST"
CERT_PATH="/etc/letsencrypt/live/rootcause.example.com/fullchain.pem"
KEY_PATH="/etc/letsencrypt/live/rootcause.example.com/privkey.pem"

if ! sudo test -f "$CERT_PATH" || ! sudo test -f "$KEY_PATH"; then
  CERT_PATH="/etc/nginx/certs/rootcause-selfsigned.pem"
  KEY_PATH="/etc/nginx/certs/rootcause-selfsigned.key"
fi

if ! sudo test -f "$CERT_PATH" || ! sudo test -f "$KEY_PATH"; then
  tmpdir="$(mktemp -d)"
  trap 'rm -rf "$tmpdir"' EXIT
  cat >"$tmpdir/rootcause-selfsigned.cnf" <<'EOF'
[req]
default_bits = 2048
distinguished_name = dn
x509_extensions = v3_req
prompt = no

[dn]
CN = rootcause.example.com

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = rootcause.example.com
DNS.2 = rootcause.example.com
EOF
  openssl req -x509 -nodes -newkey rsa:2048 -days 7 \
    -keyout "$tmpdir/rootcause-selfsigned.key" \
    -out "$tmpdir/rootcause-selfsigned.pem" \
    -config "$tmpdir/rootcause-selfsigned.cnf" >/dev/null 2>&1
  sudo install -m 0600 "$tmpdir/rootcause-selfsigned.key" /etc/nginx/certs/rootcause-selfsigned.key
  sudo install -m 0644 "$tmpdir/rootcause-selfsigned.pem" /etc/nginx/certs/rootcause-selfsigned.pem
  CERT_PATH="/etc/nginx/certs/rootcause-selfsigned.pem"
  KEY_PATH="/etc/nginx/certs/rootcause-selfsigned.key"
fi
sudo sed -i \
  -e "s|^[[:space:]]*ssl_certificate .*;|    ssl_certificate $CERT_PATH;|" \
  -e "s|^[[:space:]]*ssl_certificate_key .*;|    ssl_certificate_key $KEY_PATH;|" \
  "$CONF_DST"
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx
