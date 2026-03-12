from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .models import MessagePreview


def tail_messages(session_file: Path | None) -> tuple[MessagePreview | None, MessagePreview | None]:
    if not session_file or not session_file.exists():
        return None, None

    last_user: MessagePreview | None = None
    last_assistant: MessagePreview | None = None

    try:
        with session_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    doc = json.loads(line)
                except Exception:
                    continue

                role, preview, ts = _extract_message(doc)
                if not role:
                    continue
                if role == "user":
                    last_user = MessagePreview(preview=preview, ts_ms=ts)
                elif role == "assistant":
                    last_assistant = MessagePreview(preview=preview, ts_ms=ts)
    except Exception:
        return None, None

    return last_user, last_assistant


def _extract_message(doc: dict) -> tuple[str | None, str, int | None]:
    inner = doc.get("message") if isinstance(doc.get("message"), dict) else doc
    role = inner.get("role") if isinstance(inner, dict) else None
    if role not in ("user", "assistant"):
        return None, "", None
    ts = _coerce_ms(doc.get("timestamp") or inner.get("timestamp") or doc.get("ts") or inner.get("ts") or inner.get("timeMs"))
    preview = _content_preview(inner.get("content")) or _extract_preview(inner) or _extract_preview(doc)
    return role, preview, ts


def _content_preview(content) -> str:
    if isinstance(content, str):
        return content.strip()[:200]
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("thinking")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
            elif isinstance(item, str) and item.strip():
                parts.append(item.strip())
            if sum(len(p) for p in parts) > 200:
                break
        return " ".join(parts)[:200]
    return ""


def _extract_preview(doc: dict) -> str:
    for key in ("text", "message", "content", "preview"):
        value = doc.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:200]
    return ""


def _coerce_ms(value) -> int | None:
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)
        except Exception:
            pass
    try:
        n = int(value)
        if n < 10_000_000_000:
            return n * 1000
        return n
    except Exception:
        return None
