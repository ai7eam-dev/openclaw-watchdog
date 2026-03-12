from __future__ import annotations


def parent_session_key(session_key: str) -> str | None:
    parts = session_key.split(":")
    if len(parts) < 3 or parts[0] != "agent":
        return None
    agent_id = parts[1]

    # Canonical top-level interactive session.
    main_key = f"agent:{agent_id}:main"
    if session_key == main_key:
        return None

    # Prefer main session for derived runs like cron/run/subagent descendants.
    return main_key
