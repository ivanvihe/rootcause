#!/usr/bin/env bash
# RootCause check collector → node-exporter textfile.
#
# Runs the shell/SSH checks that can't be expressed as a Prometheus metric and
# writes rootcause_check_success{check,host} (1 = OK, 0 = problem) to node-exporter's
# textfile directory. A host cron runs this every minute (the host has docker and
# the SSH key, which a container would not). Prometheus rules in
# prometheus/rules/rootcause.rules.yml alert on `== 0`; RootCause rules remediate.
set -u

OUT="${1:-/var/lib/node_exporter/textfile/rootcause_checks.prom}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519}"
MS="${MEDIASERVER_SSH:-user@mediaserver.example.lan}"
SSH=(ssh -i "$SSH_KEY" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8)
TMP="$(mktemp)"

emit() { printf 'rootcause_check_success{check="%s",host="%s"} %s\n' "$1" "$2" "$3" >> "$TMP"; }
# Run a command, emit 1 on success (exit 0) / 0 on failure.
check() { if "${@:3}" >/dev/null 2>&1; then emit "$1" "$2" 1; else emit "$1" "$2" 0; fi; }

echo "# RootCause textfile checks — generated $(date -Is)" > "$TMP"

# containers_health — no exited/dead containers (local + mediaserver).
check containers_health localhost  bash -c '[ -z "$(docker ps -a --filter status=exited --filter status=dead --format "{{.Names}}")" ]'
check containers_health mediaserver "${SSH[@]}" "$MS" '[ -z "$(docker ps -a --filter status=exited --filter status=dead --format "{{.Names}}")" ]'

# jellyfin_transcode — NVENC/CUDA transcode test on the mediaserver.
check jellyfin_transcode mediaserver "${SSH[@]}" "$MS" \
  'docker exec jellyfin /usr/lib/jellyfin-ffmpeg/ffmpeg -f lavfi -i testsrc=duration=1:size=320x240:rate=25 -init_hw_device cuda=cu:0 -filter_hw_device cu -c:v h264_nvenc -f null - >/dev/null 2>&1'

# wireguard_vpn — container running.
check wireguard_vpn mediaserver "${SSH[@]}" "$MS" \
  'docker ps --filter name=wireguard --format "{{.Status}}" | grep -q "^Up"'

# ssl_certificates — no certbot cert expiring within 7 days (604800s).
# openssl -checkend exits non-zero if the cert expires within the window.
check ssl_certificates mediaserver "${SSH[@]}" "$MS" \
  'docker exec certbot sh -c "for c in /etc/letsencrypt/live/*/cert.pem; do openssl x509 -checkend 604800 -noout -in \"\$c\" || exit 1; done"'

mv "$TMP" "$OUT"
chmod 0644 "$OUT"   # node-exporter runs as a different uid and must read it
