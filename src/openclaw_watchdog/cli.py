from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

from .config import default_config_path, load_config
from .service import install_user_service
from .session_store import list_sessions
from .state_eval import evaluate_session
from .watchdog import run_once


def cmd_init(args: argparse.Namespace) -> int:
    dst = default_config_path()
    src = Path(__file__).resolve().parents[2] / "config.example.toml"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not args.force:
        print(f"Config already exists: {dst}", file=sys.stderr)
        return 2
    shutil.copyfile(src, dst)
    print(dst)
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    rows = []
    for meta in list_sessions(cfg.openclaw_root):
        ev = evaluate_session(meta)
        rows.append({
            "sessionKey": meta.key,
            "agentId": meta.agent_id,
            "state": ev.state.value,
            "reason": ev.reason,
            "abortedLastRun": meta.aborted_last_run,
            "lastUser": ev.last_user.preview if ev.last_user else None,
            "lastAssistant": ev.last_assistant.preview if ev.last_assistant else None,
        })
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


def cmd_once(args: argparse.Namespace) -> int:
    result = run_once(config_path=args.config, dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_watch(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    interval = float(args.interval or cfg.interval_seconds)
    try:
        while True:
            result = run_once(config_path=args.config, dry_run=args.dry_run)
            print(json.dumps({"ts": int(time.time() * 1000), "actions": result}, ensure_ascii=False, indent=2))
            time.sleep(interval)
    except KeyboardInterrupt:
        return 0


def cmd_install_service(args: argparse.Namespace) -> int:
    try:
        path = install_user_service(force=bool(args.force))
    except FileExistsError as e:
        print(f"Service already exists: {e}", file=sys.stderr)
        return 2
    print(path)
    return 0


def main() -> None:
    p = argparse.ArgumentParser(prog="openclaw-watchdog")
    p.add_argument("--config", help="Path to config.toml")
    sub = p.add_subparsers(dest="cmd", required=True)

    init = sub.add_parser("init", help="Write default config")
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)

    inspect = sub.add_parser("inspect", help="Inspect current session states")
    inspect.set_defaults(func=cmd_inspect)

    once = sub.add_parser("once", help="Run one watchdog pass")
    once.add_argument("--dry-run", action="store_true")
    once.set_defaults(func=cmd_once)

    watch = sub.add_parser("watch", help="Run watch loop")
    watch.add_argument("--dry-run", action="store_true")
    watch.add_argument("--interval", type=float)
    watch.set_defaults(func=cmd_watch)

    svc = sub.add_parser("install-service", help="Install example systemd user service")
    svc.add_argument("--force", action="store_true")
    svc.set_defaults(func=cmd_install_service)

    args = p.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
