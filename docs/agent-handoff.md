# Agent Handoff Guide

If a user gives this repository to an OpenClaw-capable agent, the agent should be able to finish setup with minimal supervision.

## What the agent should inspect

1. Where OpenClaw stores runtime data
   - default: `~/.openclaw`
   - important subpaths:
     - `agents/*/sessions/sessions.json`
     - `agents/*/sessions/*.jsonl`

2. Whether `openclaw` is on PATH
   - if not, set `openclaw.openclaw_bin` to an absolute path

3. Where the repository lives
   - if it is not in `~/.openclaw/workspace/openclaw-watchdog`, the systemd unit should be edited

4. Whether the machine uses systemd user services
   - if not, use `watch` directly or another supervisor

## What the agent should edit

Usually only `~/.config/openclaw-watchdog/config.toml`:

- `openclaw.root`
- `openclaw.openclaw_bin`
- per-agent policy blocks
- notify target/channel
- optional custom state and event log paths

For notify configuration, treat it as fallback only. The watchdog should prefer alerting the related parent/main agent session before using an external channel.

## Safe validation steps

```bash
cd <repo>
PYTHONPATH=src python3 -m openclaw_watchdog inspect
PYTHONPATH=src python3 -m openclaw_watchdog once --dry-run
```

Then optionally enable the service.
