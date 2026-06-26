#!/usr/bin/env python3
"""Unified problem model and store for RootCause.

Phase 0 of the "RootCause as a frontend/orchestrator" redesign. Instead of the
native check engine owning every alert, RootCause normalizes problems coming from
external systems (today Alertmanager; later Prometheus, Zabbix, Elastic, and a
webhook receiver) into a single :class:`Problem` model and persists them in a
dedicated store with dedupe + history.

This module is intentionally standalone — it has no dependency on
``rootcause_checker`` so it can be imported from there without a circular import
and unit-tested in isolation. It only does data modelling + persistence; the
actual network fetching lives in the connectors (see :class:`Connector`).
"""

from __future__ import annotations

import hashlib
import json
import re
from abc import ABC, abstractmethod

import rootcause_db
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HostResolver = Callable[[dict[str, Any]], "str | None"]

# Severity ranking so the store and UI can sort "worst first" consistently
# regardless of which source a problem came from.
SEVERITY_ORDER = {
    "critical": 0,
    "high": 1,
    "warning": 2,
    "info": 3,
    "unknown": 4,
}

HISTORY_LIMIT = 1000


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_severity(value: Any) -> str:
    """Map source-specific severity strings onto RootCause's canonical levels."""
    text = str(value or "").strip().lower()
    if text in SEVERITY_ORDER:
        return text
    aliases = {
        "crit": "critical",
        "disaster": "critical",
        "emergency": "critical",
        "error": "high",
        "average": "high",
        "major": "high",
        "warn": "warning",
        "minor": "warning",
        "information": "info",
        "informational": "info",
        "notice": "info",
        "ok": "info",
    }
    return aliases.get(text, "warning" if text else "unknown")


@dataclass
class Problem:
    """A normalized problem from any source.

    The store keys problems by ``(source, fingerprint)`` so the same upstream
    alert is deduplicated across polls/webhooks. ``status`` is ``problem`` while
    active and flips to ``resolved`` when the source stops reporting it (pull)
    or sends an explicit resolved event (push).
    """

    source: str
    fingerprint: str
    name: str
    severity: str = "warning"
    status: str = "problem"  # problem | resolved
    datasource_id: str = ""  # which configured datasource produced this problem
    host: str | None = None
    summary: str = ""
    description: str = ""
    labels: dict[str, Any] = field(default_factory=dict)
    annotations: dict[str, Any] = field(default_factory=dict)
    value: str = ""
    source_url: str = ""  # link back to the source (generatorURL, dashboard, ...)
    started_at: str | None = None
    resolved_at: str | None = None
    silenced: bool = False
    # Store-managed bookkeeping (set/preserved by ProblemStore).
    acknowledged: bool = False
    acknowledged_by: str = ""
    comments: list[dict[str, Any]] = field(default_factory=list)
    first_seen: str | None = None
    last_seen: str | None = None

    def __post_init__(self) -> None:
        self.severity = normalize_severity(self.severity)
        if not self.fingerprint:
            self.fingerprint = self.compute_fingerprint()

    @property
    def key(self) -> str:
        return f"{self.source}:{self.fingerprint}"

    @property
    def severity_rank(self) -> int:
        return SEVERITY_ORDER.get(self.severity, SEVERITY_ORDER["unknown"])

    def compute_fingerprint(self) -> str:
        """Stable fallback fingerprint when the source doesn't provide one."""
        basis = json.dumps(
            {"source": self.source, "name": self.name, "host": self.host, "labels": self.labels},
            sort_keys=True,
            default=str,
        )
        return hashlib.sha1(basis.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        data = {
            "source": self.source,
            "fingerprint": self.fingerprint,
            "key": self.key,
            "name": self.name,
            "severity": self.severity,
            "severity_rank": self.severity_rank,
            "status": self.status,
            "datasource_id": self.datasource_id,
            "host": self.host,
            "summary": self.summary,
            "description": self.description,
            "labels": self.labels,
            "annotations": self.annotations,
            "value": self.value,
            "source_url": self.source_url,
            "started_at": self.started_at,
            "resolved_at": self.resolved_at,
            "silenced": self.silenced,
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "comments": self.comments,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
        }
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Problem":
        return cls(
            source=str(data.get("source") or "unknown"),
            fingerprint=str(data.get("fingerprint") or ""),
            name=str(data.get("name") or "unnamed"),
            severity=str(data.get("severity") or "warning"),
            status=str(data.get("status") or "problem"),
            datasource_id=str(data.get("datasource_id") or ""),
            host=data.get("host"),
            summary=str(data.get("summary") or ""),
            description=str(data.get("description") or ""),
            labels=dict(data.get("labels") or {}),
            annotations=dict(data.get("annotations") or {}),
            value=str(data.get("value") or ""),
            source_url=str(data.get("source_url") or ""),
            started_at=data.get("started_at"),
            resolved_at=data.get("resolved_at"),
            silenced=bool(data.get("silenced")),
            acknowledged=bool(data.get("acknowledged")),
            acknowledged_by=str(data.get("acknowledged_by") or ""),
            comments=list(data.get("comments") or []),
            first_seen=data.get("first_seen"),
            last_seen=data.get("last_seen"),
        )


def normalize_alertmanager_alert(raw: dict[str, Any]) -> Problem:
    """Convert a dict produced by RootCause's ``fetch_alertmanager_alerts`` into a
    :class:`Problem`.

    Alertmanager's ``/api/v2/alerts`` only returns active alerts, so the result
    is always ``status="problem"``; resolution is inferred by the store when a
    fingerprint disappears from a later poll.
    """
    labels = dict(raw.get("labels") or {})
    annotations = dict(raw.get("annotations") or {})
    return Problem(
        source="alertmanager",
        fingerprint=str(raw.get("fingerprint") or ""),
        name=str(raw.get("name") or labels.get("alertname") or "unnamed"),
        severity=str(raw.get("severity") or labels.get("severity") or "warning"),
        status="problem",
        host=raw.get("host"),
        summary=str(raw.get("summary") or ""),
        description=str(raw.get("description") or ""),
        labels=labels,
        annotations=annotations,
        source_url=str(raw.get("generator_url") or ""),
        started_at=raw.get("starts_at"),
        silenced=bool(raw.get("silenced")),
    )


def _default_host_resolver(labels: dict[str, Any]) -> str | None:
    """Best-effort host extraction from labels when no catalog resolver is given."""
    for key in ("host", "hostname", "instance", "node", "target"):
        value = labels.get(key)
        if value:
            return str(value).split(":")[0]
    return None


def _normalize_prom_style_alerts(
    alerts: list[dict[str, Any]],
    source: str,
    host_resolver: HostResolver | None = None,
) -> list[Problem]:
    """Normalize Alertmanager-/Grafana-style webhook ``alerts[]`` into Problems.

    Both Alertmanager (webhook v4) and Grafana unified alerting POST a list of
    alerts each carrying ``status`` (``firing``/``resolved``), ``labels``,
    ``annotations`` and timing fields, so a single parser covers both.
    """
    resolve = host_resolver or _default_host_resolver
    problems: list[Problem] = []
    for item in alerts:
        labels = dict(item.get("labels") or {})
        annotations = dict(item.get("annotations") or {})
        status = "resolved" if str(item.get("status") or "").lower() == "resolved" else "problem"
        problems.append(
            Problem(
                source=source,
                fingerprint=str(item.get("fingerprint") or ""),
                name=str(labels.get("alertname") or annotations.get("title") or "unnamed"),
                severity=str(labels.get("severity") or "warning"),
                status=status,
                host=resolve(labels),
                summary=str(annotations.get("summary") or annotations.get("description") or annotations.get("title") or ""),
                description=str(annotations.get("description") or annotations.get("summary") or ""),
                labels=labels,
                annotations=annotations,
                value=str(item.get("valueString") or item.get("value") or ""),
                source_url=str(item.get("generatorURL") or item.get("panelURL") or item.get("dashboardURL") or ""),
                started_at=item.get("startsAt"),
                resolved_at=item.get("endsAt") if status == "resolved" else None,
            )
        )
    return problems


def normalize_alertmanager_webhook(
    payload: dict[str, Any],
    host_resolver: HostResolver | None = None,
) -> list[Problem]:
    """Parse an Alertmanager webhook v4 payload into Problems (push path)."""
    return _normalize_prom_style_alerts(payload.get("alerts") or [], "alertmanager", host_resolver)


def normalize_grafana_webhook(
    payload: dict[str, Any],
    host_resolver: HostResolver | None = None,
) -> list[Problem]:
    """Parse a Grafana unified-alerting webhook payload into Problems (push path)."""
    return _normalize_prom_style_alerts(payload.get("alerts") or [], "grafana", host_resolver)


def normalize_generic_webhook(
    payload: dict[str, Any],
    host_resolver: HostResolver | None = None,
) -> list[Problem]:
    """Parse a generic problem payload (Zabbix media type, scripts, Elastic).

    Accepts either a single problem object or ``{"problems": [...]}`` /
    ``{"alerts": [...]}``. Recognized fields per item:
    ``name``/``alertname``, ``severity``, ``status`` (``problem``/``firing`` vs
    ``resolved``/``ok``), ``host``, ``summary``, ``description``, ``labels``,
    ``fingerprint``, ``value``, ``source``, ``url``.
    """
    resolve = host_resolver or _default_host_resolver
    if isinstance(payload.get("problems"), list):
        items = payload["problems"]
    elif isinstance(payload.get("alerts"), list):
        items = payload["alerts"]
    else:
        items = [payload]

    problems: list[Problem] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        labels = dict(item.get("labels") or {})
        raw_status = str(item.get("status") or item.get("state") or "problem").lower()
        status = "resolved" if raw_status in ("resolved", "ok", "recovered", "0") else "problem"
        host = item.get("host") or labels.get("host") or resolve(labels)
        problems.append(
            Problem(
                source=str(item.get("source") or "generic"),
                fingerprint=str(item.get("fingerprint") or item.get("id") or ""),
                name=str(item.get("name") or item.get("alertname") or labels.get("alertname") or "unnamed"),
                severity=str(item.get("severity") or labels.get("severity") or "warning"),
                status=status,
                host=str(host) if host else None,
                summary=str(item.get("summary") or item.get("message") or ""),
                description=str(item.get("description") or item.get("summary") or ""),
                labels=labels,
                annotations=dict(item.get("annotations") or {}),
                value=str(item.get("value") or ""),
                source_url=str(item.get("url") or item.get("source_url") or ""),
                started_at=item.get("started_at") or item.get("startsAt"),
                resolved_at=item.get("resolved_at") if status == "resolved" else None,
            )
        )
    return problems


def problem_matches(matcher: dict[str, Any], problem: Problem) -> bool:
    """Whether a problem matches a rule's ``problem_match`` block.

    The matcher reframes a rule's classic "trigger" as a selector over incoming
    problems instead of an active check. Recognized facets (all optional):
    ``source`` (list), ``severity`` (list of levels), ``name`` (exact),
    ``name_regex``, ``host`` (list) and ``labels`` (dict of exact label values).
    ``match`` is ``all`` (default) or ``any`` over the *specified* facets.
    """
    facets: list[bool] = []

    def add(specified: bool, ok: bool) -> None:
        if specified:
            facets.append(ok)

    sources = matcher.get("source")
    add(sources is not None, problem.source in _as_list(sources))

    sevs = matcher.get("severity")
    add(sevs is not None, problem.severity in {normalize_severity(s) for s in _as_list(sevs)})

    name = matcher.get("name")
    add(name is not None, problem.name == name)

    name_rx = matcher.get("name_regex")
    add(name_rx is not None, bool(name_rx and re.search(str(name_rx), problem.name)))

    hosts = matcher.get("host")
    add(hosts is not None, (problem.host or "") in _as_list(hosts))

    labels = matcher.get("labels")
    if labels is not None:
        add(True, all(str(problem.labels.get(k)) == str(v) for k, v in labels.items()))

    if not facets:
        return False  # an empty matcher must not match everything (safety)
    mode = str(matcher.get("match") or "all").lower()
    return any(facets) if mode == "any" else all(facets)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _round_value(value: str) -> str:
    """Round a numeric value string to drop float jitter; pass through non-numbers."""
    try:
        return f"{float(value):.2f}".rstrip("0").rstrip(".")
    except (TypeError, ValueError):
        return str(value)


def _detect_problem_changes(existing: dict[str, Any], prob: "Problem") -> list[str]:
    """Narratable changes between a stored problem and its newest poll.

    Produces system-comment text like "Update: severity changed warning → high"
    so RootCause can post a running commentary onto the problem (and its ticket).
    """
    notes: list[str] = []
    old_sev = str(existing.get("severity") or "")
    if old_sev and old_sev != prob.severity:
        notes.append(f"Update: severity changed {old_sev} → {prob.severity}")
    old_val, new_val = _round_value(existing.get("value") or ""), _round_value(prob.value or "")
    if old_val and new_val and old_val != new_val:
        notes.append(f"Update: value changed {old_val} → {new_val}")
    return notes


class Connector(ABC):
    """A pull source of problems.

    Phase 0 only ships the Alertmanager path (wrapped by the checker), but every
    future source (Prometheus ``/api/v1/alerts``, Zabbix ``problem.get``, ...)
    implements this same interface so the run loop can treat them uniformly.
    """

    source: str = "unknown"

    @abstractmethod
    def poll(self) -> list[Problem]:
        """Fetch the current set of active problems from this source."""
        raise NotImplementedError


class ProblemStore:
    """Persisted active problems + rolling history, deduped by ``(source, fp)``."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    # ── persistence ──────────────────────────────────────────────────────────
    # Problems live in SQLite (rootcause.db) now; self.path is kept only as the
    # stable document identity for the kv store — see rootcause_db.
    def _load(self) -> dict[str, Any]:
        doc = rootcause_db.doc_name_for(self.path)
        if doc is not None:
            data = rootcause_db.load_doc(doc, {"active": {}, "history": []})
        elif not self.path.exists():
            return {"active": {}, "history": []}
        else:
            try:
                with open(self.path, encoding="utf-8") as handle:
                    data = json.load(handle)
            except (json.JSONDecodeError, OSError):
                return {"active": {}, "history": []}
        data.setdefault("active", {})
        data.setdefault("history", [])
        return data

    def _save(self, data: dict[str, Any]) -> None:
        doc = rootcause_db.doc_name_for(self.path)
        if doc is not None:
            rootcause_db.save_doc(doc, data)
            return
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
        tmp.replace(self.path)  # atomic rename, prevents partial-write corruption

    # ── reads ────────────────────────────────────────────────────────────────
    def active_problems(self) -> list[Problem]:
        data = self._load()
        problems = [Problem.from_dict(p) for p in data.get("active", {}).values()]
        problems.sort(key=lambda p: (p.severity_rank, p.host or "zzzz", p.name))
        return problems

    # ── writes ───────────────────────────────────────────────────────────────
    @staticmethod
    def _scope_of(entry: dict[str, Any]) -> str:
        """Reconciliation scope: the datasource id when set, else the source type.

        Keying by datasource id lets two datasources of the same type (e.g. two
        Prometheus servers) reconcile independently instead of resolving each
        other's problems.
        """
        return str(entry.get("datasource_id") or entry.get("source") or "")

    def sync(self, scope: str, problems: list[Problem], *, now: str | None = None) -> dict[str, list[Problem]]:
        """Reconcile a full poll snapshot for one ``scope`` (datasource id or source).

        Problems present become/stay active (preserving ack/comments and the
        original ``first_seen``); active problems of this scope that are absent
        from ``problems`` are marked resolved and moved to history. Returns the
        transitions: ``{"new": [...], "ongoing": [...], "resolved": [...]}``.
        """
        ts = now or _now_iso()
        data = self._load()
        active: dict[str, dict[str, Any]] = data.get("active", {})

        incoming = {p.key: p for p in problems}
        prior_keys = {k for k, v in active.items() if self._scope_of(v) == scope}

        new: list[Problem] = []
        ongoing: list[Problem] = []
        resolved: list[Problem] = []
        # System updates worth narrating (e.g. severity escalation) — the caller
        # mirrors these as comments on the problem's ticket.
        updates: list[dict[str, Any]] = []

        for key, prob in incoming.items():
            existing = active.get(key)
            if existing:
                # Preserve store-managed bookkeeping across polls.
                prob.first_seen = existing.get("first_seen") or ts
                prob.acknowledged = bool(existing.get("acknowledged"))
                prob.acknowledged_by = str(existing.get("acknowledged_by") or "")
                prob.comments = list(existing.get("comments") or [])
                prob.started_at = prob.started_at or existing.get("started_at")
                prob.last_seen = ts
                # Preserve store-managed annotations (e.g. jira_issue_key,
                # remediation outcome) which the fresh poll doesn't carry.
                prob.annotations = {**(existing.get("annotations") or {}), **(prob.annotations or {})}
                for note in _detect_problem_changes(existing, prob):
                    prob.comments.append({"at": ts, "by": "rootcause-system", "text": note})
                    updates.append({"problem": prob, "text": note})
                active[key] = prob.to_dict()
                ongoing.append(prob)
            else:
                prob.first_seen = ts
                prob.last_seen = ts
                prob.started_at = prob.started_at or ts
                active[key] = prob.to_dict()
                new.append(prob)

        for key in prior_keys - set(incoming):
            entry = active.pop(key)
            prob = Problem.from_dict(entry)
            prob.status = "resolved"
            prob.resolved_at = ts
            prob.last_seen = ts
            resolved.append(prob)
            data.setdefault("history", []).append(prob.to_dict())

        data["history"] = data.get("history", [])[-HISTORY_LIMIT:]
        data["active"] = active
        self._save(data)
        return {"new": new, "ongoing": ongoing, "resolved": resolved, "updates": updates}

    def acknowledge(self, key: str, by: str = "web", *, now: str | None = None) -> bool:
        """Mark an active problem acknowledged (local bookkeeping only)."""
        store = self._load()
        entry = store.get("active", {}).get(key)
        if not entry:
            return False
        entry["acknowledged"] = True
        entry["acknowledged_by"] = by
        entry["acknowledged_at"] = now or _now_iso()
        self._save(store)
        return True

    def annotate(self, key: str, data: dict[str, Any]) -> bool:
        """Merge extra annotations into an active problem (e.g. remediation outcome)."""
        store = self._load()
        entry = store.get("active", {}).get(key)
        if not entry:
            return False
        entry.setdefault("annotations", {}).update({k: str(v) for k, v in data.items()})
        self._save(store)
        return True

    def ingest(self, problems: list[Problem], *, now: str | None = None) -> dict[str, list[Problem]]:
        """Apply pushed problems (webhooks), honoring each one's explicit status.

        Unlike :meth:`sync`, this performs no full reconciliation — a webhook only
        tells us about the problems it carries. ``status="problem"`` upserts an
        active problem (preserving ``first_seen``/ack); ``status="resolved"``
        closes it and moves it to history. Returns the same transition buckets.
        """
        ts = now or _now_iso()
        data = self._load()
        active: dict[str, dict[str, Any]] = data.get("active", {})

        new: list[Problem] = []
        ongoing: list[Problem] = []
        resolved: list[Problem] = []

        for prob in problems:
            key = prob.key
            existing = active.get(key)
            if prob.status == "resolved":
                if existing:
                    closed = Problem.from_dict(existing)
                    closed.status = "resolved"
                    closed.resolved_at = prob.resolved_at or ts
                    closed.last_seen = ts
                    resolved.append(closed)
                    data.setdefault("history", []).append(closed.to_dict())
                    active.pop(key, None)
                continue
            if existing:
                prob.first_seen = existing.get("first_seen") or ts
                prob.acknowledged = bool(existing.get("acknowledged"))
                prob.acknowledged_by = str(existing.get("acknowledged_by") or "")
                prob.comments = list(existing.get("comments") or [])
                prob.started_at = prob.started_at or existing.get("started_at")
                prob.last_seen = ts
                active[key] = prob.to_dict()
                ongoing.append(prob)
            else:
                prob.first_seen = ts
                prob.last_seen = ts
                prob.started_at = prob.started_at or ts
                active[key] = prob.to_dict()
                new.append(prob)

        data["history"] = data.get("history", [])[-HISTORY_LIMIT:]
        data["active"] = active
        self._save(data)
        return {"new": new, "ongoing": ongoing, "resolved": resolved}

    def add_comment(self, key: str, text: str, by: str = "web", *, now: str | None = None) -> bool:
        """Append a free-text comment to an active problem (Zabbix-style)."""
        text = str(text or "").strip()
        if not text:
            return False
        store = self._load()
        entry = store.get("active", {}).get(key)
        if not entry:
            return False
        entry.setdefault("comments", []).append({"at": now or _now_iso(), "by": by, "text": text})
        self._save(store)
        return True
