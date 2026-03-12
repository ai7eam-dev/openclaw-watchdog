from __future__ import annotations

from .actions import send_escalation
from .models import EvaluatedSession, NotificationPolicy


def notify_escalation(openclaw_bin: str, notify: NotificationPolicy, session: EvaluatedSession, dry_run: bool = False) -> tuple[bool, str]:
    return send_escalation(openclaw_bin, notify, session, dry_run=dry_run)
