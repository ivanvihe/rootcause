# RootCause

**RootCause** is a self-healing monitoring layer. It unifies problems from your
existing observability stack (Prometheus, Alertmanager, Zabbix, …) into a single
problem store and, when a problem matches one of your rules, runs a remediation
action chain — including AI agents that diagnose and fix the root cause within
strict, configurable safety limits.

It is **not** a ticketing system: problems either auto-resolve or notify you.

> This repository ships **empty** on purpose. There are no hosts, datasources,
> rules or secrets baked in — clone it, point it at your own infrastructure and
> go. Contributions are welcome.

---

## Features

- **Unified problem store** fed by pluggable connectors (Prometheus polling,
  Alertmanager, Zabbix, and a generic webhook ingest endpoint).
- **Remediation rules**: match a firing problem and run an action chain
  (notify, run a command, or hand off to an AI agent).
- **AI agents** (`claude`, `codex`, …) with strict token budgets, blocked
  command patterns and a safe-cleanup policy so automated fixes stay bounded.
- **Web UI** (localhost by default) to manage hosts, datasources, rules,
  problems and an embedded Grafana metrics view.
- **Optional embedded observability stack** (`monitoring/`) via Docker Compose:
  Prometheus, Alertmanager, Blackbox exporter, Script exporter, Grafana with
  provisioned dashboards.
- **Android companion app** (`android/`) for push notifications and quick
  acknowledge / silence / rerun actions.

## Requirements

- Python 3.11+
- `pip install -r requirements.txt` (just `requests`)
- *Optional:* Docker + Docker Compose for the embedded monitoring stack
- *Optional:* a CLI AI agent on your `PATH` (e.g. `claude` or `codex`) for the
  self-healing actions

## Quick start

```bash
# 1. Create your local configuration from the template
cp checks.example.json checks.json

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the web UI (binds to 127.0.0.1:8787 by default)
python3 rootcause_checker.py --serve
```

Then open <http://127.0.0.1:8787> and add your hosts, datasources and rules from
the UI. `checks.json` is git-ignored — it holds your real config and secrets and
must never be committed.

Run a single check cycle (no UI) by invoking the checker without `--serve`.

## Configuration

All configuration lives in `checks.json` (created from `checks.example.json`).
Key sections:

| Section | What it holds |
| --- | --- |
| `hosts` | Hosts to monitor (address, connection, labels, Grafana panels) |
| `datasources` | Prometheus / Alertmanager / Zabbix endpoints to poll or ingest |
| `rules` | Problem-match → action-chain remediation rules |
| `agents` / `ai_routing` | AI agents and how requests are routed between them |
| `safety` | Blocked command patterns, prompt rules, safe-cleanup examples |
| `notifications` | SMTP email settings |
| `mobile` | Android app API keys, devices and push configuration |
| `integrations` | External integrations (e.g. Jira) |

The example ships with sensible `safety` defaults and reusable
`check_templates`, but no hosts, datasources or rules — add only what matches
your environment.

## Embedded monitoring stack (optional)

```bash
cd monitoring
docker compose up -d
```

This brings up Prometheus (`:9090`), Grafana (`:3000`) with provisioned
RootCause dashboards, Blackbox and Script exporters, and an optional
Alertmanager. Edit `monitoring/prometheus/prometheus.yml` to add your scrape
targets — it ships with localhost-only jobs plus commented examples.

To use the Alertmanager push path, generate an ingest token and wire it into
`monitoring/alertmanager/alertmanager.yml`:

```bash
python3 rootcause_checker.py --add-ingest-token alertmanager
```

## Deployment

`deploy/` contains example systemd units and helper scripts (UI service, nginx
reverse proxy with TLS, deSEC dynamic DNS, certbot renewal). They use generic
placeholder hostnames and paths (`rootcause.example.com`, `/opt/rootcause`) —
edit them for your host before installing.

## Android app

`android/` is a Gradle project for the companion app. Provide your own
`android/local.properties`, `android/keystore.properties` and Firebase
`google-services.json` (all git-ignored) — see `android/README.md` and the
`*.example` files.

## Contributing

Contributions are welcome — open an issue or a pull request. Please never commit
real configuration: keep hosts, datasources, tokens and rules in your local
`checks.json`, not in the repository.

## License

MIT — see [LICENSE](LICENSE).
