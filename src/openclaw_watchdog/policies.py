from __future__ import annotations

import time

from .models import EvaluatedSession, Policy, SessionState, SessionWatchState


def policy_for(agent_id: str, default_policy: Policy, agent_policies: dict[str, Policy]) -> Policy:
    return agent_policies.get(agent_id, default_policy)


def should_resume(session: EvaluatedSession, policy: Policy, watch_state: SessionWatchState) -> tuple[bool, str]:
    if not policy.enabled:
        return False, "policy disabled"
    if session.state != SessionState.INTERRUPTED:
        return False, f"state is {session.state.value}"
    if policy.require_pending_reply and session.last_user is None:
        return False, "no pending user message"
    if watch_state.auto_resume_count >= policy.max_auto_resume:
        return False, "max auto resume reached"
    now_ms = int(time.time() * 1000)
    if watch_state.last_resume_at is not None:
        elapsed = now_ms - watch_state.last_resume_at
        if elapsed < policy.cooldown_seconds * 1000:
            return False, "cooldown active"
    return True, "eligible"
