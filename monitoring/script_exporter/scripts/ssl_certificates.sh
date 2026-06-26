#!/bin/sh
# Migrated from the native `ssl_certificates` check (remote, on the mediaserver).
# Exits non-zero if any certbot-managed certificate expires within WARN_DAYS.
SSH_KEY="${SSH_KEY:-/scripts/keys/id_ed25519}"
HOST="${MEDIASERVER_SSH:-user@mediaserver.example.lan}"
WARN_DAYS="${WARN_DAYS:-7}"

out="$(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 "$HOST" -- \
  "docker exec certbot python3 -c \"
import subprocess, datetime, glob
warn = ${WARN_DAYS}
bad = []
for cert in glob.glob('/etc/letsencrypt/live/*/cert.pem'):
    name = cert.split('/')[-2]
    end = subprocess.run(['openssl','x509','-enddate','-noout','-in',cert],
                         capture_output=True, text=True).stdout.strip().split('=')[-1]
    days = (datetime.datetime.strptime(end, '%b %d %H:%M:%S %Y %Z') - datetime.datetime.utcnow()).days
    if days <= warn:
        bad.append(f'{name}: {days}d')
        print(f'{name}: {days}d')
import sys; sys.exit(1 if bad else 0)
\"" 2>&1)"
rc=$?
if [ "$rc" -ne 0 ]; then
  echo "certificates expiring within ${WARN_DAYS}d:"
  echo "$out"
  exit 1
fi
echo "all certificates valid for > ${WARN_DAYS}d"
exit 0
