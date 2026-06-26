#!/bin/sh
# Migrated from the native `containers_health` check.
# Exit 0 when healthy, non-zero when any container is exited/dead.
# script_exporter turns the exit code into script_success{script="containers_health"},
# which the generated Prometheus rule (rootcause_check_up == 0) alerts on.
bad="$(docker ps -a --filter status=exited --filter status=dead --format '{{.Names}}: {{.Status}}')"
if [ -n "$bad" ]; then
  echo "unhealthy containers:"
  echo "$bad"
  exit 1
fi
echo "all containers healthy"
exit 0
