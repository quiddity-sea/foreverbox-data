#!/usr/bin/env python3
"""
Unified sync daemon for the Foreverbox Council Library.

Syncs data from Hermes to the council-library API:
  sync sessions  — new conversation turns → Sanctum
  sync files     — new/changed files in Quiddity Lore Sea → Commons
  sync status    — report pending counts

Usage:
  python3 sync_daemon.py sync sessions
  python3 sync_daemon.py sync files
  python3 sync_daemon.py sync all
  python3 sync_daemon.py status

Credentials from /foreverbox_data/.env (FOREVERBOX_API_KEY, DB_PASSWORD).
API URL from /foreverbox_data/profiles/leon/foreverbox.json.
"""

from __future__ import annotations

import json
import hashlib
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# ── Configuration ────────────────────────────────────────────────────────────

ROOT = Path("/foreverbox_data")
API_URL = "http://localhost:8080/v1"
API_KEY = os.environ.get("FOREVERBOX_API_KEY", "dev-key-change-in-production")
STATE_FILE = ROOT / "sync" / "sync_state.json"
PROFILES = ["leon", "zeon7", "gemma", "otec"]
SESSION_DB_GLOB = "profiles/{agent}/state.db"
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"sessions": {}, "files": {}}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def api_headers(agent_slug: str) -> dict:
    return {
        "Authorization": f"Bearer {API_KEY}",
        "X-Agent-ID": agent_slug,
        "Content-Type": "application/json",
    }


def post_with_retry(url: str, json_payload: dict, headers: dict, timeout: int = 10) -> tuple[bool, str]:
    """POST with retry logic. Returns (ok: bool, error_text: str)."""
    last_error = ""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.post(url, json=json_payload, headers=headers, timeout=timeout)
            if r.ok:
                return True, ""
            last_error = r.text[:200]
        except requests.RequestException as e:
            last_error = str(e)
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_BACKOFF * attempt)
    return False, last_error


# ── Session Sync ─────────────────────────────────────────────────────────────

def sync_sessions(agent: str | None = None) -> dict:
    """Sync new conversation turns for one or all agents."""
    agents = [agent] if agent else PROFILES
    state = load_state()
    results = {}

    for ag in agents:
        db_path = ROOT / SESSION_DB_GLOB.format(agent=ag)
        if not db_path.exists():
            results[ag] = {"error": f"Session DB not found: {db_path}"}
            continue

        last_id = state.get("sessions", {}).get(ag, {}).get("last_message_id", 0)
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row

        try:
            rows = conn.execute(
                "SELECT id, session_id, role, content, timestamp "
                "FROM messages WHERE id > ? AND role IN ('user', 'assistant') "
                "AND compacted = 0 "
                "ORDER BY id ASC",
                (last_id,),
            ).fetchall()
        except sqlite3.OperationalError as e:
            results[ag] = {"error": str(e), "synced": 0}
            conn.close()
            continue

        if not rows:
            results[ag] = {"synced": 0, "message": "No new messages"}
            conn.close()
            continue

        synced = 0
        errors = 0
        max_id = last_id
        seq_number = last_id + 1

        for row in rows:
            msg_id = row["id"]
            sid = row["session_id"]
            role = row["role"]
            content = row["content"]

            if not content:
                max_id = max(max_id, msg_id)
                continue

            # Post each message individually with role and content_text
            payload = {
                "role": role,
                "content_text": content[:5000],
                "message_seq": seq_number,
            }

            ok, err = post_with_retry(
                f"{API_URL}/sanctum/conversations/{sid}/messages",
                payload,
                api_headers(ag),
                timeout=10,
            )

            if ok:
                synced += 1
            else:
                errors += 1

            seq_number += 1
            max_id = max(max_id, msg_id)

        # Update state
        if "sessions" not in state:
            state["sessions"] = {}
        state["sessions"][ag] = {
            "last_message_id": max_id,
            "last_sync": datetime.now(timezone.utc).isoformat(),
        }
        save_state(state)

        results[ag] = {"synced": synced, "errors": errors, "messages": max_id - last_id}
        conn.close()

    return results


# ── File Sync ────────────────────────────────────────────────────────────────

def sync_files() -> dict:
    """Sync new/changed files from the Quiddity Lore Sea to Commons."""

    sea_root = ROOT / "Quiddity_Lore_Sea"
    state = load_state()
    file_state = state.get("files", {})
    synced = 0
    errors = 0
    details = []

    for file_path in sea_root.rglob("*"):
        if not file_path.is_file():
            continue
        if any(p.startswith(".") for p in file_path.parts):
            continue
        # Fix: Windows Zone.Identifier files end with :Zone.Identifier
        if file_path.name.endswith(":Zone.Identifier"):
            continue

        rel_path = str(file_path.relative_to(sea_root))
        file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()

        prev = file_state.get(rel_path, {})
        if prev.get("hash") == file_hash:
            continue  # unchanged

        # Fix: Use leon as the agent for file sync (Leon is the Producer)
        ok, err = post_with_retry(
            f"{API_URL}/commons/files/sync",
            {"paths": [rel_path], "organise": True},
            api_headers("leon"),
            timeout=30,
        )

        if ok:
            synced += 1
            file_state[rel_path] = {
                "hash": file_hash,
                "synced_at": datetime.now(timezone.utc).isoformat(),
            }
        else:
            errors += 1
            details.append({"path": rel_path, "status": "failed", "error": err})

    state["files"] = file_state
    save_state(state)

    return {"synced": synced, "errors": errors, "details": details}


# ── Status ───────────────────────────────────────────────────────────────────

def show_status() -> dict:
    """Show pending sync counts."""
    state = load_state()
    status = {"sessions": {}, "files": {}}

    for ag in PROFILES:
        db_path = ROOT / SESSION_DB_GLOB.format(agent=ag)
        if not db_path.exists():
            status["sessions"][ag] = "DB not found"
            continue

        last_id = state.get("sessions", {}).get(ag, {}).get("last_message_id", 0)
        conn = sqlite3.connect(str(db_path))
        count = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE id > ? AND compacted = 0", (last_id,)
        ).fetchone()[0]
        conn.close()
        status["sessions"][ag] = {
            "pending_messages": count,
            "last_sync": state.get("sessions", {}).get(ag, {}).get("last_sync", "never"),
        }

    sea_root = ROOT / "Quiddity_Lore_Sea"
    if sea_root.exists():
        file_state = state.get("files", {})
        pending = 0
        for fp in sea_root.rglob("*"):
            if not fp.is_file():
                continue
            if any(p.startswith(".") for p in fp.parts):
                continue
            if fp.name.endswith(":Zone.Identifier"):
                continue
            rel = str(fp.relative_to(sea_root))
            if rel not in file_state:
                pending += 1
        status["files"]["pending"] = pending

    return status


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sync_daemon.py <sync|status> [sessions|files|all] [agent]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "status":
        result = show_status()
        print(json.dumps(result, indent=2))
    elif cmd == "sync":
        target = sys.argv[2] if len(sys.argv) > 2 else "all"
        agent = sys.argv[3] if len(sys.argv) > 3 else None

        if target in ("sessions", "all"):
            r = sync_sessions(agent)
            print(f"Sessions: {json.dumps(r, indent=2)}")
        if target in ("files", "all"):
            r = sync_files()
            print(f"Files: {json.dumps(r, indent=2)}")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
