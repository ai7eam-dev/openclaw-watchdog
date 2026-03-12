from __future__ import annotations

import json
from pathlib import Path

from .models import LockInfo


def lock_path_for_session(session_file: Path | None) -> Path | None:
    if not session_file:
        return None
    return Path(str(session_file) + ".lock")


def read_lock(session_file: Path | None) -> LockInfo | None:
    lock_path = lock_path_for_session(session_file)
    if not lock_path or not lock_path.exists():
        return None
    created_at_ms = None
    try:
        doc = json.loads(lock_path.read_text())
        created_at_ms = _coerce_ms(doc.get("createdAt") or doc.get("createdAtMs"))
    except Exception:
        created_at_ms = None
    return LockInfo(exists=True, created_at_ms=created_at_ms)


def _coerce_ms(value) -> int | None:
    if value is None:
        return None
    try:
        n = int(value)
        if n < 10_000_000_000:
            return n * 1000
        return n
    except Exception:
        return None
