from __future__ import annotations

import json
import subprocess
import uuid

from .models import EvaluatedSession, NotificationPolicy


TEMPLATES: dict[str, str] = {
    "continue": "继续完成你正在做/上次未完成的任务；如果仍在长任务中，不要放弃，完成后汇报 DONE。",
    "progress": "请用不超过6行汇报当前进度、下一步、预计完成时间；完成请写 DONE；受阻请写 BLOCKED: 原因。",
    "finalize": "如果任务已完成，请给出最终总结与结果位置；否则简短汇报当前进度与下一步。",
}


def send_nudge(openclaw_bin: str, session_key: str, template_id: str, dry_run: bool = False) -> tuple[bool, str]:
    msg = TEMPLATES.get(template_id)
    if not msg:
        return False, f"unknown template: {template_id}"
    args = [
        openclaw_bin, "gateway", "call", "chat.send",
        "--params", json.dumps({
            "sessionKey": session_key,
            "message": msg,
            "deliver": True,
            "timeoutMs": 0,
            "idempotencyKey": str(uuid.uuid4()),
        }, ensure_ascii=False)
    ]
    if dry_run:
        return True, "dry-run"
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode == 0:
        return True, p.stdout.strip() or "ok"
    return False, p.stderr.strip() or p.stdout.strip() or f"rc={p.returncode}"


def send_escalation(openclaw_bin: str, notify: NotificationPolicy, session: EvaluatedSession, dry_run: bool = False) -> tuple[bool, str]:
    if not notify.enabled or not notify.channel or not notify.target:
        return False, "notification disabled"
    msg = (
        f"Watchdog alert: session {session.meta.key} ({session.meta.agent_id}) remains interrupted. "
        f"Reason={session.reason}. Please inspect manually."
    )
    args = [
        openclaw_bin, "message", "send",
        "--channel", notify.channel,
        "--target", notify.target,
        "--message", msg,
        "--json",
    ]
    if notify.silent:
        args.append("--silent")
    if dry_run:
        return True, "dry-run"
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode == 0:
        return True, p.stdout.strip() or "ok"
    return False, p.stderr.strip() or p.stdout.strip() or f"rc={p.returncode}"


def send_session_alert(openclaw_bin: str, session_key: str, interrupted_session_key: str, reason: str, dry_run: bool = False) -> tuple[bool, str]:
    msg = (
        f"Watchdog notice: related session {interrupted_session_key} appears interrupted. "
        f"Reason={reason}. Please inspect or resume manually if needed."
    )
    args = [
        openclaw_bin, "gateway", "call", "chat.send",
        "--params", json.dumps({
            "sessionKey": session_key,
            "message": msg,
            "deliver": True,
            "timeoutMs": 0,
            "idempotencyKey": str(uuid.uuid4()),
        }, ensure_ascii=False)
    ]
    if dry_run:
        return True, "dry-run"
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode == 0:
        return True, p.stdout.strip() or "ok"
    return False, p.stderr.strip() or p.stdout.strip() or f"rc={p.returncode}"
