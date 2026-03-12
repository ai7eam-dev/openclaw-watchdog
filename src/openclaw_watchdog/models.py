from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class SessionState(str, Enum):
    WORKING = "WORKING"
    FINISHED = "FINISHED"
    INTERRUPTED = "INTERRUPTED"
    NO_MESSAGE = "NO_MESSAGE"
    NO_FEEDBACK = "NO_FEEDBACK"


@dataclass(frozen=True)
class SessionMeta:
    key: str
    agent_id: str
    session_file: Optional[Path]
    updated_at_ms: Optional[int]
    channel: Optional[str]
    account_id: Optional[str]
    to: Optional[str]
    aborted_last_run: bool
    system_sent: bool


@dataclass(frozen=True)
class MessagePreview:
    preview: str
    ts_ms: Optional[int]


@dataclass(frozen=True)
class LockInfo:
    exists: bool
    created_at_ms: Optional[int]


@dataclass(frozen=True)
class EvaluatedSession:
    meta: SessionMeta
    state: SessionState
    reason: str
    last_user: Optional[MessagePreview]
    last_assistant: Optional[MessagePreview]
    lock: Optional[LockInfo]


@dataclass
class SessionWatchState:
    auto_resume_count: int = 0
    last_handled_abort_at: Optional[int] = None
    last_resume_at: Optional[int] = None
    last_action: Optional[str] = None
    status: Optional[str] = None


@dataclass(frozen=True)
class Policy:
    enabled: bool = True
    max_auto_resume: int = 2
    cooldown_seconds: int = 120
    nudge_template: str = "continue"
    require_pending_reply: bool = True


@dataclass(frozen=True)
class NotificationPolicy:
    enabled: bool = False
    channel: Optional[str] = None
    target: Optional[str] = None
    silent: bool = False


@dataclass(frozen=True)
class Config:
    openclaw_root: Path
    openclaw_bin: str
    interval_seconds: float
    default_policy: Policy
    notify: NotificationPolicy
    agent_policies: dict[str, Policy] = field(default_factory=dict)
    config_path: Optional[Path] = None
    state_path: Optional[Path] = None
    event_log_path: Optional[Path] = None
