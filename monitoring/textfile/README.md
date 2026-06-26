# Textfile checks (shell/SSH → node-exporter)

The shell/SSH command checks that can't be expressed as a Prometheus metric —
`containers_health`, `jellyfin_transcode`, `wireguard_vpn`, `ssl_certificates` —
are run by [`collect.sh`](./collect.sh) and exposed through node-exporter's
**textfile collector** as `rootcause_check_success{check,host}` (1 = OK, 0 = problem).

A bespoke script exporter was avoided on purpose: these checks need the host's
Docker socket and SSH key, which a container would not have. Running them from a
host cron is simpler and more robust.

## How it works

1. `collect.sh` runs each check (local `docker`, or `ssh` to the mediaserver with
   `~/.ssh/id_ed25519`) and writes `/var/lib/node_exporter/textfile/rootcause_checks.prom`.
2. node-exporter is started with `--collector.textfile.directory=/textfile`
   (that host dir is bind-mounted read-only into the container).
3. Prometheus rules in `../prometheus/rules/rootcause.rules.yml` alert on `== 0`.
4. RootCause polls Prometheus, and the matching rule in `checks.json` remediates.

## Install (host cron, every minute)

```sh
sudo mkdir -p /var/lib/node_exporter/textfile && sudo chown "$USER" /var/lib/node_exporter/textfile
( crontab -l 2>/dev/null; echo "* * * * * /usr/bin/env HOME=$HOME /bin/bash $PWD/collect.sh >/dev/null 2>&1" ) | crontab -
```

Env overrides: `SSH_KEY` (default `$HOME/.ssh/id_ed25519`), `MEDIASERVER_SSH`
(default `user@mediaserver.example.lan`), and the output path as `$1`.
