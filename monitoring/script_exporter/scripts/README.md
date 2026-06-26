# script_exporter scripts

These replace the native `ssh`/`local`/`composite` command checks. Each script
exits `0` when OK and non-zero when there is a problem; script_exporter exposes
that as `script_success{script="<name>"}`, and the generated Prometheus rule
(`tools/migrate_checks_to_rules.py`) alerts on it. When the alert fires,
Alertmanager forwards it to RootCause's `/api/ingest/alertmanager`, which can run a
remediation action chain (via a rule `problem_match`).

## Local vs remote (SSH) checks

- **Local** checks (e.g. `containers_health` on the workstation) run directly in
  the exporter container — mount whatever the script needs (here the Docker
  socket via host networking).
- **Remote** checks (e.g. `jellyfin_transcode` on the mediaserver) must shell out
  over SSH. Mount an SSH key into the container and wrap the original command:

  ```sh
  #!/bin/sh
  ssh -i /scripts/keys/id_ed25519 -o StrictHostKeyChecking=accept-new \
      user@mediaserver.example.lan -- 'docker exec jellyfin /usr/lib/jellyfin-ffmpeg/ffmpeg -f lavfi -i testsrc=duration=1:size=32x32 -f null - >/dev/null 2>&1'
  ```

  Add the key mount to the `script-exporter` service in `docker-compose.yml`.

## Regenerating

After editing `checks.json`, regenerate the rules and re-read the report for any
new scripts/targets to add:

```sh
python tools/migrate_checks_to_rules.py
```
