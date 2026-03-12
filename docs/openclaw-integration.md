# OpenClaw Integration

## Local run

```bash
PYTHONPATH=src python3 -m openclaw_watchdog inspect
PYTHONPATH=src python3 -m openclaw_watchdog once --dry-run
PYTHONPATH=src python3 -m openclaw_watchdog watch --dry-run
```

## Install config

```bash
python3 -m openclaw_watchdog init
```

## systemd user service

Fast path:

```bash
./scripts/install.sh
```

Manual path:

```bash
mkdir -p ~/.config/systemd/user
cp examples/systemd/openclaw-watchdog.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now openclaw-watchdog
```

`scripts/install.sh` writes a unit using the current repository path automatically.

If you copy the example file manually, edit it and update:

- `WorkingDirectory=`
- `Environment=PYTHONPATH=...`

## Notes

- Start with `--dry-run`
- Confirm your `openclaw` binary path if it is not on PATH
- Confirm your `openclaw.root` path if your runtime is not `~/.openclaw`
- Use per-agent overrides for sensitive sessions
