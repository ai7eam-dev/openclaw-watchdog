#!/usr/bin/env bash
set -euo pipefail

SERVICE_PATH="${HOME}/.config/systemd/user/openclaw-watchdog.service"

systemctl --user disable --now openclaw-watchdog 2>/dev/null || true
rm -f "${SERVICE_PATH}"
systemctl --user daemon-reload

echo "Removed service: ${SERVICE_PATH}"
echo "Kept config and runtime state on disk."
echo "Optional cleanup:"
echo "  rm -rf ~/.config/openclaw-watchdog ~/.local/state/openclaw-watchdog"
