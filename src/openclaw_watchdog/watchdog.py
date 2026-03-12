from __future__ import annotations

import time

from .actions import send_escalation, send_nudge, send_session_alert
from .config import load_config
from .eventlog import EventLog
from .models import SessionWatchState
from .policies import policy_for, should_resume
from .routing import parent_session_key
from .session_store import list_sessions
from .state_eval import evaluate_session
from .state_store import load_state, save_state


def run_once(config_path=None, dry_run: bool = False) -> list[dict]:
    cfg = load_config(config_path)
    elog = EventLog(cfg.event_log_path)
    state = load_state(cfg.state_path)
    actions: list[dict] = []

    for meta in list_sessions(cfg.openclaw_root):
        evaluated = evaluate_session(meta)
        pol = policy_for(meta.agent_id, cfg.default_policy, cfg.agent_policies)
        watch_state = state.get(meta.key, SessionWatchState())

        eligible, reason = should_resume(evaluated, pol, watch_state)
        action = {
            "sessionKey": meta.key,
            "agentId": meta.agent_id,
            "state": evaluated.state.value,
            "reason": evaluated.reason,
            "decision": reason,
        }

        if eligible:
            ok, detail = send_nudge(cfg.openclaw_bin, meta.key, pol.nudge_template, dry_run=dry_run)
            watch_state.auto_resume_count += 1
            watch_state.last_resume_at = int(time.time() * 1000)
            watch_state.last_handled_abort_at = watch_state.last_resume_at
            watch_state.last_action = pol.nudge_template
            watch_state.status = "resumed" if ok else "resume_failed"
            state[meta.key] = watch_state
            elog.write("resume.attempt", sessionKey=meta.key, ok=ok, detail=detail, template=pol.nudge_template, dryRun=dry_run)
            action["action"] = "resume"
            action["ok"] = ok
            action["detail"] = detail
        elif evaluated.state.value == "INTERRUPTED" and reason == "max auto resume reached":
            parent_key = parent_session_key(meta.key)
            if parent_key:
                ok, detail = send_session_alert(cfg.openclaw_bin, parent_key, meta.key, evaluated.reason, dry_run=dry_run)
                elog.write("resume.parent_alert", sessionKey=meta.key, parentSessionKey=parent_key, ok=ok, detail=detail, dryRun=dry_run)
                action["action"] = "alert-parent-session"
                action["targetSessionKey"] = parent_key
                action["ok"] = ok
                action["detail"] = detail
            else:
                ok, detail = send_escalation(cfg.openclaw_bin, cfg.notify, evaluated, dry_run=dry_run)
                elog.write("resume.escalated", sessionKey=meta.key, ok=ok, detail=detail, dryRun=dry_run)
                action["action"] = "escalate-external"
                action["ok"] = ok
                action["detail"] = detail
        else:
            action["action"] = "none"

        actions.append(action)

    save_state(cfg.state_path, state)
    return actions
