#!/usr/bin/env python3
"""RootCause - Automated Network Operations Center.

Monitors one or more hosts, evaluates reusable alert rules, attempts AI-guided
remediation with Claude or Codex, and falls back to emergency actions when the
agents or connectivity are unavailable.
"""

import argparse
import base64
import hashlib
import hmac
import ipaddress
import mimetypes
import json
import logging
import logging.handlers
import os
import re
import secrets
import shlex
import shutil
import smtplib
import ssl
import subprocess
import sys
import time
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

import requests
import urllib3

import rootcause_problems
from rootcause_problems import Problem, ProblemStore

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SCRIPT_DIR = Path(__file__).parent
CHECKS_FILE = SCRIPT_DIR / "checks.json"
LOG_FILE = SCRIPT_DIR / "rootcause.log"
STATE_FILE = SCRIPT_DIR / "rootcause_state.json"
STATUS_FILE = SCRIPT_DIR / "rootcause_status.json"
HISTORY_FILE = SCRIPT_DIR / "rootcause_history.json"
STATIC_DIR = SCRIPT_DIR / "static"
AGENT_CALLS_FILE = SCRIPT_DIR / "rootcause_agent_calls.json"
METRICS_COUNTERS_FILE = SCRIPT_DIR / "rootcause_metrics_counters.json"
# Unified problem store (Phase 0 of the frontend/orchestrator redesign). External
# problems from every source are normalized into rootcause_problems.Problem and
# persisted here with dedupe + history, independent of the native check state
# machine in STATE_FILE. See rootcause_problems.ProblemStore.
PROBLEMS_FILE = SCRIPT_DIR / "rootcause_problems.json"
# Latest network-stability probe results (loss/latency/hops per target) plus the
# rolling latency/hop baselines. Written by the `network_ping` check evaluation
# and served verbatim as rootcause_ping_* gauges by /metrics, so the SAME probe
# feeds both the alert and the embedded Grafana panels.
PING_STATS_FILE = SCRIPT_DIR / "rootcause_ping_stats.json"

# In-memory tally of SSH sessions opened during the current run, keyed by host
# address. Folded into METRICS_COUNTERS_FILE by update_metrics_counters() and
# served as rootcause_ssh_sessions_total by the /metrics endpoint.
_SSH_SESSION_COUNTS: dict[str, int] = {}
_CODEX_FALLBACK_MODELS: list[dict[str, str]] = [
    {"id": "gpt-5.5", "name": "GPT-5.5"},
    {"id": "gpt-5.4", "name": "GPT-5.4"},
    {"id": "gpt-5.4-mini", "name": "GPT-5.4-mini"},
    {"id": "gpt-5.3-codex", "name": "GPT-5.3-Codex"},
    {"id": "gpt-5.2", "name": "GPT-5.2"},
]
_CODEX_MODELS_CACHE: dict[str, Any] = {"models": None, "fetched_at": 0.0}
_CODEX_MODELS_TTL = 300.0  # 5 minutes
PROBE_CACHE_FILE = SCRIPT_DIR / "rootcause_probe_cache.json"
DEFAULT_PROBE_CACHE_TTL = 600.0  # seconds; override with ai_routing.probe_cache_ttl


def _probe_cache_key(agent: dict[str, Any]) -> str:
    return f"{agent.get('name', '')}:{agent.get('command', '')}:{agent.get('model') or ''}"


def _probe_cache_get(key: str, ttl: float) -> tuple[bool, str] | None:
    cache = load_json_file(PROBE_CACHE_FILE, default={})
    entry = cache.get(key)
    if isinstance(entry, dict) and time.time() - float(entry.get("ts", 0)) < ttl:
        return bool(entry.get("ok")), str(entry.get("output", ""))
    return None


def _probe_cache_put(key: str, ok: bool, output: str, ttl: float) -> None:
    cache = load_json_file(PROBE_CACHE_FILE, default={})
    now = time.time()
    cache = {k: v for k, v in cache.items() if isinstance(v, dict) and now - float(v.get("ts", 0)) < ttl * 4}
    cache[key] = {"ts": now, "ok": ok, "output": (output or "")[:200]}
    save_json_file(PROBE_CACHE_FILE, cache)


def _fetch_codex_models() -> list[dict[str, str]]:
    now = time.time()
    if _CODEX_MODELS_CACHE["models"] is not None and now - _CODEX_MODELS_CACHE["fetched_at"] < _CODEX_MODELS_TTL:
        return _CODEX_MODELS_CACHE["models"]  # type: ignore[return-value]
    try:
        result = subprocess.run(
            ["codex", "debug", "models"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            models = [
                {"id": m["slug"], "name": m.get("display_name") or m["slug"]}
                for m in data.get("models", [])
                if m.get("visibility") != "hide"
            ]
            if models:
                _CODEX_MODELS_CACHE["models"] = models
                _CODEX_MODELS_CACHE["fetched_at"] = now
                return models
    except Exception as exc:
        log.debug("codex model fetch failed, using fallback: %s", exc)
    return _CODEX_FALLBACK_MODELS


KNOWN_AGENT_MODELS: dict[str, list[dict[str, str]]] = {
    "claude": [
        {"id": "claude-opus-4-7", "name": "Claude Opus 4.7"},
        {"id": "claude-sonnet-4-6", "name": "Claude Sonnet 4.6"},
        {"id": "claude-haiku-4-5-20251001", "name": "Claude Haiku 4.5"},
        {"id": "claude-opus-4-5", "name": "Claude Opus 4.5"},
        {"id": "claude-sonnet-4-5", "name": "Claude Sonnet 4.5"},
        {"id": "claude-3-7-sonnet-20250219", "name": "Claude 3.7 Sonnet"},
        {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet"},
        {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku"},
    ],
}
ANDROID_RELEASE_APK = SCRIPT_DIR / "android" / "app" / "build" / "outputs" / "apk" / "release" / "app-release.apk"
ANDROID_BUILD_GRADLE = SCRIPT_DIR / "android" / "app" / "build.gradle.kts"
MOBILE_ACTION_SCOPES = {
    "read": "mobile:read",
    "device": "mobile:device",
    "ack": "mobile:ack",
    "silence": "mobile:silence",
    "rerun": "mobile:rerun",
}
DEFAULT_INTERNET_CHECKS = [
    "https://1.1.1.1",
    "https://8.8.8.8",
    "https://www.google.com/generate_204",
]
DEFAULT_RULE_SCHEDULE = "*/30 * * * *"
SCHEDULE_SHORTCUTS = {
    "every minute": "* * * * *",
    "every 5 minutes": "*/5 * * * *",
    "every 10 minutes": "*/10 * * * *",
    "every 15 minutes": "*/15 * * * *",
    "every 30 minutes": "*/30 * * * *",
    "every hour": "0 * * * *",
    "hourly": "0 * * * *",
    "daily": "0 0 * * *",
    "5min": "*/5 * * * *",
    "10min": "*/10 * * * *",
    "15min": "*/15 * * * *",
    "30min": "*/30 * * * *",
}
DEFAULT_BLOCKED_COMMAND_PATTERNS = [
    r"\brm\s+-rf\s+/",
    r"\bmkfs(\.| )",
    r"\bdd\s+if=",
    r"\b(shutdown|reboot|poweroff|halt)\b",
    r":\(\)\s*\{",
    r"\bcurl\b.*\|\s*(sh|bash)",
    r"\bwget\b.*\|\s*(sh|bash)",
    r"\bdocker\s+system\s+prune\b.*--volumes",
    r"\bdocker\s+volume\s+prune\b",
    r"\bdocker\s+volume\s+rm\b",
    r"\bdocker\s+compose\s+down\b.*-v",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.handlers.RotatingFileHandler(
            LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        ),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("rootcause")


@dataclass
class AgentStatus:
    name: str
    enabled: bool
    available: bool
    reason: str
    quota_score: float | None
    priority: int


def estimate_tokens(text: str) -> int:
    # Rough heuristic (~4 chars/token). Used for the token_protection budget and
    # the cost panel; it is approximate and can under/over-estimate. When a CLI
    # reports real usage, prefer parsing that over this estimate.
    return max(1, len(text or "") // 4)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def utc_iso() -> str:
    return now_utc().isoformat()


def load_json_file(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        # Recover from partial writes: extract the first valid JSON object
        try:
            with open(path, encoding="utf-8") as handle:
                content = handle.read()
            obj, _ = json.JSONDecoder().raw_decode(content.lstrip())
            return obj
        except Exception:
            return {} if default is None else default


def save_json_file(path: Path, data: Any) -> None:
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
    tmp.replace(path)  # atomic rename, prevents partial-write corruption


def pbkdf2_hex(secret: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), salt.encode("utf-8"), 200_000).hex()


def build_mobile_public_base_url(mobile: dict[str, Any]) -> str:
    explicit = str(mobile.get("public_base_url") or "").strip()
    if explicit:
        return explicit.rstrip("/")
    scheme = str(mobile.get("public_scheme") or "https").strip() or "https"
    hostname = str(mobile.get("public_hostname") or "").strip().strip("/")
    port = mobile.get("public_port")
    if not hostname:
        return ""
    try:
        port_value = int(port) if port not in (None, "") else None
    except (TypeError, ValueError):
        port_value = None
    if port_value and ((scheme == "https" and port_value != 443) or (scheme == "http" and port_value != 80)):
        return f"{scheme}://{hostname}:{port_value}"
    return f"{scheme}://{hostname}"


def get_mobile_config(config: dict[str, Any]) -> dict[str, Any]:
    mobile = config.setdefault("mobile", {})
    mobile.setdefault("enabled", True)
    mobile.setdefault("require_https", True)
    mobile.setdefault("public_base_url", "")
    mobile.setdefault("public_scheme", "https")
    mobile.setdefault("public_hostname", "")
    mobile.setdefault("public_port", 443)
    mobile.setdefault(
        "allowed_scopes",
        [
            "mobile:read",
            "mobile:device",
            "mobile:ack",
            "mobile:silence",
            "mobile:rerun",
        ],
    )
    mobile.setdefault("api_keys", [])
    mobile.setdefault("devices", [])
    mobile.setdefault("push", {"enabled": False, "provider": "fcm_v1", "service_account_path": ""})
    if mobile["push"].get("provider") == "fcm":
        mobile["push"]["provider"] = "fcm_v1"
    mobile["public_base_url"] = build_mobile_public_base_url(mobile)
    return mobile


def create_mobile_api_key_record(
    name: str,
    scopes: list[str],
    notes: str = "",
    device_limit: int = 5,
    allowed_targets: list[str] | None = None,
) -> tuple[str, dict[str, Any]]:
    key_id = secrets.token_hex(6)
    raw_secret = secrets.token_urlsafe(32)
    raw_key = f"ank_live_{key_id}_{raw_secret}"
    salt = secrets.token_hex(16)
    return raw_key, {
        "id": key_id,
        "name": name,
        "key_prefix": raw_key[:18],
        "salt": salt,
        "key_hash": pbkdf2_hex(raw_key, salt),
        "created_at": utc_iso(),
        "last_used_at": None,
        "revoked_at": None,
        "scopes": scopes,
        "notes": notes,
        "device_limit": int(device_limit or 5),
        "allowed_targets": [item for item in (allowed_targets or []) if item],
    }


def sanitize_mobile_api_key(record: dict[str, Any], device_count: int = 0) -> dict[str, Any]:
    return {
        "id": record.get("id"),
        "name": record.get("name"),
        "key_prefix": record.get("key_prefix"),
        "created_at": record.get("created_at"),
        "last_used_at": record.get("last_used_at"),
        "revoked_at": record.get("revoked_at"),
        "scopes": record.get("scopes", []),
        "notes": record.get("notes", ""),
        "device_limit": record.get("device_limit", 5),
        "device_count": device_count,
        "allowed_targets": record.get("allowed_targets", []),
    }


def sanitize_mobile_device(device: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": device.get("id"),
        "name": device.get("name"),
        "platform": device.get("platform"),
        "model": device.get("model"),
        "app_version": device.get("app_version"),
        "api_key_id": device.get("api_key_id"),
        "created_at": device.get("created_at"),
        "last_seen_at": device.get("last_seen_at"),
        "last_ip": device.get("last_ip"),
        "host": device.get("host"),
        "port": device.get("port"),
        "revoked_at": device.get("revoked_at"),
        "push_enabled": bool(device.get("push_token")),
    }


def list_mobile_api_keys(config: dict[str, Any]) -> list[dict[str, Any]]:
    mobile = get_mobile_config(config)
    devices = mobile.get("devices", [])
    counts: dict[str, int] = {}
    for device in devices:
        if device.get("revoked_at"):
            continue
        key_id = str(device.get("api_key_id") or "")
        if key_id:
            counts[key_id] = counts.get(key_id, 0) + 1
    return [sanitize_mobile_api_key(item, counts.get(str(item.get("id")), 0)) for item in mobile.get("api_keys", []) if not item.get("revoked_at")]


def list_mobile_devices(config: dict[str, Any]) -> list[dict[str, Any]]:
    return [sanitize_mobile_device(item) for item in get_mobile_config(config).get("devices", []) if not item.get("revoked_at")]


def verify_mobile_api_key(
    config: dict[str, Any],
    raw_key: str,
    required_scope: str | None = None,
) -> dict[str, Any] | None:
    mobile = get_mobile_config(config)
    for record in mobile.get("api_keys", []):
        if record.get("revoked_at"):
            continue
        salt = str(record.get("salt") or "")
        expected = str(record.get("key_hash") or "")
        if not salt or not expected:
            continue
        if not hmac.compare_digest(expected, pbkdf2_hex(raw_key, salt)):
            continue
        scopes = record.get("scopes", [])
        if required_scope and required_scope not in scopes:
            return None
        if "allowed_targets" not in record:
            record["allowed_targets"] = []
        record["last_used_at"] = utc_iso()
        return record
    return None


def get_ingest_config(config: dict[str, Any]) -> dict[str, Any]:
    """Config block for the webhook ingest endpoints (/api/ingest/*).

    Sources (Alertmanager, Grafana, Zabbix, scripts) authenticate with a bearer
    token whose pbkdf2 hash is stored here — never the raw token. Absent/empty
    => every ingest request is rejected, so enabling ingestion is opt-in.
    """
    ingest = config.setdefault("ingest", {})
    ingest.setdefault("enabled", True)
    ingest.setdefault("tokens", [])
    return ingest


def create_ingest_token_record(name: str) -> tuple[str, dict[str, Any]]:
    """Return (raw_token, stored_record). The raw token is shown once."""
    raw = secrets.token_urlsafe(32)
    salt = secrets.token_hex(16)
    record = {
        "id": secrets.token_hex(8),
        "name": name or "ingest",
        "salt": salt,
        "key_hash": pbkdf2_hex(raw, salt),
        "created_at": utc_iso(),
    }
    return raw, record


def verify_ingest_token(config: dict[str, Any], raw_key: str) -> dict[str, Any] | None:
    if not raw_key:
        return None
    ingest = get_ingest_config(config)
    if not ingest.get("enabled", True):
        return None
    for record in ingest.get("tokens", []):
        if record.get("revoked_at"):
            continue
        salt = str(record.get("salt") or "")
        expected = str(record.get("key_hash") or "")
        if not salt or not expected:
            continue
        if hmac.compare_digest(expected, pbkdf2_hex(raw_key, salt)):
            return record
    return None


# ── Datasources (Grafana-style integrations) ──────────────────────────────────
# A datasource is one configured monitoring integration (Prometheus, Alertmanager,
# Grafana, Zabbix, Elastic). Rules reference datasources to decide which problems
# they act on. Polling datasources are scraped each run; webhook datasources have
# their own ingest token and receive pushes. Datasources REPLACE the old per-host
# prometheus_url/alertmanager_url + connectors config.
DATASOURCE_TYPES = ("prometheus", "alertmanager", "grafana", "zabbix", "elastic")
DATASOURCE_DEFAULT_MODE = {
    "prometheus": "polling",
    "alertmanager": "webhook",
    "grafana": "polling",
    "zabbix": "polling",
    "elastic": "polling",
}


def get_datasources(config: dict[str, Any]) -> list[dict[str, Any]]:
    return config.setdefault("datasources", [])


def find_datasource(config: dict[str, Any], ds_id: str) -> dict[str, Any] | None:
    for ds in get_datasources(config):
        if str(ds.get("id")) == str(ds_id):
            return ds
    return None


def new_datasource_id() -> str:
    return "ds_" + secrets.token_hex(5)


def migrate_to_datasources(config: dict[str, Any]) -> bool:
    """Build config.datasources from legacy host/connector config (one-shot).

    Runs only when the key is absent, so it never clobbers a user-managed list.
    """
    if "datasources" in config:
        return False
    datasources: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    def add(name: str, dtype: str, url: str, **extra: Any) -> None:
        url = str(url or "").strip()
        if not url or (dtype, url) in seen:
            return
        seen.add((dtype, url))
        datasources.append({
            "id": new_datasource_id(),
            "name": name,
            "type": dtype,
            "url": url,
            # Migrated datasources were all pull-based, so keep them polling to
            # preserve current behaviour. New ones default per type via the UI.
            "mode": "polling",
            "enabled": True,
            **extra,
        })

    for hname, host in config.get("hosts", {}).items():
        add(f"Alertmanager · {hname}", "alertmanager", host.get("alertmanager_url"))
        add(f"Prometheus · {hname}", "prometheus", host.get("prometheus_url"))
    conn = config.get("connectors", {})
    pc = conn.get("prometheus", {})
    for url in pc.get("urls", []) if isinstance(pc, dict) else []:
        add(f"Prometheus · {url}", "prometheus", url)
    for dtype in ("zabbix", "grafana", "elastic"):
        c = conn.get(dtype, {})
        if isinstance(c, dict) and c.get("url"):
            extra = {k: c[k] for k in ("token", "user", "password", "index", "api_key", "field_map", "query") if k in c}
            add(f"{dtype.title()}", dtype, c.get("url"), **extra)

    config["datasources"] = datasources
    return True


def create_datasource_ingest_token(datasource: dict[str, Any]) -> str:
    """Mint a per-datasource ingest token (stores only its hash). Returns raw once."""
    raw = secrets.token_urlsafe(32)
    salt = secrets.token_hex(16)
    datasource["ingest"] = {"salt": salt, "key_hash": pbkdf2_hex(raw, salt), "created_at": utc_iso()}
    return raw


def resolve_ingest_token(config: dict[str, Any], raw_key: str) -> tuple[str, dict[str, Any]] | None:
    """Match a bearer token to a datasource (preferred) or a global ingest token.

    Returns ("datasource", ds) so the webhook can tag problems with the datasource
    id, or ("global", record) for a legacy shared token, or None.
    """
    if not raw_key:
        return None
    for ds in get_datasources(config):
        ing = ds.get("ingest") or {}
        salt, expected = str(ing.get("salt") or ""), str(ing.get("key_hash") or "")
        if salt and expected and hmac.compare_digest(expected, pbkdf2_hex(raw_key, salt)):
            return "datasource", ds
    record = verify_ingest_token(config, raw_key)
    if record is not None:
        return "global", record
    return None


DATASOURCE_SECRET_FIELDS = ("token", "password", "api_key")


def sanitize_datasource(ds: dict[str, Any]) -> dict[str, Any]:
    """Datasource view for the UI: drop secrets, expose only whether they are set."""
    clean = {k: v for k, v in ds.items() if k not in DATASOURCE_SECRET_FIELDS and k != "ingest"}
    for field in DATASOURCE_SECRET_FIELDS:
        if ds.get(field):
            clean[f"{field}_set"] = True
    clean["webhook_configured"] = bool((ds.get("ingest") or {}).get("key_hash"))
    return clean


def sanitize_rule(rule: dict[str, Any]) -> dict[str, Any]:
    """Rules carry no secrets; passed through verbatim for the UI."""
    return dict(rule)


# ── Jira integration (Settings ▸ Webhooks ▸ Jira) ─────────────────────────────
# Configured once in Settings, referenced by the "Send to Jira" rule action.
# Tickets are deduped per problem (a label rootcause-fp-<fingerprint> + the issue
# key cached on the problem), commented when the problem is commented, and closed
# when the problem resolves.
JIRA_SECRET_FIELDS = ("api_token",)
JIRA_FP_LABEL_PREFIX = "rootcause-fp-"


def get_jira_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.setdefault("integrations", {}).setdefault("jira", {})


def sanitize_jira(cfg: dict[str, Any]) -> dict[str, Any]:
    """UI view of the Jira config: drop the secret, expose only whether it's set."""
    clean = {k: v for k, v in cfg.items() if k not in JIRA_SECRET_FIELDS}
    clean["api_token_set"] = bool(cfg.get("api_token"))
    return clean


def jira_enabled(config: dict[str, Any]) -> bool:
    cfg = get_jira_config(config)
    return bool(cfg.get("enabled") and cfg.get("base_url") and cfg.get("email") and cfg.get("api_token") and cfg.get("project_key"))


def _jira_auth_header(cfg: dict[str, Any]) -> str:
    raw = f"{cfg.get('email', '').strip()}:{cfg.get('api_token', '')}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def jira_request(cfg: dict[str, Any], method: str, path: str, payload: Any = None, timeout: int = 15) -> requests.Response:
    base = str(cfg.get("base_url") or "").rstrip("/")
    url = f"{base}/rest/api/3{path}"
    headers = {
        "Authorization": _jira_auth_header(cfg),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    return requests.request(method, url, headers=headers, json=payload, timeout=timeout)


def _jira_adf(text: str) -> dict[str, Any]:
    """Wrap plain text in Atlassian Document Format (required by api/3 bodies)."""
    return {
        "type": "doc",
        "version": 1,
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": str(text or "")[:30000] or " "}]}],
    }


def jira_test_connection(cfg: dict[str, Any]) -> tuple[bool, str]:
    try:
        resp = jira_request(cfg, "GET", "/myself")
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
    if resp.status_code == 200:
        who = resp.json()
        return True, f"Connected as {who.get('displayName') or who.get('emailAddress') or 'user'}"
    if resp.status_code in (401, 403):
        return False, "Auth failed — check email + API token"
    return False, f"HTTP {resp.status_code}: {resp.text[:200]}"


def jira_find_issue_by_fingerprint(cfg: dict[str, Any], fingerprint: str) -> str | None:
    """Secondary dedupe: locate an existing open issue tagged with the fingerprint."""
    if not fingerprint:
        return None
    jql = f'project = "{cfg.get("project_key")}" AND labels = "{JIRA_FP_LABEL_PREFIX}{fingerprint}" ORDER BY created DESC'
    try:
        resp = jira_request(cfg, "POST", "/search", {"jql": jql, "maxResults": 1, "fields": ["key"]})
        if resp.status_code == 200:
            issues = resp.json().get("issues") or []
            if issues:
                return str(issues[0].get("key"))
    except Exception as exc:  # noqa: BLE001
        log.warning("  jira fingerprint search failed: %s", exc)
    return None


def _jira_severity_label(sev: str) -> str:
    return {"critical": "Highest", "high": "High", "warning": "Medium", "info": "Low"}.get(str(sev), "Medium")


def jira_create_issue_for_problem(cfg: dict[str, Any], problem: dict[str, Any]) -> tuple[str | None, str]:
    """Create a Jira issue for a problem and return (issue_key, message)."""
    fp = str(problem.get("fingerprint") or problem.get("key") or "")
    name = str(problem.get("name") or "Problem")
    host = str(problem.get("host") or "")
    sev = str(problem.get("severity") or "warning")
    summary = f"[RootCause] {name}" + (f" on {host}" if host else "")
    desc_lines = [
        f"Problem: {name}",
        f"Host: {host or '—'}",
        f"Severity: {sev}",
        f"Source: {problem.get('source') or '?'}",
        f"Summary: {problem.get('summary') or problem.get('description') or '—'}",
        f"Started: {problem.get('started_at') or problem.get('first_seen') or '—'}",
        f"RootCause key: {problem.get('key')}",
    ]
    labels = ["rootcause", f"{JIRA_FP_LABEL_PREFIX}{fp}", f"rootcause-sev-{sev}"]
    fields: dict[str, Any] = {
        "project": {"key": cfg.get("project_key")},
        "issuetype": {"name": cfg.get("issue_type") or "Task"},
        "summary": summary[:250],
        "description": _jira_adf("\n".join(desc_lines)),
        "labels": labels,
    }
    try:
        resp = jira_request(cfg, "POST", "/issue", {"fields": fields})
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)
    if resp.status_code in (200, 201):
        key = str(resp.json().get("key"))
        return key, f"created {key}"
    return None, f"HTTP {resp.status_code}: {resp.text[:300]}"


def jira_add_comment(cfg: dict[str, Any], issue_key: str, text: str, by: str = "") -> tuple[bool, str]:
    body = (f"*{by}*: " if by else "") + str(text or "")
    try:
        resp = jira_request(cfg, "POST", f"/issue/{issue_key}/comment", {"body": _jira_adf(body)})
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
    return (resp.status_code in (200, 201)), (f"HTTP {resp.status_code}" if resp.status_code not in (200, 201) else "ok")


def jira_close_issue(cfg: dict[str, Any], issue_key: str, comment: str = "") -> tuple[bool, str]:
    """Transition an issue to a done/closed status (best match among transitions)."""
    try:
        resp = jira_request(cfg, "GET", f"/issue/{issue_key}/transitions")
        if resp.status_code != 200:
            return False, f"transitions HTTP {resp.status_code}"
        transitions = resp.json().get("transitions") or []
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
    target = None
    prefer = [str(cfg.get("close_transition") or "").lower(), "done", "closed", "resolve", "resolved", "complete"]
    for want in prefer:
        if not want:
            continue
        for tr in transitions:
            tname = str(tr.get("name") or "").lower()
            tto = str((tr.get("to") or {}).get("name") or "").lower()
            if want in tname or want in tto:
                target = tr
                break
        if target:
            break
    if not target:
        return False, "no matching close transition"
    if comment:
        jira_add_comment(cfg, issue_key, comment)
    try:
        resp = jira_request(cfg, "POST", f"/issue/{issue_key}/transitions", {"transition": {"id": target.get("id")}})
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
    return (resp.status_code in (200, 204)), (target.get("name") or "closed")


def jira_ensure_issue_for_problem(config: dict[str, Any], problem: dict[str, Any]) -> tuple[str | None, str]:
    """Idempotently get-or-create the Jira issue for a problem (dedupe by stored
    key, then by fingerprint label). Persists the key onto the problem's store
    annotations so later comments/closes can find it."""
    cfg = get_jira_config(config)
    if not jira_enabled(config):
        return None, "jira not configured"
    existing = str((problem.get("annotations") or {}).get("jira_issue_key") or "")
    if not existing:
        existing = jira_find_issue_by_fingerprint(cfg, str(problem.get("fingerprint") or "")) or ""
    if existing:
        return existing, f"reusing {existing}"
    key, msg = jira_create_issue_for_problem(cfg, problem)
    if key:
        try:
            ProblemStore(PROBLEMS_FILE).annotate(str(problem.get("key")), {"jira_issue_key": key})
        except Exception as exc:  # noqa: BLE001
            log.warning("  could not cache jira key on problem: %s", exc)
    return key, msg


def jira_sync_resolutions(config: dict[str, Any], resolved: list["Problem"]) -> None:
    """Close Jira issues for problems that just resolved."""
    if not jira_enabled(config) or not resolved:
        return
    cfg = get_jira_config(config)
    for prob in resolved:
        key = str((prob.annotations or {}).get("jira_issue_key") or "")
        if not key:
            key = jira_find_issue_by_fingerprint(cfg, prob.fingerprint) or ""
        if not key:
            continue
        ok, info = jira_close_issue(cfg, key, comment="RootCause: problem resolved — auto-closing.")
        log.info("  JIRA: close %s -> %s (%s)", key, ok, info)


def jira_sync_updates(config: dict[str, Any], updates: list[dict[str, Any]]) -> None:
    """Post RootCause system-update comments (e.g. severity escalation) onto the
    problem's Jira ticket. The store already appended them to the problem."""
    if not jira_enabled(config) or not updates:
        return
    cfg = get_jira_config(config)
    for item in updates:
        prob = item.get("problem")
        text = str(item.get("text") or "")
        if prob is None or not text:
            continue
        key = str((getattr(prob, "annotations", None) or {}).get("jira_issue_key") or "")
        if not key:
            key = jira_find_issue_by_fingerprint(cfg, getattr(prob, "fingerprint", "")) or ""
        if key:
            jira_add_comment(cfg, key, text, by="RootCause")


# ── Rules (datasource-triggered action chains) ────────────────────────────────
# A rule binds one or more datasources to a matcher + the existing RootCause action
# chain. When a problem from a selected datasource matches, the rule's actions run.
def get_rules(config: dict[str, Any]) -> list[dict[str, Any]]:
    return config.setdefault("rules", [])


def find_rule(config: dict[str, Any], rule_id: str) -> dict[str, Any] | None:
    for rule in get_rules(config):
        if str(rule.get("id")) == str(rule_id):
            return rule
    return None


def new_rule_id() -> str:
    return "rule_" + secrets.token_hex(5)


def normalize_allowed_mobile_targets(value: Any) -> list[str]:
    if isinstance(value, str):
        raw_items = [part.strip() for part in value.split(",")]
    elif isinstance(value, list):
        raw_items = [str(part).strip() for part in value]
    else:
        raw_items = []
    seen: set[str] = set()
    normalized: list[str] = []
    for item in raw_items:
        if not item or item in seen:
            continue
        seen.add(item)
        normalized.append(item)
    return normalized


def api_key_allowed_targets(api_key: dict[str, Any]) -> set[str] | None:
    targets = normalize_allowed_mobile_targets(api_key.get("allowed_targets"))
    if not targets:
        return None
    return set(targets)


def find_registered_device(
    config: dict[str, Any],
    api_key_id: str,
    device_id: str | None,
) -> dict[str, Any] | None:
    mobile = get_mobile_config(config)
    if not device_id:
        return None
    for device in mobile.get("devices", []):
        if device.get("revoked_at"):
            continue
        if str(device.get("api_key_id") or "") != api_key_id:
            continue
        if str(device.get("id") or "") == device_id:
            return device
    return None


def register_mobile_device(
    config: dict[str, Any],
    payload: dict[str, Any],
    api_key: dict[str, Any],
    client_ip: str,
) -> dict[str, Any]:
    mobile = get_mobile_config(config)
    api_key_id = str(api_key.get("id") or "")
    device_id = str(payload.get("device_id") or "").strip()
    existing = find_registered_device(config, api_key_id, device_id)
    active_for_key = [
        item
        for item in mobile.get("devices", [])
        if not item.get("revoked_at") and str(item.get("api_key_id") or "") == api_key_id
    ]
    if existing is None and len(active_for_key) >= int(api_key.get("device_limit", 5)):
        raise ValueError("device limit reached for this API key")

    device = existing or {
        "id": device_id or secrets.token_hex(8),
        "created_at": utc_iso(),
        "api_key_id": api_key_id,
    }
    device["name"] = str(payload.get("name") or payload.get("device_name") or "Android device").strip()
    device["platform"] = str(payload.get("platform") or "android").strip()
    device["model"] = str(payload.get("model") or "").strip()
    device["app_version"] = str(payload.get("app_version") or "").strip()
    device["host"] = str(payload.get("host") or "").strip()
    device["port"] = int(payload.get("port") or 443)
    device["push_token"] = str(payload.get("push_token") or "").strip()
    device["last_seen_at"] = utc_iso()
    device["last_ip"] = client_ip
    device["revoked_at"] = None
    if existing is None:
        mobile.setdefault("devices", []).append(device)
    return sanitize_mobile_device(device)


def revoke_mobile_api_key(config: dict[str, Any], key_id: str) -> None:
    mobile = get_mobile_config(config)
    found = False
    for record in mobile.get("api_keys", []):
        if str(record.get("id")) == key_id and not record.get("revoked_at"):
            record["revoked_at"] = utc_iso()
            found = True
    for device in mobile.get("devices", []):
        if str(device.get("api_key_id")) == key_id and not device.get("revoked_at"):
            device["revoked_at"] = utc_iso()
    if not found:
        raise ValueError("api key not found or already revoked")


def revoke_mobile_device(config: dict[str, Any], device_id: str) -> None:
    mobile = get_mobile_config(config)
    for device in mobile.get("devices", []):
        if str(device.get("id")) == device_id and not device.get("revoked_at"):
            device["revoked_at"] = utc_iso()
            return
    raise ValueError("device not found")


def load_history() -> dict[str, Any]:
    return load_json_file(HISTORY_FILE, default={"runs": [], "checks": []})


def trim_history(entries: list[dict[str, Any]], limit: int = 250) -> list[dict[str, Any]]:
    if len(entries) <= limit:
        return entries
    return entries[-limit:]


def ensure_alert_ids(config: dict[str, Any]) -> bool:
    changed = False
    rules = config.setdefault("alert_rules", [])
    used_ids = {str(rule.get("id")) for rule in rules if rule.get("id")}
    next_number = 1

    for rule in rules:
        if rule.get("id"):
            continue
        while f"{next_number:04d}" in used_ids:
            next_number += 1
        alert_id = f"{next_number:04d}"
        rule["id"] = alert_id
        used_ids.add(alert_id)
        changed = True
        next_number += 1

    return changed


def normalize_config(raw: dict[str, Any]) -> dict[str, Any]:
    config = deepcopy(raw)
    ensure_alert_ids(config)

    if "hosts" not in config:
        server = config.get("server", "127.0.0.1")
        ssh_user = config.get("ssh_user", os.environ.get("USER", "root"))
        prometheus_url = config.get("prometheus_url")
        pushgateway_url = config.get("pushgateway_url")
        alertmanager_url = config.get("alertmanager_url")
        config["hosts"] = {
            "default": {
                "address": server,
                "ssh_user": ssh_user,
                "ssh_port": 22,
                "connection": "ssh",
                "prometheus_url": prometheus_url,
                "pushgateway_url": pushgateway_url,
                "alertmanager_url": alertmanager_url,
                "labels": {"role": "default"},
            }
        }

    default_agents = [
        {
            "name": "claude",
            "type": "claude",
            "command": config.get("claude_path", "claude"),
            "enabled": True,
            "priority": 20,
            "timeout": 300,
        },
        {
            "name": "codex",
            "type": "codex",
            "command": config.get("codex_path", "codex"),
            "enabled": True,
            "priority": 10,
            "timeout": 300,
        },
        {
            "name": "opencode",
            "type": "custom",
            "command_template": "opencode run {prompt}",
            "command": "opencode",
            "enabled": False,
            "priority": 15,
            "timeout": 300,
            "probe": False,
        },
    ]
    if "agents" not in config:
        config["agents"] = default_agents
    else:
        existing = {item.get("name"): item for item in config.get("agents", [])}
        for agent in default_agents:
            if agent["name"] not in existing:
                config["agents"].append(agent)

    config.setdefault(
        "ai_routing",
        {
            "prefer_highest_quota": True,
            "fallback_to_next_agent": True,
            "probe_prompt": "Return exactly OK",
        },
    )
    config.setdefault(
        "connectivity",
        {
            "internet_checks": DEFAULT_INTERNET_CHECKS,
            "timeout": 5,
        },
    )
    config.setdefault(
        "alerting",
        {
            "failure_threshold_runs": 1,
            "repeat_notification_minutes": 60,
            "notify_on_resolve": True,
            "pause_schedule_on_fix_failed": True,
        },
    )
    config.setdefault(
        "ui",
        {
            "status_file": str(STATUS_FILE),
            "serve_host": "127.0.0.1",
            "serve_port": 8787,
            "tls_enabled": False,
            "tls_certfile": "",
            "tls_keyfile": "",
        },
    )
    config["ui"].setdefault("trusted_proxies", ["127.0.0.1", "::1"])
    config["ui"].setdefault("allowed_hosts", [])
    get_mobile_config(config)
    config.setdefault("maintenance_windows", [])
    config.setdefault("alertmanager_sources", [])
    config.setdefault(
        "safety",
        {
            "enabled": True,
            "blocked_command_patterns": DEFAULT_BLOCKED_COMMAND_PATTERNS,
            "safe_cleanup_examples": [
                "journalctl --vacuum-time=3d",
                "docker image prune -f",
                "docker container prune -f",
                "docker builder prune -f",
            ],
            "prompt_rules": [
                "Nunca uses rm -rf fuera de rutas explícitamente aprobadas.",
                "Nunca borres volúmenes Docker ni datos de usuario.",
                "Nunca ejecutes mkfs, dd, reboot, shutdown o poweroff.",
                "Si limpias Docker, usa prune seguro sin --volumes.",
                "Prioriza vacuum de journal, rotación de logs y prune de imágenes/contenedores no usados.",
            ],
        },
    )
    config.setdefault(
        "token_protection",
        {
            "enabled": True,
            "max_prompt_tokens": 4000,
            "max_response_tokens": 4000,
            "max_total_tokens_per_run": 12000,
            "max_error_chars": DEFAULT_MAX_ERROR_CHARS,
            "notify_on_stop": True,
        },
    )
    config.setdefault("ai_routing", {}).setdefault("probe_cache_ttl", DEFAULT_PROBE_CACHE_TTL)
    config.setdefault("notifications", {"enabled": False})

    rules = config.get("alert_rules")
    if not rules:
        legacy_checks = config.get("checks", [])
        rules = []
        for check in legacy_checks:
            wrapped = deepcopy(check)
            wrapped.setdefault("targets", list(config["hosts"].keys()))
            rules.append(wrapped)
        config["alert_rules"] = rules

    config.setdefault("check_templates", {})
    for rule in config.get("alert_rules", []):
        rule.setdefault("pause_schedule_on_fix_failed", bool(config.get("alerting", {}).get("pause_schedule_on_fix_failed", True)))
    return config


def render_value(value: Any, context: dict[str, Any]) -> Any:
    if isinstance(value, str):
        protected = value.replace("{{", "__ROOTCAUSE_LDB__").replace("}}", "__ROOTCAUSE_RDB__")
        try:
            rendered = protected.format(**context)
        except Exception:
            rendered = protected
        return rendered.replace("__ROOTCAUSE_LDB__", "{{").replace("__ROOTCAUSE_RDB__", "}}")
    if isinstance(value, list):
        return [render_value(item, context) for item in value]
    if isinstance(value, dict):
        return {key: render_value(item, context) for key, item in value.items()}
    return value


def build_context(host_name: str, host: dict[str, Any], rule: dict[str, Any]) -> dict[str, Any]:
    return {
        "host_name": host_name,
        "host": {
            "name": host_name,
            "address": host.get("address", host_name),
            "ssh_user": host.get("ssh_user", ""),
            "ssh_port": host.get("ssh_port", 22),
            "ssh_key_path": host.get("ssh_key_path", ""),
            "prometheus_url": host.get("prometheus_url", ""),
            "pushgateway_url": host.get("pushgateway_url", ""),
            "alertmanager_url": host.get("alertmanager_url", ""),
            "workdir": host.get("workdir", ""),
        },
        "rule": rule,
    }


def compile_rules(config: dict[str, Any]) -> list[dict[str, Any]]:
    compiled: list[dict[str, Any]] = []
    templates = config.get("check_templates", {})

    for rule in config.get("alert_rules", []):
        rule_name = rule.get("name", "unnamed")
        base = deepcopy(templates.get(rule.get("template"), {}))
        base.update(deepcopy(rule))
        if not base.get("enabled", True):
            continue
        targets = base.get("targets") or list(config["hosts"].keys())

        for host_name in targets:
            host = config["hosts"].get(host_name)
            if not host or not host.get("enabled", True):
                continue

            merged = deepcopy(base)
            merged["target"] = host_name
            merged["host"] = host
            merged["instance_key"] = f"{host_name}:{merged['name']}"
            merged["description"] = merged.get("description", merged["name"])

            context = build_context(host_name, host, merged)
            merged = render_value(merged, context)

            # Host-specific param substitution: <<key>> in command/steps is replaced
            # with values from host_params[host_name]. Uses <<key>> to avoid conflicts
            # with shell braces (awk, bash) and Python format strings.
            host_params = {**merged.get("host_params", {}).get("*", {}),
                           **merged.get("host_params", {}).get(host_name, {})}
            if host_params:
                def _apply_params(val: Any) -> Any:
                    if isinstance(val, str):
                        for k, v in host_params.items():
                            val = val.replace(f"<<{k}>>", str(v))
                        return val
                    if isinstance(val, list):
                        return [_apply_params(i) for i in val]
                    if isinstance(val, dict):
                        return {dk: _apply_params(dv) for dk, dv in val.items()}
                    return val
                merged["command"] = _apply_params(merged.get("command", ""))
                if "steps" in merged:
                    merged["steps"] = _apply_params(merged["steps"])
                if "preview_command" in merged:
                    merged["preview_command"] = _apply_params(merged["preview_command"])

            compiled.append(merged)

    return compiled


def run_local(command: str, timeout: int = 30, cwd: str | None = None) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
        output = (result.stdout or "").strip()
        error = (result.stderr or "").strip()
        if result.returncode != 0:
            return False, error or output or f"Command exited with {result.returncode}"
        # Return the real (possibly empty) output. Do NOT substitute "OK" here:
        # that placeholder defeats expect_empty / expect_nonempty assertions,
        # which need to see true emptiness. The cosmetic "OK" is applied later,
        # only on the success path, by evaluate_check.
        return True, output or error
    except subprocess.TimeoutExpired:
        return False, "Local command timed out"
    except Exception as exc:
        return False, str(exc)


def run_ssh(
    server: str,
    user: str,
    command: str,
    timeout: int = 30,
    port: int = 22,
    identity_file: str | None = None,
) -> tuple[bool, str]:
    _SSH_SESSION_COUNTS[server] = _SSH_SESSION_COUNTS.get(server, 0) + 1
    try:
        ssh_command = [
            "ssh",
            "-F",
            "/dev/null",
            "-o",
            "ConnectTimeout=10",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "BatchMode=yes",
            "-p",
            str(port or 22),
        ]
        if identity_file:
            ssh_command.extend(["-i", identity_file])
        ssh_command.extend([f"{user}@{server}", command])
        result = subprocess.run(
            ssh_command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = (result.stdout or "").strip()
        error = (result.stderr or "").strip()
        if result.returncode != 0:
            return False, error or output or f"SSH exited with {result.returncode}"
        # Return the real (possibly empty) output — see run_local for why the
        # "OK" placeholder is intentionally not applied at the transport layer.
        return True, output or error
    except subprocess.TimeoutExpired:
        return False, "SSH command timed out"
    except Exception as exc:
        return False, str(exc)


def run_host_command(host: dict[str, Any], command: str, timeout: int = 30) -> tuple[bool, str]:
    if host.get("connection") == "local":
        return run_local(command, timeout=timeout, cwd=host.get("workdir") or None)
    return run_ssh(
        host["address"],
        host["ssh_user"],
        command,
        timeout=timeout,
        port=int(host.get("ssh_port", 22) or 22),
        identity_file=str(host.get("ssh_key_path") or "").strip() or None,
    )


def check_http(
    url: str,
    timeout: int = 10,
    accept_codes: list[int] | None = None,
    expect_contains: str | None = None,
    expect_not_contains: str | None = None,
) -> tuple[bool, str]:
    if accept_codes is None:
        accept_codes = [200]
    try:
        response = requests.get(url, timeout=timeout, verify=False)
    except requests.RequestException as exc:
        return False, str(exc)
    # When a body expectation is set it drives the verdict (any non-error status
    # is fine); otherwise fall back to the classic status-code check.
    if expect_contains or expect_not_contains:
        if response.status_code >= 400:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
        body = response.text or ""
        if expect_contains and expect_contains not in body:
            return False, f"respuesta no contiene «{expect_contains}» (HTTP {response.status_code})"
        if expect_not_contains and expect_not_contains in body:
            return False, f"respuesta contiene «{expect_not_contains}» (HTTP {response.status_code})"
        return True, f"HTTP {response.status_code} · expectativa cumplida"
    if response.status_code in accept_codes:
        return True, f"HTTP {response.status_code}"
    return False, f"HTTP {response.status_code}: {response.text[:200]}"


def query_prometheus(prom_url: str, query: str, timeout: int = 10) -> tuple[bool, float | str]:
    try:
        response = requests.get(f"{prom_url}/api/v1/query", params={"query": query}, timeout=timeout)
        data = response.json()
        if data["status"] != "success":
            return False, f"Prometheus error: {data.get('error', 'unknown')}"
        results = data["data"]["result"]
        if not results:
            return False, "No data returned"
        value = float(results[0]["value"][1])
        return True, value
    except Exception as exc:
        return False, str(exc)


def query_prometheus_firing(prom_url: str, expr: str, timeout: int = 10) -> tuple[bool, bool, str]:
    """Evaluate a PromQL expression as an alerting condition.

    Returns (query_ok, firing, detail). ``firing`` is True when the expression
    returns at least one series — i.e. write the *problem* condition directly,
    e.g. ``node_load5 > 10``. Mirrors Prometheus' own alerting model.
    """
    try:
        response = requests.get(f"{prom_url}/api/v1/query", params={"query": expr}, timeout=timeout)
        data = response.json()
        if data.get("status") != "success":
            return False, False, f"Prometheus error: {data.get('error', 'unknown')}"
        results = data["data"]["result"]
        if not results:
            return True, False, "sin coincidencias"
        parts = []
        for series in results[:5]:
            metric = series.get("metric", {})
            label = metric.get("instance") or metric.get("__name__") or ""
            val = series.get("value", ["", "?"])[1]
            parts.append(f"{label}={val}" if label else str(val))
        suffix = f" (+{len(results) - 5} más)" if len(results) > 5 else ""
        return True, True, "; ".join(parts) + suffix
    except Exception as exc:
        return False, False, str(exc)


def get_prometheus_targets(
    prom_url: str,
    ignore_targets: list[str] | None = None,
    timeout: int = 10,
) -> tuple[bool, str]:
    ignore_targets = ignore_targets or []
    try:
        response = requests.get(f"{prom_url}/api/v1/targets", timeout=timeout)
        data = response.json()
        if data["status"] != "success":
            return False, f"Prometheus error: {data.get('error', 'unknown')}"

        down = []
        for target in data["data"]["activeTargets"]:
            if target["health"] == "up":
                continue
            job = target.get("labels", {}).get("job", "unknown")
            instance = target.get("labels", {}).get("instance", "unknown")
            haystack = f"{job} {instance}".lower()
            if any(ignored.lower() in haystack for ignored in ignore_targets):
                continue
            down.append(f"{job} ({instance}): {target['health']}")

        if down:
            return False, "; ".join(down)
        return True, "All monitored targets UP"
    except Exception as exc:
        return False, str(exc)


def normalize_external_host_candidate(value: str) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    return text.split(":", 1)[0]


def infer_external_alert_host(
    labels: dict[str, Any],
    host_catalog: dict[str, Any],
    fallback_hosts: list[str] | None = None,
) -> str | None:
    candidates = [
        labels.get("host"),
        labels.get("hostname"),
        labels.get("instance"),
        labels.get("node"),
        labels.get("target"),
    ]
    normalized = {normalize_external_host_candidate(item) for item in candidates if item}
    for host_name, host in host_catalog.items():
        haystack = {
            str(host_name).strip().lower(),
            str(host.get("address") or "").strip().lower(),
            normalize_external_host_candidate(host.get("address") or ""),
        }
        if normalized & {item for item in haystack if item}:
            return str(host_name)
    if fallback_hosts and len(fallback_hosts) == 1:
        return fallback_hosts[0]
    return None


def fetch_alertmanager_alerts(
    alertmanager_url: str,
    host_catalog: dict[str, Any],
    fallback_hosts: list[str] | None = None,
    timeout: int = 10,
) -> tuple[bool, list[dict[str, Any]] | str]:
    try:
        response = requests.get(f"{alertmanager_url.rstrip('/')}/api/v2/alerts", timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            return False, "Alertmanager returned an unexpected payload"
        alerts: list[dict[str, Any]] = []
        for item in payload:
            labels = item.get("labels") or {}
            annotations = item.get("annotations") or {}
            status = item.get("status") or {}
            host_name = infer_external_alert_host(labels, host_catalog, fallback_hosts=fallback_hosts)
            state = str(status.get("state") or "unknown").strip().lower()
            silenced = bool(status.get("silencedBy"))
            alerts.append(
                {
                    "source": "alertmanager",
                    "alertmanager_url": alertmanager_url,
                    "name": str(labels.get("alertname") or "unnamed"),
                    "severity": str(labels.get("severity") or "warning"),
                    "state": state,
                    "status_text": "Silenced" if silenced else state.title(),
                    "host": host_name,
                    "summary": str(annotations.get("summary") or annotations.get("description") or ""),
                    "description": str(annotations.get("description") or annotations.get("summary") or ""),
                    "fingerprint": str(item.get("fingerprint") or ""),
                    "starts_at": item.get("startsAt"),
                    "ends_at": item.get("endsAt"),
                    "updated_at": item.get("updatedAt"),
                    "generator_url": str(item.get("generatorURL") or ""),
                    "silenced": silenced,
                    "inhibited": bool(status.get("inhibitedBy")),
                    "receivers": [receiver.get("name") for receiver in item.get("receivers", []) if receiver.get("name")],
                    "labels": labels,
                    "annotations": annotations,
                }
            )
        alerts.sort(key=lambda alert: (alert.get("host") or "zzzz", alert.get("name") or "", alert.get("starts_at") or ""), reverse=False)
        return True, alerts
    except Exception as exc:
        return False, str(exc)


def build_external_alert_snapshot(config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    host_catalog = config.get("hosts", {})
    grouped_hosts: dict[str, list[str]] = {}
    for host_name, host in host_catalog.items():
        url = str(host.get("alertmanager_url") or "").strip()
        if not url:
            continue
        grouped_hosts.setdefault(url, []).append(str(host_name))

    external_alerts: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    for url, hosts in grouped_hosts.items():
        ok, payload = fetch_alertmanager_alerts(url, host_catalog, fallback_hosts=hosts)
        if ok:
            alerts = payload if isinstance(payload, list) else []
            external_alerts.extend(alerts)
            sources.append(
                {
                    "type": "alertmanager",
                    "url": url,
                    "hosts": hosts,
                    "ok": True,
                    "alert_count": len(alerts),
                    "error": "",
                }
            )
        else:
            sources.append(
                {
                    "type": "alertmanager",
                    "url": url,
                    "hosts": hosts,
                    "ok": False,
                    "alert_count": 0,
                    "error": str(payload),
                }
            )
    return external_alerts, sources


ZABBIX_SEVERITY = {0: "info", 1: "info", 2: "warning", 3: "high", 4: "high", 5: "critical"}


class DatasourceConnector(rootcause_problems.Connector):
    """Base for polling connectors bound to a single configured datasource.

    ``scope`` is the datasource id so two datasources of the same type reconcile
    independently in the ProblemStore, and every problem is tagged with that id.
    """

    def __init__(self, datasource: dict[str, Any], catalog: dict[str, Any]) -> None:
        self.ds = datasource
        self.catalog = catalog
        self.scope = str(datasource.get("id") or self.source)
        self.url = str(datasource.get("url") or "").strip()


def fetch_prometheus_alerts(prom_url: str, timeout: int = 10) -> tuple[bool, list[dict[str, Any]] | str]:
    """Fetch active alerts from a Prometheus server's /api/v1/alerts."""
    try:
        response = requests.get(f"{prom_url.rstrip('/')}/api/v1/alerts", timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") != "success":
            return False, f"Prometheus returned {payload.get('status')}"
        return True, payload.get("data", {}).get("alerts", []) or []
    except Exception as exc:
        return False, str(exc)


class AlertmanagerConnector(DatasourceConnector):
    """Poll one Alertmanager datasource's /api/v2/alerts into Problems."""

    source = "alertmanager"

    def poll(self) -> list[Problem]:
        if not self.url:
            return []
        ok, payload = fetch_alertmanager_alerts(self.url, self.catalog)
        if not ok or not isinstance(payload, list):
            if not ok:
                log.warning("  alertmanager datasource %s failed: %s", self.url, payload)
            return []
        problems = []
        for alert in payload:
            prob = rootcause_problems.normalize_alertmanager_alert(alert)
            prob.datasource_id = self.scope
            problems.append(prob)
        return problems


class PrometheusConnector(DatasourceConnector):
    """Poll one Prometheus datasource's /api/v1/alerts into Problems."""

    source = "prometheus"

    def poll(self) -> list[Problem]:
        if not self.url:
            return []
        ok, payload = fetch_prometheus_alerts(self.url)
        if not ok or not isinstance(payload, list):
            if not ok:
                log.warning("  prometheus datasource %s failed: %s", self.url, payload)
            return []
        problems: list[Problem] = []
        for item in payload:
            if str(item.get("state") or "").lower() != "firing":
                continue  # skip pending/inactive; only fire on active alerts
            labels = dict(item.get("labels") or {})
            annotations = dict(item.get("annotations") or {})
            problems.append(
                Problem(
                    source="prometheus",
                    fingerprint="",  # Prometheus gives none here; derived from labels
                    datasource_id=self.scope,
                    name=str(labels.get("alertname") or "unnamed"),
                    severity=str(labels.get("severity") or "warning"),
                    host=infer_external_alert_host(labels, self.catalog),
                    summary=str(annotations.get("summary") or annotations.get("description") or ""),
                    description=str(annotations.get("description") or annotations.get("summary") or ""),
                    labels=labels,
                    annotations=annotations,
                    value=str(item.get("value") or ""),
                    source_url=f"{self.url.rstrip('/')}/alerts",
                    started_at=item.get("activeAt"),
                )
            )
        return problems


def _zabbix_rpc(url: str, method: str, params: Any, auth: str | None, timeout: int = 10) -> Any:
    body = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    headers = {"Content-Type": "application/json-rpc"}
    # Zabbix 6.4+ accepts the token as a Bearer header; older needs the "auth" field.
    if auth and method not in ("user.login", "apiinfo.version"):
        headers["Authorization"] = f"Bearer {auth}"
        body["auth"] = auth
    response = requests.post(f"{url.rstrip('/')}/api_jsonrpc.php", json=body, headers=headers, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        raise RuntimeError(data["error"].get("data") or data["error"].get("message") or "zabbix error")
    return data.get("result")


class ZabbixConnector(DatasourceConnector):
    """Pull active problems from a Zabbix datasource via JSON-RPC.

    Datasource fields: ``{url, token}`` for an API token, or ``{url, user, password}``.
    """

    source = "zabbix"

    def _auth(self, url: str) -> str | None:
        token = str(self.ds.get("token") or "").strip()
        if token:
            return token
        user = str(self.ds.get("user") or "").strip()
        password = str(self.ds.get("password") or "")
        if user:
            return _zabbix_rpc(url, "user.login", {"username": user, "password": password}, None)
        return None

    def poll(self) -> list[Problem]:
        url = self.url
        if not url:
            return []
        auth = self._auth(url)
        problems_raw = _zabbix_rpc(url, "problem.get", {"output": "extend", "recent": False, "sortfield": ["eventid"]}, auth)
        if not isinstance(problems_raw, list):
            return []
        # Enrich with host names via event.get(selectHosts).
        event_ids = [str(p.get("eventid")) for p in problems_raw if p.get("eventid")]
        host_by_event: dict[str, str] = {}
        if event_ids:
            events = _zabbix_rpc(url, "event.get", {"eventids": event_ids, "output": ["eventid"], "selectHosts": ["host", "name"]}, auth)
            for ev in events or []:
                hosts = ev.get("hosts") or []
                if hosts:
                    host_by_event[str(ev.get("eventid"))] = str(hosts[0].get("host") or hosts[0].get("name") or "")
        problems: list[Problem] = []
        for item in problems_raw:
            eventid = str(item.get("eventid") or "")
            sev = ZABBIX_SEVERITY.get(int(item.get("severity") or 0), "warning")
            zbx_host = host_by_event.get(eventid) or ""
            host = infer_external_alert_host({"host": zbx_host}, self.catalog) or (zbx_host or None)
            started = None
            if item.get("clock"):
                started = datetime.fromtimestamp(int(item["clock"]), tz=timezone.utc).isoformat()
            problems.append(
                Problem(
                    source="zabbix",
                    fingerprint=eventid or "",
                    datasource_id=self.scope,
                    name=str(item.get("name") or "unnamed"),
                    severity=sev,
                    host=host,
                    summary=str(item.get("name") or ""),
                    labels={"eventid": eventid, "zabbix_host": zbx_host},
                    value=str(item.get("severity") or ""),
                    source_url=f"{url.rstrip('/')}/tr_events.php?triggerid={item.get('objectid','')}&eventid={eventid}",
                    started_at=started,
                    acknowledged=str(item.get("acknowledged")) == "1",
                )
            )
        return problems


class GrafanaConnector(DatasourceConnector):
    """Pull Grafana-managed alerts via its embedded Alertmanager API.

    Grafana unified alerting exposes firing alerts at
    ``/api/alertmanager/grafana/api/v2/alerts`` in Alertmanager v2 format, so the
    same normalization applies — only the source label differs. Datasource fields:
    ``{url, token?}``.
    """

    source = "grafana"

    def poll(self) -> list[Problem]:
        url = self.url
        if not url:
            return []
        headers = {}
        token = str(self.ds.get("token") or "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        endpoint = f"{url.rstrip('/')}/api/alertmanager/grafana/api/v2/alerts"
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            return []
        problems: list[Problem] = []
        for item in payload:
            labels = dict(item.get("labels") or {})
            annotations = dict(item.get("annotations") or {})
            status = item.get("status") or {}
            if str(status.get("state") or "").lower() == "suppressed" and not labels:
                continue
            problems.append(
                Problem(
                    source="grafana",
                    fingerprint=str(item.get("fingerprint") or ""),
                    datasource_id=self.scope,
                    name=str(labels.get("alertname") or annotations.get("summary") or "unnamed"),
                    severity=str(labels.get("severity") or "warning"),
                    host=infer_external_alert_host(labels, self.catalog),
                    summary=str(annotations.get("summary") or annotations.get("description") or ""),
                    description=str(annotations.get("description") or annotations.get("summary") or ""),
                    labels=labels,
                    annotations=annotations,
                    source_url=str(item.get("generatorURL") or ""),
                    started_at=item.get("startsAt"),
                    silenced=bool(status.get("silencedBy")),
                )
            )
        return problems


class ElasticConnector(DatasourceConnector):
    """Pull problems from an Elasticsearch datasource via a configurable query.

    Elastic/Kibana alerting is deployment-specific, so this connector runs a
    user-supplied query against an index and maps each hit to a Problem through a
    field map. Datasource fields:
    ``{url, index, query?, field_map?, api_key?, user?, password?}``.
    ``field_map`` keys: ``name, severity, host, summary, id, value`` (dotted paths).
    """

    source = "elastic"
    DEFAULT_FIELD_MAP = {
        "name": "rule.name",
        "severity": "kibana.alert.severity",
        "host": "host.name",
        "summary": "message",
        "id": "_id",
        "value": "kibana.alert.evaluation.value",
    }

    @staticmethod
    def _dig(source: dict[str, Any], dotted: str, hit: dict[str, Any]) -> Any:
        if dotted == "_id":
            return hit.get("_id")
        cur: Any = source
        for part in dotted.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return None
        return cur

    def poll(self) -> list[Problem]:
        url = self.url
        index = str(self.ds.get("index") or "").strip()
        if not url or not index:
            return []
        headers = {"Content-Type": "application/json"}
        api_key = str(self.ds.get("api_key") or "").strip()
        auth = None
        if api_key:
            headers["Authorization"] = f"ApiKey {api_key}"
        elif self.ds.get("user"):
            auth = (str(self.ds.get("user")), str(self.ds.get("password") or ""))
        body = self.ds.get("query") or {"query": {"match_all": {}}, "size": 100}
        response = requests.post(f"{url.rstrip('/')}/{index}/_search", json=body, headers=headers, auth=auth, timeout=15, verify=False)
        response.raise_for_status()
        hits = response.json().get("hits", {}).get("hits", [])
        fmap = {**self.DEFAULT_FIELD_MAP, **(self.ds.get("field_map") or {})}
        problems: list[Problem] = []
        for hit in hits:
            src = hit.get("_source", {}) or {}
            host = self._dig(src, fmap["host"], hit)
            problems.append(
                Problem(
                    source="elastic",
                    fingerprint=str(self._dig(src, fmap["id"], hit) or hit.get("_id") or ""),
                    datasource_id=self.scope,
                    name=str(self._dig(src, fmap["name"], hit) or "unnamed"),
                    severity=str(self._dig(src, fmap["severity"], hit) or "warning"),
                    host=infer_external_alert_host({"host": host}, self.catalog) or (str(host) if host else None),
                    summary=str(self._dig(src, fmap["summary"], hit) or ""),
                    labels={"index": index},
                    value=str(self._dig(src, fmap["value"], hit) or ""),
                    source_url=f"{url.rstrip('/')}/{index}",
                )
            )
        return problems


DATASOURCE_CONNECTORS = {
    "alertmanager": AlertmanagerConnector,
    "prometheus": PrometheusConnector,
    "zabbix": ZabbixConnector,
    "grafana": GrafanaConnector,
    "elastic": ElasticConnector,
}


def build_pull_connectors(config: dict[str, Any]) -> list[rootcause_problems.Connector]:
    """One polling connector per enabled, polling-mode datasource."""
    catalog = config.get("hosts", {})
    connectors: list[rootcause_problems.Connector] = []
    for ds in get_datasources(config):
        if not ds.get("enabled", True) or str(ds.get("mode") or "polling") == "webhook":
            continue
        cls = DATASOURCE_CONNECTORS.get(str(ds.get("type")))
        if cls and str(ds.get("url") or "").strip():
            connectors.append(cls(ds, catalog))
    return connectors


def sync_datasource_problems(config: dict[str, Any]) -> dict[str, list[Problem]]:
    """Poll every polling-mode datasource and reconcile it into the ProblemStore.

    Each datasource reconciles independently (scope = datasource id), so two
    Prometheus servers don't resolve each other's problems, and a failed poll
    skips that datasource entirely rather than wrongly resolving its problems.
    Webhook-mode datasources are not polled here — they push via /api/ingest/*.
    """
    store = ProblemStore(PROBLEMS_FILE)
    transitions: dict[str, list[Any]] = {"new": [], "ongoing": [], "resolved": [], "updates": []}
    for connector in build_pull_connectors(config):
        try:
            polled = connector.poll()
        except Exception as exc:  # noqa: BLE001
            log.warning("  datasource %s poll failed: %s", connector.scope, exc)
            continue
        result = store.sync(connector.scope, polled)
        for bucket, items in result.items():
            transitions[bucket].extend(items)
    return transitions


def build_matchable_rules(config: dict[str, Any]) -> list[dict[str, Any]]:
    """All enabled rules that can act on problems, newest model first.

    New ``config.rules`` (datasource_ids + match + actions) plus legacy
    ``alert_rules`` carrying a ``problem_match`` block.
    """
    rules = [r for r in config.get("rules", []) if r.get("enabled", True)]
    rules += [r for r in config.get("alert_rules", []) if isinstance(r.get("problem_match"), dict)]
    return rules


def rule_matches_problem(rule: dict[str, Any], problem: Problem) -> bool:
    """Whether a rule applies to a problem (handles both rule shapes)."""
    # New model: filter by datasource then by the match facets.
    if "datasource_ids" in rule or "match" in rule:
        ds_ids = rule.get("datasource_ids") or []
        if ds_ids and problem.datasource_id not in ds_ids:
            return False
        matcher = rule.get("match")
        if isinstance(matcher, dict) and matcher:
            return rootcause_problems.problem_matches(matcher, problem)
        return True  # datasource-only rule: any problem from those datasources
    # Legacy model.
    if isinstance(rule.get("problem_match"), dict):
        return rootcause_problems.problem_matches(rule["problem_match"], problem)
    return False


def _synthetic_rule_for_problem(config: dict[str, Any], rule: dict[str, Any], problem: Problem) -> dict[str, Any]:
    """Build the rule dict the action engine expects from a matched rule+problem.

    The action engine (run_actions / attempt_agent_remediation) reads ``name``,
    ``target`` (host name), ``host`` (host dict), ``instance_key`` and the
    ``actions``/remediation fields off the rule. A problem-driven rule has no
    native check, so ``target``/``host`` come from the problem's host (falling
    back to localhost), and the problem detail is threaded through for prompts.
    """
    hosts = config.get("hosts", {})
    target = problem.host if problem.host in hosts else (problem.host or "localhost")
    host = hosts.get(target) or hosts.get("localhost") or {"name": target, "connection": "local", "address": "127.0.0.1"}
    syn = dict(rule)
    syn["name"] = rule.get("name") or f"problem:{problem.name}"
    syn["target"] = target
    syn["host"] = host
    syn["description"] = rule.get("description") or problem.summary or problem.name
    syn["instance_key"] = f"problem:{problem.key}"
    syn["_config"] = config
    syn["_problem"] = problem.to_dict()
    return syn


def remediate_matched_problems(
    config: dict[str, Any],
    new_problems: list[Problem],
    ctx: dict[str, Any],
) -> list[dict[str, Any]]:
    """Run action chains for newly-seen problems that match a rule.

    Two rule shapes participate: the new ``config.rules`` (datasource_ids + match
    + actions) and legacy ``alert_rules`` carrying a ``problem_match`` block. We
    act on first-seen problems only; an ongoing problem is not re-remediated on
    every poll, which prevents runaway loops. Returns per-problem outcome records.
    """
    matchable = build_matchable_rules(config)
    if not matchable or not new_problems:
        return []
    # Agents are only needed once we know there is matcher work to do, so resolve
    # them lazily here rather than on every (matcher-less) run.
    if not ctx.get("selected_agents"):
        ctx["selected_agents"] = select_agents(config, probe=False)
    outcomes: list[dict[str, Any]] = []
    store = ProblemStore(PROBLEMS_FILE)
    for problem in new_problems:
        for rule in matchable:
            if not rule_matches_problem(rule, problem):
                continue
            syn = _synthetic_rule_for_problem(config, rule, problem)
            result: dict[str, Any] = {
                "name": syn["name"],
                "target": syn["target"],
                "description": syn["description"],
                "detail": problem.summary or problem.description or problem.name,
                "result": "failed",
                "agent_used": None,
                "agent_attempts": [],
                "emergency_actions": [],
                "actions_log": [],
                "alert_state": {"key": syn["instance_key"], "consecutive_failures": 1, "status": "firing"},
            }
            log.warning("  PROBLEM-MATCH: rule '%s' matched %s (%s) — running actions", rule.get("name"), problem.key, problem.severity)
            try:
                if has_action_pipeline(syn):
                    run_actions(syn, result["detail"], result, ctx)
                else:
                    attempt_agent_remediation(syn, result["detail"], result, ctx)
            except Exception as exc:  # never let remediation break the run loop
                log.exception("  problem remediation failed for %s", problem.key)
                result["result"] = "fix_failed"
                result["detail"] = f"remediation error: {exc}"
            store.annotate(problem.key, {
                "rootcause_remediation": result.get("result"),
                "rootcause_remediation_rule": rule.get("name"),
                "rootcause_remediation_at": ctx["now"].isoformat(),
            })
            outcomes.append({
                "problem": problem.key,
                "rule": rule.get("name"),
                "result": result.get("result"),
                "actions_log": result.get("actions_log", []),
            })
            break  # first matching rule wins
    return outcomes


def find_external_alert(
    config: dict[str, Any],
    payload: dict[str, Any],
) -> dict[str, Any]:
    fingerprint = str(payload.get("fingerprint") or "").strip()
    alertmanager_url = str(payload.get("alertmanager_url") or "").strip()
    if not fingerprint:
        raise ValueError("external alert fingerprint is required")
    external_alerts, _ = build_external_alert_snapshot(config)
    for item in external_alerts:
        if str(item.get("fingerprint") or "").strip() != fingerprint:
            continue
        if alertmanager_url and str(item.get("alertmanager_url") or "").strip() != alertmanager_url:
            continue
        return item
    raise ValueError("external alert not found")


def build_alertmanager_silence_payload(alert: dict[str, Any], minutes: int, created_by: str, comment: str) -> dict[str, Any]:
    labels = alert.get("labels") or {}
    matchers = [
        {
            "name": "alertname",
            "value": str(labels.get("alertname") or alert.get("name") or ""),
            "isRegex": False,
            "isEqual": True,
        }
    ]
    for label_name in ("host", "hostname", "instance", "node", "target", "job", "service"):
        value = str(labels.get(label_name) or "").strip()
        if value:
            matchers.append(
                {
                    "name": label_name,
                    "value": value,
                    "isRegex": False,
                    "isEqual": True,
                }
            )
    now = now_utc()
    starts_at = now.isoformat()
    ends_at = (now + timedelta(minutes=max(1, minutes))).isoformat()
    return {
        "matchers": matchers,
        "startsAt": starts_at,
        "endsAt": ends_at,
        "createdBy": created_by,
        "comment": comment,
    }


def create_alertmanager_silence(
    alertmanager_url: str,
    alert: dict[str, Any],
    minutes: int = 60,
    created_by: str = "rootcause",
    comment: str = "",
    timeout: int = 10,
) -> tuple[bool, dict[str, Any] | str]:
    try:
        payload = build_alertmanager_silence_payload(alert, minutes, created_by, comment)
        response = requests.post(
            f"{alertmanager_url.rstrip('/')}/api/v2/silences",
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
        return True, {
            "silence_id": str(data.get("silenceID") or data.get("silenceId") or ""),
            "payload": payload,
        }
    except Exception as exc:
        return False, str(exc)


def normalize_schedule(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return DEFAULT_RULE_SCHEDULE
    if text in SCHEDULE_SHORTCUTS:
        return SCHEDULE_SHORTCUTS[text]
    parts = text.split()
    if len(parts) == 5:
        return text
    return DEFAULT_RULE_SCHEDULE


def _parse_cron_field(field: str, lo: int, hi: int) -> set[int]:
    out: set[int] = set()
    for part in field.split(","):
        step = 1
        token = part
        if "/" in token:
            base, step_str = token.split("/", 1)
            step = max(1, int(step_str))
            token = base
        if token == "*" or token == "":
            start, end = lo, hi
        elif "-" in token:
            start_str, end_str = token.split("-", 1)
            start, end = int(start_str), int(end_str)
        else:
            start = end = int(token)
        for value in range(start, end + 1, step):
            if lo <= value <= hi:
                out.add(value)
    return out


def cron_due(expr: str, dt: datetime) -> bool:
    fields = (expr or "").strip().split()
    if len(fields) != 5:
        return True
    try:
        minute = _parse_cron_field(fields[0], 0, 59)
        hour = _parse_cron_field(fields[1], 0, 23)
        dom = _parse_cron_field(fields[2], 1, 31)
        month = _parse_cron_field(fields[3], 1, 12)
        dow_field = _parse_cron_field(fields[4].replace("7", "0"), 0, 6)
    except (ValueError, IndexError):
        return True
    cron_dow = (dt.weekday() + 1) % 7
    return (
        dt.minute in minute
        and dt.hour in hour
        and dt.day in dom
        and dt.month in month
        and cron_dow in dow_field
    )


def parse_numeric(value: str) -> float | None:
    match = re.search(r"(-?\d+(?:\.\d+)?)", value or "")
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def run_self_diagnostic(config: dict[str, Any]) -> tuple[bool, str]:
    """Validate RootCause's own configuration and infrastructure."""
    issues: list[str] = []
    warnings: list[str] = []

    # ── 1. Config file readable ───────────────────────────────────────────
    if not config:
        issues.append("config is empty or unreadable")

    # ── 2. Alert rules validation (compiled, templates expanded) ──────────
    try:
        compiled = compile_rules(config)
    except Exception as exc:
        issues.append(f"compile_rules failed: {exc}")
        compiled = []
    raw_rules = config.get("alert_rules", [])
    if not raw_rules:
        warnings.append("no alert_rules defined")
    hosts_cfg = config.get("hosts", {})
    seen_names: dict[str, int] = {}
    for r in compiled:
        if r.get("type") == "rootcause_self":
            continue
        n = r.get("name", "<unnamed>")
        seen_names[n] = seen_names.get(n, 0) + 1
        rtype = r.get("type", "")
        if not rtype:
            issues.append(f"rule '{n}': missing type after template expansion")
        elif rtype in ("ssh", "local") and not r.get("command"):
            issues.append(f"rule '{n}': {rtype} check has no command")
        elif rtype == "http" and not r.get("url"):
            issues.append(f"rule '{n}': http check has no url")
        elif rtype == "composite" and not r.get("steps"):
            issues.append(f"rule '{n}': composite check has no steps")

        if r.get("comparator") and "threshold" not in r and not r.get("threshold_query"):
            issues.append(f"rule '{n}': has comparator '{r['comparator']}' but no threshold or threshold_query")

        # target host exists
        t = r.get("target")
        if t and t not in hosts_cfg:
            issues.append(f"rule '{n}': target '{t}' not in hosts")

    # ── 3. Host reachability ──────────────────────────────────────────────
    for hname, host in hosts_cfg.items():
        if host.get("connection") == "local":
            ok, out = run_local("echo ok", timeout=5, cwd=None)
            if not ok:
                issues.append(f"host '{hname}': local exec failed: {out[:80]}")
        else:
            addr = host.get("address", "")
            user = host.get("ssh_user", "")
            if not addr or not user:
                issues.append(f"host '{hname}': missing address or ssh_user")
            else:
                ok, out = run_ssh(
                    addr, user, "echo ok",
                    timeout=10,
                    port=int(host.get("ssh_port", 22) or 22),
                    identity_file=str(host.get("ssh_key_path") or "").strip() or None,
                )
                if not ok:
                    issues.append(f"host '{hname}': SSH unreachable — {out[:80]}")

    # ── 4. State / status files writable ──────────────────────────────────
    ui_cfg = config.get("ui", {})
    status_path = Path(ui_cfg.get("status_file", str(STATUS_FILE)))
    for fpath, label in [(STATE_FILE, "state"), (status_path, "status")]:
        try:
            fpath.touch(exist_ok=True)
            with open(fpath, "a"):
                pass
        except OSError as exc:
            issues.append(f"{label} file not writable: {exc}")

    # ── 5. Scheduled runner exists (crontab OR systemd timer) ──────────────
    _, cron_out = run_local("crontab -l 2>/dev/null | grep rootcause_checker", timeout=5)
    _, timer_out = run_local(
        "systemctl --user list-timers --all --no-legend 2>/dev/null | grep -i rootcause", timeout=5
    )
    if not cron_out.strip() and not timer_out.strip():
        warnings.append("no crontab entry or systemd timer found for rootcause_checker — scheduled runs may be missing")

    # ── 6. Agent commands reachable ───────────────────────────────────────
    for agent in config.get("agents", []):
        if not agent.get("enabled", True):
            continue
        cmd = str(agent.get("command") or "").strip()
        name = agent.get("name", "?")
        if cmd and not shutil.which(cmd) and not Path(cmd).exists():
            issues.append(f"agent '{name}': command not found: {cmd}")

    total = len(issues)
    if total:
        return False, f"{total} issue(s) found — " + " | ".join(issues[:5]) + (f" (+{total-5} more)" if total > 5 else "")
    if warnings:
        return True, f"OK (warnings: {'; '.join(warnings)})"
    n_rules = len(raw_rules)
    n_hosts = len(hosts_cfg)
    return True, f"OK — {n_rules} rule(s), {n_hosts} host(s), connectivity verified"


def run_ping_probe(address: str, count: int = 20, timeout: int = 45) -> dict[str, Any]:
    """Run ONE probe to ``address`` and return parsed end-to-end stats.

    Prefers ``mtr -j`` (one tool gives loss%, latency stats AND hop count from a
    single pass). Falls back to plain ``ping`` (loss + latency, no hop count)
    when mtr is unavailable. The returned dict is the single source consumed by
    both the alert evaluation and the rootcause_ping_* Prometheus gauges.
    """
    result: dict[str, Any] = {
        "up": 0, "loss_pct": 0.0, "avg_ms": 0.0, "best_ms": 0.0,
        "worst_ms": 0.0, "stdev_ms": 0.0, "hops": None, "sent": 0,
        "dst": address, "error": "",
    }
    if shutil.which("mtr"):
        ok, output = run_local(
            f"mtr -n -r -c {int(count)} -j {shlex.quote(address)}", timeout=timeout
        )
        if ok and output.strip():
            try:
                hubs = json.loads(output)["report"]["hubs"]
                if hubs:
                    last = hubs[-1]
                    result.update({
                        "up": 1,
                        "loss_pct": float(last.get("Loss%", 0.0)),
                        "avg_ms": float(last.get("Avg", 0.0)),
                        "best_ms": float(last.get("Best", 0.0)),
                        "worst_ms": float(last.get("Wrst", 0.0)),
                        "stdev_ms": float(last.get("StDev", 0.0)),
                        "hops": int(last.get("count", len(hubs))),
                        "sent": int(last.get("Snt", count)),
                        "dst": str(last.get("host", address)),
                    })
                    return result
                result["error"] = "mtr returned no hops"
            except (ValueError, KeyError, TypeError) as exc:
                result["error"] = f"mtr parse error: {exc}"
        else:
            result["error"] = (output or "mtr failed")[:200]

    # Fallback: plain ping (no hop count available).
    ok, output = run_local(
        f"ping -n -c {int(count)} -i 0.5 -w {int(timeout)} {shlex.quote(address)}",
        timeout=timeout + 5,
    )
    m_loss = re.search(r"(\d+(?:\.\d+)?)% packet loss", output or "")
    m_rtt = re.search(r"=\s*([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)\s*ms", output or "")
    if m_rtt:
        result.update({
            "up": 1,
            "loss_pct": float(m_loss.group(1)) if m_loss else 0.0,
            "best_ms": float(m_rtt.group(1)),
            "avg_ms": float(m_rtt.group(2)),
            "worst_ms": float(m_rtt.group(3)),
            "stdev_ms": float(m_rtt.group(4)),
            "sent": int(count),
        })
    elif m_loss:
        result["loss_pct"] = float(m_loss.group(1))
        result["error"] = f"{m_loss.group(1)}% packet loss"
    else:
        result["error"] = (output or "ping failed")[:200]
    return result


def evaluate_network_ping(rule: dict[str, Any]) -> tuple[bool, Any]:
    """Probe each configured target once, persist stats for /metrics, and trip
    the alert when packet loss, latency-vs-baseline, or hop count look unstable.

    The persisted PING_STATS_FILE is the same source served as rootcause_ping_*
    gauges, so the Grafana panels and this alert share one probe per run.
    """
    targets = rule.get("ping_targets") or [
        {"label": "internet", "address": "8.8.8.8"},
        {"label": "router", "address": "192.168.1.1"},
    ]
    count = int(rule.get("ping_count", 20))
    probe_timeout = int(rule.get("probe_timeout", max(count + 15, 35)))
    alpha = float(rule.get("baseline_alpha", 0.2))
    g_loss = float(rule.get("loss_threshold_pct", 5.0))
    g_factor = float(rule.get("latency_factor", 2.5))
    g_floor = float(rule.get("latency_floor_ms", 80.0))
    g_hop_delta = int(rule.get("hop_delta", 3))

    prev_targets = (load_json_file(PING_STATS_FILE, default={}) or {}).get("targets", {})
    new_targets: dict[str, Any] = {}
    triggers: list[str] = []
    summary_parts: list[str] = []

    for tgt in targets:
        addr = str(tgt.get("address") or "").strip()
        if not addr:
            continue
        label = str(tgt.get("label") or addr).strip()
        loss_thr = float(tgt.get("loss_threshold_pct", g_loss))
        factor = float(tgt.get("latency_factor", g_factor))
        floor = float(tgt.get("latency_floor_ms", g_floor))
        hop_delta = int(tgt.get("hop_delta", g_hop_delta))

        probe = run_ping_probe(addr, count, probe_timeout)
        prev = prev_targets.get(label, {})
        base_avg = prev.get("baseline_avg_ms")
        base_hops = prev.get("baseline_hops")

        entry: dict[str, Any] = {"label": label, "address": addr, "ts": time.time(), **probe}
        reasons: list[str] = []

        if not probe.get("up"):
            reasons.append(f"sin respuesta ({probe.get('error') or 'timeout'})")
        else:
            loss = float(probe["loss_pct"])
            avg = float(probe["avg_ms"])
            hops = probe.get("hops")
            if loss > loss_thr:
                reasons.append(f"packet loss {loss:.0f}% (>{loss_thr:.0f}%)")
            if base_avg and avg > max(base_avg * factor, floor):
                reasons.append(
                    f"latencia {avg:.1f}ms vs media {base_avg:.1f}ms (x{avg / base_avg:.1f})"
                )
            elif base_avg is None and avg > floor:
                reasons.append(f"latencia {avg:.1f}ms (>{floor:.0f}ms)")
            if hops is not None and base_hops is not None and abs(hops - base_hops) >= hop_delta:
                reasons.append(f"hops {hops} vs base {base_hops}")

            # Update rolling baselines only on a healthy probe so an outage does
            # not poison the "media" we compare future runs against.
            if loss <= loss_thr:
                entry["baseline_avg_ms"] = round(
                    avg if base_avg is None else alpha * avg + (1 - alpha) * base_avg, 3
                )
                if hops is not None:
                    if base_hops is None or abs(hops - base_hops) < hop_delta:
                        entry["baseline_hops"] = hops
                    else:
                        entry["baseline_hops"] = base_hops

        # Carry forward prior baselines whenever we did not refresh them above.
        if "baseline_avg_ms" not in entry and base_avg is not None:
            entry["baseline_avg_ms"] = base_avg
        if "baseline_hops" not in entry and base_hops is not None:
            entry["baseline_hops"] = base_hops

        entry["triggered"] = bool(reasons)
        entry["trigger_reasons"] = reasons
        new_targets[label] = entry

        if reasons:
            triggers.append(f"{label} ({addr}): " + ", ".join(reasons))
        if probe.get("up"):
            hops_str = probe["hops"] if probe.get("hops") is not None else "?"
            summary_parts.append(
                f"{label} avg {probe['avg_ms']:.1f}ms loss {probe['loss_pct']:.0f}% hops {hops_str}"
            )
        else:
            summary_parts.append(f"{label} DOWN")

    try:
        save_json_file(PING_STATS_FILE, {"updated": utc_iso(), "targets": new_targets})
    except Exception as exc:
        log.warning("Failed to persist ping stats: %s", exc)

    rule["_last_run_output"] = " | ".join(summary_parts)
    if triggers:
        return False, "Inestabilidad de red — " + "; ".join(triggers)
    return True, " | ".join(summary_parts) or "OK"


def check_output_assertions(rule: dict[str, Any], output: str) -> tuple[bool, str] | None:
    """String assertions on a command's output (shared by ssh and local).

    Covers empty / non-empty and contains / not-contains. Returns a
    ``(False, detail)`` failure tuple when an assertion is violated, or ``None``
    when the output passes all configured assertions.
    """
    if rule.get("expect_empty") and output:
        return False, output
    if rule.get("expect_nonempty") and not output:
        return False, "Expected output but got nothing"
    expect_contains = rule.get("expect_contains")
    if expect_contains and expect_contains not in output:
        return False, f"la salida no contiene «{expect_contains}»"
    expect_not_contains = rule.get("expect_not_contains")
    if expect_not_contains and expect_not_contains in output:
        return False, f"la salida contiene «{expect_not_contains}»"
    return None


def evaluate_check(rule: dict[str, Any]) -> tuple[bool, Any]:
    host = rule["host"]
    check_type = rule["type"]

    if check_type == "rootcause_self":
        config = rule.get("_config", {})
        return run_self_diagnostic(config)

    if check_type == "ssh":
        ok, output = run_host_command(host, rule["command"], timeout=rule.get("timeout", 30))
        rule["_last_run_output"] = output
        if not ok:
            return False, f"Command failed: {output}"

        assertion = check_output_assertions(rule, output)
        if assertion is not None:
            return assertion
        if "threshold" in rule and rule.get("comparator"):
            value = parse_numeric(output)
            if value is None:
                return False, f"Could not parse numeric value: {output}"
            threshold = rule["threshold"]
            if rule["comparator"] == "gt" and value > threshold:
                return False, value
            if rule["comparator"] == "lt" and value < threshold:
                return False, value
        if rule.get("parse_cert_days"):
            warn_days = rule.get("cert_warn_days", 7)
            expiring = []
            for line in output.splitlines():
                if ":" not in line:
                    continue
                domain, days_str = line.rsplit(":", 1)
                days = parse_numeric(days_str)
                if days is not None and days <= warn_days:
                    expiring.append(f"{domain.strip()}: {int(days)} days left")
            if expiring:
                return False, "; ".join(expiring)
        return True, output or "OK"

    if check_type == "local":
        ok, output = run_local(rule["command"], timeout=rule.get("timeout", 30), cwd=rule.get("cwd") or None)
        rule["_last_run_output"] = output
        if not ok:
            return False, f"Command failed: {output}"
        assertion = check_output_assertions(rule, output)
        if assertion is not None:
            return assertion
        return True, output or "OK"

    if check_type == "network_ping":
        return evaluate_network_ping(rule)

    if check_type == "http":
        return check_http(
            rule["url"],
            rule.get("timeout", 10),
            rule.get("accept_codes", [200]),
            expect_contains=(rule.get("expect_contains") or None),
            expect_not_contains=(rule.get("expect_not_contains") or None),
        )

    if check_type == "composite":
        errors = []
        for step in rule["steps"]:
            step_type = step["type"]
            if step_type == "ssh":
                ok, output = run_host_command(host, step["command"], timeout=step.get("timeout", 30))
            elif step_type == "local":
                ok, output = run_local(step["command"], timeout=step.get("timeout", 30), cwd=step.get("cwd") or None)
            elif step_type == "http":
                ok, output = check_http(step["url"], step.get("timeout", 10), step.get("accept_codes", [200]))
            else:
                ok, output = False, f"Unsupported composite step type: {step_type}"
            if not ok or not output:
                label = step.get("name") or step_type
                errors.append(f"{label}: {output or 'no output'}")
        if errors:
            return False, "; ".join(errors)
        return True, "All steps passed"

    if check_type == "prometheus_query":
        prom_url = host.get("prometheus_url")
        if not prom_url:
            return False, "Host has no prometheus_url configured"

        # Inline-expression mode: when no comparator/threshold is configured the
        # query IS the alert condition (e.g. "node_load5 > 10") — it fires when
        # Prometheus returns any series. This is the simple single-field path.
        if not rule.get("comparator") and rule.get("threshold") in (None, "") and not rule.get("threshold_query"):
            ok, firing, detail = query_prometheus_firing(prom_url, rule["query"], timeout=rule.get("timeout", 10))
            if not ok:
                return False, f"Query failed: {detail}"
            if firing:
                return False, detail
            return True, "OK (sin coincidencias)"

        ok, value = query_prometheus(prom_url, rule["query"], timeout=rule.get("timeout", 10))
        if not ok:
            return False, f"Query failed: {value}"

        threshold = rule.get("threshold")
        if rule.get("threshold_query"):
            threshold_ok, threshold_value = query_prometheus(
                prom_url,
                rule["threshold_query"],
                timeout=rule.get("timeout", 10),
            )
            if not threshold_ok:
                return False, f"Threshold query failed: {threshold_value}"
            threshold = threshold_value

        if threshold is not None and rule.get("comparator"):
            if rule["comparator"] == "gt" and value > threshold:
                return False, value
            if rule["comparator"] == "lt" and value < threshold:
                return False, value
        return True, value

    if check_type == "prometheus_targets":
        prom_url = host.get("prometheus_url")
        if not prom_url:
            return False, "Host has no prometheus_url configured"
        return get_prometheus_targets(
            prom_url,
            ignore_targets=rule.get("ignore_targets", []),
            timeout=rule.get("timeout", 10),
        )

    if check_type == "alertmanager":
        alertmanager_url = str(rule.get("alertmanager_url") or host.get("alertmanager_url") or "").strip()
        if not alertmanager_url:
            return False, "No alertmanager_url configured on check or host"
        filter_silenced = rule.get("filter_silenced", True)
        filter_inhibited = rule.get("filter_inhibited", True)
        alert_filter = {k: str(v) for k, v in (rule.get("alertmanager_filter") or {}).items() if v}
        ok, result = fetch_alertmanager_alerts(alertmanager_url, {})
        if not ok:
            return False, f"Alertmanager unreachable: {result}"
        all_alerts = result if isinstance(result, list) else []
        filtered = all_alerts
        for label_key, label_value in alert_filter.items():
            filtered = [
                a for a in filtered
                if str((a.get("labels") or {}).get(label_key) or a.get(label_key) or "") == label_value
            ]
        active = [
            a for a in filtered
            if not (filter_silenced and a.get("silenced"))
            and not (filter_inhibited and a.get("inhibited"))
            and a.get("state") not in ("resolved",)
        ]
        if not active:
            checked = (
                f"{len(filtered)} matching, {len(all_alerts)} total"
                if alert_filter and len(filtered) != len(all_alerts)
                else f"{len(all_alerts)} total"
            )
            return True, f"No active alerts ({checked} checked)"
        lines = []
        for a in active[:10]:
            sev = a.get("severity") or "?"
            name = a.get("name") or "?"
            summary = (a.get("summary") or a.get("description") or "")[:100]
            lines.append(f"[{sev}] {name}{f': {summary}' if summary else ''}")
        suffix = f" (showing 10 of {len(active)})" if len(active) > 10 else ""
        return False, f"{len(active)} active alert(s){suffix}:\n" + "\n".join(lines)

    return False, f"Unknown check type: {check_type}"


def evaluate_triggers(rule: dict[str, Any]) -> tuple[bool, Any]:
    """Evaluate a check's trigger(s) and combine them.

    Backwards compatible: a rule without a ``triggers`` block is evaluated by the
    classic single-trigger ``evaluate_check``. With ``triggers`` present it is
    ``{"match": "any"|"all", "list": [ <trigger>, ... ]}`` where each trigger is a
    normal detection spec (type + command/query/threshold/...). ``any`` fires the
    alert when ANY trigger reports a problem; ``all`` only when every trigger does.
    """
    triggers = rule.get("triggers")
    tlist = triggers.get("list") if isinstance(triggers, dict) else triggers
    if not tlist:
        return evaluate_check(rule)

    match = (triggers.get("match") if isinstance(triggers, dict) else "any") or "any"
    match = str(match).lower()
    inherited = {k: v for k, v in rule.items() if k not in ("triggers", "actions")}
    evaluated: list[tuple[str, bool, Any]] = []
    for idx, trig in enumerate(tlist):
        sub = {**inherited, **(trig if isinstance(trig, dict) else {})}
        label = (trig.get("label") if isinstance(trig, dict) else None) or sub.get("type") or f"trigger{idx + 1}"
        ok, detail = evaluate_check(sub)
        if sub.get("_last_run_output"):
            rule["_last_run_output"] = sub["_last_run_output"]
        evaluated.append((label, ok, detail))

    healthy = [ok for _, ok, _ in evaluated]
    passed = any(healthy) if match == "all" else all(healthy)
    if passed:
        return True, "; ".join(f"{lbl}: {det}" for lbl, ok, det in evaluated if ok) or "OK"
    failing = [f"{lbl}: {det}" for lbl, ok, det in evaluated if not ok]
    return False, "; ".join(failing) or "Trigger condition met"


def run_json_command(command: str) -> tuple[bool, Any]:
    ok, output = run_local(command, timeout=20)
    if not ok:
        return False, output
    try:
        return True, json.loads(output)
    except json.JSONDecodeError:
        return False, output


def get_agent_executable(agent: dict[str, Any]) -> str | None:
    command = agent.get("command")
    if command:
        return str(command)
    template = str(agent.get("command_template") or "").strip()
    if not template:
        return None
    return shlex.split(template)[0] if shlex.split(template) else None


def get_agent_status(
    agent: dict[str, Any],
    probe_prompt: str,
    probe: bool | None = None,
    probe_cache_ttl: float = DEFAULT_PROBE_CACHE_TTL,
) -> AgentStatus:
    name = agent["name"]
    command = get_agent_executable(agent) or name
    enabled = agent.get("enabled", True)
    priority = agent.get("priority", 100)

    if not enabled:
        return AgentStatus(name, False, False, "disabled", None, priority)
    if not shutil.which(command):
        return AgentStatus(name, True, False, "command not found", None, priority)

    quota_score = None
    reason = "available"

    quota_command = agent.get("quota_command")
    if quota_command:
        ok, payload = run_json_command(quota_command)
        if ok and isinstance(payload, dict):
            quota_score = payload.get("quota_score")
        elif ok:
            quota_score = parse_numeric(str(payload))

    agent_type = agent.get("type", name)
    if agent_type == "claude":
        ok, status = run_json_command(f"{shlex.quote(command)} auth status")
        if not ok:
            return AgentStatus(name, True, False, f"auth status failed: {status}", quota_score, priority)
        if not status.get("loggedIn"):
            return AgentStatus(name, True, False, "not logged in", quota_score, priority)
        if quota_score is None:
            quota_score = 100 if status.get("subscriptionType") else None
        reason = status.get("subscriptionType") or "logged in"
    elif agent_type == "codex":
        ok, output = run_local(f"{shlex.quote(command)} login status", timeout=20)
        if not ok:
            return AgentStatus(name, True, False, f"login status failed: {output}", quota_score, priority)
        if "Logged in" not in output:
            return AgentStatus(name, True, False, "not logged in", quota_score, priority)
        reason = output.strip()
    elif agent_type == "custom":
        reason = "configured"

    probe_allowed = agent.get("probe", agent.get("probe_enabled", True))
    if probe is not None:
        probe_allowed = probe_allowed and probe
    if probe_allowed:
        cache_key = _probe_cache_key(agent)
        cached = _probe_cache_get(cache_key, probe_cache_ttl)
        if cached is None:
            probe_ok, probe_output = invoke_agent(
                agent, probe_prompt, timeout=min(agent.get("timeout", 300), 45), read_only=True
            )
            _probe_cache_put(cache_key, probe_ok, probe_output, probe_cache_ttl)
        else:
            probe_ok, probe_output = cached
        if not probe_ok:
            return AgentStatus(name, True, False, f"probe failed: {probe_output[:120]}", quota_score, priority)
        reason = "healthy"

    return AgentStatus(name, True, True, reason, quota_score, priority)


def probe_agent_status(
    agent: dict[str, Any],
    status: AgentStatus,
    probe_prompt: str,
    probe_cache_ttl: float = DEFAULT_PROBE_CACHE_TTL,
) -> AgentStatus:
    """Lazy probe: run the (cached) live invocation probe only when an agent is
    actually about to be used, so healthy runs spend zero AI tokens on probes."""
    if not status.available:
        return status
    if not agent.get("probe", agent.get("probe_enabled", True)):
        return status
    cache_key = _probe_cache_key(agent)
    cached = _probe_cache_get(cache_key, probe_cache_ttl)
    if cached is None:
        ok, output = invoke_agent(agent, probe_prompt, timeout=min(agent.get("timeout", 300), 45), read_only=True)
        _probe_cache_put(cache_key, ok, output, probe_cache_ttl)
    else:
        ok, output = cached
    if not ok:
        return AgentStatus(status.name, True, False, f"probe failed: {output[:120]}", status.quota_score, status.priority)
    return AgentStatus(status.name, True, True, "healthy", status.quota_score, status.priority)


def get_probe_cache_ttl(config: dict[str, Any]) -> float:
    try:
        return float(config.get("ai_routing", {}).get("probe_cache_ttl", DEFAULT_PROBE_CACHE_TTL))
    except (TypeError, ValueError):
        return DEFAULT_PROBE_CACHE_TTL


def select_agents(config: dict[str, Any], probe: bool | None = None) -> list[tuple[dict[str, Any], AgentStatus]]:
    probe_prompt = config.get("ai_routing", {}).get("probe_prompt", "Return exactly OK")
    probe_cache_ttl = get_probe_cache_ttl(config)
    agent_statuses: list[tuple[dict[str, Any], AgentStatus]] = []
    for agent in config.get("agents", []):
        status = get_agent_status(agent, probe_prompt, probe=probe, probe_cache_ttl=probe_cache_ttl)
        agent_statuses.append((agent, status))

    prefer_quota = config.get("ai_routing", {}).get("prefer_highest_quota", True)

    def sort_key(item: tuple[dict[str, Any], AgentStatus]) -> tuple[int, float, int]:
        _, status = item
        quota = status.quota_score if status.quota_score is not None else -1.0
        quota_rank = -quota if prefer_quota else 0
        return (0 if status.available else 1, quota_rank, status.priority)

    return sorted(agent_statuses, key=sort_key)


# Read-only tool profile for the analysis stage: diagnosis commands only, no
# write/file-edit tools. ssh stays in because RootCause hosts are reached over it.
CLAUDE_READ_ONLY_TOOLS = ",".join([
    "Read", "Glob", "Grep",
    "Bash(cat:*)", "Bash(ls:*)", "Bash(head:*)", "Bash(tail:*)", "Bash(grep:*)", "Bash(rg:*)",
    "Bash(df:*)", "Bash(du:*)", "Bash(free:*)", "Bash(ps:*)", "Bash(uptime:*)", "Bash(date:*)",
    "Bash(journalctl:*)", "Bash(systemctl status:*)", "Bash(systemctl list-units:*)", "Bash(systemctl is-active:*)",
    "Bash(docker ps:*)", "Bash(docker logs:*)", "Bash(docker inspect:*)", "Bash(docker stats:*)",
    "Bash(ss:*)", "Bash(ip:*)", "Bash(ping:*)", "Bash(curl:*)", "Bash(dig:*)", "Bash(nslookup:*)",
    "Bash(uname:*)", "Bash(lsblk:*)", "Bash(top:*)", "Bash(sensors:*)", "Bash(nvidia-smi:*)",
    "Bash(ssh:*)",
])


def _claude_safety_settings(config: dict[str, Any] | None) -> str | None:
    """Inline Claude settings with a PreToolUse hook that enforces
    safety.blocked_command_patterns as a technical barrier (not just prompt text)."""
    if not config or not config.get("safety", {}).get("enabled", True):
        return None
    hook_command = (
        f"{shlex.quote(sys.executable)} {shlex.quote(str(Path(__file__).resolve()))} --safety-hook"
    )
    return json.dumps({
        "hooks": {
            "PreToolUse": [
                {"matcher": "Bash", "hooks": [{"type": "command", "command": hook_command}]}
            ]
        }
    })


def run_safety_hook() -> int:
    """Entry point for the Claude PreToolUse hook: read the tool call from
    stdin, block it (exit 2) if it matches a blocked command pattern."""
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0
    command = str((payload.get("tool_input") or {}).get("command") or "")
    if not command:
        return 0
    config = load_json_file(CHECKS_FILE, default={})
    allowed, reason = validate_command_safety(command, config)
    if not allowed:
        print(f"RootCause safety layer: {reason}", file=sys.stderr)
        return 2
    return 0


def invoke_claude(
    agent: dict[str, Any],
    prompt: str,
    timeout: int,
    read_only: bool = False,
    config: dict[str, Any] | None = None,
) -> tuple[bool, str]:
    command = agent.get("command", "claude")
    model = agent.get("model")
    cmd = [command]
    if model:
        cmd.extend(["--model", model])
    if read_only:
        cmd.extend(["-p", prompt, "--allowedTools", CLAUDE_READ_ONLY_TOOLS])
    else:
        cmd.extend(["-p", prompt, "--allowedTools", "Bash"])
        settings = _claude_safety_settings(config)
        if settings:
            cmd.extend(["--settings", settings])
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = (result.stdout or "").strip()
        error = (result.stderr or "").strip()
        if result.returncode != 0:
            return False, f"Claude exit code {result.returncode}: {error}\n{output}"
        return True, output
    except subprocess.TimeoutExpired:
        return False, "Claude invocation timed out"
    except Exception as exc:
        return False, str(exc)


def invoke_codex(
    agent: dict[str, Any],
    prompt: str,
    timeout: int,
    read_only: bool = False,
    config: dict[str, Any] | None = None,
) -> tuple[bool, str]:
    command = agent.get("command", "codex")
    args = [command, "exec", "--skip-git-repo-check"]
    if read_only:
        args.extend(["--sandbox", "read-only"])
    else:
        # safety.codex_fix_sandbox: "bypass" (default, full access for remediation),
        # "workspace-write" or "read-only" to keep Codex sandboxed during fixes.
        sandbox_mode = str((config or {}).get("safety", {}).get("codex_fix_sandbox", "bypass"))
        if sandbox_mode in {"read-only", "workspace-write"}:
            args.extend(["--sandbox", sandbox_mode])
        else:
            args.append("--dangerously-bypass-approvals-and-sandbox")
    args.extend(["--cd", str(SCRIPT_DIR), prompt])
    model = agent.get("model")
    if model:
        args.extend(["--model", model])
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        output = (result.stdout or "").strip()
        error = (result.stderr or "").strip()
        if result.returncode != 0:
            return False, f"Codex exit code {result.returncode}: {error}\n{output}"
        return True, output
    except subprocess.TimeoutExpired:
        return False, "Codex invocation timed out"
    except Exception as exc:
        return False, str(exc)


def invoke_custom(agent: dict[str, Any], prompt: str, timeout: int) -> tuple[bool, str]:
    template = str(agent.get("command_template") or "").strip()
    if not template:
        command = agent.get("command")
        if not command:
            return False, "custom agent has no command or command_template"
        template = f"{command} {{prompt}}"

    prompt_value = shlex.quote(prompt)
    command = template.replace("{prompt}", prompt_value)
    return run_local(command, timeout=timeout)


def invoke_agent(
    agent: dict[str, Any],
    prompt: str,
    timeout: int | None = None,
    read_only: bool = False,
    config: dict[str, Any] | None = None,
) -> tuple[bool, str]:
    timeout = timeout or agent.get("timeout", 300)
    agent_type = agent.get("type", agent["name"])
    if agent_type == "claude":
        return invoke_claude(agent, prompt, timeout, read_only=read_only, config=config)
    if agent_type == "codex":
        return invoke_codex(agent, prompt, timeout, read_only=read_only, config=config)
    if agent_type == "custom":
        return invoke_custom(agent, prompt, timeout)
    return False, f"Unsupported agent type: {agent_type}"


def get_agent_cooldown_minutes(rule: dict[str, Any], config: dict[str, Any]) -> int:
    rule_cooldown = rule.get("agent_cooldown_minutes")
    if rule_cooldown is not None:
        return int(rule_cooldown)
    return int(config.get("alerting", {}).get("agent_cooldown_minutes", 60))


def record_agent_call(
    check_id: str,
    check_name: str,
    target: str,
    agent_name: str,
    agent_type: str,
    model: str | None,
    prompt_tokens: int,
    response_tokens: int,
    total_tokens: int,
    duration_seconds: float,
    success: bool,
    output_summary: str,
    cooldown_skipped: bool = False,
    stage: str | None = None,
) -> None:
    calls = load_json_file(AGENT_CALLS_FILE, default=[])
    calls.append({
        "timestamp": utc_iso(),
        "check_id": check_id,
        "check_name": check_name,
        "target": target,
        "agent_name": agent_name,
        "agent_type": agent_type,
        "model": model,
        "prompt_tokens": prompt_tokens,
        "response_tokens": response_tokens,
        "total_tokens": total_tokens,
        "duration_seconds": round(duration_seconds, 2),
        "success": success,
        "output_summary": (output_summary or "")[:500],
        "cooldown_skipped": cooldown_skipped,
        "stage": stage,
    })
    if len(calls) > 500:
        calls = calls[-500:]
    save_json_file(AGENT_CALLS_FILE, calls)


def check_internet(config: dict[str, Any]) -> tuple[bool, str]:
    connectivity = config.get("connectivity", {})
    timeout = connectivity.get("timeout", 5)
    last_error = "no connectivity checks configured"
    for url in connectivity.get("internet_checks", DEFAULT_INTERNET_CHECKS):
        ok, detail = check_http(url, timeout=timeout, accept_codes=[200, 204, 301, 302, 400, 403])
        if ok:
            return True, url
        last_error = detail
    return False, last_error


# ── AI Pipeline (3-stage: analysis → fix → eval) ─────────────────────────────

def get_ai_pipeline_config(config: dict[str, Any], rule: dict[str, Any]) -> dict[str, Any]:
    """Merge global ai_pipeline config with per-rule override."""
    global_pipeline = config.get("ai_pipeline", {})
    rule_pipeline = rule.get("ai_pipeline", {})
    return {**global_pipeline, **rule_pipeline}


def is_pipeline_enabled(config: dict[str, Any], rule: dict[str, Any]) -> bool:
    pipeline = get_ai_pipeline_config(config, rule)
    return bool(pipeline.get("enabled", False))


def _get_pipeline_agent(
    pipeline_cfg: dict[str, Any],
    stage: str,
    base_agents: list[tuple[dict[str, Any], Any]],
    config: dict[str, Any],
) -> tuple[dict[str, Any], Any] | None:
    """Return (agent_dict, status) overriding the model for the given pipeline stage."""
    stage_cfg = pipeline_cfg.get(stage, {})
    if not stage_cfg:
        return base_agents[0] if base_agents else None

    agent_name = stage_cfg.get("agent")
    model_override = stage_cfg.get("model")

    for agent, status in base_agents:
        if not agent_name or agent.get("name") == agent_name or agent.get("type") == agent_name:
            merged = {**agent}
            if model_override:
                merged["model"] = model_override
            return merged, status

    return base_agents[0] if base_agents else None


_ANALYSIS_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}


DEFAULT_MAX_ERROR_CHARS = 1000


def _get_max_error_chars(config: dict[str, Any] | None) -> int:
    if not config:
        return DEFAULT_MAX_ERROR_CHARS
    try:
        return int(config.get("token_protection", {}).get("max_error_chars", DEFAULT_MAX_ERROR_CHARS))
    except (TypeError, ValueError):
        return DEFAULT_MAX_ERROR_CHARS


def _truncate_error(error: str, max_chars: int = DEFAULT_MAX_ERROR_CHARS) -> str:
    """Cap error/log text for prompts. For multi-line command output the tail
    holds the failure, so keep the last non-empty lines; otherwise keep head+tail."""
    if len(error) <= max_chars:
        return error
    lines = [ln for ln in error.splitlines() if ln.strip()]
    if len(lines) > 3:
        tail_lines: list[str] = []
        total = 0
        for ln in reversed(lines):
            total += len(ln) + 1
            tail_lines.insert(0, ln)
            if total >= max_chars:
                break
        omitted = len(lines) - len(tail_lines)
        body = "\n".join(tail_lines)
        if omitted > 0:
            return f"...[{omitted} earlier line(s) omitted]...\n{body}"
        return body
    half = max_chars // 2
    omitted = len(error) - max_chars
    return f"{error[:half]}\n...[{omitted} chars omitted]...\n{error[-half:]}"


def get_cached_analysis(rule_key: str, cooldown_seconds: int) -> dict[str, Any] | None:
    """Return a cached analysis result if it's still within the cooldown window."""
    entry = _ANALYSIS_CACHE.get(rule_key)
    if entry is None:
        return None
    ts, result = entry
    if time.time() - ts < cooldown_seconds:
        return result
    del _ANALYSIS_CACHE[rule_key]
    return None


def cache_analysis(rule_key: str, result: dict[str, Any]) -> None:
    _ANALYSIS_CACHE[rule_key] = (time.time(), result)


def build_analysis_prompt(rule: dict[str, Any], detail: Any, config: dict[str, Any]) -> str:
    """Diagnostic-only prompt for the analysis pass. No writes allowed by instruction."""
    error = _truncate_error(str(detail), _get_max_error_chars(config))
    host_name = rule["host"].get("name", rule["target"])
    host_addr = rule["host"].get("address", rule["target"])
    check_name = rule.get("name", "")
    description = rule.get("description", "")

    return (
        f"DIAGNOSIS ONLY — run only read-only commands. Do NOT restart, modify, or delete anything.\n\n"
        f"System: {host_name} ({host_addr})\n"
        f"Check: {check_name} — {description}\n"
        f"Failure signal: {error}\n\n"
        f"Instructions:\n"
        f"1. Run read-only diagnostics to identify the root cause.\n"
        f"2. Respond with ONLY a JSON object (no other text):\n\n"
        f'{{"root_cause":"<one sentence>","confidence":"high|medium|low",'
        f'"plan":["ordered step 1","step 2"],'
        f'"fix_commands":["exact command 1","exact command 2"],'
        f'"risk":"low|medium|high",'
        f'"needs_human":false,"human_action":""}}\n\n'
        f"Set needs_human=true if the fix requires manual access, passwords, or physical action.\n"
        f"Set risk=high if fixing could cause data loss or downtime to other services."
    )


def parse_analysis_output(output: str) -> dict[str, Any] | None:
    """Extract structured JSON from analysis pass output."""
    # Try to find a JSON object containing root_cause
    m = re.search(r'\{[^{}]*"root_cause".*?\}', output, re.DOTALL)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    # Try the whole output
    stripped = output.strip()
    if stripped.startswith("{"):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            pass
    return None


def build_fix_prompt_from_analysis(
    rule: dict[str, Any], analysis: dict[str, Any], config: dict[str, Any]
) -> str:
    """Short fix prompt built from the analysis plan — cheaper for Haiku/mini."""
    host_name = rule["host"].get("name", rule["target"])
    host_addr = rule["host"].get("address", rule["target"])
    root_cause = analysis.get("root_cause", "unknown issue")
    plan = analysis.get("plan", [])
    fix_commands = analysis.get("fix_commands", [])

    plan_text = "\n".join(f"  {i+1}. {step}" for i, step in enumerate(plan)) if plan else "  1. Investigate and fix."
    cmd_text = "\n".join(f"  - {c}" for c in fix_commands) if fix_commands else "  (derive from plan)"

    return (
        f"Fix the following on {host_name} ({host_addr}).\n\n"
        f"Root cause: {root_cause}\n\n"
        f"Execute this plan:\n{plan_text}\n\n"
        f"Expected commands:\n{cmd_text}\n\n"
        f"After fixing, confirm the service/check is healthy.\n"
        f"Report: what you did and the final state."
    ) + build_safety_prompt(config)


def derive_human_state(result: dict[str, Any]) -> str:
    """Map result + alert_state to a human-readable state label."""
    r = result.get("result", "")
    alert_state = result.get("alert_state", {}) or {}
    if r == "pass":
        return "ok"
    if r == "fixed" and alert_state.get("resolved"):
        return "resolved_auto"
    if r == "fixed":
        return "resolved_auto"
    if alert_state.get("schedule_paused"):
        return "needs_you"
    if r == "fix_failed":
        return "needs_you"
    if r == "failed":
        return "acting"
    return "ok"


def build_safety_prompt(config: dict[str, Any]) -> str:
    safety = config.get("safety", {})
    if not safety.get("enabled", True):
        return ""

    rules = safety.get("prompt_rules", [])
    examples = safety.get("safe_cleanup_examples", [])

    # Compact mode (default): a single short, stable block so the fixed safety
    # framework costs few tokens per invocation. The hard technical barrier is
    # the PreToolUse hook / blocked_command_patterns, not this prose.
    if safety.get("compact_prompt", True):
        parts = ["", "Seguridad: no destruyas datos (sin rm -rf no aprobado, mkfs, dd, reboot, ni borrado de volúmenes Docker)."]
        if rules:
            parts.append("Reglas: " + " ".join(str(item).rstrip(".") + "." for item in rules))
        if examples:
            parts.append("Limpieza segura preferida: " + ", ".join(str(item) for item in examples) + ".")
        parts.append("Si no es seguro arreglarlo, diagnostica y no ejecutes acciones destructivas.")
        return "\n".join(parts)

    lines = ["", "Restricciones obligatorias de seguridad e integridad:"]
    for item in rules:
        lines.append(f"- {item}")
    if examples:
        lines.append("")
        lines.append("Ejemplos de acciones conservadoras aceptables:")
        for item in examples:
            lines.append(f"- {item}")
    lines.append("")
    lines.append("Si no puedes arreglarlo sin riesgo, diagnostica, explica y no ejecutes acciones destructivas.")
    return "\n".join(lines)


def format_fix_prompt(rule: dict[str, Any], detail: Any, config: dict[str, Any]) -> str:
    if isinstance(detail, (int, float)):
        error = str(detail)
        value = detail
    else:
        error = _truncate_error(str(detail), _get_max_error_chars(config))
        value = parse_numeric(error)
        if value is None:
            value = float("nan")

    prompt = rule.get("fix_prompt") or (
        "Hay un problema en {host_name} ({host[address]}): {error}. "
        "Diagnostica y corrige de forma conservadora."
    )
    context = build_context(rule["target"], rule["host"], rule)
    context.update({"error": error, "value": value})
    return prompt.format(**context) + build_safety_prompt(config)


def validate_command_safety(command: str, config: dict[str, Any]) -> tuple[bool, str]:
    safety = config.get("safety", {})
    if not safety.get("enabled", True):
        return True, "safety disabled"

    normalized = " ".join((command or "").split())
    for pattern in safety.get("blocked_command_patterns", DEFAULT_BLOCKED_COMMAND_PATTERNS):
        if re.search(pattern, normalized, re.IGNORECASE):
            return False, f"blocked by safety policy: {pattern}"
    return True, "allowed"


def run_emergency_actions(
    rule: dict[str, Any],
    reason: str,
    hosts: dict[str, dict[str, Any]],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    actions_run: list[dict[str, Any]] = []
    for action in rule.get("emergency_actions", []):
        when = action.get("when", ["no_agent", "agent_failure", "no_internet"])
        if reason not in when:
            continue

        action_host_name = action.get("target", rule["target"])
        action_host = hosts.get(action_host_name, rule["host"])
        allowed, safety_reason = validate_command_safety(action["command"], config)
        if not allowed:
            action_result = {
                "name": action.get("name", action["command"]),
                "reason": reason,
                "success": False,
                "output": safety_reason,
            }
            actions_run.append(action_result)
            log.error("  Emergency action blocked by safety layer %s: %s", action_result["name"], safety_reason)
            continue

        if action.get("type") == "local":
            ok, output = run_local(action["command"], timeout=action.get("timeout", 60), cwd=action.get("cwd") or None)
        else:
            ok, output = run_host_command(action_host, action["command"], timeout=action.get("timeout", 60))

        action_result = {
            "name": action.get("name", action["command"]),
            "reason": reason,
            "success": ok,
            "output": output[:500],
        }
        actions_run.append(action_result)
        level = logging.INFO if ok else logging.ERROR
        log.log(level, "  Emergency action %s: %s", action_result["name"], output[:300])

    return actions_run


def load_state() -> dict[str, Any]:
    return load_json_file(STATE_FILE, default={"alerts": {}})


def default_alert_state_entry(rule: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "ok",
        "consecutive_failures": 0,
        "first_failure_at": None,
        "last_failure_at": None,
        "last_ok_at": None,
        "last_notification_at": None,
        "detail": "",
        "alert_id": rule.get("id"),
        "alert_name": rule.get("name"),
        "target": rule.get("target"),
        "schedule_paused": False,
        "schedule_paused_at": None,
        "schedule_pause_reason": "",
        "last_rearmed_at": None,
        "acknowledged_at": None,
        "acknowledged_by": "",
        "silenced_until": None,
        "silenced_reason": "",
        "maintenance_active": False,
        "maintenance_window_id": None,
        "maintenance_reason": "",
        "maintenance_until": None,
        "last_agent_called_at": None,
    }


def parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def utc_now_iso() -> str:
    return now_utc().isoformat()


def sanitize_maintenance_window(window: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    current = now or now_utc()
    starts_at = str(window.get("starts_at") or "")
    ends_at = str(window.get("ends_at") or "")
    starts_dt = parse_iso_datetime(starts_at)
    ends_dt = parse_iso_datetime(ends_at)
    is_active = bool(starts_dt and ends_dt and starts_dt <= current <= ends_dt)
    return {
        "id": str(window.get("id") or ""),
        "scope": str(window.get("scope") or ""),
        "host": str(window.get("host") or ""),
        "alert_id": str(window.get("alert_id") or ""),
        "alert_name": str(window.get("alert_name") or ""),
        "starts_at": starts_at,
        "ends_at": ends_at,
        "reason": str(window.get("reason") or ""),
        "created_at": str(window.get("created_at") or ""),
        "active": is_active,
    }


def list_maintenance_windows(config: dict[str, Any]) -> list[dict[str, Any]]:
    current = now_utc()
    windows = [sanitize_maintenance_window(item, current) for item in config.get("maintenance_windows", [])]
    return sorted(windows, key=lambda item: (not item["active"], item["starts_at"], item["id"]))


def get_active_maintenance_for_rule(config: dict[str, Any], rule: dict[str, Any], now: datetime | None = None) -> dict[str, Any] | None:
    current = now or now_utc()
    for raw_window in config.get("maintenance_windows", []):
        window = sanitize_maintenance_window(raw_window, current)
        if not window["active"]:
            continue
        if window["scope"] == "host" and window["host"] == str(rule.get("target") or ""):
            return window
        if window["scope"] == "alert":
            if window["alert_id"] and window["alert_id"] != str(rule.get("id") or ""):
                continue
            if not window["alert_id"] and window["alert_name"] and window["alert_name"] != str(rule.get("name") or ""):
                continue
            if window["host"] and window["host"] != str(rule.get("target") or ""):
                continue
            return window
    return None


def create_maintenance_window(config: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    scope = str(payload.get("scope") or "").strip()
    if scope not in {"host", "alert"}:
        raise ValueError("scope must be host or alert")
    host = str(payload.get("host") or "").strip()
    alert_id = str(payload.get("alert_id") or "").strip()
    alert_name = str(payload.get("alert_name") or "").strip()
    if scope == "host":
        if not host:
            raise ValueError("host is required for host maintenance")
    elif not alert_id and not alert_name:
        raise ValueError("alert id or name is required for alert maintenance")

    starts_at = str(payload.get("starts_at") or "").strip()
    ends_at = str(payload.get("ends_at") or "").strip()
    starts_dt = parse_iso_datetime(starts_at)
    ends_dt = parse_iso_datetime(ends_at)
    if starts_dt is None or ends_dt is None:
        raise ValueError("starts_at and ends_at must be valid ISO datetimes")
    if ends_dt <= starts_dt:
        raise ValueError("ends_at must be after starts_at")

    if host and host not in (config.get("hosts") or {}):
        raise ValueError("unknown host")
    if alert_id or alert_name:
        rules = config.get("alert_rules", [])
        matched = next((rule for rule in rules if str(rule.get("id") or "") == alert_id or str(rule.get("name") or "") == alert_name), None)
        if matched is None:
            raise ValueError("unknown alert")
        alert_id = str(matched.get("id") or alert_id)
        alert_name = str(matched.get("name") or alert_name)

    window = {
        "id": secrets.token_hex(8),
        "scope": scope,
        "host": host,
        "alert_id": alert_id,
        "alert_name": alert_name,
        "starts_at": starts_dt.isoformat(),
        "ends_at": ends_dt.isoformat(),
        "reason": str(payload.get("reason") or "").strip(),
        "created_at": utc_now_iso(),
    }
    config.setdefault("maintenance_windows", []).append(window)
    return window


def delete_maintenance_window(config: dict[str, Any], payload: dict[str, Any]) -> None:
    target_id = str(payload.get("id") or "").strip()
    if not target_id:
        raise ValueError("maintenance window id is required")
    windows = config.get("maintenance_windows", [])
    remaining = [item for item in windows if str(item.get("id") or "") != target_id]
    if len(remaining) == len(windows):
        raise ValueError("maintenance window not found")
    config["maintenance_windows"] = remaining


def should_pause_on_unresolved(config: dict[str, Any], rule: dict[str, Any]) -> bool:
    alerting = config.get("alerting", {})
    if "pause_schedule_on_fix_failed" in rule:
        return bool(rule.get("pause_schedule_on_fix_failed"))
    return bool(alerting.get("pause_schedule_on_fix_failed", True))


def set_alert_schedule_paused(
    state: dict[str, Any],
    rule: dict[str, Any],
    paused: bool,
    reason: str = "",
    failure_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    key = rule["instance_key"]
    alerts = state.setdefault("alerts", {})
    entry = alerts.get(key, default_alert_state_entry(rule))
    entry["alert_id"] = rule.get("id")
    entry["alert_name"] = rule.get("name")
    entry["target"] = rule.get("target")
    entry["schedule_paused"] = paused
    if paused:
        entry["schedule_paused_at"] = utc_iso()
        entry["schedule_pause_reason"] = reason
        # Persist a forensic snapshot of WHY the check was paused so the UI can
        # explain the last failure long after the run that triggered it.
        ctx = failure_context or {}
        entry["pause_failure_detail"] = str(ctx.get("failure_detail") or "")
        entry["pause_last_output"] = str(ctx.get("last_output") or "")
        entry["pause_attempts"] = ctx.get("attempts") or []
        entry["pause_consecutive_failures"] = int(
            ctx.get("consecutive_failures") or entry.get("consecutive_failures") or 0
        )
    else:
        entry["schedule_paused_at"] = None
        entry["schedule_pause_reason"] = ""
        entry["last_rearmed_at"] = utc_iso()
        entry["pause_failure_detail"] = ""
        entry["pause_last_output"] = ""
        entry["pause_attempts"] = []
        entry["pause_consecutive_failures"] = 0
    alerts[key] = entry
    return entry


def build_paused_result(rule: dict[str, Any], prior: dict[str, Any] | None, state_entry: dict[str, Any]) -> dict[str, Any]:
    if prior:
        cached = deepcopy(prior)
    else:
        cached = {
            "name": rule["name"],
            "target": rule["target"],
            "description": rule["description"],
            "detail": state_entry.get("detail") or "Alert paused after an unresolved remediation failure",
            "result": "fix_failed",
            "agent_used": None,
            "agent_attempts": [],
            "emergency_actions": [],
            "token_usage": {
                "enabled": False,
                "prompt_tokens": 0,
                "response_tokens": 0,
                "total_tokens": 0,
                "stopped": False,
                "reason": "",
            },
        }
    cached["cached"] = True
    cached["schedule_paused"] = True
    cached["detail"] = state_entry.get("detail") or cached.get("detail") or "Alert paused"
    cached["notifications_enabled"] = bool(rule.get("notifications", True))
    cached["alert_state"] = {
        "key": rule["instance_key"],
        "status": state_entry.get("status", "firing"),
        "consecutive_failures": state_entry.get("consecutive_failures", 0),
        "should_notify": False,
        "resolved": False,
        "detail": state_entry.get("detail", ""),
        "schedule_paused": True,
        "schedule_paused_at": state_entry.get("schedule_paused_at"),
        "schedule_pause_reason": state_entry.get("schedule_pause_reason", ""),
        "last_rearmed_at": state_entry.get("last_rearmed_at"),
        "pause_failure_detail": state_entry.get("pause_failure_detail", ""),
        "pause_last_output": state_entry.get("pause_last_output", ""),
        "pause_attempts": state_entry.get("pause_attempts", []),
        "pause_consecutive_failures": state_entry.get("pause_consecutive_failures", 0),
    }
    return cached


def update_alert_state(
    state: dict[str, Any],
    rule: dict[str, Any],
    passed: bool,
    detail: Any,
    config: dict[str, Any],
) -> dict[str, Any]:
    key = rule["instance_key"]
    alerts = state.setdefault("alerts", {})
    entry = alerts.get(key, default_alert_state_entry(rule))
    entry["alert_id"] = rule.get("id")
    entry["alert_name"] = rule.get("name")
    entry["target"] = rule.get("target")

    threshold = config.get("alerting", {}).get("failure_threshold_runs", 1)
    repeat_minutes = config.get("alerting", {}).get("repeat_notification_minutes", 60)
    now = now_utc()
    should_notify = False
    resolved = False
    silenced_until = entry.get("silenced_until")
    silence_active = False
    if silenced_until:
        try:
            silence_active = datetime.fromisoformat(silenced_until) > now
        except ValueError:
            silence_active = False
    maintenance = get_active_maintenance_for_rule(config, rule, now)
    maintenance_active = maintenance is not None

    if passed:
        resolved = entry["status"] == "firing"
        entry["status"] = "ok"
        entry["consecutive_failures"] = 0
        entry["detail"] = str(detail)
        entry["schedule_paused"] = False
        entry["schedule_paused_at"] = None
        entry["schedule_pause_reason"] = ""
        entry["last_ok_at"] = now.isoformat()
        entry["first_failure_at"] = None
        entry["last_failure_at"] = None
        entry["last_agent_called_at"] = None
        if resolved and not config.get("alerting", {}).get("notify_on_resolve", True):
            resolved = False
    else:
        entry["consecutive_failures"] += 1
        entry["detail"] = str(detail)
        entry["last_failure_at"] = now.isoformat()
        if not entry["first_failure_at"]:
            entry["first_failure_at"] = now.isoformat()
        if entry["consecutive_failures"] >= threshold:
            last_notified = entry.get("last_notification_at")
            notify_again = True
            if last_notified:
                delta = now - datetime.fromisoformat(last_notified)
                notify_again = delta.total_seconds() >= repeat_minutes * 60
            if entry["status"] != "firing" or notify_again:
                if not silence_active and not maintenance_active:
                    should_notify = True
                    entry["last_notification_at"] = now.isoformat()
            entry["status"] = "firing"
        else:
            entry["status"] = "pending"

    entry["maintenance_active"] = maintenance_active
    entry["maintenance_window_id"] = maintenance.get("id") if maintenance else None
    entry["maintenance_reason"] = maintenance.get("reason", "") if maintenance else ""
    entry["maintenance_until"] = maintenance.get("ends_at") if maintenance else None

    alerts[key] = entry
    return {
        "key": key,
        "status": entry["status"],
        "consecutive_failures": entry["consecutive_failures"],
        "should_notify": should_notify,
        "resolved": resolved,
        "detail": entry["detail"],
        "schedule_paused": bool(entry.get("schedule_paused")),
        "schedule_paused_at": entry.get("schedule_paused_at"),
        "schedule_pause_reason": entry.get("schedule_pause_reason", ""),
        "last_rearmed_at": entry.get("last_rearmed_at"),
        "acknowledged_at": entry.get("acknowledged_at"),
        "acknowledged_by": entry.get("acknowledged_by", ""),
        "silenced_until": entry.get("silenced_until"),
        "silenced_reason": entry.get("silenced_reason", ""),
        "maintenance_active": bool(entry.get("maintenance_active")),
        "maintenance_window_id": entry.get("maintenance_window_id"),
        "maintenance_reason": entry.get("maintenance_reason", ""),
        "maintenance_until": entry.get("maintenance_until"),
    }


def finalize_alert_state_after_remediation(
    state: dict[str, Any],
    rule: dict[str, Any],
    passed: bool,
    detail: Any,
    config: dict[str, Any],
) -> dict[str, Any]:
    key = rule["instance_key"]
    alerts = state.setdefault("alerts", {})
    entry = alerts.get(key, default_alert_state_entry(rule))
    entry["alert_id"] = rule.get("id")
    entry["alert_name"] = rule.get("name")
    entry["target"] = rule.get("target")
    entry["detail"] = str(detail)
    now = now_utc()
    threshold = config.get("alerting", {}).get("failure_threshold_runs", 1)
    maintenance = get_active_maintenance_for_rule(config, rule, now)

    if passed:
        entry["status"] = "ok"
        entry["consecutive_failures"] = 0
        entry["last_ok_at"] = now.isoformat()
        entry["first_failure_at"] = None
        entry["last_failure_at"] = None
        entry["schedule_paused"] = False
        entry["schedule_paused_at"] = None
        entry["schedule_pause_reason"] = ""
    else:
        if not entry.get("consecutive_failures"):
            entry["consecutive_failures"] = 1
        entry["last_failure_at"] = now.isoformat()
        if not entry.get("first_failure_at"):
            entry["first_failure_at"] = now.isoformat()
        entry["status"] = "firing" if entry["consecutive_failures"] >= threshold else "pending"
    entry["maintenance_active"] = maintenance is not None
    entry["maintenance_window_id"] = maintenance.get("id") if maintenance else None
    entry["maintenance_reason"] = maintenance.get("reason", "") if maintenance else ""
    entry["maintenance_until"] = maintenance.get("ends_at") if maintenance else None

    alerts[key] = entry
    return {
        "key": key,
        "status": entry["status"],
        "consecutive_failures": entry["consecutive_failures"],
        "should_notify": False,
        "resolved": False,
        "detail": entry["detail"],
        "schedule_paused": bool(entry.get("schedule_paused")),
        "schedule_paused_at": entry.get("schedule_paused_at"),
        "schedule_pause_reason": entry.get("schedule_pause_reason", ""),
        "last_rearmed_at": entry.get("last_rearmed_at"),
        "acknowledged_at": entry.get("acknowledged_at"),
        "acknowledged_by": entry.get("acknowledged_by", ""),
        "silenced_until": entry.get("silenced_until"),
        "silenced_reason": entry.get("silenced_reason", ""),
        "maintenance_active": bool(entry.get("maintenance_active")),
        "maintenance_window_id": entry.get("maintenance_window_id"),
        "maintenance_reason": entry.get("maintenance_reason", ""),
        "maintenance_until": entry.get("maintenance_until"),
    }


def _iso_to_epoch(value: Any) -> float:
    """Best-effort parse of an ISO-8601 timestamp into a unix epoch float."""
    if not value:
        return 0.0
    try:
        text = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except Exception:
        return 0.0


def update_metrics_counters(
    results: list[dict[str, Any]],
    host_summaries: dict[str, Any],
    duration: float,
    agent_stats: dict[str, int],
) -> None:
    """Accumulate monotonic counters into METRICS_COUNTERS_FILE.

    agent_calls.json is a rolling list (capped at 500), so it cannot be used as a
    Prometheus counter directly. Here we keep an ever-growing tally that the
    /metrics endpoint serves verbatim. Per-model token data is folded in by
    consuming only agent calls newer than the stored cursor.
    """
    counters = load_json_file(METRICS_COUNTERS_FILE, default={})
    counters.setdefault("runs_total", 0)
    counters.setdefault("run_duration_seconds_sum", 0.0)
    counters.setdefault("agent_invocations_total", 0)
    counters.setdefault("agent_success_total", 0)
    counters.setdefault("agent_failure_total", 0)
    counters.setdefault("emergency_actions_total", 0)
    counters.setdefault("hosts", {})
    counters.setdefault("checks", {})
    counters.setdefault("models", {})
    counters.setdefault("ssh", {})
    counters.setdefault("agent_calls_cursor", "")

    # Fold in SSH sessions opened during this run, then reset the in-memory tally.
    for address, count in list(_SSH_SESSION_COUNTS.items()):
        counters["ssh"][address] = int(counters["ssh"].get(address, 0)) + int(count)
    _SSH_SESSION_COUNTS.clear()

    counters["runs_total"] += 1
    counters["run_duration_seconds_sum"] = round(
        float(counters["run_duration_seconds_sum"]) + float(duration), 2
    )
    counters["agent_invocations_total"] += int(agent_stats.get("invocations", 0))
    counters["agent_success_total"] += int(agent_stats.get("successes", 0))
    counters["agent_failure_total"] += int(agent_stats.get("failures", 0))
    counters["emergency_actions_total"] += int(agent_stats.get("emergency_runs", 0))

    for host_name, host_result in host_summaries.items():
        bucket = counters["hosts"].setdefault(
            host_name, {"passed": 0, "failed": 0, "fixed": 0, "fix_failed": 0}
        )
        bucket["passed"] += int(host_result.get("passed", 0))
        bucket["failed"] += int(host_result.get("failed", 0))
        bucket["fixed"] += int(host_result.get("fixed", 0))
        bucket["fix_failed"] += int(host_result.get("fix_failed", 0))

    for item in results:
        if item.get("cached"):
            continue
        key = f"{item.get('target', '')}|{item.get('name', '')}"
        bucket = counters["checks"].setdefault(key, {"runs": 0, "failures": 0, "fixed": 0})
        bucket["runs"] += 1
        if not result_success(item.get("result", "")):
            bucket["failures"] += 1
        if item.get("result") == "fixed" or item.get("agent_used") and result_success(item.get("result", "")):
            # best-effort: a check that ran an agent and ended up healthy was fixed
            if item.get("agent_used"):
                bucket["fixed"] += 1

    # Fold in per-model token usage from agent calls newer than the cursor.
    cursor = counters.get("agent_calls_cursor", "") or ""
    new_cursor = cursor
    calls = load_json_file(AGENT_CALLS_FILE, default=[])
    if isinstance(calls, list):
        for call in calls:
            ts = str(call.get("timestamp", ""))
            if not ts or ts <= cursor:
                continue
            if ts > new_cursor:
                new_cursor = ts
            model = call.get("model")
            if not model:
                continue
            mbucket = counters["models"].setdefault(
                model,
                {"prompt_tokens": 0, "response_tokens": 0, "calls_success": 0, "calls_failure": 0},
            )
            mbucket["prompt_tokens"] += int(call.get("prompt_tokens", 0) or 0)
            mbucket["response_tokens"] += int(call.get("response_tokens", 0) or 0)
            if call.get("success"):
                mbucket["calls_success"] += 1
            else:
                mbucket["calls_failure"] += 1
    counters["agent_calls_cursor"] = new_cursor

    try:
        save_json_file(METRICS_COUNTERS_FILE, counters)
    except Exception as exc:
        log.warning("Failed to persist metrics counters: %s", exc)


def _prom_escape(value: str) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def render_prometheus_metrics() -> str:
    """Render RootCause state + accumulated counters in Prometheus exposition format."""
    out: list[str] = []

    def emit(name: str, mtype: str, help_text: str, samples: list[tuple[str, Any]]) -> None:
        out.append(f"# HELP {name} {help_text}")
        out.append(f"# TYPE {name} {mtype}")
        for labels, value in samples:
            suffix = f"{{{labels}}}" if labels else ""
            out.append(f"{name}{suffix} {value}")

    counters = load_json_file(METRICS_COUNTERS_FILE, default={})
    report = load_json_file(STATUS_FILE, default={})

    # --- liveness / run-level gauges ---
    emit("rootcause_up", "gauge", "RootCause web service is up and serving metrics", [("", 1)])
    emit(
        "rootcause_last_run_timestamp",
        "gauge",
        "Unix timestamp of the last completed check run",
        [("", f"{_iso_to_epoch(report.get('timestamp')):.0f}")],
    )
    emit(
        "rootcause_run_duration_seconds",
        "gauge",
        "Duration of the last check run in seconds",
        [("", report.get("duration_seconds", 0) or 0)],
    )
    emit(
        "rootcause_internet_ok",
        "gauge",
        "Whether RootCause had internet connectivity on the last run",
        [("", 1 if report.get("internet_ok") else 0)],
    )
    emit(
        "rootcause_last_run_tokens",
        "gauge",
        "Estimated tokens spent on the last run",
        [("", (report.get("summary") or {}).get("estimated_tokens", 0) or 0)],
    )

    # --- accumulated counters ---
    emit("rootcause_runs_total", "counter", "Total number of check runs", [("", counters.get("runs_total", 0))])
    emit(
        "rootcause_run_duration_seconds_total",
        "counter",
        "Cumulative time spent running checks",
        [("", counters.get("run_duration_seconds_sum", 0))],
    )
    emit("rootcause_agent_invocations_total", "counter", "Total AI agent invocations", [("", counters.get("agent_invocations_total", 0))])
    emit("rootcause_agent_success_total", "counter", "Total successful AI agent runs", [("", counters.get("agent_success_total", 0))])
    emit("rootcause_agent_failure_total", "counter", "Total failed AI agent runs", [("", counters.get("agent_failure_total", 0))])
    emit("rootcause_emergency_actions_total", "counter", "Total emergency actions taken", [("", counters.get("emergency_actions_total", 0))])

    host_counter_samples: dict[str, list[tuple[str, Any]]] = {
        "passed": [], "failed": [], "fixed": [], "fix_failed": []
    }
    for host_name, bucket in (counters.get("hosts") or {}).items():
        lbl = f'host="{_prom_escape(host_name)}"'
        for kind in host_counter_samples:
            host_counter_samples[kind].append((lbl, bucket.get(kind, 0)))
    emit("rootcause_host_passed_total", "counter", "Cumulative passed checks per host", host_counter_samples["passed"])
    emit("rootcause_host_failed_total", "counter", "Cumulative failed checks per host", host_counter_samples["failed"])
    emit("rootcause_host_fixed_total", "counter", "Cumulative auto-fixed checks per host", host_counter_samples["fixed"])
    emit("rootcause_host_fix_failed_total", "counter", "Cumulative failed fixes per host", host_counter_samples["fix_failed"])

    check_runs, check_failures, check_fixed = [], [], []
    for key, bucket in (counters.get("checks") or {}).items():
        host_name, _, check_name = key.partition("|")
        lbl = f'check="{_prom_escape(check_name)}",host="{_prom_escape(host_name)}"'
        check_runs.append((lbl, bucket.get("runs", 0)))
        check_failures.append((lbl, bucket.get("failures", 0)))
        check_fixed.append((lbl, bucket.get("fixed", 0)))
    emit("rootcause_check_runs_total", "counter", "Cumulative runs per check", check_runs)
    emit("rootcause_check_failures_total", "counter", "Cumulative failures per check", check_failures)
    emit("rootcause_check_fixed_total", "counter", "Cumulative auto-fixes per check", check_fixed)

    prompt_samples, response_samples, mcall_ok, mcall_fail = [], [], [], []
    for model, bucket in (counters.get("models") or {}).items():
        lbl = f'model="{_prom_escape(model)}"'
        prompt_samples.append((f'{lbl},kind="prompt"', bucket.get("prompt_tokens", 0)))
        response_samples.append((f'{lbl},kind="response"', bucket.get("response_tokens", 0)))
        mcall_ok.append((f'{lbl},success="true"', bucket.get("calls_success", 0)))
        mcall_fail.append((f'{lbl},success="false"', bucket.get("calls_failure", 0)))
    emit("rootcause_tokens_total", "counter", "Cumulative tokens per model and kind", prompt_samples + response_samples)
    emit("rootcause_model_calls_total", "counter", "Cumulative agent calls per model and outcome", mcall_ok + mcall_fail)

    # --- SSH sessions opened by RootCause (cumulative, per host) ---
    addr_to_name: dict[str, str] = {}
    try:
        cfg = load_json_file(CHECKS_FILE, default={})
        for hname, hcfg in (cfg.get("hosts") or {}).items():
            addr = str((hcfg or {}).get("address") or "").strip()
            if addr:
                addr_to_name[addr] = hname
    except Exception:
        pass
    ssh_samples = []
    for address, count in (counters.get("ssh") or {}).items():
        host_label = addr_to_name.get(address, address)
        ssh_samples.append((f'host="{_prom_escape(host_label)}"', count))
    emit("rootcause_ssh_sessions_total", "counter", "Cumulative SSH sessions opened by RootCause per host", ssh_samples)

    # --- per-check current state gauges (from the latest report) ---
    up_s, failed_s, consec_s, paused_s, maint_s, ack_s, notif_s = [], [], [], [], [], [], []
    for item in report.get("checks", []) or []:
        alert = item.get("alert_state") or {}
        lbl = f'check="{_prom_escape(item.get("name", ""))}",host="{_prom_escape(item.get("target", ""))}"'
        passed = 1 if result_success(item.get("result", "")) else 0
        up_s.append((lbl, passed))
        failed_s.append((lbl, 0 if passed else 1))
        consec_s.append((lbl, int(alert.get("consecutive_failures", 0) or 0)))
        paused_s.append((lbl, 1 if alert.get("schedule_paused") else 0))
        maint_s.append((lbl, 1 if alert.get("maintenance_active") else 0))
        ack_s.append((lbl, 1 if alert.get("acknowledged_at") else 0))
        notif_s.append((lbl, 1 if item.get("notifications_enabled") else 0))
    emit("rootcause_check_up", "gauge", "1 if the check passed on the last run, else 0", up_s)
    emit("rootcause_check_failed", "gauge", "1 if the check failed on the last run, else 0", failed_s)
    emit("rootcause_check_consecutive_failures", "gauge", "Consecutive failures for the check", consec_s)
    emit("rootcause_check_paused", "gauge", "1 if the check is schedule-paused", paused_s)
    emit("rootcause_check_maintenance", "gauge", "1 if the check is in a maintenance window", maint_s)
    emit("rootcause_check_acknowledged", "gauge", "1 if the active alert is acknowledged", ack_s)
    emit("rootcause_check_notifications_enabled", "gauge", "1 if notifications are enabled for the check", notif_s)

    # --- per-host current snapshot gauges ---
    hp, hf, hx, hxf = [], [], [], []
    for host_name, summary in (report.get("hosts") or {}).items():
        lbl = f'host="{_prom_escape(host_name)}"'
        hp.append((lbl, summary.get("passed", 0)))
        hf.append((lbl, summary.get("failed", 0)))
        hx.append((lbl, summary.get("fixed", 0)))
        hxf.append((lbl, summary.get("fix_failed", 0)))
    emit("rootcause_host_passed", "gauge", "Checks passed per host on the last run", hp)
    emit("rootcause_host_failed", "gauge", "Checks failed per host on the last run", hf)
    emit("rootcause_host_fixed", "gauge", "Checks auto-fixed per host on the last run", hx)
    emit("rootcause_host_fix_failed", "gauge", "Failed fixes per host on the last run", hxf)

    # --- network stability probe (same source as the internet_stability check) ---
    ping_stats = load_json_file(PING_STATS_FILE, default={})
    up_p, loss_p, avg_p, best_p, worst_p, std_p, hops_p, base_p, trig_p = ([] for _ in range(9))
    for label, e in (ping_stats.get("targets") or {}).items():
        lbl = f'probe="{_prom_escape(label)}",address="{_prom_escape(e.get("address", ""))}"'
        up_p.append((lbl, 1 if e.get("up") else 0))
        loss_p.append((lbl, e.get("loss_pct", 0) or 0))
        avg_p.append((lbl, e.get("avg_ms", 0) or 0))
        best_p.append((lbl, e.get("best_ms", 0) or 0))
        worst_p.append((lbl, e.get("worst_ms", 0) or 0))
        std_p.append((lbl, e.get("stdev_ms", 0) or 0))
        if e.get("hops") is not None:
            hops_p.append((lbl, e.get("hops")))
        if e.get("baseline_avg_ms") is not None:
            base_p.append((lbl, e.get("baseline_avg_ms")))
        trig_p.append((lbl, 1 if e.get("triggered") else 0))
    emit("rootcause_ping_up", "gauge", "1 if the last network probe to the target completed", up_p)
    emit("rootcause_ping_loss_percent", "gauge", "End-to-end packet loss to the target (percent)", loss_p)
    emit("rootcause_ping_rtt_avg_ms", "gauge", "Average round-trip latency to the target (ms)", avg_p)
    emit("rootcause_ping_rtt_best_ms", "gauge", "Best round-trip latency to the target (ms)", best_p)
    emit("rootcause_ping_rtt_worst_ms", "gauge", "Worst round-trip latency to the target (ms)", worst_p)
    emit("rootcause_ping_rtt_stddev_ms", "gauge", "Round-trip latency jitter, stddev (ms)", std_p)
    emit("rootcause_ping_hops", "gauge", "Number of network hops to the target", hops_p)
    emit("rootcause_ping_rtt_baseline_ms", "gauge", "Rolling baseline average latency (ms)", base_p)
    emit("rootcause_ping_triggered", "gauge", "1 if the last probe tripped a stability threshold", trig_p)

    return "\n".join(out) + "\n"


def push_metrics(
    config: dict[str, Any],
    host_summaries: dict[str, Any],
    duration: float,
    agent_stats: dict[str, int],
    results: list[dict[str, Any]] | None = None,
) -> None:
    # Persist local cumulative counters for the native /metrics endpoint.
    try:
        update_metrics_counters(results or [], host_summaries, duration, agent_stats)
    except Exception as exc:
        log.warning("Failed to update local metrics counters: %s", exc)

    first_host = next(iter(config["hosts"].values()), {})
    pushgateway_url = first_host.get("pushgateway_url") or config.get("pushgateway_url")
    if not pushgateway_url:
        log.warning("No pushgateway_url configured, skipping metrics push")
        return

    lines = [
        f"rootcause_run_total 1",
        f"rootcause_run_duration_seconds {duration:.2f}",
        f"rootcause_last_run_timestamp {time.time():.0f}",
        f"rootcause_agent_invocations_total {agent_stats['invocations']}",
        f"rootcause_agent_success_total {agent_stats['successes']}",
        f"rootcause_agent_failure_total {agent_stats['failures']}",
        f"rootcause_emergency_actions_total {agent_stats['emergency_runs']}",
    ]

    for host_name, host_result in host_summaries.items():
        labels = f'{{host="{host_name}"}}'
        lines.append(f"rootcause_host_passed_total{labels} {host_result['passed']}")
        lines.append(f"rootcause_host_failed_total{labels} {host_result['failed']}")
        lines.append(f"rootcause_host_fixed_total{labels} {host_result['fixed']}")
        lines.append(f"rootcause_host_fix_failed_total{labels} {host_result['fix_failed']}")

    payload = "\n".join(lines) + "\n"
    try:
        response = requests.post(
            f"{pushgateway_url}/metrics/job/rootcause",
            data=payload,
            headers={"Content-Type": "text/plain"},
            timeout=10,
        )
        if response.status_code in (200, 202):
            log.info("Metrics pushed to Pushgateway successfully")
        else:
            log.warning("Pushgateway returned %d: %s", response.status_code, response.text[:200])
    except Exception as exc:
        log.error("Failed to push metrics: %s", exc)


NOTIFICATION_ID_FILE = SCRIPT_DIR / ".rootcause_notify_id"
NOTIFICATION_SYNC_KEY = "rootcause-summary"


def _desktop_env() -> dict[str, str] | None:
    dbus_addr = os.environ.get("DBUS_SESSION_BUS_ADDRESS")
    if not dbus_addr:
        bus_path = Path(f"/run/user/{os.getuid()}/bus")
        if bus_path.exists():
            dbus_addr = f"unix:path={bus_path}"
        else:
            return None
    env = os.environ.copy()
    env["DBUS_SESSION_BUS_ADDRESS"] = dbus_addr
    env.setdefault("DISPLAY", ":0")
    env.setdefault("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    return env


def _fcm_access_token(service_account_json: str) -> str:
    import json as _json
    import time as _time
    import base64 as _b64
    import urllib.request as _req
    import urllib.parse as _parse
    from cryptography.hazmat.primitives import hashes as _hashes, serialization as _ser
    from cryptography.hazmat.primitives.asymmetric import padding as _pad

    sa = _json.loads(service_account_json)
    now = int(_time.time())
    header = _b64.urlsafe_b64encode(b'{"alg":"RS256","typ":"JWT"}').rstrip(b"=").decode()
    claims = _b64.urlsafe_b64encode(_json.dumps({
        "iss": sa["client_email"],
        "scope": "https://www.googleapis.com/auth/firebase.messaging",
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now,
        "exp": now + 3600,
    }).encode()).rstrip(b"=").decode()
    signing_input = f"{header}.{claims}".encode()
    key = _ser.load_pem_private_key(sa["private_key"].encode(), password=None)
    sig = _b64.urlsafe_b64encode(key.sign(signing_input, _pad.PKCS1v15(), _hashes.SHA256())).rstrip(b"=").decode()
    jwt = f"{header}.{claims}.{sig}"

    req = _req.Request(
        "https://oauth2.googleapis.com/token",
        data=_parse.urlencode({"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": jwt}).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with _req.urlopen(req, timeout=10) as resp:
        return _json.loads(resp.read())["access_token"]


def send_fcm_push(service_account_json: str, token: str, title: str, body: str, data: dict[str, Any] | None = None) -> bool:
    import json as _json
    import urllib.request as _req

    try:
        sa = _json.loads(service_account_json)
        project_id = sa["project_id"]
        access_token = _fcm_access_token(service_account_json)
        message: dict[str, Any] = {
            "message": {
                "token": token,
                "notification": {"title": title, "body": body},
                "android": {"priority": "HIGH"},
            },
        }
        if data:
            message["message"]["data"] = {str(k): str(v) for k, v in data.items()}
        req = _req.Request(
            f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send",
            data=_json.dumps(message).encode(),
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
            method="POST",
        )
        with _req.urlopen(req, timeout=10) as resp:
            return resp.status in (200, 201)
    except Exception:
        log.exception("FCM v1 push failed for token %s", token[:12])
        return False


def send_desktop_notification(report: dict[str, Any]) -> None:
    env = _desktop_env()
    if env is None:
        log.warning("No DBUS session found, skipping desktop notification")
        return

    totals = report.get("notification_summary") or report["summary"]
    has_failures = totals["failed"] or totals["fix_failed"]
    has_changes = (
        totals.get("fixed")
        or totals.get("new_alerts")
        or totals.get("resolved_alerts")
        or totals.get("token_protection_stops")
    )
    if not has_failures and not has_changes:
        return

    if totals["fix_failed"]:
        urgency, icon = "critical", "dialog-error"
        title = f"RootCause · {totals['fix_failed']} fix FAILED"
    elif totals["failed"]:
        urgency, icon = "critical", "dialog-error"
        title = f"RootCause · {totals['failed']} FAILED"
    elif totals["fixed"]:
        urgency, icon = "normal", "dialog-warning"
        title = f"RootCause · {totals['fixed']} auto-fixed"
    elif totals["resolved_alerts"]:
        urgency, icon = "low", "dialog-information"
        title = f"RootCause · {totals['resolved_alerts']} resolved"
    else:
        urgency, icon = "low", "dialog-information"
        title = "RootCause update"

    body = (
        f"Passed {totals['passed']} · Failed {totals['failed']} · "
        f"Fixed {totals['fixed']} · Fix-failed {totals['fix_failed']}"
    )

    dunstify = shutil.which("dunstify")
    notify_send = shutil.which("notify-send")
    sync_hint = f"string:x-canonical-private-synchronous:{NOTIFICATION_SYNC_KEY}"

    try:
        if dunstify:
            replace_id = "0"
            if NOTIFICATION_ID_FILE.exists():
                replace_id = NOTIFICATION_ID_FILE.read_text().strip() or "0"
            args = [
                dunstify,
                "-a", "RootCause",
                "-u", urgency,
                "-i", icon,
                "-r", replace_id,
                "-h", sync_hint,
                "-h", "string:desktop-entry:RootCause",
                "--printid",
                title,
                body,
            ]
            result = subprocess.run(args, env=env, timeout=5, capture_output=True, text=True)
            new_id = (result.stdout or "").strip()
            if new_id.isdigit():
                NOTIFICATION_ID_FILE.write_text(new_id)
        elif notify_send:
            args = [
                notify_send,
                "-a", "RootCause",
                "-u", urgency,
                "-i", icon,
                "-h", sync_hint,
                title,
                body,
            ]
            subprocess.run(args, env=env, timeout=5, capture_output=True)
    except Exception as exc:
        log.warning("Failed to send desktop notification: %s", exc)


def send_notification(config: dict[str, Any], report: dict[str, Any]) -> None:
    notif = config.get("notifications", {})
    if not notif.get("enabled"):
        return

    summary = report.get("notification_summary") or report["summary"]
    if (
        not summary["fixed"]
        and not summary["fix_failed"]
        and not summary["new_alerts"]
        and not summary["resolved_alerts"]
        and not summary.get("token_protection_stops")
    ):
        return

    smtp_host = notif.get("smtp_host")
    smtp_port = notif.get("smtp_port", 587)
    smtp_user = notif.get("smtp_user")
    smtp_password = notif.get("smtp_password")
    email_to = notif.get("email_to")
    email_from = notif.get("email_from", smtp_user)
    placeholder_values = {"TU_EMAIL@gmail.com", "TU_APP_PASSWORD", "RootCause <TU_EMAIL@gmail.com>"}
    if smtp_user in placeholder_values or smtp_password in placeholder_values or email_from in placeholder_values:
        log.warning("SMTP placeholders detected, skipping email notification")
        return
    if not all([smtp_host, smtp_user, smtp_password, email_to]):
        log.warning("SMTP not fully configured, skipping email notification")
        return

    parts = [
        f"Timestamp: {report['timestamp']}",
        f"Passed: {summary['passed']}",
        f"Failed: {summary['failed']}",
        f"Fixed: {summary['fixed']}",
        f"Fix failed: {summary['fix_failed']}",
        f"New alerts: {summary['new_alerts']}",
        f"Resolved alerts: {summary['resolved_alerts']}",
        f"Token protection stops: {summary.get('token_protection_stops', 0)}",
        "",
    ]

    for item in report["checks"]:
        if item["result"] == "pass":
            continue
        if not item.get("notifications_enabled", True):
            continue
        parts.append(
            f"[{item['target']}] {item['name']} -> {item['result']} | "
            f"agent={item.get('agent_used') or 'none'} | detail={item['detail']}"
        )

    msg = MIMEText("\n".join(parts))
    msg["Subject"] = (
        "RootCause"
        f" | fixed={summary['fixed']}"
        f" failed={summary['failed']}"
        f" new_alerts={summary['new_alerts']}"
        f" token_stops={summary.get('token_protection_stops', 0)}"
    )
    msg["From"] = email_from
    msg["To"] = email_to

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [email_to], msg.as_string())
        log.info("Notification email sent to %s", email_to)
    except Exception as exc:
        log.error("Failed to send email notification: %s", exc)


def summarize_hosts(check_results: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for result in check_results:
        host_summary = summary.setdefault(
            result["target"],
            {"passed": 0, "failed": 0, "fixed": 0, "fix_failed": 0},
        )
        if result["result"] == "pass":
            host_summary["passed"] += 1
        else:
            host_summary["failed"] += 1
            if result["result"] == "fixed":
                host_summary["fixed"] += 1
            elif result["result"] == "fix_failed":
                host_summary["fix_failed"] += 1
    return summary


def result_success(result: str) -> bool:
    return result in {"pass", "fixed"}


def build_rule_catalog(config: dict[str, Any], rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    host_targets = {rule["name"]: [] for rule in rules}
    for rule in rules:
        host_targets.setdefault(rule["name"], []).append(rule["target"])

    catalog: list[dict[str, Any]] = []
    for rule in config.get("alert_rules", []):
        base = deepcopy(config.get("check_templates", {}).get(rule.get("template"), {}))
        base.update(deepcopy(rule))
        if not base.get("enabled", True):
            continue
        name = base.get("name", "unnamed")
        if base.get("command"):
            command_preview = base["command"]
        elif base.get("query"):
            command_preview = base["query"]
        elif base.get("url"):
            command_preview = base["url"]
        elif base.get("steps"):
            command_preview = " | ".join(
                step.get("command") or step.get("url") or step.get("type", "step")
                for step in base.get("steps", [])
            )
        else:
            command_preview = base.get("type", "check")
        catalog.append(
            {
                "name": name,
                "id": base.get("id"),
                "description": base.get("description", name),
                "command": command_preview,
                "type": base.get("type", "check"),
                "schedule": base.get("schedule", "Every 5 minutes"),
                "severity": base.get("severity", "info"),
                "timeout": base.get("timeout", 30),
                "notifications": base.get("notifications", True),
                "targets": host_targets.get(name, base.get("targets", [])),
                "template": base.get("template"),
                "url": base.get("url"),
                "query": base.get("query"),
                "expect_contains": base.get("expect_contains"),
                "expect_not_contains": base.get("expect_not_contains"),
                "threshold": base.get("threshold"),
                "threshold_query": base.get("threshold_query"),
                "comparator": base.get("comparator"),
                "accept_codes": base.get("accept_codes", []),
                "ignore_targets": base.get("ignore_targets", []),
                "expect_empty": base.get("expect_empty", False),
                "expect_nonempty": base.get("expect_nonempty", False),
                "parse_cert_days": base.get("parse_cert_days", False),
                "cert_warn_days": base.get("cert_warn_days"),
                "steps": base.get("steps", []),
                "fix_prompt": base.get("fix_prompt", ""),
                "allowed_agents": base.get("allowed_agents", []),
                "custom_agents": base.get("custom_agents", []),
                "emergency_actions": base.get("emergency_actions", []),
                "pause_schedule_on_fix_failed": bool(base.get("pause_schedule_on_fix_failed", True)),
                "enabled": bool(base.get("enabled", True)),
                "locked": bool(base.get("locked", False)),
                "token_protection": get_token_protection(base, config),
                "preview_command": base.get("preview_command", ""),
                "host_params": base.get("host_params", {}),
                "triggers": base.get("triggers"),
                "actions": base.get("actions", []),
                "auto_remediate": bool(base.get("auto_remediate", True)),
                "ping_targets": base.get("ping_targets", []),
            }
        )
    return catalog


def build_history_snapshot(history: dict[str, Any], checks: list[dict[str, Any]]) -> dict[str, Any]:
    keys = {item["alert_state"]["key"] for item in checks}
    recent_checks = [item for item in history.get("checks", []) if item.get("key") in keys]
    return {
        "runs": history.get("runs", []),
        "checks": recent_checks,
    }


def refresh_status_snapshot_config(config: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_config(config)
    rules = compile_rules(normalized)
    status_path = Path(normalized.get("ui", {}).get("status_file", str(STATUS_FILE)))
    report = load_json_file(status_path, default={}) if status_path.exists() else {}
    report["alert_rules"] = build_rule_catalog(normalized, rules)
    report["host_catalog"] = normalized.get("hosts", {})
    report["datasources"] = [sanitize_datasource(ds) for ds in get_datasources(normalized)]
    report["rules"] = [sanitize_rule(r) for r in normalized.get("rules", [])]
    report["integrations"] = {"jira": sanitize_jira(get_jira_config(normalized))}
    report["native_engine_enabled"] = normalized.get("native_engine", {}).get("enabled", True)
    report["maintenance_windows"] = list_maintenance_windows(normalized)
    report["config_updated_at"] = utc_iso()
    save_json_file(status_path, report)
    return report


def refresh_status_snapshot_state(config: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_config(config)
    status_path = Path(normalized.get("ui", {}).get("status_file", str(STATUS_FILE)))
    report = load_json_file(status_path, default={}) if status_path.exists() else {}
    checks = report.get("checks", [])
    for item in checks:
        key = str((item.get("alert_state") or {}).get("key") or "")
        if not key:
            continue
        state_entry = state.get("alerts", {}).get(key)
        if not state_entry:
            continue
        item.setdefault("alert_state", {})
        item["alert_state"]["acknowledged_at"] = state_entry.get("acknowledged_at")
        item["alert_state"]["acknowledged_by"] = state_entry.get("acknowledged_by", "")
        item["alert_state"]["silenced_until"] = state_entry.get("silenced_until")
        item["alert_state"]["silenced_reason"] = state_entry.get("silenced_reason", "")
        item["alert_state"]["schedule_paused"] = bool(state_entry.get("schedule_paused"))
        item["alert_state"]["schedule_paused_at"] = state_entry.get("schedule_paused_at")
        item["alert_state"]["schedule_pause_reason"] = state_entry.get("schedule_pause_reason", "")
        item["alert_state"]["last_rearmed_at"] = state_entry.get("last_rearmed_at")
        item["alert_state"]["pause_failure_detail"] = state_entry.get("pause_failure_detail", "")
        item["alert_state"]["pause_last_output"] = state_entry.get("pause_last_output", "")
        item["alert_state"]["pause_attempts"] = state_entry.get("pause_attempts", [])
        item["alert_state"]["pause_consecutive_failures"] = state_entry.get("pause_consecutive_failures", 0)
        item["alert_state"]["maintenance_active"] = bool(state_entry.get("maintenance_active"))
        item["alert_state"]["maintenance_window_id"] = state_entry.get("maintenance_window_id")
        item["alert_state"]["maintenance_reason"] = state_entry.get("maintenance_reason", "")
        item["alert_state"]["maintenance_until"] = state_entry.get("maintenance_until")
    report["mobile_alerts"] = build_mobile_alerts(report)
    report["problems"] = [p.to_dict() for p in ProblemStore(PROBLEMS_FILE).active_problems()]
    report["maintenance_windows"] = list_maintenance_windows(normalized)
    report["state_updated_at"] = utc_iso()
    save_json_file(status_path, report)
    return report


def get_token_protection(rule: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(config.get("token_protection", {}))
    merged.update(deepcopy(rule.get("token_protection", {})))
    return {
        "enabled": bool(merged.get("enabled", True)),
        "max_prompt_tokens": int(merged.get("max_prompt_tokens", 4000)),
        "max_response_tokens": int(merged.get("max_response_tokens", 4000)),
        "max_total_tokens_per_run": int(merged.get("max_total_tokens_per_run", 12000)),
        "notify_on_stop": bool(merged.get("notify_on_stop", True)),
    }


def delete_alert_from_config(config: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    target_id = str(payload.get("id") or "").strip()
    target_name = str(payload.get("name") or "").strip()
    if not target_id and not target_name:
        raise ValueError("alert id or name is required")

    rules = config.get("alert_rules", [])

    def matches(rule: dict[str, Any]) -> bool:
        rule_id = str(rule.get("id") or "").strip()
        rule_name = str(rule.get("name") or "").strip()
        # Match by id when both sides have one; otherwise fall back to name. This
        # covers imported/legacy rules saved with an empty id, where the UI sends
        # the name as the id.
        if target_id and rule_id and rule_id == target_id:
            return True
        if target_name and rule_name == target_name:
            return True
        if target_id and not rule_id and target_id == rule_name:
            return True
        return False

    matched = [rule for rule in rules if matches(rule)]
    if not matched:
        raise ValueError("alert not found")
    if any(rule.get("locked") for rule in matched):
        raise ValueError("check is locked; unlock it first to delete")
    config["alert_rules"] = [rule for rule in rules if not matches(rule)]
    return config


def rearm_alert_in_state(state: dict[str, Any], payload: dict[str, Any]) -> tuple[dict[str, Any], int]:
    target_id = str(payload.get("id") or "").strip()
    target_name = str(payload.get("name") or "").strip()
    if not target_id and not target_name:
        raise ValueError("alert id or name is required")

    touched = 0
    for key, entry in state.setdefault("alerts", {}).items():
        entry_id = str(entry.get("alert_id") or "").strip()
        entry_name = str(entry.get("alert_name") or "").strip()
        key_name = key.split(":", 1)[1] if ":" in key else key
        if target_id and entry_id != target_id:
            continue
        if not target_id and target_name not in {entry_name, key_name}:
            continue
        if entry.get("schedule_paused"):
            touched += 1
        entry["schedule_paused"] = False
        entry["schedule_paused_at"] = None
        entry["schedule_pause_reason"] = ""
        entry["last_rearmed_at"] = utc_iso()
        entry["pause_failure_detail"] = ""
        entry["pause_last_output"] = ""
        entry["pause_attempts"] = []
        entry["pause_consecutive_failures"] = 0
    if not touched:
        raise ValueError("alert is not paused")
    return state, touched


def _alert_matches_payload(entry: dict[str, Any], payload: dict[str, Any]) -> bool:
    target_id = str(payload.get("id") or payload.get("alert_id") or "").strip()
    target_name = str(payload.get("name") or payload.get("alert_name") or "").strip()
    target_host = str(payload.get("target") or "").strip()
    entry_id = str(entry.get("alert_id") or "").strip()
    entry_name = str(entry.get("alert_name") or "").strip()
    entry_target = str(entry.get("target") or "").strip()

    if target_id and entry_id != target_id:
        return False
    if not target_id and target_name and entry_name != target_name:
        return False
    if target_host and entry_target != target_host:
        return False
    return bool(target_id or target_name)


def acknowledge_alerts_in_state(state: dict[str, Any], payload: dict[str, Any], actor: str) -> int:
    touched = 0
    for entry in state.setdefault("alerts", {}).values():
        if not _alert_matches_payload(entry, payload):
            continue
        entry["acknowledged_at"] = utc_iso()
        entry["acknowledged_by"] = actor
        touched += 1
    if not touched:
        raise ValueError("alert not found")
    return touched


def silence_alerts_in_state(state: dict[str, Any], payload: dict[str, Any], actor: str) -> int:
    minutes = int(payload.get("minutes") or 60)
    if minutes < 1 or minutes > 24 * 60:
        raise ValueError("minutes must be between 1 and 1440")
    touched = 0
    until = (now_utc().timestamp() + minutes * 60)
    until_iso = datetime.fromtimestamp(until, tz=timezone.utc).isoformat()
    reason = str(payload.get("reason") or f"Silenced by {actor}").strip()
    for entry in state.setdefault("alerts", {}).values():
        if not _alert_matches_payload(entry, payload):
            continue
        entry["silenced_until"] = until_iso
        entry["silenced_reason"] = reason
        touched += 1
    if not touched:
        raise ValueError("alert not found")
    return touched


def build_mobile_alerts(report: dict[str, Any], allowed_targets: set[str] | None = None) -> list[dict[str, Any]]:
    catalog_by_name = {item.get("name"): item for item in report.get("alert_rules", [])}
    grouped: dict[str, dict[str, Any]] = {}
    for check in report.get("checks", []):
        name = str(check.get("name") or "")
        catalog = catalog_by_name.get(name, {})
        if not catalog.get("mobile_visible", True):
            continue
        target = str(check.get("target") or "")
        if allowed_targets is not None and target not in allowed_targets:
            continue
        alert_id = str(catalog.get("id") or name)
        entry = grouped.setdefault(
            alert_id,
            {
                "id": alert_id,
                "name": name,
                "status": "ok",
                "targets": [],
                "detail": "",
                "agent_used": None,
                "paused": False,
                "acknowledged_at": None,
                "acknowledged_by": "",
                "silenced_until": None,
                "silenced_reason": "",
            },
        )
        if target and target not in entry["targets"]:
            entry["targets"].append(target)
        alert_state = check.get("alert_state") or {}
        status = str(alert_state.get("status") or "ok")
        if alert_state.get("schedule_paused"):
            entry["status"] = "idle"
            entry["paused"] = True
        elif status in {"firing", "pending"}:
            entry["status"] = "failing"
        entry["detail"] = str(check.get("detail") or entry["detail"])
        entry["agent_used"] = check.get("agent_used") or entry["agent_used"]
        entry["acknowledged_at"] = alert_state.get("acknowledged_at") or entry["acknowledged_at"]
        entry["acknowledged_by"] = alert_state.get("acknowledged_by") or entry["acknowledged_by"]
        entry["silenced_until"] = alert_state.get("silenced_until") or entry["silenced_until"]
        entry["silenced_reason"] = alert_state.get("silenced_reason") or entry["silenced_reason"]
    return sorted(grouped.values(), key=lambda item: ({"failing": 0, "idle": 1, "ok": 2}.get(item["status"], 9), item["name"]))


def summarize_mobile_alerts(alerts: list[dict[str, Any]]) -> dict[str, int]:
    summary = {
        "passed": 0,
        "failed": 0,
        "fixed": 0,
        "fix_failed": 0,
        "new_alerts": 0,
        "resolved_alerts": 0,
        "paused": 0,
        "estimated_tokens": 0,
        "token_protection_stops": 0,
    }
    for item in alerts:
        status = str(item.get("status") or "ok")
        if status == "failing":
            summary["failed"] += 1
        else:
            summary["passed"] += 1
        if status == "idle":
            summary["paused"] += 1
    return summary


def is_mobile_alert_allowed(alert: dict[str, Any], api_key: dict[str, Any]) -> bool:
    allowed_targets = api_key_allowed_targets(api_key)
    if allowed_targets is None:
        return True
    targets = {str(item).strip() for item in alert.get("targets", []) if str(item).strip()}
    return bool(targets & allowed_targets)


def ensure_mobile_alert_allowed(report: dict[str, Any], api_key: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    alerts = build_mobile_alerts(report, allowed_targets=api_key_allowed_targets(api_key))
    target_id = str(payload.get("id") or payload.get("alert_id") or "").strip()
    target_name = str(payload.get("name") or payload.get("alert_name") or "").strip()
    for alert in alerts:
        alert_id = str(alert.get("id") or "").strip()
        alert_name = str(alert.get("name") or "").strip()
        if target_id and alert_id == target_id:
            return alert
        if not target_id and target_name and alert_name == target_name:
            return alert
    raise PermissionError("alert not allowed for this api key")


def alert_targets_in_report(report: dict[str, Any], alert_id: str = "", alert_name: str = "") -> set[str]:
    targets: set[str] = set()
    for alert in build_mobile_alerts(report):
        current_id = str(alert.get("id") or "").strip()
        current_name = str(alert.get("name") or "").strip()
        if alert_id and current_id != alert_id:
            continue
        if not alert_id and alert_name and current_name != alert_name:
            continue
        targets.update(str(item).strip() for item in alert.get("targets", []) if str(item).strip())
    return targets


def upsert_host_in_config(config: dict[str, Any], payload: dict[str, Any]) -> tuple[dict[str, Any], str]:
    name = str(payload.get("name") or "").strip()
    if not name:
        raise ValueError("host name is required")
    original = str(payload.get("original_name") or "").strip() or name

    existing = config.get("hosts", {}).get(original, {})
    host_entry: dict[str, Any] = deepcopy(existing)
    connection = str(payload.get("connection") or existing.get("connection") or "ssh").strip()

    if "address" in payload:
        address = str(payload.get("address") or "").strip()
        if not address and connection != "local":
            raise ValueError("host address is required")
        host_entry["address"] = address or existing.get("address") or "127.0.0.1"
    elif not existing:
        if connection != "local":
            raise ValueError("host address is required")
        host_entry["address"] = "127.0.0.1"

    if "connection" in payload:
        host_entry["connection"] = connection
    elif "connection" not in host_entry:
        host_entry["connection"] = "ssh"
    if "ssh_user" in payload:
        host_entry["ssh_user"] = str(payload.get("ssh_user") or os.environ.get("USER", "root")).strip()
    elif "ssh_user" not in host_entry:
        host_entry["ssh_user"] = os.environ.get("USER", "root")
    if "ssh_port" in payload:
        host_entry["ssh_port"] = int(payload.get("ssh_port") or 22)
    elif "ssh_port" not in host_entry:
        host_entry["ssh_port"] = 22
    if "enabled" in payload:
        host_entry["enabled"] = bool(payload.get("enabled", True))
    elif "enabled" not in host_entry:
        host_entry["enabled"] = True
    if "role" in payload:
        role = str(payload.get("role") or "").strip()
        host_entry["labels"] = {"role": role or existing.get("labels", {}).get("role") or "default"}
    elif "labels" not in host_entry:
        host_entry["labels"] = {"role": "default"}
    # Only overwrite optional fields that are actually present in the payload, so
    # partial forms (e.g. the focused Settings → Hosts editor) don't wipe values
    # the full Targets-tab editor set.
    for field in ("ssh_key_path", "workdir", "prometheus_url", "pushgateway_url", "alertmanager_url"):
        if field in payload:
            host_entry[field] = str(payload.get(field) or "").strip()
    for field in ("grafana_url", "alias", "prometheus_instance"):
        if field in payload:
            value = str(payload.get(field) or "").strip()
            if value:
                host_entry[field] = value
            else:
                host_entry.pop(field, None)

    hosts = config.setdefault("hosts", {})
    if original != name and original in hosts:
        del hosts[original]
        for rule in config.get("alert_rules", []):
            targets = rule.get("targets", [])
            rule["targets"] = [name if item == original else item for item in targets]
    hosts[name] = host_entry
    return config, name


def delete_host_from_config(config: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    name = str(payload.get("name") or "").strip()
    if not name:
        raise ValueError("host name is required")
    hosts = config.get("hosts", {})
    if name not in hosts:
        raise ValueError("host not found")
    del hosts[name]
    for rule in config.get("alert_rules", []):
        targets = rule.get("targets", [])
        rule["targets"] = [item for item in targets if item != name]
    return config


# Fields frozen on a locked check: its identity and shape. Everything else
# (thresholds, queries, schedule, severity, fix_prompt, toggles…) stays editable
# so the autosave keeps working for minor tuning. See _handle_alert_toggle_lock.
LOCKED_FROZEN_FIELDS = ("name", "type", "targets", "steps", "triggers", "actions")


def upsert_alert_config(config: dict[str, Any], payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    alert = payload.get("alert_rule")
    if not isinstance(alert, dict):
        raise ValueError("Missing alert_rule payload")

    name = str(alert.get("name", "")).strip()
    if not name:
        raise ValueError("Alert name is required")

    alert_id = str(alert.get("id") or "").strip()
    original_name = str(payload.get("original_name") or name).strip()
    original_id = str(payload.get("original_id") or alert_id or "").strip()
    allowed_agents = [str(item).strip() for item in alert.get("allowed_agents", []) if str(item).strip()]
    targets = [str(item).strip() for item in alert.get("targets", []) if str(item).strip()]
    if not targets:
        raise ValueError("At least one target is required")

    rule: dict[str, Any] = {
        "id": alert_id or original_id,
        "name": name,
        "description": str(alert.get("description") or name).strip(),
        "type": str(alert.get("type") or "ssh").strip(),
        "targets": targets,
        "fix_prompt": str(alert.get("fix_prompt") or "").strip(),
        "severity": str(alert.get("severity") or "info").strip(),
        "schedule": str(alert.get("schedule") or "Every 5 minutes").strip(),
        "timeout": int(alert.get("timeout") or 30),
        "notifications": bool(alert.get("notifications", True)),
        "mobile_visible": bool(alert.get("mobile_visible", True)),
        "mobile_notify": bool(alert.get("mobile_notify", alert.get("notifications", True))),
    }

    optional_scalar_fields = [
        "command",
        "preview_command",
        "url",
        "query",
        "threshold_query",
        "comparator",
        "preferred_model",
        "model_tip",
        "expect_contains",
        "expect_not_contains",
    ]
    for field in optional_scalar_fields:
        value = alert.get(field)
        if value not in (None, ""):
            rule[field] = value

    optional_bool_fields = ["expect_empty", "expect_nonempty", "parse_cert_days"]
    for field in optional_bool_fields:
        if field in alert:
            rule[field] = bool(alert.get(field))

    if alert.get("threshold") not in (None, ""):
        rule["threshold"] = float(alert["threshold"])
    if alert.get("cert_warn_days") not in (None, ""):
        rule["cert_warn_days"] = int(alert["cert_warn_days"])

    accept_codes = alert.get("accept_codes", [])
    if accept_codes:
        rule["accept_codes"] = [int(item) for item in accept_codes]

    ignore_targets = alert.get("ignore_targets", [])
    if ignore_targets:
        rule["ignore_targets"] = [str(item).strip() for item in ignore_targets if str(item).strip()]

    if allowed_agents:
        rule["allowed_agents"] = allowed_agents

    custom_agents = alert.get("custom_agents", [])
    if custom_agents:
        rule["custom_agents"] = custom_agents

    token_protection = alert.get("token_protection", {})
    if token_protection:
        rule["token_protection"] = {
            "enabled": bool(token_protection.get("enabled", True)),
            "max_prompt_tokens": int(token_protection.get("max_prompt_tokens", 4000)),
            "max_response_tokens": int(token_protection.get("max_response_tokens", 4000)),
            "max_total_tokens_per_run": int(token_protection.get("max_total_tokens_per_run", 12000)),
            "notify_on_stop": bool(token_protection.get("notify_on_stop", True)),
        }

    if "pause_schedule_on_fix_failed" in alert:
        rule["pause_schedule_on_fix_failed"] = bool(alert.get("pause_schedule_on_fix_failed"))

    am_url = str(alert.get("alertmanager_url") or "").strip()
    if am_url:
        rule["alertmanager_url"] = am_url
    am_filter = alert.get("alertmanager_filter")
    if isinstance(am_filter, dict) and am_filter:
        rule["alertmanager_filter"] = {k: str(v) for k, v in am_filter.items() if v}
    for field in ("filter_silenced", "filter_inhibited"):
        if field in alert:
            rule[field] = bool(alert.get(field))

    steps = alert.get("steps", [])
    if steps:
        rule["steps"] = steps

    emergency_actions = alert.get("emergency_actions", [])
    if emergency_actions:
        rule["emergency_actions"] = emergency_actions

    host_params = alert.get("host_params")
    if isinstance(host_params, dict) and host_params:
        validated: dict[str, Any] = {}
        for host_key, params in host_params.items():
            if isinstance(params, dict):
                validated[str(host_key)] = {str(k): str(v) for k, v in params.items()}
        if validated:
            rule["host_params"] = validated
    elif "host_params" in alert and not host_params:
        rule.pop("host_params", None)

    # New trigger/action model (chained, Alexa-routine style). Persisted as-is.
    triggers = alert.get("triggers")
    if isinstance(triggers, dict) and triggers.get("list"):
        match = str(triggers.get("match") or "any").lower()
        rule["triggers"] = {"match": "all" if match == "all" else "any", "list": list(triggers["list"])}
    elif isinstance(triggers, list) and triggers:
        rule["triggers"] = {"match": "any", "list": list(triggers)}

    actions = alert.get("actions")
    if isinstance(actions, list) and actions:
        rule["actions"] = actions

    if "auto_remediate" in alert:
        rule["auto_remediate"] = bool(alert.get("auto_remediate"))

    # network_ping passthrough fields (probe targets + stability thresholds).
    for field in (
        "ping_targets", "ping_count", "probe_timeout", "loss_threshold_pct",
        "latency_factor", "latency_floor_ms", "hop_delta", "baseline_alpha",
    ):
        if alert.get(field) not in (None, ""):
            rule[field] = alert.get(field)

    config.setdefault("alert_rules", [])
    existing_index = None
    for index, item in enumerate(config["alert_rules"]):
        if (original_id and item.get("id") == original_id) or item.get("name") == original_name:
            existing_index = index
            break

    locked_blocked: list[str] = []
    if existing_index is not None:
        existing = config["alert_rules"][existing_index]
        # `locked` is never settable through a normal save — it is preserved from
        # the stored rule and only flipped by _handle_alert_toggle_lock.
        if existing.get("locked"):
            rule["locked"] = True
            # Freeze identity/shape: drop incoming changes to structural fields,
            # report which were attempted so the UI can warn. Minor fields still save.
            for field in LOCKED_FROZEN_FIELDS:
                if rule.get(field) != existing.get(field):
                    locked_blocked.append(field)
                if field in existing:
                    rule[field] = existing[field]
                else:
                    rule.pop(field, None)
        config["alert_rules"][existing_index] = rule
    else:
        config["alert_rules"].append(rule)

    ensure_alert_ids(config)

    if "agents" in payload:
        incoming_agents = payload.get("agents", [])
        if not isinstance(incoming_agents, list):
            raise ValueError("agents must be a list")
        config["agents"] = incoming_agents

    return config, locked_blocked


def has_action_pipeline(rule: dict[str, Any]) -> bool:
    """True when a check defines an explicit, ordered actions[] chain.

    Checks without it keep the classic single-flow (AI remediation + emergency
    actions) so existing behaviour is byte-for-byte unchanged.
    """
    actions = rule.get("actions")
    return isinstance(actions, list) and len(actions) > 0


def send_action_email(config: dict[str, Any], subject: str, body: str, to: str | None = None) -> tuple[bool, str]:
    """Send a single email using the configured SMTP settings (reused by the
    notification/escalate actions). Mirrors the guards in send_notification.
    ``to`` overrides the default recipient (notifications.email_to)."""
    notif = config.get("notifications", {})
    if not notif.get("enabled"):
        return False, "notifications disabled"
    smtp_host = notif.get("smtp_host")
    smtp_port = notif.get("smtp_port", 587)
    smtp_user = notif.get("smtp_user")
    smtp_password = notif.get("smtp_password")
    email_to = (to or "").strip() or notif.get("email_to")
    email_from = notif.get("email_from", smtp_user)
    placeholders = {"TU_EMAIL@gmail.com", "TU_APP_PASSWORD", "RootCause <TU_EMAIL@gmail.com>"}
    if smtp_user in placeholders or smtp_password in placeholders or email_from in placeholders:
        return False, "SMTP placeholders configured"
    if not all([smtp_host, smtp_user, smtp_password, email_to]):
        return False, "SMTP not fully configured"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = email_to
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [email_to], msg.as_string())
        return True, f"email sent to {email_to}"
    except Exception as exc:
        return False, str(exc)


def _action_message(template: str | None, rule: dict[str, Any], result: dict[str, Any]) -> str:
    detail = str(result.get("detail") or "")
    base = template or "[{target}] {name} → {result} | {detail}"
    return (
        base.replace("{name}", str(rule.get("name", "")))
        .replace("{target}", str(rule.get("target", "")))
        .replace("{detail}", detail)
        .replace("{result}", str(result.get("result", "")))
    )


def _action_when_ok(when: Any, result: dict[str, Any], action_ctx: dict[str, Any]) -> bool:
    when = str(when or "on_alert").lower()
    if when in ("always", "on_alert", "on_fail", "on_failure"):
        return True
    if when in ("on_resolve", "recovered", "resolved", "fixed"):
        return not action_ctx.get("still_failing", True)
    if when in ("still_failing", "unresolved"):
        return bool(action_ctx.get("still_failing", True))
    if when == "no_internet":
        return not action_ctx.get("internet_ok", True)
    if when.startswith("after_failures"):
        try:
            need = int(when.split(":", 1)[1])
        except (IndexError, ValueError):
            need = 1
        have = int((result.get("alert_state") or {}).get("consecutive_failures", 0) or 0)
        return have >= need
    return True


_SERVICE_VERBS = {"start", "stop", "restart", "reload", "status"}


def _exec_bash_action(rule: dict[str, Any], result: dict[str, Any], ctx: dict[str, Any], action: dict[str, Any]) -> bool:
    config = ctx["config"]
    command = str(action.get("command") or "").strip()
    entry: dict[str, Any] = {"type": action.get("type", "bash"), "name": action.get("name") or command[:60], "command": command[:200]}
    if not command:
        entry.update(success=False, output="empty command")
        result.setdefault("actions_log", []).append(entry)
        return False
    allowed, why = validate_command_safety(command, config)
    if not allowed:
        entry.update(success=False, output=f"blocked by safety layer: {why}")
        result.setdefault("actions_log", []).append(entry)
        log.error("  action bash blocked: %s", why)
        return False
    host_name = action.get("target") or rule["target"]
    run_local_flag = str(action.get("run_on", "")).lower() == "local" or host_name == "localhost"
    if run_local_flag:
        ok, output = run_local(command, timeout=action.get("timeout", 60), cwd=action.get("cwd") or None)
    else:
        host = config["hosts"].get(host_name, rule["host"])
        ok, output = run_host_command(host, command, timeout=action.get("timeout", 60))
    entry.update(success=ok, output=output[:500])
    result.setdefault("actions_log", []).append(entry)
    # Surface in the existing emergency_actions UI list too.
    result.setdefault("emergency_actions", []).append(
        {"name": entry["name"], "reason": "action", "success": ok, "output": output[:500]}
    )
    log.log(logging.INFO if ok else logging.ERROR, "  action %s: %s", entry["name"], output[:300])
    return ok


def _exec_service_action(rule: dict[str, Any], result: dict[str, Any], ctx: dict[str, Any], action: dict[str, Any], kind: str) -> bool:
    verb = str(action.get("action") or "restart").lower()
    if verb not in _SERVICE_VERBS:
        result.setdefault("actions_log", []).append({"type": kind, "success": False, "output": f"verb '{verb}' not allowed"})
        return False
    if kind == "docker":
        name = str(action.get("name") or "")
        command = f"docker {verb} {shlex.quote(name)}"
    else:
        unit = str(action.get("unit") or "")
        scope = "--user " if str(action.get("scope", "system")).lower() == "user" else ""
        command = f"systemctl {scope}{verb} {shlex.quote(unit)}"
    return _exec_bash_action(rule, result, ctx, {**action, "type": kind, "command": command, "name": action.get("name") or command})


def run_actions(rule: dict[str, Any], detail: Any, result: dict[str, Any], ctx: dict[str, Any]) -> str | None:
    """Execute a check's ordered actions[] chain, Alexa-routine style.

    Runs only for failing checks (we are in the failure branch). Supports
    notification / ai_agent / bash / docker / systemd / http / wait / recheck /
    silence / escalate / noop, each gated by an optional ``when`` condition and a
    ``continue_on_error`` flag. The ai_agent action reuses the exact same engine
    as legacy checks via attempt_agent_remediation.
    """
    config = ctx["config"]
    # A manual rerun / preview (remediation disabled) records the failure without
    # firing side-effectful actions, mirroring the legacy no-remediation path.
    if not ctx.get("remediation_enabled", True):
        result.setdefault("token_usage", {
            "enabled": False, "prompt_tokens": 0, "response_tokens": 0,
            "total_tokens": 0, "stopped": False, "reason": "",
        })
        return "early"
    action_ctx = {"still_failing": True, "internet_ok": ctx.get("internet_ok", True)}
    for action in rule.get("actions") or []:
        atype = str(action.get("type") or "").lower()
        if not _action_when_ok(action.get("when"), result, action_ctx):
            result.setdefault("actions_log", []).append({"type": atype, "skipped": str(action.get("when") or "on_alert")})
            continue
        try:
            if atype == "ai_agent":
                overlay_keys = (
                    "allowed_agents", "custom_agents", "fix_prompt", "preferred_model",
                    "token_protection", "ai_pipeline", "emergency_actions",
                    "agent_cooldown_minutes", "pause_schedule_on_fix_failed",
                )
                overlay = {k: action[k] for k in overlay_keys if k in action}
                rrule = {**rule, **overlay} if overlay else rule
                attempt_agent_remediation(rrule, detail, result, ctx, force=True)
                action_ctx["still_failing"] = result.get("result") not in ("fixed", "pass")
            elif atype == "notification":
                channels = action.get("channels") or ["email"]
                message = _action_message(action.get("message"), rule, result)
                entry: dict[str, Any] = {"type": "notification", "channels": channels}
                if "email" in channels:
                    subj = action.get("subject") or f"RootCause: {rule['name']} on {rule['target']}"
                    ok, info = send_action_email(config, subj, message, to=action.get("to"))
                    entry["email"] = info
                    entry["success"] = ok
                if "push" in channels:
                    entry["push"] = "queued (push provider disabled)"
                result["notifications_enabled"] = True
                result.setdefault("actions_log", []).append(entry)
            elif atype == "jira":
                # Create-or-reuse the Jira ticket for this problem, then add a
                # comment noting this firing/remediation outcome.
                entry = {"type": "jira"}
                problem = rule.get("_problem") or {}
                if not jira_enabled(config):
                    entry.update(success=False, output="Jira not configured (Settings ▸ Webhooks ▸ Jira)")
                elif not problem:
                    entry.update(success=False, output="no problem context (Jira action only runs on problem-matched rules)")
                else:
                    key, msg = jira_ensure_issue_for_problem(config, problem)
                    if key:
                        note = _action_message(action.get("message"), rule, result) or f"RootCause: {rule.get('name')} fired on {rule.get('target')}."
                        jira_add_comment(get_jira_config(config), key, note, by="RootCause")
                        entry.update(success=True, output=f"{msg}", issue_key=key)
                        result["jira_issue_key"] = key
                    else:
                        entry.update(success=False, output=msg)
                result.setdefault("actions_log", []).append(entry)
            elif atype == "bash":
                if _exec_bash_action(rule, result, ctx, action) and action.get("marks_fixed"):
                    result["result"] = "fixed"
            elif atype in ("docker", "systemd"):
                if _exec_service_action(rule, result, ctx, action, atype) and action.get("marks_fixed"):
                    result["result"] = "fixed"
            elif atype in ("http", "webhook"):
                url = str(action.get("url") or "")
                method = str(action.get("method") or "POST").upper()
                body = action.get("body")
                headers = dict(action.get("headers") or {})
                entry = {"type": "http", "method": method, "url": url[:200]}
                try:
                    if isinstance(body, (dict, list)):
                        headers.setdefault("Content-Type", "application/json")
                        data = json.dumps(body)
                    else:
                        data = None if body is None else str(body)
                    resp = requests.request(method, url, data=data, headers=headers, timeout=action.get("timeout", 10))
                    entry.update(success=resp.status_code < 400, status=resp.status_code, output=resp.text[:200])
                except Exception as exc:
                    entry.update(success=False, output=str(exc))
                result.setdefault("actions_log", []).append(entry)
            elif atype == "wait":
                secs = min(max(float(action.get("seconds", 5) or 0), 0.0), 120.0)
                time.sleep(secs)
                result.setdefault("actions_log", []).append({"type": "wait", "seconds": secs})
            elif atype == "recheck":
                ok, det = evaluate_triggers(rule)
                rule.pop("_last_run_output", None)
                action_ctx["still_failing"] = not ok
                if ok and result.get("result") != "fixed":
                    result["result"] = "fixed"
                result.setdefault("actions_log", []).append({"type": "recheck", "passed": ok, "detail": str(det)[:200]})
            elif atype == "silence":
                minutes = int(action.get("minutes", 30) or 30)
                state = ctx["state"]
                entry_state = state.setdefault("alerts", {}).setdefault(rule["instance_key"], default_alert_state_entry(rule))
                until = (ctx["now"] + timedelta(minutes=max(1, minutes))).isoformat()
                entry_state["silenced_until"] = until
                entry_state["silenced_reason"] = action.get("reason") or "auto-silenced by action"
                result.setdefault("alert_state", {})["silenced_until"] = until
                result["alert_state"]["silenced_reason"] = entry_state["silenced_reason"]
                result.setdefault("actions_log", []).append({"type": "silence", "until": until, "minutes": minutes})
            elif atype == "escalate":
                after = int(action.get("after_failures", 3) or 3)
                have = int((result.get("alert_state") or {}).get("consecutive_failures", 0) or 0)
                log_entry: dict[str, Any] = {"type": "escalate", "after_failures": after, "consecutive_failures": have, "escalated": have >= after}
                if have >= after:
                    if action.get("severity"):
                        result["severity"] = action["severity"]
                    subj = f"[ESCALADO] {rule['name']} on {rule['target']}"
                    msg = _action_message(action.get("message") or "Escalado tras {result}: {detail}", rule, result)
                    ok, info = send_action_email(config, subj, msg)
                    log_entry["email"] = info
                result.setdefault("actions_log", []).append(log_entry)
            elif atype in ("noop", "do_nothing", "record"):
                result.setdefault("actions_log", []).append({"type": "noop", "note": action.get("note", "")})
            else:
                result.setdefault("actions_log", []).append({"type": atype, "error": "unknown action type"})
        except Exception as exc:
            log.error("  action %s raised: %s", atype, exc)
            result.setdefault("actions_log", []).append({"type": atype, "error": str(exc)})
            if not action.get("continue_on_error", True):
                break

    result.setdefault("token_usage", {
        "enabled": False, "prompt_tokens": 0, "response_tokens": 0,
        "total_tokens": 0, "stopped": False, "reason": "",
    })
    return None


def attempt_agent_remediation(
    rule: dict[str, Any],
    detail: Any,
    result: dict[str, Any],
    ctx: dict[str, Any],
    *,
    force: bool = False,
) -> str | None:
    """AI-agent remediation + emergency fallback + post-fix validation.

    Extracted verbatim from run_checks so the SAME pipeline backs both legacy
    checks and the `ai_agent` action in the actions[] chain. Mutates ``result``
    and shared run state carried in ``ctx``. Returns "early" when the failure was
    recorded without remediation (caller appends the result and skips narrative).
    """
    config = ctx["config"]
    state = ctx["state"]
    now = ctx["now"]
    internet_ok = ctx["internet_ok"]
    selected_agents = ctx["selected_agents"]
    custom_status_cache = ctx["custom_status_cache"]
    probed_status_cache = ctx["probed_status_cache"]
    probe_prompt = ctx["probe_prompt"]
    probe_cache_ttl = ctx["probe_cache_ttl"]
    agent_stats = ctx["agent_stats"]
    summary = ctx["summary"]
    remediation_enabled = ctx.get("remediation_enabled", True)
    name = rule["name"]
    target = rule["target"]
    token_guard = get_token_protection(rule, config)
    token_usage = {
        "enabled": token_guard["enabled"],
        "prompt_tokens": 0,
        "response_tokens": 0,
        "total_tokens": 0,
        "stopped": False,
        "reason": "",
    }
    if not force and (not remediation_enabled or not rule.get("auto_remediate", True)):
        result["token_usage"] = token_usage
        summary["estimated_tokens"] += 0
        if not remediation_enabled:
            log.info("  Manual rerun recorded failure for %s on %s without remediation", name, target)
        else:
            log.info("  %s on %s failed; auto_remediate disabled — alert only, no AI", name, target)
        return "early"

    prompt = format_fix_prompt(rule, detail, config)
    token_usage["prompt_tokens"] = estimate_tokens(prompt)

    allowed_agent_names = {str(item).strip() for item in rule.get("allowed_agents", []) if str(item).strip()}
    custom_agents = rule.get("custom_agents", [])
    custom_agent_statuses: list[tuple[dict[str, Any], AgentStatus]] = []
    for agent in custom_agents:
        cache_key = _probe_cache_key(agent)
        if cache_key not in custom_status_cache:
            custom_status_cache[cache_key] = get_agent_status(
                agent, probe_prompt, probe=False, probe_cache_ttl=probe_cache_ttl
            )
        custom_agent_statuses.append((agent, custom_status_cache[cache_key]))
    usable_agents = [
        item
        for item in (selected_agents + custom_agent_statuses)
        if item[1].available and (not allowed_agent_names or item[1].name in allowed_agent_names)
    ]
    preferred_model = rule.get("preferred_model")
    if preferred_model:
        usable_agents = [
            ({**agent, "model": preferred_model} if agent.get("type") == "claude" else agent, status)
            for agent, status in usable_agents
        ]
    failure_reason = None
    if not usable_agents:
        failure_reason = "no_agent"
    elif not internet_ok:
        failure_reason = "no_internet"
    elif token_guard["enabled"] and token_usage["prompt_tokens"] > token_guard["max_prompt_tokens"]:
        failure_reason = "token_budget_exceeded"
        token_usage["stopped"] = True
        token_usage["reason"] = "prompt budget exceeded"
        summary["token_protection_stops"] += 1

    if not failure_reason:
        cooldown_minutes = get_agent_cooldown_minutes(rule, config)
        state_alert_entry = state.get("alerts", {}).get(rule["instance_key"], {})
        last_agent_ts = parse_iso_datetime(state_alert_entry.get("last_agent_called_at"))
        if last_agent_ts:
            elapsed_min = (now - last_agent_ts).total_seconds() / 60
            if elapsed_min < cooldown_minutes:
                log.info(
                    "  Agent cooldown active for %s on %s: last called %.0f min ago (cooldown: %d min)",
                    name, target, elapsed_min, cooldown_minutes,
                )
                record_agent_call(
                    rule.get("id", ""), name, target,
                    "", "", None,
                    token_usage["prompt_tokens"], 0, 0,
                    0.0, False, "Agent cooldown active — skipped",
                    cooldown_skipped=True,
                )
                failure_reason = "agent_cooldown"

    if not failure_reason and usable_agents:
        # Lazy probe (cached with TTL): verify agents respond before paying
        # for a remediation attempt. Runs once per agent per run at most.
        probed_usable: list[tuple[dict[str, Any], AgentStatus]] = []
        for agent, status in usable_agents:
            cache_key = _probe_cache_key(agent)
            if cache_key not in probed_status_cache:
                probed_status_cache[cache_key] = probe_agent_status(agent, status, probe_prompt, probe_cache_ttl)
            probed = probed_status_cache[cache_key]
            if probed.available:
                probed_usable.append((agent, probed))
            else:
                log.warning("  Agent %s skipped: %s", probed.name, probed.reason)
        usable_agents = probed_usable
        if not usable_agents:
            failure_reason = "no_agent"

    # ── AI Pipeline: optional analysis pass before fix ──────────────────
    pipeline_cfg = get_ai_pipeline_config(config, rule)
    analysis_data: dict[str, Any] | None = None
    if not failure_reason and is_pipeline_enabled(config, rule) and usable_agents:
        analysis_agent_tuple = _get_pipeline_agent(pipeline_cfg, "analysis", usable_agents, config)
        if analysis_agent_tuple:
            analysis_agent, analysis_status = analysis_agent_tuple
            # Key includes a hash of the failure detail so a stale analysis
            # is not reused when the symptom changes.
            detail_hash = hashlib.sha1(str(detail).encode("utf-8")).hexdigest()[:8]
            rule_key = (rule.get("id") or f"{name}:{target}") + f":{detail_hash}"
            cooldown_secs = get_agent_cooldown_minutes(rule, config) * 60
            cached = get_cached_analysis(rule_key, cooldown_secs)
            if cached:
                log.info("  [pipeline] Using cached analysis (within cooldown window)")
                analysis_data = cached
                result["agent_attempts"].append({
                    "agent": analysis_status.name,
                    "stage": "analysis",
                    "model": analysis_agent.get("model"),
                    "success": True,
                    "output": "(cached)",
                    "analysis": analysis_data,
                    "estimated_tokens": 0,
                })
            else:
                analysis_prompt = build_analysis_prompt(rule, detail, config)
                a_prompt_tokens = estimate_tokens(analysis_prompt)
                log.info(
                    "  [pipeline] Analysis pass — agent=%s model=%s",
                    analysis_status.name, analysis_agent.get("model"),
                )
                t_a = time.time()
                _, analysis_output = invoke_agent(
                    analysis_agent, analysis_prompt, read_only=True, config=config
                )
                a_duration = time.time() - t_a
                a_response_tokens = estimate_tokens(analysis_output)
                token_usage["total_tokens"] += a_prompt_tokens + a_response_tokens

                record_agent_call(
                    rule.get("id", ""), name, target,
                    analysis_status.name, analysis_agent.get("type", analysis_status.name),
                    analysis_agent.get("model"),
                    a_prompt_tokens, a_response_tokens, a_prompt_tokens + a_response_tokens,
                    a_duration, True, analysis_output[:500],
                    stage="analysis",
                )
                analysis_data = parse_analysis_output(analysis_output)
                if analysis_data:
                    cache_analysis(rule_key, analysis_data)
                result["agent_attempts"].append({
                    "agent": analysis_status.name,
                    "stage": "analysis",
                    "model": analysis_agent.get("model"),
                    "success": analysis_data is not None,
                    "output": analysis_output[:500],
                    "analysis": analysis_data,
                    "estimated_tokens": a_prompt_tokens + a_response_tokens,
                })

            if analysis_data:
                log.info(
                    "  [pipeline] root_cause=%s confidence=%s risk=%s needs_human=%s",
                    str(analysis_data.get("root_cause", "?"))[:80],
                    analysis_data.get("confidence"),
                    analysis_data.get("risk"),
                    analysis_data.get("needs_human"),
                )
                if analysis_data.get("needs_human") or (
                    analysis_data.get("confidence") == "low"
                    and analysis_data.get("risk") == "high"
                ):
                    log.info("  [pipeline] Skipping fix pass — needs_human or high-risk/low-confidence")
                    failure_reason = "needs_human"
                else:
                    # Replace fix prompt with shorter pipeline prompt and use fix model
                    prompt = build_fix_prompt_from_analysis(rule, analysis_data, config)
                    token_usage["prompt_tokens"] = estimate_tokens(prompt)
                    fix_agent_tuple = _get_pipeline_agent(pipeline_cfg, "fix", usable_agents, config)
                    if fix_agent_tuple:
                        usable_agents = [fix_agent_tuple]
            else:
                log.warning("  [pipeline] Could not parse analysis JSON; using standard fix pass")
    # ───────────────────────────────────────────────────────────────────

    if not failure_reason:
        for agent, status in usable_agents:
            if token_guard["enabled"] and (
                token_usage["total_tokens"] + token_usage["prompt_tokens"] > token_guard["max_total_tokens_per_run"]
            ):
                failure_reason = "token_budget_exceeded"
                token_usage["stopped"] = True
                token_usage["reason"] = "total token budget exceeded before invocation"
                summary["token_protection_stops"] += 1
                break

            state_alert_live = state.get("alerts", {}).get(rule["instance_key"])
            if state_alert_live is not None:
                state_alert_live["last_agent_called_at"] = now.isoformat()
            agent_stats["invocations"] += 1
            t_agent_start = time.time()
            ok, output = invoke_agent(agent, prompt, config=config)
            agent_duration = time.time() - t_agent_start
            output_tokens = estimate_tokens(output)
            token_usage["response_tokens"] += output_tokens
            token_usage["total_tokens"] += token_usage["prompt_tokens"] + output_tokens

            if token_guard["enabled"] and output_tokens > token_guard["max_response_tokens"]:
                ok = False
                output = f"Token protection stopped response from {status.name}: response budget exceeded"
                token_usage["stopped"] = True
                token_usage["reason"] = "response budget exceeded"
                failure_reason = "token_budget_exceeded"
                summary["token_protection_stops"] += 1

            record_agent_call(
                rule.get("id", ""), name, target,
                status.name, agent.get("type", status.name), agent.get("model"),
                token_usage["prompt_tokens"], output_tokens,
                token_usage["prompt_tokens"] + output_tokens,
                agent_duration, ok, output[:500],
                stage="fix",
            )
            attempt = {
                "agent": status.name,
                "stage": "fix",
                "model": agent.get("model"),
                "success": ok,
                "output": output[:500],
                "estimated_tokens": token_usage["prompt_tokens"] + output_tokens,
            }
            result["agent_attempts"].append(attempt)
            if ok:
                result["result"] = "fixed"
                result["agent_used"] = status.name
                result["detail"] = output[:500] or result["detail"]
                summary["fixed"] += 1
                agent_stats["successes"] += 1
                log.info("  Fixed by %s: %s on %s", status.name, name, target)
                break
            agent_stats["failures"] += 1
            log.error("  %s failed for %s on %s: %s", status.name, name, target, output[:300])
            if failure_reason == "token_budget_exceeded":
                break
            if not config.get("ai_routing", {}).get("fallback_to_next_agent", True):
                break

        if result["result"] != "fixed":
            failure_reason = failure_reason or "agent_failure"

    if failure_reason:
        result["token_usage"] = token_usage
        result["emergency_actions"] = run_emergency_actions(rule, failure_reason, config["hosts"], config)
        agent_stats["emergency_runs"] += len(result["emergency_actions"])
        successful_emergency = any(action["success"] for action in result["emergency_actions"])
        if successful_emergency:
            result["result"] = "fixed"
            summary["fixed"] += 1
            log.info("  Emergency remediation applied for %s on %s", name, target)
        else:
            result["result"] = "fix_failed"
            summary["fix_failed"] += 1
    elif result["result"] != "fixed":
        result["result"] = "fix_failed"
        summary["fix_failed"] += 1

    if result["result"] == "fixed":
        validated_ok, validated_detail = evaluate_triggers(rule)
        result["alert_state"] = finalize_alert_state_after_remediation(
            state,
            rule,
            validated_ok,
            validated_detail,
            config,
        )
        if validated_ok:
            log.info("  Post-remediation validation passed for %s on %s", name, target)
        else:
            result["result"] = "fix_failed"
            result["detail"] = str(validated_detail)
            summary["fixed"] -= 1
            summary["fix_failed"] += 1
            log.warning("  Post-remediation validation failed for %s on %s - %s", name, target, validated_detail)

    if result["result"] == "fix_failed" and should_pause_on_unresolved(config, rule):
        last_output = ""
        if result.get("agent_attempts"):
            last_output = (result["agent_attempts"][-1].get("output") or "").strip()
        if last_output:
            pause_reason = f"Auto-paused: remediation failed. Diagnóstico: {last_output[:400]}"
        else:
            pause_reason = "Auto-paused after unresolved remediation failure"
        attempts_summary = [
            {
                "agent": a.get("agent"),
                "stage": a.get("stage"),
                "success": bool(a.get("success")),
                "output": (a.get("output") or "")[:800],
                "estimated_tokens": a.get("estimated_tokens"),
            }
            for a in result.get("agent_attempts", [])
        ]
        failure_context = {
            "failure_detail": str(result.get("detail") or ""),
            "last_output": last_output,
            "attempts": attempts_summary,
            "consecutive_failures": result.get("alert_state", {}).get("consecutive_failures"),
            "paused_run_at": utc_iso(),
        }
        paused_entry = set_alert_schedule_paused(
            state,
            rule,
            True,
            reason=pause_reason,
            failure_context=failure_context,
        )
        result["schedule_paused"] = True
        result["alert_state"]["schedule_paused"] = True
        result["alert_state"]["schedule_paused_at"] = paused_entry.get("schedule_paused_at")
        result["alert_state"]["schedule_pause_reason"] = paused_entry.get("schedule_pause_reason", "")
        result["alert_state"]["last_rearmed_at"] = paused_entry.get("last_rearmed_at")
        result["alert_state"]["pause_failure_detail"] = paused_entry.get("pause_failure_detail", "")
        result["alert_state"]["pause_last_output"] = paused_entry.get("pause_last_output", "")
        result["alert_state"]["pause_attempts"] = paused_entry.get("pause_attempts", [])
        result["alert_state"]["pause_consecutive_failures"] = paused_entry.get("pause_consecutive_failures", 0)
        summary["paused"] += 1

    result.setdefault("token_usage", token_usage)
    summary["estimated_tokens"] += int((result.get("token_usage") or {}).get("total_tokens", 0))
    return None



def run_checks(
    config: dict[str, Any],
    force_alert_names: set[str] | None = None,
    remediation_enabled: bool = True,
    emit_notifications: bool = True,
) -> dict[str, Any]:
    state = load_state()
    history = load_history()
    rules = compile_rules(config)
    status_path = Path(config.get("ui", {}).get("status_file", str(STATUS_FILE)))
    previous_status = load_json_file(status_path, default={}) if status_path.exists() else {}
    previous_checks_by_key: dict[str, dict[str, Any]] = {
        item.get("alert_state", {}).get("key"): item
        for item in previous_status.get("checks", [])
        if item.get("alert_state", {}).get("key")
    }
    is_first_run = not previous_checks_by_key
    now = now_utc()
    due_rules: list[dict[str, Any]] = []
    paused_rules: list[tuple[dict[str, Any], dict[str, Any] | None, dict[str, Any]]] = []
    skipped_rules: list[tuple[dict[str, Any], dict[str, Any] | None]] = []
    force_alert_names = {str(item).strip() for item in (force_alert_names or set()) if str(item).strip()}
    # Phase 3: when the native engine is disabled, RootCause stops evaluating its
    # own checks and acts purely as a problem orchestrator (connector sync +
    # matchers below). The compiled rules still feed the UI catalog and the
    # problem_match matchers, so nothing else changes.
    native_enabled = config.get("native_engine", {}).get("enabled", True)
    if native_enabled:
        for rule in rules:
            schedule = normalize_schedule(rule.get("schedule"))
            rule["schedule_normalized"] = schedule
            prior = previous_checks_by_key.get(rule["instance_key"])
            state_entry = state.get("alerts", {}).get(rule["instance_key"], {})
            if force_alert_names and (rule.get("name") in force_alert_names or rule.get("id") in force_alert_names):
                due_rules.append(rule)
            elif state_entry.get("schedule_paused"):
                paused_rules.append((rule, prior, state_entry))
            elif is_first_run or cron_due(schedule, now) or prior is None:
                due_rules.append(rule)
            else:
                skipped_rules.append((rule, prior))

    # probe=False: cheap availability checks only (which/auth). The expensive
    # live-invocation probe runs lazily (and cached) when an agent is about to
    # be used for remediation, so healthy runs spend zero AI tokens on probes.
    selected_agents = select_agents(config, probe=False) if due_rules else []
    probe_cache_ttl = get_probe_cache_ttl(config)
    probe_prompt = config.get("ai_routing", {}).get("probe_prompt", "Return exactly OK")
    custom_status_cache: dict[str, AgentStatus] = {}
    probed_status_cache: dict[str, AgentStatus] = {}

    log.info("=" * 60)
    log.info(
        "RootCause check run started - %d due / %d paused / %d skipped (cached)",
        len(due_rules),
        len(paused_rules),
        len(skipped_rules),
    )
    for _, status in selected_agents:
        log.info(
            "Agent %s -> enabled=%s available=%s quota=%s reason=%s",
            status.name,
            status.enabled,
            status.available,
            status.quota_score if status.quota_score is not None else "n/a",
            status.reason,
        )
    log.info("=" * 60)

    internet_ok, internet_detail = check_internet(config)
    log.info("Internet availability: %s (%s)", internet_ok, internet_detail)

    start = time.time()
    results: list[dict[str, Any]] = []
    agent_stats = {"invocations": 0, "successes": 0, "failures": 0, "emergency_runs": 0}
    summary = {
        "passed": 0,
        "failed": 0,
        "fixed": 0,
        "fix_failed": 0,
        "paused": 0,
        "new_alerts": 0,
        "resolved_alerts": 0,
        "token_protection_stops": 0,
        "estimated_tokens": 0,
    }
    notification_summary = deepcopy(summary)

    for rule in due_rules:
        name = rule["name"]
        target = rule["target"]
        log.info("--- Checking: %s on %s (%s)", name, target, rule["description"])

        rule["_config"] = config
        passed, detail = evaluate_triggers(rule)
        last_run_output = rule.pop("_last_run_output", "")
        alert_state = update_alert_state(state, rule, passed, detail, config)

        result = {
            "name": name,
            "target": target,
            "description": rule["description"],
            "detail": str(detail),
            "last_run_output": last_run_output,
            "result": "pass" if passed else "failed",
            "agent_used": None,
            "agent_attempts": [],
            "emergency_actions": [],
            "alert_state": alert_state,
            "notifications_enabled": bool(rule.get("notifications", True)) and not bool(alert_state.get("maintenance_active")),
        }

        if passed:
            summary["passed"] += 1
            if alert_state["resolved"]:
                summary["resolved_alerts"] += 1
            result["human_state"] = "resolved_auto" if alert_state.get("resolved") else "ok"
            result["narrative"] = {"what_happened": "", "what_rootcause_did": "", "what_you_should_do": ""}
            results.append(result)
            log.info("  PASS: %s on %s", name, target)
            continue

        summary["failed"] += 1
        if alert_state["should_notify"]:
            summary["new_alerts"] += 1

        log.warning("  FAIL: %s on %s - %s", name, target, detail)
        ctx = {
            "config": config,
            "state": state,
            "now": now,
            "internet_ok": internet_ok,
            "selected_agents": selected_agents,
            "custom_status_cache": custom_status_cache,
            "probed_status_cache": probed_status_cache,
            "probe_prompt": probe_prompt,
            "probe_cache_ttl": probe_cache_ttl,
            "agent_stats": agent_stats,
            "summary": summary,
            "remediation_enabled": remediation_enabled,
        }
        if has_action_pipeline(rule):
            remediation_outcome = run_actions(rule, detail, result, ctx)
        else:
            remediation_outcome = attempt_agent_remediation(rule, detail, result, ctx)
        if remediation_outcome == "early":
            results.append(result)
            continue

        # ── Populate human_state narrative for UI feedback (Phase 2) ────────
        human_state = derive_human_state(result)
        result["human_state"] = human_state
        fix_attempt = next(
            (a for a in reversed(result.get("agent_attempts", [])) if a.get("stage") in (None, "fix")),
            None,
        )
        analysis_attempt = next(
            (a for a in result.get("agent_attempts", []) if a.get("stage") == "analysis"),
            None,
        )
        what_happened = result.get("detail", "")[:300]
        what_rootcause_did = ""
        what_you_should_do = ""
        if analysis_attempt and analysis_attempt.get("analysis"):
            ad = analysis_attempt["analysis"]
            what_rootcause_did = f"Análisis: {ad.get('root_cause','?')}"
            if ad.get("needs_human"):
                what_you_should_do = ad.get("human_action") or "Acción manual requerida."
        if fix_attempt:
            action_verb = "Arregló" if fix_attempt.get("success") else "Intentó arreglar"
            agent_name_str = fix_attempt.get("agent", "agente")
            what_rootcause_did = (
                f"{what_rootcause_did + '. ' if what_rootcause_did else ''}"
                f"{action_verb} via {agent_name_str}: {fix_attempt.get('output','')[:200]}"
            )
        if human_state == "needs_you" and not what_you_should_do:
            if result.get("alert_state", {}).get("schedule_paused"):
                what_you_should_do = "Revisa el diagnóstico y rearma el check cuando esté resuelto."
            else:
                what_you_should_do = "Investiga el error y ejecuta remediation manual si es necesario."
        result["narrative"] = {
            "what_happened": what_happened,
            "what_rootcause_did": what_rootcause_did,
            "what_you_should_do": what_you_should_do,
        }
        # ────────────────────────────────────────────────────────────────────

        results.append(result)

    for rule, prior, state_entry in paused_rules:
        summary["paused"] += 1
        results.append(build_paused_result(rule, prior, state_entry))

    for rule, prior in skipped_rules:
        cached = deepcopy(prior)
        cached["cached"] = True
        cached["notifications_enabled"] = bool(rule.get("notifications", True))
        results.append(cached)

    # Fleet-wide snapshot counts for the Activity "Recent Runs" view. The timer
    # fires every minute but most checks only run every few minutes, so a given
    # run usually evaluates 0-3 checks. Counting only those made PASSED read as
    # 0 even when the whole fleet was healthy. Now the per-run summary describes
    # the WHOLE fleet at that moment: passed = all currently-healthy checks,
    # failed = all currently-failing, paused = all paused. (fixed / fix_failed /
    # new_alerts / resolved_alerts / tokens stay as this-run events.)
    def _result_is_paused(item: dict[str, Any]) -> bool:
        return bool(item.get("schedule_paused") or (item.get("alert_state") or {}).get("schedule_paused"))

    summary["passed"] = sum(1 for r in results if not _result_is_paused(r) and r.get("result") in ("pass", "fixed"))
    summary["failed"] = sum(1 for r in results if not _result_is_paused(r) and r.get("result") in ("failed", "fix_failed"))
    summary["paused"] = sum(1 for r in results if _result_is_paused(r))

    for item in results:
        if item.get("cached") or not item.get("notifications_enabled", True):
            continue
        outcome = item.get("result")
        alert_meta = item.get("alert_state", {}) or {}
        if outcome == "pass":
            notification_summary["passed"] += 1
            if alert_meta.get("resolved"):
                notification_summary["resolved_alerts"] += 1
        elif outcome == "fixed":
            notification_summary["failed"] += 1
            notification_summary["fixed"] += 1
            if alert_meta.get("should_notify"):
                notification_summary["new_alerts"] += 1
        elif outcome in {"failed", "fix_failed"}:
            notification_summary["failed"] += 1
            if outcome == "fix_failed":
                notification_summary["fix_failed"] += 1
            if alert_meta.get("should_notify"):
                notification_summary["new_alerts"] += 1
        token_usage = item.get("token_usage") or {}
        if token_usage.get("stopped"):
            notification_summary["token_protection_stops"] += 1

    duration = time.time() - start
    host_summaries = summarize_hosts(results)
    timestamp = utc_iso()
    try:
        transitions = sync_datasource_problems(config)
        if transitions["new"] or transitions["resolved"]:
            log.info(
                "  PROBLEMS: %d new, %d resolved (datasources)",
                len(transitions["new"]),
                len(transitions["resolved"]),
            )
        # Opt-in: run action chains for newly-seen problems matching a rule's
        # problem_match block. No-op unless such rules exist, so the live system
        # is unaffected until matchers are configured.
        problem_ctx = {
            "config": config,
            "state": state,
            "now": now,
            "internet_ok": internet_ok,
            "selected_agents": selected_agents,
            "custom_status_cache": custom_status_cache,
            "probed_status_cache": probed_status_cache,
            "probe_prompt": probe_prompt,
            "probe_cache_ttl": probe_cache_ttl,
            "agent_stats": agent_stats,
            "summary": summary,
            "remediation_enabled": remediation_enabled,
        }
        remediate_matched_problems(config, transitions["new"], problem_ctx)
        # Mirror system updates (severity/value changes) onto Jira tickets, then
        # close tickets for problems that just resolved (if Jira is wired).
        jira_sync_updates(config, transitions.get("updates", []))
        jira_sync_resolutions(config, transitions["resolved"])
    except Exception as exc:  # never let problem-store bookkeeping break a run
        log.warning("  problem store sync failed: %s", exc)

    # Only log a run in the Activity history when it actually did something
    # (evaluated a due check or carried a paused one). The bare every-minute
    # timer ticks that evaluate nothing are noise — they previously filled the
    # table with all-zero / 0.00s rows. The live status snapshot still refreshes
    # every minute regardless, so the dashboard stays current.
    evaluated_count = len(due_rules)
    record_run = bool(due_rules or paused_rules)
    if record_run:
        history["runs"] = trim_history(
            history.get("runs", [])
            + [
                {
                    "timestamp": timestamp,
                    "duration_seconds": round(duration, 2),
                    "evaluated": evaluated_count,
                    "fleet_total": len(results),
                    "summary": deepcopy(summary),
                }
            ]
        )
    history["checks"] = trim_history(
        history.get("checks", [])
        + [
            {
                "timestamp": timestamp,
                "key": item["alert_state"]["key"],
                "name": item["name"],
                "target": item["target"],
                "result": item["result"],
                "duration_seconds": round(duration / max(len(results), 1), 2),
                "success": result_success(item["result"]),
                "agent_used": item.get("agent_used"),
                "detail": item.get("detail"),
                "token_total": int((item.get("token_usage") or {}).get("total_tokens", 0)),
                "alert_status": (item.get("alert_state") or {}).get("status"),
            }
            for item in results
            if not item.get("cached")
        ],
        limit=3000,
    )

    report = {
        "timestamp": timestamp,
        "duration_seconds": round(duration, 2),
        "internet_ok": internet_ok,
        "internet_detail": internet_detail,
        "notification_summary": notification_summary,
        "agents": [
            {
                "name": status.name,
                "enabled": status.enabled,
                "available": status.available,
                "reason": status.reason,
                "quota_score": status.quota_score,
                "priority": status.priority,
            }
            for _, status in selected_agents
        ],
        "checks": results,
        "hosts": host_summaries,
        "summary": summary,
        "alert_rules": build_rule_catalog(config, rules),
        "native_engine_enabled": native_enabled,
        "host_catalog": config.get("hosts", {}),
        "problems": [p.to_dict() for p in ProblemStore(PROBLEMS_FILE).active_problems()],
        "datasources": [sanitize_datasource(ds) for ds in get_datasources(config)],
        "rules": [sanitize_rule(r) for r in config.get("rules", [])],
        "integrations": {"jira": sanitize_jira(get_jira_config(config))},
        "maintenance_windows": list_maintenance_windows(config),
        "history": build_history_snapshot(history, results),
    }

    save_json_file(STATE_FILE, state)
    save_json_file(HISTORY_FILE, history)
    status_path = Path(config.get("ui", {}).get("status_file", str(STATUS_FILE)))
    save_json_file(status_path, report)
    push_metrics(config, host_summaries, duration, agent_stats, results)
    if emit_notifications:
        send_desktop_notification(report)
        send_notification(config, report)

    log.info("=" * 60)
    log.info("RootCause run completed in %.1fs", duration)
    log.info("  Passed:      %d", summary["passed"])
    log.info("  Failed:      %d", summary["failed"])
    log.info("  Fixed:       %d", summary["fixed"])
    log.info("  Fix failed:  %d", summary["fix_failed"])
    log.info("  Paused:      %d", summary["paused"])
    log.info("  New alerts:  %d", summary["new_alerts"])
    log.info("  Resolved:    %d", summary["resolved_alerts"])
    log.info("=" * 60)
    return report


def build_light_status(report: dict[str, Any]) -> dict[str, Any]:
    """Trimmed status payload for the dashboard poll: drops heavy per-check
    output and the full host catalog so the frequent poll stays small."""
    if not isinstance(report, dict):
        return report

    light_checks = []
    for item in report.get("checks", []):
        if not isinstance(item, dict):
            continue
        alert_state = item.get("alert_state") or {}
        light_checks.append({
            "name": item.get("name"),
            "target": item.get("target"),
            "description": item.get("description"),
            "result": item.get("result"),
            "human_state": item.get("human_state"),
            "agent_used": item.get("agent_used"),
            "detail": (str(item.get("detail") or ""))[:280],
            "cached": item.get("cached", False),
            "notifications_enabled": item.get("notifications_enabled", True),
            "alert_state": {
                "key": alert_state.get("key"),
                "status": alert_state.get("status"),
                "severity": alert_state.get("severity"),
                "schedule_paused": alert_state.get("schedule_paused"),
                "acknowledged_at": alert_state.get("acknowledged_at"),
                "silenced_until": alert_state.get("silenced_until"),
                "maintenance_active": alert_state.get("maintenance_active"),
                "resolved": alert_state.get("resolved"),
                "should_notify": alert_state.get("should_notify"),
            },
        })

    light = {
        "light": True,
        "timestamp": report.get("timestamp"),
        "duration_seconds": report.get("duration_seconds"),
        "internet_ok": report.get("internet_ok"),
        "summary": report.get("summary"),
        "notification_summary": report.get("notification_summary"),
        "agents": report.get("agents"),
        "hosts": report.get("hosts"),
        "checks": light_checks,
        "external_alerts": report.get("external_alerts"),
        "maintenance_windows": report.get("maintenance_windows"),
        "history": report.get("history"),
    }
    return light


class StatusHandler(BaseHTTPRequestHandler):
    report_path = STATUS_FILE
    static_dir = STATIC_DIR
    config_path = CHECKS_FILE
    trusted_proxies: tuple[str, ...] = ("127.0.0.1", "::1")
    allowed_hosts: tuple[str, ...] = ()

    def _cors_enabled_path(self) -> bool:
        # Open CORS is only for the mobile API, which authenticates via API key
        # headers. UI/admin endpoints rely on same-origin access and must not
        # be readable cross-origin.
        path = self._request_path()
        return path.startswith("/api/mobile/") and not path.startswith("/api/mobile/admin/")

    def _write_json(self, payload: dict[str, Any], status_code: int = 200) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        if self._cors_enabled_path():
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key, X-Device-Id")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_file(self, path: Path, status_code: int = 200) -> None:
        data = path.read_bytes()
        mime_type, _ = mimetypes.guess_type(str(path))
        self.send_response(status_code)
        self.send_header("Content-Type", mime_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON body: {exc}") from exc

    def _request_path(self) -> str:
        return self.path.split("?", 1)[0]

    def _query_params(self) -> dict[str, list[str]]:
        return parse_qs(urlsplit(self.path).query)

    def _peer_is_trusted_proxy(self) -> bool:
        peer = self.client_address[0]
        for item in self.trusted_proxies:
            entry = str(item).strip()
            if not entry:
                continue
            try:
                if "/" in entry:
                    if ipaddress.ip_address(peer) in ipaddress.ip_network(entry, strict=False):
                        return True
                elif peer == entry:
                    return True
            except ValueError:
                continue
        return False

    def _client_ip(self) -> str:
        # Forwarding headers are client-controlled: only honor them when the
        # TCP peer is an explicitly trusted proxy (ui.trusted_proxies).
        peer = self.client_address[0]
        if not self._peer_is_trusted_proxy():
            return peer
        real_ip = self.headers.get("X-Real-IP", "").strip()
        if real_ip:
            return real_ip
        # Our nginx appends the real client as the LAST hop; the first entry
        # is attacker-controlled and must never be trusted.
        hops = [part.strip() for part in self.headers.get("X-Forwarded-For", "").split(",") if part.strip()]
        if hops:
            return hops[-1]
        return peer

    def _request_was_forwarded(self) -> bool:
        return bool(
            self.headers.get("X-Real-IP")
            or self.headers.get("X-Forwarded-For")
            or self.headers.get("Forwarded")
        )

    def _request_is_secure(self) -> bool:
        if self._peer_is_trusted_proxy():
            if self._request_was_forwarded():
                forwarded = self.headers.get("Forwarded", "")
                if "proto=https" in forwarded.lower():
                    return True
                return self.headers.get("X-Forwarded-Proto", "").lower() == "https"
            return self.client_address[0] in {"127.0.0.1", "::1"}
        return self.client_address[0] in {"127.0.0.1", "::1"}

    def _load_config(self) -> dict[str, Any]:
        return load_json_file(self.config_path, default={})

    def _save_config(self, config: dict[str, Any]) -> None:
        save_json_file(self.config_path, config)

    def _host_is_allowed(self, host_value: str) -> bool:
        hostname = host_value.strip().lower()
        if hostname.startswith("["):
            hostname = hostname.split("]", 1)[0].lstrip("[")
        else:
            hostname = hostname.rsplit(":", 1)[0] if ":" in hostname and hostname.count(":") == 1 else hostname
        if hostname in {"127.0.0.1", "localhost", "::1"}:
            return True
        return hostname in {str(item).strip().lower() for item in self.allowed_hosts if str(item).strip()}

    def _ensure_host_header(self) -> None:
        # DNS-rebinding mitigation: the Host header must name us explicitly.
        host = self.headers.get("Host", "")
        if host and not self._host_is_allowed(host):
            raise PermissionError("host header is not allowed")

    def _ensure_admin_post_origin(self) -> None:
        # CSRF mitigation: browsers always attach Origin to cross-site POSTs.
        origin = self.headers.get("Origin", "")
        if origin and origin != "null":
            origin_host = urlsplit(origin).netloc
            if not self._host_is_allowed(origin_host):
                raise PermissionError("cross-origin admin requests are not allowed")
        fetch_site = self.headers.get("Sec-Fetch-Site", "").lower()
        if fetch_site and fetch_site not in {"same-origin", "same-site", "none"}:
            raise PermissionError("cross-site admin requests are not allowed")

    def _ensure_local_admin(self) -> None:
        self._ensure_host_header()
        if self._client_ip() not in {"127.0.0.1", "::1"}:
            raise PermissionError("admin api is only available from localhost")

    def _ensure_local_ui_access(self) -> None:
        self._ensure_host_header()
        if self._client_ip() not in {"127.0.0.1", "::1"}:
            raise PermissionError("web ui is only available from localhost")

    def _extract_api_key(self) -> str:
        bearer = self.headers.get("Authorization", "")
        if bearer.lower().startswith("bearer "):
            return bearer[7:].strip()
        return self.headers.get("X-API-Key", "").strip()

    def _require_mobile_api_key(self, required_scope: str) -> tuple[dict[str, Any], dict[str, Any]]:
        config = self._load_config()
        mobile = get_mobile_config(config)
        if not mobile.get("enabled", True):
            raise PermissionError("mobile api is disabled")
        if mobile.get("require_https", True) and not self._request_is_secure():
            raise PermissionError("mobile api requires https")
        raw_key = self._extract_api_key()
        if not raw_key:
            raise PermissionError("missing api key")
        api_key = verify_mobile_api_key(config, raw_key, required_scope=required_scope)
        if api_key is None:
            raise PermissionError("invalid api key or scope")
        self._save_config(config)
        return config, api_key

    def _require_ingest(self) -> tuple[dict[str, Any], dict[str, Any] | None]:
        """Authenticate an ingest request, returning (config, datasource-or-None).

        A datasource-scoped token tags incoming problems with that datasource id;
        a legacy global token authenticates but does not tag.
        """
        config = self._load_config()
        resolved = resolve_ingest_token(config, self._extract_api_key())
        if resolved is None:
            raise PermissionError("invalid or missing ingest token")
        kind, obj = resolved
        return config, (obj if kind == "datasource" else None)

    def _ingest_problems(self, problems: list[Problem], datasource: dict[str, Any] | None) -> dict[str, Any]:
        ds_id = str(datasource.get("id")) if datasource else ""
        if ds_id:
            for prob in problems:
                prob.datasource_id = ds_id
        store = ProblemStore(PROBLEMS_FILE)
        transitions = store.ingest(problems)
        return {
            "ok": True,
            "datasource": ds_id,
            "accepted": len(problems),
            "new": len(transitions["new"]),
            "ongoing": len(transitions["ongoing"]),
            "resolved": len(transitions["resolved"]),
        }

    def _handle_ingest_alertmanager(self, payload: dict[str, Any]) -> dict[str, Any]:
        config, ds = self._require_ingest()
        resolver = (lambda labels: infer_external_alert_host(labels, config.get("hosts", {})))
        return self._ingest_problems(rootcause_problems.normalize_alertmanager_webhook(payload, resolver), ds)

    def _handle_ingest_grafana(self, payload: dict[str, Any]) -> dict[str, Any]:
        config, ds = self._require_ingest()
        resolver = (lambda labels: infer_external_alert_host(labels, config.get("hosts", {})))
        return self._ingest_problems(rootcause_problems.normalize_grafana_webhook(payload, resolver), ds)

    def _handle_ingest_generic(self, payload: dict[str, Any]) -> dict[str, Any]:
        config, ds = self._require_ingest()
        resolver = (lambda labels: infer_external_alert_host(labels, config.get("hosts", {})))
        return self._ingest_problems(rootcause_problems.normalize_generic_webhook(payload, resolver), ds)

    def _handle_problem_ack(self, payload: dict[str, Any]) -> dict[str, Any]:
        key = str(payload.get("key") or "").strip()
        if not key:
            raise ValueError("problem key is required")
        store = ProblemStore(PROBLEMS_FILE)
        ok = store.acknowledge(key, by="web")
        return {"ok": ok, "problems": [p.to_dict() for p in store.active_problems()]}

    def _handle_problem_comment(self, payload: dict[str, Any]) -> dict[str, Any]:
        key = str(payload.get("key") or "").strip()
        text = str(payload.get("text") or "").strip()
        if not key or not text:
            raise ValueError("problem key and comment text are required")
        store = ProblemStore(PROBLEMS_FILE)
        ok = store.add_comment(key, text, by="web")
        # Mirror the comment onto the problem's Jira ticket, if one exists.
        if ok:
            try:
                config = self._load_config()
                if jira_enabled(config):
                    prob = next((p for p in store.active_problems() if p.key == key), None)
                    issue_key = str((prob.annotations or {}).get("jira_issue_key") or "") if prob else ""
                    if issue_key:
                        jira_add_comment(get_jira_config(config), issue_key, text, by="web")
            except Exception as exc:  # never let Jira break the local comment
                log.warning("  jira comment mirror failed: %s", exc)
        return {"ok": ok, "problems": [p.to_dict() for p in store.active_problems()]}

    def _handle_datasource_save(self, payload: dict[str, Any]) -> dict[str, Any]:
        config = self._load_config()
        datasources = get_datasources(config)
        ds_id = str(payload.get("id") or "").strip()
        existing = find_datasource(config, ds_id) if ds_id else None
        if existing is None:
            existing = {"id": new_datasource_id()}
            datasources.append(existing)
        dtype = str(payload.get("type") or existing.get("type") or "prometheus")
        if dtype not in DATASOURCE_TYPES:
            raise ValueError(f"unknown datasource type '{dtype}'")
        existing["name"] = str(payload.get("name") or existing.get("name") or dtype).strip()
        existing["type"] = dtype
        existing["url"] = str(payload.get("url") or "").strip()
        existing["mode"] = str(payload.get("mode") or existing.get("mode") or DATASOURCE_DEFAULT_MODE.get(dtype, "polling"))
        existing["enabled"] = bool(payload.get("enabled", existing.get("enabled", True)))
        for field in ("index", "user", "field_map", "query"):
            if field in payload:
                existing[field] = payload[field]
        # Secret fields are only overwritten when a (non-empty) value is provided,
        # so the sanitized round-trip from the UI never wipes a stored secret.
        for field in DATASOURCE_SECRET_FIELDS:
            if payload.get(field):
                existing[field] = payload[field]
        raw_token = None
        if existing["mode"] == "webhook" and not (existing.get("ingest") or {}).get("key_hash"):
            raw_token = create_datasource_ingest_token(existing)
        self._save_config(config)
        refresh_status_snapshot_config(config)
        resp = {
            "ok": True,
            "saved_id": existing["id"],
            "datasources": [sanitize_datasource(d) for d in datasources],
        }
        if raw_token:
            resp["ingest_token"] = raw_token  # shown once
            resp["ingest_url"] = f"/api/ingest/{dtype if dtype in ('alertmanager', 'grafana') else 'generic'}"
        return resp

    def _handle_datasource_token(self, payload: dict[str, Any]) -> dict[str, Any]:
        config = self._load_config()
        ds = find_datasource(config, str(payload.get("id") or ""))
        if ds is None:
            raise ValueError("datasource not found")
        raw_token = create_datasource_ingest_token(ds)
        self._save_config(config)
        return {
            "ok": True,
            "ingest_token": raw_token,
            "datasources": [sanitize_datasource(d) for d in get_datasources(config)],
        }

    def _handle_datasource_delete(self, payload: dict[str, Any]) -> dict[str, Any]:
        config = self._load_config()
        ds_id = str(payload.get("id") or "").strip()
        config["datasources"] = [d for d in get_datasources(config) if str(d.get("id")) != ds_id]
        self._save_config(config)
        refresh_status_snapshot_config(config)
        return {"ok": True, "datasources": [sanitize_datasource(d) for d in config["datasources"]]}

    def _handle_datasource_test(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Probe a datasource by running its connector once and reporting the result.

        Tests a saved datasource by ``id`` (preferred, so stored secrets are used)
        or an unsaved one built from the inline payload. Webhook-mode datasources
        have nothing to poll, so we just confirm the ingest path instead.
        """
        config = self._load_config()
        ds_id = str(payload.get("id") or "").strip()
        ds = find_datasource(config, ds_id) if ds_id else None
        if ds is None:
            ds = {k: payload.get(k) for k in ("type", "url", "user", "index", "query", "mode") if payload.get(k) is not None}
            for field in DATASOURCE_SECRET_FIELDS:
                if payload.get(field):
                    ds[field] = payload[field]
        dtype = str(ds.get("type") or "")
        if str(ds.get("mode") or "polling") == "webhook":
            return {"ok": True, "message": "Webhook datasource — receives pushes at the ingest URL, nothing to poll."}
        if not str(ds.get("url") or "").strip():
            raise ValueError("url is required to test the connection")
        cls = DATASOURCE_CONNECTORS.get(dtype)
        if not cls:
            raise ValueError(f"no connector available for type '{dtype}'")
        started = time.monotonic()
        try:
            problems = cls(ds, config.get("hosts", {})).poll()
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}
        elapsed_ms = int((time.monotonic() - started) * 1000)
        return {
            "ok": True,
            "count": len(problems),
            "elapsed_ms": elapsed_ms,
            "message": f"Connected — {len(problems)} active problem(s) in {elapsed_ms} ms",
        }

    def _handle_rule_save(self, payload: dict[str, Any]) -> dict[str, Any]:
        config = self._load_config()
        rules = get_rules(config)
        rule_id = str(payload.get("id") or "").strip()
        existing = find_rule(config, rule_id) if rule_id else None
        if existing is None:
            existing = {"id": new_rule_id()}
            rules.append(existing)
        existing["name"] = str(payload.get("name") or existing.get("name") or "rule").strip()
        existing["enabled"] = bool(payload.get("enabled", existing.get("enabled", True)))
        existing["datasource_ids"] = [str(x) for x in (payload.get("datasource_ids") or [])]
        existing["trigger"] = str(payload.get("trigger") or existing.get("trigger") or "auto")
        existing["match"] = payload.get("match") if isinstance(payload.get("match"), dict) else {}
        existing["actions"] = payload.get("actions") if isinstance(payload.get("actions"), list) else []
        # Author aid: the PromQL used in the editor's preview chart (not used for
        # matching — detection lives in Prometheus — but kept so the editor can
        # restore it and link back to the datasource).
        if "preview_query" in payload:
            existing["preview_query"] = str(payload.get("preview_query") or "")
        self._save_config(config)
        refresh_status_snapshot_config(config)
        return {"ok": True, "saved_id": existing["id"], "rules": [sanitize_rule(r) for r in rules]}

    def _handle_rule_delete(self, payload: dict[str, Any]) -> dict[str, Any]:
        config = self._load_config()
        rule_id = str(payload.get("id") or "").strip()
        config["rules"] = [r for r in get_rules(config) if str(r.get("id")) != rule_id]
        self._save_config(config)
        refresh_status_snapshot_config(config)
        return {"ok": True, "rules": [sanitize_rule(r) for r in config["rules"]]}

    def _handle_jira_save(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = self._load_config()
        jira = get_jira_config(config)
        jira["enabled"] = bool(payload.get("enabled", jira.get("enabled", False)))
        for field in ("base_url", "email", "project_key", "issue_type", "close_transition"):
            if field in payload:
                jira[field] = str(payload.get(field) or "").strip()
        # Secret only overwritten when a non-empty value is supplied.
        if payload.get("api_token"):
            jira["api_token"] = str(payload["api_token"])
        self._save_config(config)
        refresh_status_snapshot_config(config)
        return {"ok": True, "jira": sanitize_jira(jira)}

    def _handle_jira_test(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = self._load_config()
        cfg = dict(get_jira_config(config))
        # Allow testing inline (unsaved) values from the form.
        for field in ("base_url", "email", "project_key", "issue_type"):
            if payload.get(field):
                cfg[field] = str(payload[field]).strip()
        if payload.get("api_token"):
            cfg["api_token"] = str(payload["api_token"])
        ok, message = jira_test_connection(cfg)
        return {"ok": ok, "message" if ok else "error": message}

    def _mobile_bootstrap_payload(
        self,
        report: dict[str, Any],
        config: dict[str, Any],
        api_key: dict[str, Any] | None = None,
        device: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        mobile = get_mobile_config(config)
        alerts = build_mobile_alerts(report, allowed_targets=api_key_allowed_targets(api_key or {}))
        return {
            "app": {"name": "RootCause", "logo_url": "/static/rootcause-icon.svg"},
            "server": {
                "base_url": mobile.get("public_base_url", ""),
                "timestamp": report.get("timestamp"),
                "secure_transport_required": bool(mobile.get("require_https", True)),
            },
            "device": device,
            "summary": summarize_mobile_alerts(alerts),
            "alerts": alerts,
            "agents": report.get("agents", []),
            "hosts": report.get("hosts", {}),
            "history": report.get("history", {}),
            "available_actions": ["ack", "silence", "rerun"],
        }

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        if self._cors_enabled_path():
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key, X-Device-Id")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def _handle_mobile_admin_overview(self) -> dict[str, Any]:
        self._ensure_local_admin()
        config = self._load_config()
        mobile = get_mobile_config(config)
        ui_config = config.get("ui", {})
        return {
            "ok": True,
            "mobile": {
                "enabled": bool(mobile.get("enabled", True)),
                "require_https": bool(mobile.get("require_https", True)),
                "public_base_url": mobile.get("public_base_url", ""),
                "public_scheme": mobile.get("public_scheme", "https"),
                "public_hostname": mobile.get("public_hostname", ""),
                "public_port": mobile.get("public_port", 443),
                "allowed_scopes": mobile.get("allowed_scopes", []),
            },
            "ui": {
                "serve_host": ui_config.get("serve_host", "127.0.0.1"),
                "serve_port": ui_config.get("serve_port", 8787),
                "tls_enabled": bool(ui_config.get("tls_enabled", False)),
                "tls_certfile": ui_config.get("tls_certfile", ""),
                "tls_keyfile": ui_config.get("tls_keyfile", ""),
            },
            "downloads": {
                "apk_path": "/downloads/rootcause.apk",
                "apk_available": ANDROID_RELEASE_APK.exists(),
            },
            "push": {
                "enabled": bool(mobile.get("push", {}).get("enabled", False)),
                "service_account_path": mobile.get("push", {}).get("service_account_path", ""),
            },
            "api_keys": list_mobile_api_keys(config),
            "devices": list_mobile_devices(config),
        }

    def _handle_mobile_admin_settings(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = self._load_config()
        mobile = get_mobile_config(config)
        ui_config = config.setdefault("ui", {})

        public_scheme = str(payload.get("public_scheme") or mobile.get("public_scheme") or "https").strip().lower()
        if public_scheme not in {"http", "https"}:
            raise ValueError("public scheme must be http or https")

        public_hostname = str(payload.get("public_hostname") or "").strip().strip("/")
        if public_hostname and re.search(r"\s", public_hostname):
            raise ValueError("public hostname is invalid")

        public_port_raw = payload.get("public_port", mobile.get("public_port", 443))
        try:
            public_port = int(public_port_raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("public port must be a number") from exc
        if not 1 <= public_port <= 65535:
            raise ValueError("public port must be between 1 and 65535")

        serve_host = str(payload.get("serve_host") or ui_config.get("serve_host") or "127.0.0.1").strip()
        if not serve_host:
            raise ValueError("serve host is required")
        serve_port_raw = payload.get("serve_port", ui_config.get("serve_port", 8787))
        try:
            serve_port = int(serve_port_raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("serve port must be a number") from exc
        if not 1 <= serve_port <= 65535:
            raise ValueError("serve port must be between 1 and 65535")

        tls_enabled = bool(payload.get("tls_enabled", ui_config.get("tls_enabled", False)))
        tls_certfile = str(payload.get("tls_certfile") or ui_config.get("tls_certfile") or "").strip()
        tls_keyfile = str(payload.get("tls_keyfile") or ui_config.get("tls_keyfile") or "").strip()
        if tls_enabled and (not tls_certfile or not tls_keyfile):
            raise ValueError("TLS cert and key paths are required when TLS is enabled")

        mobile["public_scheme"] = public_scheme
        mobile["public_hostname"] = public_hostname
        mobile["public_port"] = public_port
        mobile["public_base_url"] = build_mobile_public_base_url(mobile)
        ui_config["serve_host"] = serve_host
        ui_config["serve_port"] = serve_port
        ui_config["tls_enabled"] = tls_enabled
        ui_config["tls_certfile"] = tls_certfile
        ui_config["tls_keyfile"] = tls_keyfile
        self._save_config(config)
        return self._handle_mobile_admin_overview()

    def _handle_mobile_push_settings(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = self._load_config()
        mobile = get_mobile_config(config)
        push = mobile.setdefault("push", {"enabled": False, "provider": "fcm_v1", "service_account_path": ""})
        push["enabled"] = bool(payload.get("enabled", False))
        if "service_account_path" in payload:
            path = str(payload.get("service_account_path") or "").strip()
            if path and not Path(path).expanduser().exists():
                raise ValueError(f"file not found: {path}")
            push["service_account_path"] = path
        self._save_config(config)
        return self._handle_mobile_admin_overview()

    def _handle_mobile_api_key_create(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = self._load_config()
        mobile = get_mobile_config(config)
        name = str(payload.get("name") or "").strip()
        if not name:
            raise ValueError("api key name is required")
        allowed_scopes = set(mobile.get("allowed_scopes", []))
        scopes = [str(item).strip() for item in payload.get("scopes", []) if str(item).strip()]
        if not scopes:
            scopes = ["mobile:read", "mobile:device", "mobile:ack", "mobile:silence", "mobile:rerun"]
        invalid = [item for item in scopes if item not in allowed_scopes]
        if invalid:
            raise ValueError(f"invalid scopes: {', '.join(invalid)}")
        allowed_targets = normalize_allowed_mobile_targets(payload.get("allowed_targets"))
        if allowed_targets:
            known_hosts = set((config.get("hosts") or {}).keys())
            unknown = [item for item in allowed_targets if item not in known_hosts]
            if unknown:
                raise ValueError(f"unknown hosts in allowed_targets: {', '.join(unknown)}")
        raw_key, record = create_mobile_api_key_record(
            name=name,
            scopes=scopes,
            notes=str(payload.get("notes") or "").strip(),
            device_limit=int(payload.get("device_limit") or 5),
            allowed_targets=allowed_targets,
        )
        mobile.setdefault("api_keys", []).append(record)
        self._save_config(config)
        return {
            "ok": True,
            "api_key": sanitize_mobile_api_key(record),
            "raw_key": raw_key,
            "api_keys": list_mobile_api_keys(config),
            "devices": list_mobile_devices(config),
        }

    def _handle_mobile_api_key_revoke(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        key_id = str(payload.get("id") or "").strip()
        if not key_id:
            raise ValueError("api key id is required")
        config = self._load_config()
        revoke_mobile_api_key(config, key_id)
        self._save_config(config)
        return {
            "ok": True,
            "api_keys": list_mobile_api_keys(config),
            "devices": list_mobile_devices(config),
        }

    def _handle_mobile_device_revoke(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        device_id = str(payload.get("id") or "").strip()
        if not device_id:
            raise ValueError("device id is required")
        config = self._load_config()
        revoke_mobile_device(config, device_id)
        self._save_config(config)
        return {
            "ok": True,
            "devices": list_mobile_devices(config),
            "api_keys": list_mobile_api_keys(config),
        }

    def _load_service_account_json(self, push_config: dict[str, Any]) -> str:
        if not push_config.get("enabled"):
            raise ValueError("push notifications are not enabled in mobile settings")
        path = str(push_config.get("service_account_path") or "").strip()
        if not path:
            raise ValueError("service account JSON path is not configured")
        sa_path = Path(path).expanduser()
        if not sa_path.exists():
            raise ValueError(f"service account file not found: {path}")
        return sa_path.read_text()

    def _handle_mobile_test_push(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = self._load_config()
        mobile = get_mobile_config(config)
        sa_json = self._load_service_account_json(mobile.get("push", {}))
        devices = [d for d in mobile.get("devices", []) if not d.get("revoked_at") and d.get("push_token")]
        if not devices:
            raise ValueError("no registered devices with push tokens (open the app once to register)")
        sent, failed = 0, []
        for device in devices:
            if send_fcm_push(sa_json, device["push_token"], "RootCause Test", "Push notifications are working! 🎉"):
                sent += 1
            else:
                failed.append(device.get("name") or device.get("id"))
        return {"ok": True, "sent": sent, "failed": failed, "total": len(devices)}

    def _handle_mobile_device_register(self, payload: dict[str, Any]) -> dict[str, Any]:
        config, api_key = self._require_mobile_api_key(MOBILE_ACTION_SCOPES["device"])
        device = register_mobile_device(config, payload, api_key, self._client_ip())
        self._save_config(config)
        report = load_json_file(self.report_path, default={"error": "No status report yet"})
        return {
            "ok": True,
            "device": device,
            "bootstrap": self._mobile_bootstrap_payload(report, config, api_key=api_key, device=device),
        }

    def _get_apk_version_info(self) -> dict[str, Any]:
        """Read versionCode/versionName from build.gradle.kts and APK file metadata."""
        version_name = "unknown"
        version_code = 0
        try:
            text = ANDROID_BUILD_GRADLE.read_text()
            name_m = re.search(r'versionName\s*=\s*"([^"]+)"', text)
            code_m = re.search(r'versionCode\s*=\s*(\d+)', text)
            if name_m:
                version_name = name_m.group(1)
            if code_m:
                version_code = int(code_m.group(1))
        except Exception as exc:
            log.debug("could not read APK version from build.gradle.kts: %s", exc)
        apk_available = ANDROID_RELEASE_APK.exists()
        apk_size = int(ANDROID_RELEASE_APK.stat().st_size) if apk_available else 0
        apk_modified = (
            datetime.fromtimestamp(ANDROID_RELEASE_APK.stat().st_mtime, tz=timezone.utc).isoformat()
            if apk_available else None
        )
        return {
            "version_name": version_name,
            "version_code": version_code,
            "apk_available": apk_available,
            "apk_size": apk_size,
            "apk_modified": apk_modified,
            "download_path": "/api/mobile/download-apk",
        }

    def _handle_mobile_app_version(self) -> dict[str, Any]:
        self._require_mobile_api_key(MOBILE_ACTION_SCOPES["read"])
        return self._get_apk_version_info()

    def _handle_mobile_download_apk(self) -> None:
        self._require_mobile_api_key(MOBILE_ACTION_SCOPES["read"])
        if not ANDROID_RELEASE_APK.exists():
            self._write_json({"error": "apk not found"}, 404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/vnd.android.package-archive")
        self.send_header("Content-Length", str(ANDROID_RELEASE_APK.stat().st_size))
        self.send_header("Content-Disposition", 'attachment; filename="rootcause.apk"')
        self.end_headers()
        with ANDROID_RELEASE_APK.open("rb") as handle:
            shutil.copyfileobj(handle, self.wfile)

    def _handle_mobile_bootstrap(self) -> dict[str, Any]:
        config, api_key = self._require_mobile_api_key(MOBILE_ACTION_SCOPES["read"])
        device_id = self.headers.get("X-Device-Id", "").strip()
        device = find_registered_device(config, str(api_key.get("id") or ""), device_id)
        if device is not None:
            device["last_seen_at"] = utc_iso()
            device["last_ip"] = self._client_ip()
            self._save_config(config)
        report = load_json_file(self.report_path, default={"error": "No status report yet"})
        return self._mobile_bootstrap_payload(report, config, api_key=api_key, device=sanitize_mobile_device(device) if device else None)

    def _handle_mobile_ack(self, payload: dict[str, Any]) -> dict[str, Any]:
        config, api_key = self._require_mobile_api_key(MOBILE_ACTION_SCOPES["ack"])
        report = load_json_file(self.report_path, default={"error": "No status report yet"})
        allowed_alert = ensure_mobile_alert_allowed(report, api_key, payload)
        state = load_state()
        if allowed_alert.get("targets"):
            touched = sum(
                acknowledge_alerts_in_state(
                    state,
                    {**payload, "target": target},
                    actor=str(api_key.get("name") or "mobile"),
                )
                for target in allowed_alert["targets"]
            )
        else:
            touched = acknowledge_alerts_in_state(state, payload, actor=str(api_key.get("name") or "mobile"))
        save_json_file(STATE_FILE, state)
        report = refresh_status_snapshot_state(config, state)
        alerts = build_mobile_alerts(report, allowed_targets=api_key_allowed_targets(api_key))
        return {"ok": True, "acknowledged": touched, "alerts": alerts, "summary": summarize_mobile_alerts(alerts)}

    def _handle_mobile_silence(self, payload: dict[str, Any]) -> dict[str, Any]:
        config, api_key = self._require_mobile_api_key(MOBILE_ACTION_SCOPES["silence"])
        report = load_json_file(self.report_path, default={"error": "No status report yet"})
        allowed_alert = ensure_mobile_alert_allowed(report, api_key, payload)
        state = load_state()
        if allowed_alert.get("targets"):
            touched = sum(
                silence_alerts_in_state(
                    state,
                    {**payload, "target": target},
                    actor=str(api_key.get("name") or "mobile"),
                )
                for target in allowed_alert["targets"]
            )
        else:
            touched = silence_alerts_in_state(state, payload, actor=str(api_key.get("name") or "mobile"))
        save_json_file(STATE_FILE, state)
        report = refresh_status_snapshot_state(config, state)
        alerts = build_mobile_alerts(report, allowed_targets=api_key_allowed_targets(api_key))
        return {"ok": True, "silenced": touched, "alerts": alerts, "summary": summarize_mobile_alerts(alerts)}

    def _handle_mobile_rerun(self, payload: dict[str, Any]) -> dict[str, Any]:
        config, api_key = self._require_mobile_api_key(MOBILE_ACTION_SCOPES["rerun"])
        allowed_alert = ensure_mobile_alert_allowed(
            load_json_file(self.report_path, default={"error": "No status report yet"}),
            api_key,
            payload,
        )
        allowed_targets = api_key_allowed_targets(api_key)
        if allowed_targets is not None:
            all_targets = alert_targets_in_report(
                load_json_file(self.report_path, default={"error": "No status report yet"}),
                alert_id=str(allowed_alert.get("id") or ""),
                alert_name=str(allowed_alert.get("name") or ""),
            )
            if all_targets - allowed_targets:
                raise PermissionError("rerun is not allowed for alerts spanning hosts outside this api key scope")
        force = {str(payload.get("alert_id") or "").strip(), str(payload.get("alert_name") or "").strip()}
        report = run_checks(
            normalize_config(config),
            force_alert_names=force,
            remediation_enabled=False,
            emit_notifications=False,
        )
        alerts = build_mobile_alerts(report, allowed_targets=api_key_allowed_targets(api_key))
        return {
            "ok": True,
            "message": f"manual check rerun completed without ai remediation for {allowed_alert.get('name')}",
            "summary": summarize_mobile_alerts(alerts),
            "alerts": alerts,
        }

    def _handle_prom_range(self) -> dict[str, Any]:
        """Proxy a Prometheus range query (for the inline trigger preview chart).

        Browser → RootCause (same origin) → Prometheus avoids CORS. Optionally also
        evaluates the full firing ``expr`` so the editor can show "would it fire".
        """
        self._ensure_local_ui_access()
        params = self._query_params()

        def first(key: str, default: str = "") -> str:
            vals = params.get(key) or []
            return (vals[0] if vals else default).strip()

        query = first("query")
        expr = first("expr")
        host_name = first("host", "localhost") or "localhost"
        try:
            minutes = max(1, min(int(first("minutes", "60")), 1440))
        except ValueError:
            minutes = 60
        if not query:
            return {"ok": False, "error": "missing query"}
        config = load_json_file(self.config_path, default={})
        hosts = config.get("hosts") or {}
        # A datasource id (from the rule editor) resolves directly to its URL;
        # otherwise fall back to the host's prometheus_url (legacy check editor).
        ds_id = first("ds")
        prom_url = ""
        if ds_id:
            ds = find_datasource(config, ds_id)
            if ds and str(ds.get("type")) == "prometheus":
                prom_url = str(ds.get("url") or "").strip()
        if not prom_url:
            host = hosts.get(host_name) or next(iter(hosts.values()), {})
            prom_url = (host or {}).get("prometheus_url")
        if not prom_url:
            return {"ok": False, "error": "no Prometheus URL (pick a Prometheus datasource)"}
        end = time.time()
        start = end - minutes * 60
        step = max(15, int(minutes * 60 / 200))  # ~200 points
        try:
            resp = requests.get(
                f"{prom_url}/api/v1/query_range",
                params={"query": query, "start": start, "end": end, "step": step},
                timeout=10,
            )
            data = resp.json()
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
        out: dict[str, Any] = {
            "ok": data.get("status") == "success",
            "data": data.get("data", {}),
            "start": start, "end": end, "step": step,
        }
        if data.get("status") != "success":
            out["error"] = data.get("error", "prometheus error")
        if expr:
            q_ok, firing, detail = query_prometheus_firing(prom_url, expr, timeout=10)
            out["firing"] = bool(firing)
            out["firing_ok"] = bool(q_ok)
            out["firing_detail"] = detail
        # The instance label values Prometheus knows about (the real hosts), so the
        # editor can offer chips that auto-fill the {instance=...} matcher.
        try:
            r2 = requests.get(
                f"{prom_url}/api/v1/query",
                params={"query": "count by (instance)(node_uname_info)"},
                timeout=5,
            )
            d2 = r2.json()
            if d2.get("status") == "success":
                out["instances"] = sorted(
                    {s["metric"].get("instance", "") for s in d2["data"]["result"] if s["metric"].get("instance")}
                )
        except Exception:
            out["instances"] = []
        return out

    def do_GET(self) -> None:  # noqa: N802
        request_path = self._request_path()
        if request_path in {"/", "/search", "/settings", "/hosts", "/activity", "/alertmanager", "/problems", "/rules", "/observability"} or request_path.startswith("/alerts/") or request_path.startswith("/hosts/") or request_path.startswith("/rules/"):
            try:
                self._ensure_local_ui_access()
                self._write_file(self.static_dir / "index.html")
            except PermissionError as exc:
                self._write_json({"error": str(exc)}, 403)
            return
        if request_path.startswith("/static/"):
            try:
                self._ensure_local_ui_access()
                relative = request_path.removeprefix("/static/")
                asset_path = (self.static_dir / relative).resolve()
                if not str(asset_path).startswith(str(self.static_dir.resolve())) or not asset_path.exists():
                    self._write_json({"error": "not found"}, 404)
                    return
                self._write_file(asset_path)
            except PermissionError as exc:
                self._write_json({"error": str(exc)}, 403)
            return
        if request_path == "/api/status":
            try:
                self._ensure_local_ui_access()
                payload = load_json_file(self.report_path, default={"error": "No status report yet"})
                if self._query_params().get("light"):
                    payload = build_light_status(payload)
                self._write_json(payload, 200)
            except PermissionError as exc:
                self._write_json({"error": str(exc)}, 403)
            return
        if request_path == "/api/config":
            try:
                self._ensure_local_ui_access()
                payload = load_json_file(self.config_path, default={})
                self._write_json(payload, 200)
            except PermissionError as exc:
                self._write_json({"error": str(exc)}, 403)
            return
        if request_path == "/api/problems":
            try:
                self._ensure_local_ui_access()
                store = ProblemStore(PROBLEMS_FILE)
                problems = [p.to_dict() for p in store.active_problems()]
                self._write_json(
                    {"timestamp": utc_iso(), "total": len(problems), "problems": problems},
                    200,
                )
            except PermissionError as exc:
                self._write_json({"error": str(exc)}, 403)
            return
        if request_path == "/api/prom_range":
            try:
                self._write_json(self._handle_prom_range(), 200)
            except PermissionError as exc:
                self._write_json({"error": str(exc)}, 403)
            return
        if request_path == "/api/agent-calls":
            try:
                self._ensure_local_ui_access()
                self._write_json(load_json_file(AGENT_CALLS_FILE, default=[]), 200)
            except PermissionError as exc:
                self._write_json({"error": str(exc)}, 403)
            return
        if request_path == "/api/agent-models":
            try:
                self._ensure_local_ui_access()
                payload = dict(KNOWN_AGENT_MODELS)
                payload["codex"] = _fetch_codex_models()
                self._write_json(payload, 200)
            except PermissionError as exc:
                self._write_json({"error": str(exc)}, 403)
            return
        if request_path == "/api/alertmanager/alerts":
            try:
                self._write_json(self._handle_alertmanager_alerts_api(), 200)
            except PermissionError as exc:
                self._write_json({"error": str(exc)}, 401)
            return
        if request_path == "/api/mobile/admin/overview":
            try:
                self._write_json(self._handle_mobile_admin_overview(), 200)
            except PermissionError as exc:
                self._write_json({"error": str(exc)}, 401)
            return
        if request_path == "/api/mobile/bootstrap":
            try:
                self._write_json(self._handle_mobile_bootstrap(), 200)
            except PermissionError as exc:
                self._write_json({"error": str(exc)}, 401)
            return
        if request_path == "/api/mobile/app-version":
            try:
                self._write_json(self._handle_mobile_app_version(), 200)
            except PermissionError as exc:
                self._write_json({"error": str(exc)}, 401)
            return
        if request_path == "/api/mobile/download-apk":
            try:
                self._handle_mobile_download_apk()
            except PermissionError as exc:
                self._write_json({"error": str(exc)}, 401)
            return
        if request_path == "/metrics":
            try:
                self._ensure_local_ui_access()
                body = render_prometheus_metrics().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except PermissionError as exc:
                self._write_json({"error": str(exc)}, 403)
            return
        if request_path == "/healthz":
            self._write_json({"ok": True, "timestamp": utc_iso()}, 200)
            return
        if request_path == "/downloads/rootcause.apk":
            try:
                self._ensure_local_ui_access()
                if not ANDROID_RELEASE_APK.exists():
                    self._write_json({"error": "apk not found"}, 404)
                    return
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.android.package-archive")
                self.send_header("Content-Length", str(ANDROID_RELEASE_APK.stat().st_size))
                self.send_header("Content-Disposition", 'attachment; filename="rootcause.apk"')
                self.end_headers()
                with ANDROID_RELEASE_APK.open("rb") as handle:
                    shutil.copyfileobj(handle, self.wfile)
            except PermissionError as exc:
                self._write_json({"error": str(exc)}, 403)
            return
        self._write_json({"error": "not found"}, 404)

    def _handle_alert_save(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = load_json_file(self.config_path, default={})
        updated, locked_blocked = upsert_alert_config(config, payload)
        ensure_alert_ids(updated)  # never persist a rule with an empty id
        save_json_file(self.config_path, updated)
        snapshot = refresh_status_snapshot_config(updated)
        normalized = normalize_config(updated)
        rule_payload = payload.get("alert_rule", {})
        saved_name = str(rule_payload.get("name") or "").strip()
        saved_id = next(
            (rule.get("id") for rule in updated.get("alert_rules", []) if rule.get("name") == saved_name),
            rule_payload.get("id"),
        )
        return {
            "ok": True,
            "message": "Alert configuration saved",
            "saved_id": saved_id,
            "alert_rules": snapshot.get("alert_rules", []),
            "host_catalog": snapshot.get("host_catalog", normalized.get("hosts", {})),
            "agents": updated.get("agents", []),
            "locked_blocked": locked_blocked,
        }

    def _handle_alert_delete(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = load_json_file(self.config_path, default={})
        updated = delete_alert_from_config(config, payload)
        save_json_file(self.config_path, updated)
        snapshot = refresh_status_snapshot_config(updated)
        return {
            "ok": True,
            "message": "Alert deleted",
            "alert_rules": snapshot.get("alert_rules", []),
            "host_catalog": snapshot.get("host_catalog", normalize_config(updated).get("hosts", {})),
        }

    def _handle_alert_rearm(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = load_json_file(self.config_path, default={})
        state = load_state()
        try:
            updated_state, rearmed = rearm_alert_in_state(state, payload)
        except ValueError as exc:
            # "alert is not paused" means the state already agrees it's armed.
            # The UI snapshot can still be stale (e.g. a previous rearm only
            # touched state), so reconcile it instead of failing — that turns a
            # confusing "REARM does nothing" into a self-healing no-op.
            if "not paused" not in str(exc).lower():
                raise
            report = refresh_status_snapshot_state(normalize_config(config), state)
            return {
                "ok": True,
                "message": "Already armed — refreshed status (nothing was paused)",
                "rearmed": 0,
                "summary": report.get("summary", {}),
            }
        save_json_file(STATE_FILE, updated_state)
        # Refresh the UI snapshot immediately so the check stops showing as
        # paused without waiting for the next scheduled run. Without this the
        # rearm "appeared to do nothing" because the snapshot stayed stale.
        report = refresh_status_snapshot_state(normalize_config(config), updated_state)
        return {
            "ok": True,
            "message": f"Re-armed {rearmed} alert instance(s)",
            "rearmed": rearmed,
            "summary": report.get("summary", {}),
        }

    def _handle_alert_ack(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = load_json_file(self.config_path, default={})
        state = load_state()
        touched = acknowledge_alerts_in_state(state, payload, actor="web-admin")
        save_json_file(STATE_FILE, state)
        report = refresh_status_snapshot_state(config, state)
        return {
            "ok": True,
            "message": f"Acknowledged {touched} alert instance(s)",
            "acknowledged": touched,
            "summary": report.get("summary", {}),
        }

    def _handle_alert_silence(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = load_json_file(self.config_path, default={})
        state = load_state()
        touched = silence_alerts_in_state(state, payload, actor="web-admin")
        save_json_file(STATE_FILE, state)
        report = refresh_status_snapshot_state(config, state)
        return {
            "ok": True,
            "message": f"Silenced {touched} alert instance(s)",
            "silenced": touched,
            "summary": report.get("summary", {}),
        }

    def _handle_external_alert_silence(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = normalize_config(load_json_file(self.config_path, default={}))
        alert = find_external_alert(config, payload)
        alertmanager_url = str(alert.get("alertmanager_url") or payload.get("alertmanager_url") or "").strip()
        if not alertmanager_url:
            raise ValueError("alertmanager url is required for external silence")
        minutes = int(payload.get("minutes") or 60)
        comment = str(payload.get("reason") or "Silenced from RootCause").strip()
        ok, data = create_alertmanager_silence(
            alertmanager_url,
            alert,
            minutes=minutes,
            created_by="rootcause-web",
            comment=comment,
        )
        if not ok:
            raise ValueError(str(data))
        snapshot = refresh_status_snapshot_config(config)
        return {
            "ok": True,
            "message": f"External alert silenced for {minutes} minute(s)",
            "silence_id": (data or {}).get("silence_id"),
            "external_alerts": snapshot.get("external_alerts", []),
            "external_sources": snapshot.get("external_sources", []),
        }

    def _handle_alert_rerun(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = load_json_file(self.config_path, default={})
        force = {str(payload.get("alert_id") or payload.get("id") or "").strip(), str(payload.get("alert_name") or payload.get("name") or "").strip()}
        force = {item for item in force if item}
        report = run_checks(
            normalize_config(config),
            force_alert_names=force,
            remediation_enabled=False,
            emit_notifications=False,
        )
        # Figure out which checks actually ran so we can report a concrete
        # outcome instead of a vague "rerun completed".
        ran = []
        for check in report.get("checks", []):
            alert_state = check.get("alert_state") or {}
            key = str(alert_state.get("key") or "")
            key_name = key.split(":", 1)[1] if ":" in key else key
            if check.get("name") in force or key_name in force or str(alert_state.get("alert_id") or "") in force:
                ran.append({
                    "name": check.get("name"),
                    "target": check.get("target"),
                    "result": check.get("result"),
                    "detail": (check.get("detail") or "")[:400],
                    "schedule_paused": bool(alert_state.get("schedule_paused")),
                })
        passed = sum(1 for r in ran if r["result"] in ("pass", "fixed"))
        failed = len(ran) - passed
        if not ran:
            message = "No matching check ran (it may be disabled or no longer exists)"
        elif failed == 0:
            message = f"Re-ran {len(ran)} check(s) — all passing"
        else:
            message = f"Re-ran {len(ran)} check(s) — {passed} ok, {failed} still failing (no AI remediation)"
        return {
            "ok": True,
            "message": message,
            "ran": len(ran),
            "results": ran,
            "summary": report.get("summary", {}),
        }

    def _handle_alert_toggle_enabled(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        rule_id = str(payload.get("id") or "").strip()
        if not rule_id:
            raise ValueError("id is required")
        enabled = bool(payload.get("enabled", True))
        config = load_json_file(self.config_path, default={})
        rules = config.get("alert_rules", [])
        found = False
        for rule in rules:
            if rule.get("id") == rule_id or rule.get("name") == rule_id:
                rule["enabled"] = enabled
                found = True
                break
        if not found:
            raise ValueError(f"Check not found: {rule_id}")
        save_json_file(self.config_path, config)
        snapshot = refresh_status_snapshot_config(config)
        return {
            "ok": True,
            "alert_rules": snapshot.get("alert_rules", []),
            "host_catalog": snapshot.get("host_catalog", {}),
        }

    def _handle_alert_toggle_lock(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        rule_id = str(payload.get("id") or payload.get("name") or "").strip()
        if not rule_id:
            raise ValueError("id or name is required")
        locked = bool(payload.get("locked", True))
        config = load_json_file(self.config_path, default={})
        rules = config.get("alert_rules", [])
        found = False
        for rule in rules:
            if rule.get("id") == rule_id or rule.get("name") == rule_id:
                if locked:
                    rule["locked"] = True
                else:
                    rule.pop("locked", None)
                found = True
                break
        if not found:
            raise ValueError(f"Check not found: {rule_id}")
        save_json_file(self.config_path, config)
        snapshot = refresh_status_snapshot_config(config)
        return {
            "ok": True,
            "alert_rules": snapshot.get("alert_rules", []),
            "host_catalog": snapshot.get("host_catalog", {}),
        }

    def _handle_alert_run_preview(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        name = str(payload.get("name") or "").strip()
        target = str(payload.get("target") or "").strip()
        if not name or not target:
            raise ValueError("name and target are required")
        config = load_json_file(self.config_path, default={})
        normalized = normalize_config(config)
        rules = compile_rules(normalized)
        rule = next(
            (r for r in rules if r.get("name") == name and r.get("target") == target),
            None,
        )
        if not rule:
            raise ValueError(f"No compiled rule for {name!r} on {target!r}")
        host = rule["host"]
        # preview_override: live command typed in the UI input field
        override = str(payload.get("preview_override") or "").strip()
        command = override or rule.get("preview_command") or rule.get("command") or ""
        if not command:
            return {"ok": True, "output": "", "note": "No command configured"}
        check_type = rule.get("type", "ssh")
        timeout = min(int(rule.get("timeout", 30)), 60)
        if check_type == "ssh":
            _ok, output = run_host_command(host, command, timeout=timeout)
        elif check_type == "local":
            _ok, output = run_local(command, timeout=timeout)
        else:
            return {"ok": True, "output": f"(Preview not supported for type: {check_type})"}
        return {"ok": True, "output": output, "ran_at": utc_iso(), "target": target}

    def _handle_agents_settings_save(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = load_json_file(self.config_path, default={})
        existing = {a["name"]: a for a in config.get("agents", [])}
        for update in payload.get("agents", []):
            agent_name = str(update.get("name", "")).strip()
            if agent_name not in existing:
                continue
            model_val = update.get("model")
            if model_val is not None:
                existing[agent_name]["model"] = str(model_val).strip() or None
        config["agents"] = list(existing.values())
        cooldown = payload.get("agent_cooldown_minutes")
        if cooldown is not None:
            config.setdefault("alerting", {})["agent_cooldown_minutes"] = int(cooldown) if str(cooldown).strip() else 60
        # AI pipeline config
        pipeline_payload = payload.get("ai_pipeline")
        if pipeline_payload is not None:
            current = config.get("ai_pipeline", {})
            if "enabled" in pipeline_payload:
                current["enabled"] = bool(pipeline_payload["enabled"])
            for stage in ("analysis", "fix", "eval"):
                if stage in pipeline_payload:
                    stage_cfg = pipeline_payload[stage]
                    current.setdefault(stage, {})
                    if "model" in stage_cfg:
                        current[stage]["model"] = str(stage_cfg["model"]).strip() or None
                    if "agent" in stage_cfg:
                        current[stage]["agent"] = str(stage_cfg["agent"]).strip() or None
            config["ai_pipeline"] = current
        save_json_file(self.config_path, config)
        return {
            "ok": True,
            "agents": config["agents"],
            "alerting": config.get("alerting", {}),
            "ai_pipeline": config.get("ai_pipeline", {}),
        }

    def _handle_host_save(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = load_json_file(self.config_path, default={})
        updated, saved_name = upsert_host_in_config(config, payload)
        save_json_file(self.config_path, updated)
        snapshot = refresh_status_snapshot_config(updated)
        return {
            "ok": True,
            "message": "Host saved",
            "saved_name": saved_name,
            "hosts": snapshot.get("host_catalog", normalize_config(updated).get("hosts", {})),
            "alert_rules": snapshot.get("alert_rules", []),
        }

    def _handle_host_delete(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = load_json_file(self.config_path, default={})
        updated = delete_host_from_config(config, payload)
        save_json_file(self.config_path, updated)
        snapshot = refresh_status_snapshot_config(updated)
        return {
            "ok": True,
            "message": "Host deleted",
            "hosts": snapshot.get("host_catalog", normalize_config(updated).get("hosts", {})),
            "alert_rules": snapshot.get("alert_rules", []),
        }

    def _handle_maintenance_save(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = load_json_file(self.config_path, default={})
        updated = normalize_config(config)
        window = create_maintenance_window(updated, payload)
        save_json_file(self.config_path, updated)
        snapshot = refresh_status_snapshot_config(updated)
        return {
            "ok": True,
            "message": "Maintenance window saved",
            "window": sanitize_maintenance_window(window),
            "maintenance_windows": snapshot.get("maintenance_windows", list_maintenance_windows(updated)),
        }

    def _handle_maintenance_delete(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = load_json_file(self.config_path, default={})
        updated = normalize_config(config)
        delete_maintenance_window(updated, payload)
        save_json_file(self.config_path, updated)
        snapshot = refresh_status_snapshot_config(updated)
        return {
            "ok": True,
            "message": "Maintenance window deleted",
            "maintenance_windows": snapshot.get("maintenance_windows", list_maintenance_windows(updated)),
        }

    def _handle_alertmanager_alerts_api(self) -> dict[str, Any]:
        self._ensure_local_admin()
        config = self._load_config()
        normalized = normalize_config(config)
        sources_map: dict[str, dict[str, Any]] = {}
        for host_name, host in normalized.get("hosts", {}).items():
            url = str(host.get("alertmanager_url") or "").strip()
            if not url:
                continue
            entry = sources_map.setdefault(url, {"url": url, "autodiscovered": True, "hosts": [], "name": ""})
            entry["hosts"].append(host_name)
            if not entry["name"]:
                entry["name"] = host_name
        for manual in config.get("alertmanager_sources", []):
            url = str(manual.get("url") or "").strip()
            if not url:
                continue
            entry = sources_map.setdefault(url, {"url": url, "autodiscovered": False, "hosts": [], "name": ""})
            if not entry.get("autodiscovered"):
                entry["name"] = str(manual.get("name") or "")
        imported_keys: set[str] = set()
        for rule in config.get("alert_rules", []):
            if rule.get("type") == "alertmanager":
                f = rule.get("alertmanager_filter") or {}
                an = str(f.get("alertname") or "").strip()
                rule_url = str(rule.get("alertmanager_url") or "").strip()
                if an and rule_url:
                    imported_keys.add(f"{rule_url}|{an}")
        results = []
        for url, source_info in sources_map.items():
            ok, payload = fetch_alertmanager_alerts(url, normalized.get("hosts", {}))
            if ok:
                alerts = payload if isinstance(payload, list) else []
                for a in alerts:
                    alertname = str(a.get("name") or "").strip()
                    a["imported"] = f"{url}|{alertname}" in imported_keys
                source_info.update({"ok": True, "alerts": alerts, "error": "", "alert_count": len(alerts)})
            else:
                source_info.update({"ok": False, "alerts": [], "error": str(payload), "alert_count": 0})
            results.append(source_info)
        return {"ok": True, "sources": results}

    def _handle_alertmanager_source_save(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        url = str(payload.get("url") or "").strip()
        name = str(payload.get("name") or "").strip()
        if not url:
            raise ValueError("url is required")
        config = self._load_config()
        sources = config.setdefault("alertmanager_sources", [])
        existing = next((s for s in sources if s.get("url") == url), None)
        if existing:
            existing["name"] = name
        else:
            sources.append({"url": url, "name": name, "added_at": utc_iso()})
        save_json_file(self.config_path, config)
        return {"ok": True}

    def _handle_alertmanager_source_delete(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        url = str(payload.get("url") or "").strip()
        if not url:
            raise ValueError("url is required")
        config = self._load_config()
        config["alertmanager_sources"] = [s for s in config.get("alertmanager_sources", []) if s.get("url") != url]
        save_json_file(self.config_path, config)
        return {"ok": True}

    def _handle_alertmanager_import(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_local_admin()
        config = self._load_config()
        alertmanager_url = str(payload.get("alertmanager_url") or "").strip()
        alertname = str(payload.get("alertname") or "").strip()
        if not alertmanager_url or not alertname:
            raise ValueError("alertmanager_url and alertname are required")
        labels = payload.get("labels") or {}
        severity = str(payload.get("severity") or labels.get("severity") or "warning").strip()
        summary = str(payload.get("summary") or payload.get("description") or "").strip()
        alert_filter: dict[str, str] = {"alertname": alertname}
        targets = [hn for hn, h in config.get("hosts", {}).items() if str(h.get("alertmanager_url") or "").strip() == alertmanager_url]
        slug = re.sub(r"[^a-z0-9]+", "_", alertname.lower())[:40].strip("_")
        check_name = f"am_{slug}"
        rule: dict[str, Any] = {
            "name": check_name,
            "description": f"Alertmanager: {alertname}",
            "type": "alertmanager",
            "alertmanager_url": alertmanager_url,
            "alertmanager_filter": alert_filter,
            "filter_silenced": True,
            "filter_inhibited": True,
            "schedule": "*/5 * * * *",
            "severity": severity,
            "targets": targets or list(config.get("hosts", {}).keys()),
            "notifications": True,
            "mobile_notify": True,
            "mobile_visible": True,
            "fix_prompt": (
                f"Alerta de Alertmanager disparada: {alertname}\n\n"
                + (f"Descripción: {summary}\n\n" if summary else "")
                + "Fallo detectado en {host[name]} ({host[address]}):\n{error}\n\n"
                "Analiza la causa de esta alerta e intenta resolverla con el menor cambio posible.\n"
                "Si no puedes resolverla automáticamente, documenta qué has encontrado y por qué no es seguro actuar sin supervisión."
            ),
        }
        updated, _ = upsert_alert_config(config, {"alert_rule": rule})
        ensure_alert_ids(updated)  # imported rules must get a stable id
        save_json_file(self.config_path, updated)
        snapshot = refresh_status_snapshot_config(updated)
        return {
            "ok": True,
            "message": f"Check '{check_name}' importado de Alertmanager alert '{alertname}'",
            "check_name": check_name,
            "alert_rules": snapshot.get("alert_rules", []),
        }

    def do_POST(self) -> None:  # noqa: N802
        routes = {
            "/api/alert": self._handle_alert_save,
            "/api/alert/delete": self._handle_alert_delete,
            "/api/alert/rearm": self._handle_alert_rearm,
            "/api/alert/ack": self._handle_alert_ack,
            "/api/alert/silence": self._handle_alert_silence,
            "/api/external-alert/silence": self._handle_external_alert_silence,
            "/api/alert/rerun": self._handle_alert_rerun,
            "/api/alert/toggle-enabled": self._handle_alert_toggle_enabled,
            "/api/alert/toggle-lock": self._handle_alert_toggle_lock,
            "/api/alert/run-preview": self._handle_alert_run_preview,
            "/api/agents/settings": self._handle_agents_settings_save,
            "/api/host": self._handle_host_save,
            "/api/host/delete": self._handle_host_delete,
            "/api/maintenance": self._handle_maintenance_save,
            "/api/maintenance/delete": self._handle_maintenance_delete,
            "/api/alertmanager/source": self._handle_alertmanager_source_save,
            "/api/alertmanager/source/delete": self._handle_alertmanager_source_delete,
            "/api/alertmanager/import": self._handle_alertmanager_import,
            "/api/mobile/admin/settings": self._handle_mobile_admin_settings,
            "/api/mobile/admin/api-keys/create": self._handle_mobile_api_key_create,
            "/api/mobile/admin/api-keys/revoke": self._handle_mobile_api_key_revoke,
            "/api/mobile/admin/devices/revoke": self._handle_mobile_device_revoke,
            "/api/mobile/admin/test-push": self._handle_mobile_test_push,
            "/api/mobile/admin/push-settings": self._handle_mobile_push_settings,
            "/api/mobile/device/register": self._handle_mobile_device_register,
            "/api/mobile/action/ack": self._handle_mobile_ack,
            "/api/mobile/action/silence": self._handle_mobile_silence,
            "/api/mobile/action/rerun": self._handle_mobile_rerun,
            "/api/ingest/alertmanager": self._handle_ingest_alertmanager,
            "/api/ingest/grafana": self._handle_ingest_grafana,
            "/api/ingest/generic": self._handle_ingest_generic,
            "/api/problems/ack": self._handle_problem_ack,
            "/api/problems/comment": self._handle_problem_comment,
            "/api/datasource": self._handle_datasource_save,
            "/api/datasource/token": self._handle_datasource_token,
            "/api/datasource/delete": self._handle_datasource_delete,
            "/api/datasource/test": self._handle_datasource_test,
            "/api/rule": self._handle_rule_save,
            "/api/rule/delete": self._handle_rule_delete,
            "/api/integrations/jira": self._handle_jira_save,
            "/api/integrations/jira/test": self._handle_jira_test,
        }
        request_path = self._request_path()
        handler = routes.get(request_path)
        if handler is None:
            self._write_json({"error": "not found"}, 404)
            return
        try:
            # Ingest endpoints are token-authenticated and reached from remote
            # sources, so they bypass the localhost/CSRF admin-origin guard.
            # Mobile non-admin endpoints already carry their own API-key auth.
            is_ingest = request_path.startswith("/api/ingest/")
            is_mobile_user = request_path.startswith("/api/mobile/") and not request_path.startswith("/api/mobile/admin/")
            if not is_ingest and not is_mobile_user:
                self._ensure_admin_post_origin()
            payload = self._read_json_body()
            response = handler(payload)
            self._write_json(response, 200)
        except PermissionError as exc:
            self._write_json({"error": str(exc)}, 401)
        except ValueError as exc:
            self._write_json({"error": str(exc)}, 400)
        except Exception:  # noqa: BLE001
            log.exception("Failed to handle %s", request_path)
            self._write_json({"error": "internal server error"}, 500)

    def log_message(self, fmt: str, *args: Any) -> None:
        log.debug("ui %s", fmt % args)


def serve_ui(config: dict[str, Any], config_path: Path | None = None) -> None:
    ui_config = config.get("ui", {})
    host = ui_config.get("serve_host", "127.0.0.1")
    port = ui_config.get("serve_port", 8787)
    status_path = Path(ui_config.get("status_file", str(STATUS_FILE)))
    StatusHandler.report_path = status_path
    StatusHandler.config_path = config_path or CHECKS_FILE
    StatusHandler.trusted_proxies = tuple(ui_config.get("trusted_proxies", ["127.0.0.1", "::1"]))
    mobile_hostname = str(get_mobile_config(config).get("public_hostname") or "").strip()
    allowed_hosts = [str(item) for item in ui_config.get("allowed_hosts", [])]
    if mobile_hostname:
        allowed_hosts.append(mobile_hostname)
    StatusHandler.allowed_hosts = tuple(allowed_hosts)
    server = ThreadingHTTPServer((host, port), StatusHandler)
    tls_enabled = bool(ui_config.get("tls_enabled", False))
    scheme = "http"
    if tls_enabled:
        certfile = str(ui_config.get("tls_certfile") or "").strip()
        keyfile = str(ui_config.get("tls_keyfile") or "").strip()
        if not certfile or not keyfile:
            raise FileNotFoundError("TLS is enabled but tls_certfile/tls_keyfile are not configured")
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=certfile, keyfile=keyfile)
        server.socket = context.wrap_socket(server.socket, server_side=True)
        scheme = "https"
    log.info("Serving status API on %s://%s:%s", scheme, host, port)
    server.serve_forever()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RootCause checker")
    parser.add_argument("--config", default=str(CHECKS_FILE), help="Path to config JSON")
    parser.add_argument("--serve", action="store_true", help="Expose latest status report over HTTP")
    parser.add_argument("--add-ingest-token", metavar="NAME", help="Generate a webhook ingest token, store its hash, and print the raw token once")
    parser.add_argument("--safety-hook", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.safety_hook:
        sys.exit(run_safety_hook())
    config_path = Path(args.config)
    raw_config = load_json_file(config_path, default={})
    changed = ensure_alert_ids(raw_config)
    # One-shot migration to the datasource/rules + orchestrator model.
    changed = migrate_to_datasources(raw_config) or changed
    if "rules" not in raw_config:
        raw_config["rules"] = []
        changed = True
    native_engine = raw_config.setdefault("native_engine", {})
    if "enabled" not in native_engine:
        native_engine["enabled"] = False  # orchestrator-first: checks off by default
        changed = True
    if changed:
        save_json_file(config_path, raw_config)
    if args.add_ingest_token:
        raw_token, record = create_ingest_token_record(args.add_ingest_token)
        get_ingest_config(raw_config).setdefault("tokens", []).append(record)
        save_json_file(config_path, raw_config)
        print(f"Ingest token '{record['name']}' created (id {record['id']}).")
        print(f"Raw token (store it now, it is not recoverable):\n  {raw_token}")
        return
    config = normalize_config(raw_config)
    if args.serve:
        serve_ui(config, config_path)
        return
    run_checks(config)


if __name__ == "__main__":
    main()
