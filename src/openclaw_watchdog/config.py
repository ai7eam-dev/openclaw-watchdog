from __future__ import annotations

from pathlib import Path
import os
import tomllib

from .models import Config, NotificationPolicy, Policy


def _expand(path: str) -> Path:
    return Path(os.path.expanduser(path)).resolve()


def default_config_path() -> Path:
    return _expand("~/.config/openclaw-watchdog/config.toml")


def default_state_path() -> Path:
    return _expand("~/.local/state/openclaw-watchdog/state.json")


def default_event_log_path() -> Path:
    return _expand("~/.local/state/openclaw-watchdog/events.jsonl")


def load_config(path: str | Path | None = None) -> Config:
    cfg_path = Path(path).expanduser() if path else default_config_path()
    raw = tomllib.loads(cfg_path.read_text()) if cfg_path.exists() else {}

    oc = raw.get("openclaw", {})
    watch = raw.get("watch", {})
    defaults = raw.get("defaults", {})
    notify = raw.get("notify", {})
    agents = raw.get("agents", {})
    paths = raw.get("paths", {})

    default_policy = Policy(
        enabled=bool(defaults.get("enabled", True)),
        max_auto_resume=int(defaults.get("max_auto_resume", 2)),
        cooldown_seconds=int(defaults.get("cooldown_seconds", 120)),
        nudge_template=str(defaults.get("nudge_template", "continue")),
        require_pending_reply=bool(defaults.get("require_pending_reply", True)),
    )

    agent_policies: dict[str, Policy] = {}
    for agent_id, item in agents.items():
        item = item or {}
        agent_policies[str(agent_id)] = Policy(
            enabled=bool(item.get("enabled", default_policy.enabled)),
            max_auto_resume=int(item.get("max_auto_resume", default_policy.max_auto_resume)),
            cooldown_seconds=int(item.get("cooldown_seconds", default_policy.cooldown_seconds)),
            nudge_template=str(item.get("nudge_template", default_policy.nudge_template)),
            require_pending_reply=bool(item.get("require_pending_reply", default_policy.require_pending_reply)),
        )

    return Config(
        openclaw_root=_expand(str(oc.get("root", "~/.openclaw"))),
        openclaw_bin=str(oc.get("openclaw_bin", "openclaw")),
        interval_seconds=float(watch.get("interval_seconds", 60)),
        default_policy=default_policy,
        notify=NotificationPolicy(
            enabled=bool(notify.get("enabled", False)),
            channel=notify.get("channel"),
            target=notify.get("target"),
            silent=bool(notify.get("silent", False)),
        ),
        agent_policies=agent_policies,
        config_path=cfg_path,
        state_path=_expand(str(paths.get("state_path", default_state_path()))),
        event_log_path=_expand(str(paths.get("event_log_path", default_event_log_path()))),
    )
