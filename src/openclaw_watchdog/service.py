from __future__ import annotations

from pathlib import Path


SERVICE_NAME = "openclaw-watchdog.service"


def render_user_service(project_root: Path) -> str:
    root = project_root.resolve()
    src = root / "src"
    return f"""[Unit]
Description=OpenClaw Watchdog
After=default.target

[Service]
Type=simple
WorkingDirectory={root}
Environment=PYTHONPATH={src}
ExecStart=/usr/bin/python3 -m openclaw_watchdog watch
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
"""


def install_user_service(force: bool = False, project_root: Path | None = None) -> Path:
    root = (project_root or Path(__file__).resolve().parents[2]).resolve()
    dst = Path.home() / ".config" / "systemd" / "user" / SERVICE_NAME
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not force:
        raise FileExistsError(str(dst))
    dst.write_text(render_user_service(root))
    return dst
