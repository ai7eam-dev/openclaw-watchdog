from __future__ import annotations

import json
import tempfile
from pathlib import Path

from openclaw_watchdog.watchdog import run_once


def _prepare_fixture() -> tuple[Path, Path]:
    root = Path(__file__).resolve().parent / "fixtures"
    tmp = Path(tempfile.mkdtemp(prefix="ocwd-"))
    runtime = tmp / "openclaw"
    runtime.mkdir(parents=True, exist_ok=True)

    src_root = root / "openclaw"
    for src in src_root.rglob("*"):
        rel = src.relative_to(src_root)
        dst = runtime / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text())

    session_file = runtime / "agents" / "demo-agent" / "sessions" / "demo-session.jsonl"
    sessions_json = runtime / "agents" / "demo-agent" / "sessions" / "sessions.json"
    sessions_json.write_text(sessions_json.read_text().replace("REPLACE_ME", str(session_file.parent)))

    cfg_src = root / "config.test.toml"
    cfg_dst = tmp / "config.toml"
    cfg_text = cfg_src.read_text()
    cfg_text = cfg_text.replace("REPLACE_OPENCLAW_ROOT", str(runtime))
    cfg_text = cfg_text.replace("REPLACE_STATE_PATH", str(tmp / "state.json"))
    cfg_text = cfg_text.replace("REPLACE_EVENT_LOG_PATH", str(tmp / "events.jsonl"))
    cfg_dst.write_text(cfg_text)
    return runtime, cfg_dst


def test_run_once_detects_and_resumes_interrupted_session() -> None:
    runtime, cfg = _prepare_fixture()
    result = run_once(config_path=cfg, dry_run=True)
    row = next(r for r in result if r["sessionKey"] == "agent:demo-agent:cron:test-run-1")
    assert row["state"] == "INTERRUPTED"
    assert row["action"] == "resume"
    state_path = cfg.parent / "state.json"
    assert state_path.exists()


def test_second_run_escalates_after_limit() -> None:
    runtime, cfg = _prepare_fixture()
    run_once(config_path=cfg, dry_run=True)
    run_once(config_path=cfg, dry_run=True)
    result = run_once(config_path=cfg, dry_run=True)
    row = next(r for r in result if r["sessionKey"] == "agent:demo-agent:cron:test-run-1")
    assert row["action"] == "alert-parent-session"
    assert row["targetSessionKey"] == "agent:demo-agent:main"
