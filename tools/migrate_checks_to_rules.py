#!/usr/bin/env python3
"""Generate Prometheus alert rules from RootCause's checks.json.

Phase 2 of the "RootCause as a frontend/orchestrator" redesign: detection moves
out of the native check engine into Prometheus + exporters. This script reads
the existing checks and emits, per (check x target):

  - prometheus_query  -> a rule using the query verbatim (already a condition).
  - http / composite-with-http -> a rule on blackbox `probe_success == 0`, and a
    blackbox target you must add to prometheus.yml's blackbox-http job.
  - network_ping      -> a rule on blackbox `probe_success == 0` (icmp module).
  - ssh / local / composite-with-ssh -> a rule on script_exporter
    `script_success == 0`, and a script you must add under
    monitoring/script_exporter/scripts/.

It cannot mechanically translate a shell command into PromQL, so for command
checks it scaffolds the rule + reports the exporter target you must wire up. The
goal is parity validation (run native + rules in parallel), not a black-box port.

Usage:
    python tools/migrate_checks_to_rules.py            # writes the rules file + prints a report
    python tools/migrate_checks_to_rules.py --stdout   # print rules to stdout only
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CHECKS_FILE = REPO / "checks.json"
RULES_FILE = REPO / "monitoring" / "prometheus" / "rules" / "rootcause.rules.yml"

DEFAULT_FOR = "2m"


def _q(value: str) -> str:
    """Quote a PromQL label value."""
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def _composite_kind(rule: dict) -> str:
    kinds = {s.get("type") for s in rule.get("steps", [])}
    if "http" in kinds:
        return "http"
    return "ssh"


def build_rule(rule: dict, target: str, hosts: dict) -> tuple[dict, dict]:
    """Return (prometheus_rule, todo) for one check applied to one host."""
    name = rule.get("name", "unnamed")
    rtype = rule.get("type") or "template"
    severity = rule.get("severity") or "warning"
    alertname = f"{name}".strip()
    common_labels = {"severity": severity, "rootcause_check": name, "host": target}
    annotations = {
        "summary": rule.get("description") or f"{name} on {target}",
        "rootcause_source_type": rtype,
    }
    todo: dict = {}

    if rtype == "composite":
        rtype = _composite_kind(rule)

    # An explicit `prometheus_expr` on the check wins for metric-based checks
    # (disk/memory/load) that have a real node_exporter signal — the generator
    # can't derive PromQL from a shell command, so the check declares it.
    # `{instance}` expands to a regex alternation of the host's known ids so the
    # selector survives the instance-label mismatch between checks.json and
    # prometheus.yml (use it as `instance=~"{instance}"`).
    if rule.get("prometheus_expr"):
        host_cfg = hosts.get(target, {})
        ids = [target, host_cfg.get("prometheus_instance"), host_cfg.get("address")]
        instance_rx = "|".join(dict.fromkeys(str(i) for i in ids if i))
        expr = str(rule["prometheus_expr"]).replace("{instance}", instance_rx)
        if target:
            annotations["instance"] = target
    elif rtype == "prometheus_query" and rule.get("query"):
        expr = rule["query"]
        if target:
            annotations["instance"] = target
    elif rtype == "http":
        url = rule.get("url") or next((s.get("url") for s in rule.get("steps", []) if s.get("url")), "")
        url = url.replace("{host[address]}", str(hosts.get(target, {}).get("address", target)))
        expr = f'probe_success{{instance={_q(url)}}} == 0'
        todo = {"kind": "blackbox-http", "target": url, "check": name, "host": target}
    elif rtype == "network_ping":
        addrs = [t.get("address") for t in rule.get("ping_targets", []) if t.get("address")] or ["8.8.8.8"]
        expr = f'probe_success{{instance={_q(addrs[0])}}} == 0'
        todo = {"kind": "blackbox-icmp", "target": addrs[0], "check": name, "host": target}
    else:  # ssh / local / composite-ssh -> node-exporter textfile collector
        # A host cron runs the check script and writes rootcause_check_success{check,host}
        # to node-exporter's textfile dir (more robust than a bespoke script exporter,
        # and the host already has docker + the SSH key). See monitoring/textfile/.
        expr = f'rootcause_check_success{{check={_q(name)},host={_q(target)}}} == 0'
        todo = {"kind": "script", "script": name, "check": name, "host": target}

    prom_rule = {
        "alert": alertname,
        "expr": expr,
        "for": DEFAULT_FOR,
        "labels": common_labels,
        "annotations": annotations,
    }
    return prom_rule, todo


def render_yaml(rules: list[dict]) -> str:
    lines = [
        "# AUTO-GENERATED from checks.json by tools/migrate_checks_to_rules.py",
        "# Detection migrated out of the native RootCause check engine. Edit the",
        "# generator or checks.json rather than this file by hand.",
        "groups:",
        "  - name: rootcause-migrated",
        "    rules:",
    ]
    for r in rules:
        lines.append(f"      - alert: {r['alert']}")
        lines.append(f"        expr: {r['expr']}")
        lines.append(f"        for: {r['for']}")
        lines.append("        labels:")
        for k, v in r["labels"].items():
            lines.append(f"          {k}: {_q(v)}")
        lines.append("        annotations:")
        for k, v in r["annotations"].items():
            lines.append(f"          {k}: {_q(v)}")
    return "\n".join(lines) + "\n"


# ── config.rules[] generation ────────────────────────────────────────────────
# The Prometheus rules above handle *detection*; this builds the RootCause
# *remediation* rules. Each old alert_rule becomes a config.rules[] entry that
# matches the resulting problem by alertname (== check name) and carries the old
# check's action chain — so the exporters' alerts re-acquire the exact same
# notification + AI-agent remediation the native checks used to run.

# Remediation fields lifted from the old check onto its ai_agent action overlay
# (run_actions reads these overlay keys; see rootcause_checker.run_actions).
_AI_OVERLAY_FIELDS = (
    "fix_prompt",
    "allowed_agents",
    "custom_agents",
    "preferred_model",
    "token_protection",
    "emergency_actions",
    "ai_pipeline",
    "pause_schedule_on_fix_failed",
)


def _rule_id_for(name: str) -> str:
    """Stable, human-readable id so re-running the migration is idempotent."""
    slug = "".join(ch if ch.isalnum() else "_" for ch in str(name).lower()).strip("_")
    return f"rule_{slug or 'unnamed'}"


def build_config_rule(check: dict) -> dict:
    """Translate one legacy alert_rule into a config.rules[] remediation rule."""
    name = check.get("name", "unnamed")
    # Translate the legacy action chain. An ai_agent action gets the check's
    # remediation config folded in as an overlay so the rule is self-contained.
    actions: list[dict] = []
    has_ai = False
    for action in check.get("actions") or []:
        atype = str(action.get("type") or "").lower()
        new_action = dict(action)
        new_action.setdefault("when", action.get("when") or "on_alert")
        if atype == "ai_agent":
            has_ai = True
            for field in _AI_OVERLAY_FIELDS:
                if check.get(field) not in (None, "", [], {}):
                    new_action.setdefault(field, check[field])
        actions.append(new_action)
    # A check with a fix_prompt but no explicit ai_agent action still remediated
    # via the classic single-flow — preserve that as an ai_agent action.
    if not has_ai and check.get("fix_prompt"):
        ai_action = {"type": "ai_agent", "when": "on_alert"}
        for field in _AI_OVERLAY_FIELDS:
            if check.get(field) not in (None, "", [], {}):
                ai_action[field] = check[field]
        actions.append(ai_action)

    return {
        "id": _rule_id_for(name),
        "name": name,
        "enabled": check.get("enabled", True) is not False,
        # Empty = match problems from ANY datasource. Alerts for this check can
        # arrive via either the Alertmanager or Prometheus datasource (push or
        # poll), so we match on the alertname rather than pinning a datasource.
        "datasource_ids": [],
        "trigger": "auto",
        "match": {"name": name},
        "actions": actions,
    }


def build_config_rules(config: dict) -> list[dict]:
    return [build_config_rule(c) for c in config.get("alert_rules", [])]


def write_config_rules(config_path: Path) -> int:
    """Populate checks.json `rules` from `alert_rules`, idempotently (by id).

    Existing rules keep their position; a rule sharing an id is replaced in
    place; new ones are appended. A timestamped .bak is written first.
    """
    import shutil
    from datetime import datetime

    config = json.loads(config_path.read_text())
    generated = build_config_rules(config)
    existing = config.get("rules", [])
    by_id = {r.get("id"): r for r in existing}
    for rule in generated:
        by_id[rule["id"]] = rule
    order = [r.get("id") for r in existing]
    merged = [by_id[i] for i in order if i in by_id]
    merged += [r for r in generated if r["id"] not in order]

    backup = config_path.with_suffix(f".bak-{datetime.now():%Y%m%d-%H%M%S}.json")
    shutil.copyfile(config_path, backup)
    config["rules"] = merged
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {len(generated)} remediation rule(s) into {config_path.name} (backup: {backup.name})")
    return len(generated)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdout", action="store_true", help="print rules instead of writing the file")
    parser.add_argument(
        "--write-config-rules",
        action="store_true",
        help="populate checks.json `rules` (remediation chains) from `alert_rules`",
    )
    parser.add_argument(
        "--config-rules-stdout",
        action="store_true",
        help="print the generated config.rules[] JSON instead of writing checks.json",
    )
    args = parser.parse_args()

    if args.config_rules_stdout:
        config = json.loads(CHECKS_FILE.read_text())
        print(json.dumps(build_config_rules(config), indent=2, ensure_ascii=False))
        return

    config = json.loads(CHECKS_FILE.read_text())
    hosts = config.get("hosts", {})
    prom_rules: list[dict] = []
    todos: list[dict] = []

    for rule in config.get("alert_rules", []):
        targets = rule.get("targets") or [rule.get("target")] or ["localhost"]
        for target in targets:
            if not target:
                continue
            prom_rule, todo = build_rule(rule, target, hosts)
            prom_rules.append(prom_rule)
            if todo:
                todos.append(todo)

    text = render_yaml(prom_rules)
    if args.stdout:
        print(text)
    else:
        RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
        RULES_FILE.write_text(text)
        print(f"Wrote {len(prom_rules)} rules to {RULES_FILE.relative_to(REPO)}")

    # Migration report: what exporter wiring each command/probe check needs.
    blackbox = [t for t in todos if t["kind"].startswith("blackbox")]
    scripts = [t for t in todos if t["kind"] == "script"]
    if blackbox:
        print("\nBlackbox targets to add to prometheus.yml (blackbox-http / icmp job):")
        for t in blackbox:
            print(f"  - [{t['kind']}] {t['check']} ({t['host']}) -> {t['target']}")
    if scripts:
        print("\nscript_exporter scripts to add under monitoring/script_exporter/scripts/:")
        for t in scripts:
            print(f"  - {t['script']}.sh   (check {t['check']} on {t['host']}; must exit non-zero on problem)")
    print("\nReminder: run native checks + these rules in parallel and compare before disabling the native engine.")

    if args.write_config_rules:
        print()
        write_config_rules(CHECKS_FILE)


if __name__ == "__main__":
    main()
