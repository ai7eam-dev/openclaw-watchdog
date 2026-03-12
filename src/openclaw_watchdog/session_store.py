from __future__ import annotations

import glob
import json
from pathlib import Path

from .models import SessionMeta


def _session_index_files(openclaw_root: Path) -> list[Path]:
    pattern = str(openclaw_root / "agents" / "*" / "sessions" / "sessions.json")
    return [Path(p) for p in sorted(glob.glob(pattern))]


def list_sessions(openclaw_root: Path) -> list[SessionMeta]:
    out: list[SessionMeta] = []
    for path in _session_index_files(openclaw_root):
        try:
            raw = json.loads(path.read_text())
        except Exception:
            continue

        entries = raw.items() if isinstance(raw, dict) else []
        for key, entry in entries:
            if not isinstance(entry, dict):
                continue
            dc = entry.get("deliveryContext") or {}
            session_file = entry.get("sessionFile")
            if not session_file and entry.get("sessionId"):
                session_file = str(path.parent / f"{entry['sessionId']}.jsonl")
            out.append(SessionMeta(
                key=str(key or entry.get("sessionKey") or ""),
                agent_id=_agent_id_from_key(str(key or "")),
                session_file=Path(session_file).expanduser() if session_file else None,
                updated_at_ms=entry.get("updatedAt") or entry.get("updatedAtMs"),
                channel=entry.get("channel") or dc.get("channel") or entry.get("lastChannel"),
                account_id=dc.get("accountId") or entry.get("accountId") or entry.get("lastAccountId"),
                to=dc.get("to") or entry.get("to") or entry.get("lastTo"),
                aborted_last_run=bool(entry.get("abortedLastRun", False)),
                system_sent=bool(entry.get("systemSent", False)),
            ))
    return [s for s in out if s.key]


def _agent_id_from_key(key: str) -> str:
    parts = key.split(":")
    if len(parts) >= 2 and parts[0] == "agent":
        return parts[1] or "main"
    return "main"
