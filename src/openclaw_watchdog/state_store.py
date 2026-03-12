from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import SessionWatchState


def load_state(path: Path) -> dict[str, SessionWatchState]:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text())
    out: dict[str, SessionWatchState] = {}
    for key, value in (raw.items() if isinstance(raw, dict) else []):
        out[str(key)] = SessionWatchState(**value)
    return out


def save_state(path: Path, state: dict[str, SessionWatchState]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = {key: asdict(value) for key, value in state.items()}
    path.write_text(json.dumps(raw, ensure_ascii=False, indent=2))
