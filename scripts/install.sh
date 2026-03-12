#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="${HOME}/.config/openclaw-watchdog"
CONFIG_PATH="${CONFIG_DIR}/config.toml"
SYSTEMD_USER_DIR="${HOME}/.config/systemd/user"
SERVICE_NAME="openclaw-watchdog.service"
SERVICE_PATH="${SYSTEMD_USER_DIR}/${SERVICE_NAME}"

mkdir -p "${CONFIG_DIR}" "${SYSTEMD_USER_DIR}"

if [[ ! -f "${CONFIG_PATH}" ]]; then
  cp "${ROOT_DIR}/config.example.toml" "${CONFIG_PATH}"
  echo "Created config: ${CONFIG_PATH}"
else
  echo "Config already exists: ${CONFIG_PATH}"
fi

cat > "${SERVICE_PATH}" <<EOF
[Unit]
Description=OpenClaw Watchdog
After=default.target

[Service]
Type=simple
WorkingDirectory=${ROOT_DIR}
Environment=PYTHONPATH=${ROOT_DIR}/src
ExecStart=/usr/bin/python3 -m openclaw_watchdog watch
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

echo "Installed service: ${SERVICE_PATH}"

systemctl --user daemon-reload
systemctl --user enable --now openclaw-watchdog

echo
echo "Installed and started openclaw-watchdog."
echo "Next steps:"
echo "  1. Edit ${CONFIG_PATH} if your OpenClaw path or binary differs."
echo "  2. Check service status: systemctl --user status openclaw-watchdog"
echo "  3. Check one-shot output: cd '${ROOT_DIR}' && PYTHONPATH=src python3 -m openclaw_watchdog once --dry-run"
