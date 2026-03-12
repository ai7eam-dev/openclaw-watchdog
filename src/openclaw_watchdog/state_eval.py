from __future__ import annotations

from .locks import read_lock
from .models import EvaluatedSession, SessionMeta, SessionState
from .transcript import tail_messages


def evaluate_session(meta: SessionMeta) -> EvaluatedSession:
    lock = read_lock(meta.session_file)
    last_user, last_assistant = tail_messages(meta.session_file)

    if lock:
        return EvaluatedSession(meta=meta, state=SessionState.WORKING, reason="lock present", last_user=last_user, last_assistant=last_assistant, lock=lock)

    if not last_user:
        return EvaluatedSession(meta=meta, state=SessionState.NO_MESSAGE, reason="no user message found", last_user=last_user, last_assistant=last_assistant, lock=None)

    pending_reply = last_assistant is None or _gt(last_user.ts_ms, last_assistant.ts_ms)

    if meta.aborted_last_run and pending_reply:
        return EvaluatedSession(meta=meta, state=SessionState.INTERRUPTED, reason="abortedLastRun + pending reply", last_user=last_user, last_assistant=last_assistant, lock=None)

    if pending_reply:
        return EvaluatedSession(meta=meta, state=SessionState.NO_FEEDBACK, reason="pending reply but no proven abort", last_user=last_user, last_assistant=last_assistant, lock=None)

    return EvaluatedSession(meta=meta, state=SessionState.FINISHED, reason="assistant caught up", last_user=last_user, last_assistant=last_assistant, lock=None)


def _gt(a: int | None, b: int | None) -> bool:
    if a is None:
        return False
    if b is None:
        return True
    return a > b
