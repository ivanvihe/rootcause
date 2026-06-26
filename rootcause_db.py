#!/usr/bin/env python3
"""SQLite-backed document store for RootCause config and runtime state.

RootCause used to persist everything as loose JSON files next to the script
(checks.json, rootcause_state.json, rootcause_status.json, …). This module
replaces those files with a single SQLite database, ``rootcause.db``, holding a
``documents`` key/value table: one row per former file, with the JSON payload
kept verbatim as a blob.

Design goals:
  - **Document store, not a normalized schema.** Each former JSON file becomes
    one row, so the rest of the code can keep treating config/state as nested
    dicts. ``DOC_FOR_FILENAME`` maps the legacy filenames to document names.
  - **Transparent migration.** On first use, any legacy JSON file still on disk
    is imported into its document (non-destructively — the file is left in
    place), so an existing install keeps its config and state.
  - **Thread-safe.** A fresh connection is opened per call with WAL mode and a
    busy timeout, so the ThreadingHTTPServer can read/write concurrently.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).parent
DB_FILE = SCRIPT_DIR / "rootcause.db"

# Legacy JSON filename -> document name in the kv store. Every config/state blob
# that used to live in its own file is now a row in `documents`. Code keeps
# passing the old Path objects around; load/save dispatch on the filename.
DOC_FOR_FILENAME: dict[str, str] = {
    "checks.json": "config",
    "rootcause_state.json": "state",
    "rootcause_status.json": "status",
    "rootcause_history.json": "history",
    "rootcause_agent_calls.json": "agent_calls",
    "rootcause_metrics_counters.json": "metrics_counters",
    "rootcause_problems.json": "problems",
    "rootcause_ping_stats.json": "ping_stats",
    "rootcause_probe_cache.json": "probe_cache",
}

_init_lock = threading.Lock()
_initialized = False


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def doc_name_for(path: Any) -> str | None:
    """Return the document name for a legacy JSON path, or None if unmapped."""
    try:
        return DOC_FOR_FILENAME.get(Path(path).name)
    except TypeError:
        return None


def init_db() -> None:
    """Create the schema (idempotent) and import any legacy JSON files once."""
    global _initialized
    with _init_lock:
        if _initialized:
            return
        conn = _connect()
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS documents ("
                "name TEXT PRIMARY KEY, data TEXT NOT NULL, updated_at TEXT NOT NULL)"
            )
            conn.commit()
        finally:
            conn.close()
        _import_legacy_json()
        _initialized = True


def _ensure_init() -> None:
    if not _initialized:
        init_db()


def _import_legacy_json() -> None:
    """Migrate on-disk JSON files into their documents (skip ones already in DB).

    Non-destructive: the original file is left untouched, so the migration can be
    re-run / rolled back. A document already present in the DB always wins.
    """
    conn = _connect()
    try:
        existing = {row[0] for row in conn.execute("SELECT name FROM documents")}
        for filename, doc in DOC_FOR_FILENAME.items():
            if doc in existing:
                continue
            path = SCRIPT_DIR / filename
            if not path.exists():
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            conn.execute(
                "INSERT OR REPLACE INTO documents(name, data, updated_at) VALUES (?, ?, ?)",
                (doc, json.dumps(data, ensure_ascii=False, sort_keys=True), _now_iso()),
            )
        conn.commit()
    finally:
        conn.close()


def load_doc(name: str, default: Any = None) -> Any:
    _ensure_init()
    conn = _connect()
    try:
        row = conn.execute("SELECT data FROM documents WHERE name = ?", (name,)).fetchone()
    finally:
        conn.close()
    if row is None:
        return {} if default is None else default
    try:
        return json.loads(row[0])
    except json.JSONDecodeError:
        return {} if default is None else default


def save_doc(name: str, data: Any) -> None:
    _ensure_init()
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2)
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO documents(name, data, updated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at",
            (name, payload, _now_iso()),
        )
        conn.commit()
    finally:
        conn.close()


def doc_exists(name: str) -> bool:
    _ensure_init()
    conn = _connect()
    try:
        row = conn.execute("SELECT 1 FROM documents WHERE name = ?", (name,)).fetchone()
    finally:
        conn.close()
    return row is not None


def delete_doc(name: str) -> None:
    _ensure_init()
    conn = _connect()
    try:
        conn.execute("DELETE FROM documents WHERE name = ?", (name,))
        conn.commit()
    finally:
        conn.close()
