#!/usr/bin/env bash
set -euo pipefail

HOSTNAME_TO_UPDATE="${1:-rootcause.example.com}"
TOKEN="${DESEC_TOKEN:-${2:-}}"

if [[ -z "$TOKEN" ]]; then
  echo "Missing deSEC token. Pass it as DESEC_TOKEN or as the second argument."
  exit 1
fi

curl -fsS "https://update.dedyn.io/update?username=${HOSTNAME_TO_UPDATE}&password=${TOKEN}"
echo
