# openclaw-watchdog

Policy-based watchdog for long-running OpenClaw sessions.

## What it does

- Watches local OpenClaw session state under `~/.openclaw`
- Detects interrupted sessions that still owe the user a reply
- Automatically sends a recovery nudge (`continue` by default)
- Persists watchdog state to avoid duplicate handling
- Escalates after repeated failed recovery attempts
- Supports `--dry-run` for safe rollout

## Current MVP

This version already includes:

- Polling-based watcher
- Real OpenClaw agent session discovery (`~/.openclaw/agents/*/sessions/sessions.json`)
- Transcript parsing for OpenClaw JSONL message format
- Configurable auto-resume policy
- JSON state file
- JSONL event log
- OpenClaw CLI integration via `chat.send` and `message.send`
- Fixture-based tests
- Example systemd user service

## Install

```bash
git clone https://github.com/ai7eam-dev/openclaw-watchdog.git
cd openclaw-watchdog
chmod +x scripts/install.sh scripts/uninstall.sh
./scripts/install.sh
```

This will:

1. create `~/.config/openclaw-watchdog/config.toml` if missing
2. install a systemd user service using the current repository path
3. reload systemd user units
4. enable and start the watchdog service

If your system blocks editable global pip installs, that is fine — this project can run directly from source with:

```bash
cd openclaw-watchdog
PYTHONPATH=src python3 -m openclaw_watchdog inspect
```

## Quick start

### Manual path

1. Write default config:

```bash
PYTHONPATH=src python3 -m openclaw_watchdog init
```

2. Validate your environment safely:

```bash
PYTHONPATH=src python3 -m openclaw_watchdog inspect
PYTHONPATH=src python3 -m openclaw_watchdog once --dry-run
```

3. Start the loop manually if you do not want a service yet:

```bash
PYTHONPATH=src python3 -m openclaw_watchdog watch --dry-run
```

4. Install a user service if desired:

```bash
PYTHONPATH=src python3 -m openclaw_watchdog install-service
systemctl --user daemon-reload
systemctl --user enable --now openclaw-watchdog
```

## Commands

```bash
openclaw-watchdog inspect
openclaw-watchdog once [--dry-run]
openclaw-watchdog watch [--dry-run] [--interval 60]
openclaw-watchdog init [--force]
openclaw-watchdog install-service [--force]
```

Or without package install:

```bash
PYTHONPATH=src python3 -m openclaw_watchdog inspect
PYTHONPATH=src python3 -m openclaw_watchdog once --dry-run
PYTHONPATH=src python3 -m openclaw_watchdog watch --dry-run
PYTHONPATH=src python3 -m openclaw_watchdog init
PYTHONPATH=src python3 -m openclaw_watchdog install-service --force
```

## Detection model

A session is considered `INTERRUPTED` when all of the following are true:

- no active `.jsonl.lock`
- `abortedLastRun=true`
- last user message is newer than last assistant message

A session is considered `WORKING` when a lock exists.

A session is considered `NO_FEEDBACK` when the user is newer than the assistant but interruption is not proven.

## Recovery model

When a session is interrupted and policy allows it, the watchdog:

1. checks cooldown
2. checks auto-resume limit
3. sends a `continue` nudge via `openclaw gateway call chat.send`
4. records the action in the state file

If the limit is exceeded:

1. it first tries to alert the related parent/main agent session
2. only if no suitable parent session exists does it fall back to external notify

## What users usually need to configure

This project tries to work with sane defaults, but different users often need to check or edit the following.

### 1. OpenClaw runtime root
Default:

```toml
[openclaw]
root = "~/.openclaw"
```

Change this if the user stores OpenClaw somewhere else.

The watchdog expects to find session data under:

```text
<openclaw root>/agents/*/sessions/sessions.json
<openclaw root>/agents/*/sessions/*.jsonl
```

### 2. OpenClaw binary path
Default:

```toml
openclaw_bin = "openclaw"
```

If `openclaw` is not on PATH, replace it with an absolute path.

### 3. Notify target (fallback only)
In the default design, watchdog escalation should first go to the related parent/main agent session.

Only configure external notify if you want a fallback when no suitable parent session exists:

```toml
[notify]
enabled = false
channel = "telegram"
target = "<your target>"
silent = false
```

### 4. Per-agent policy
Different agents may want different retry limits or cooldowns:

```toml
[agents."my-agent"]
enabled = true
max_auto_resume = 3
cooldown_seconds = 180
nudge_template = "continue"
require_pending_reply = true
```

### 5. Runtime state/event-log paths
Optional, but useful on shared machines or for tests:

```toml
[paths]
state_path = "~/.local/state/openclaw-watchdog/state.json"
event_log_path = "~/.local/state/openclaw-watchdog/events.jsonl"
```

### 6. systemd service working directory
If you use `./scripts/install.sh`, the generated service uses the current repository path automatically.

If you copy `examples/systemd/openclaw-watchdog.service` manually, edit:

- `WorkingDirectory=`
- `Environment=PYTHONPATH=...`

so they match your local clone path.

## Verification checklist

After setup, check these in order:

### A. Can the watchdog read sessions?

```bash
cd openclaw-watchdog
PYTHONPATH=src python3 -m openclaw_watchdog inspect
```

Expected: JSON output with one or more sessions. If it prints `[]`, check `openclaw.root`.

### B. Can it evaluate safely without acting?

```bash
PYTHONPATH=src python3 -m openclaw_watchdog once --dry-run
```

Expected: session decisions with `action: none` or a dry-run resume path.

### C. Is the service running?

```bash
systemctl --user status openclaw-watchdog
```

### D. Did runtime files appear?

```bash
ls -la ~/.local/state/openclaw-watchdog/
```

Expected files:
- `state.json`
- `events.jsonl`

## Add it to TOOLS.md

If the user keeps a workspace-level `TOOLS.md` cheat sheet for local services, add `openclaw-watchdog` there after installation.

Suggested entry:

```markdown
### openclaw-watchdog

- Repo: `<local clone path>`
- systemd user service: `openclaw-watchdog.service`
- Status check:
  - `systemctl --user status openclaw-watchdog`
  - `journalctl --user -u openclaw-watchdog -n 50 --no-pager`
- Service control:
  - start: `systemctl --user start openclaw-watchdog`
  - stop: `systemctl --user stop openclaw-watchdog`
  - restart: `systemctl --user restart openclaw-watchdog`
- Runtime files:
  - `~/.local/state/openclaw-watchdog/state.json`
  - `~/.local/state/openclaw-watchdog/events.jsonl`
```

This makes it much easier for future agent sessions to understand how to inspect and operate the service.

## Recommended: hand this repo to an agent

For most users, the easiest setup path is to give this repository directly to an OpenClaw-capable agent and ask it to install and validate the watchdog for the local machine.

Why this is recommended:

- the agent can inspect the real OpenClaw runtime path
- the agent can adjust `config.toml` for the local environment
- the agent can run safe validation steps before enabling the service
- the agent can detect when `systemctl --user` or `openclaw` path assumptions need adjustment

### Suggested handoff prompt

You can give an agent this repository together with a prompt like this:

```text
Please install and configure this openclaw-watchdog project for the current machine.

Requirements:
1. Detect the real OpenClaw runtime directory.
2. Check whether the `openclaw` CLI is on PATH; if not, set an absolute path in config.
3. Review `README.md` and `docs/agent-handoff.md` before making changes.
4. Edit `~/.config/openclaw-watchdog/config.toml` only as needed for this machine.
5. Run safe validation first:
   - `PYTHONPATH=src python3 -m openclaw_watchdog inspect`
   - `PYTHONPATH=src python3 -m openclaw_watchdog once --dry-run`
6. If validation looks correct, install and start the service.
7. Verify final status with:
   - `systemctl --user status openclaw-watchdog`
8. If the environment does not support `systemctl --user`, explain the issue and fall back to a manual `watch` run instead of forcing it.
9. Prefer session-first defaults; do not configure external fallback notify unless clearly needed.
10. Summarize exactly what you changed.
```

### Agent-friendly setup flow

If a user hands this repository to another agent, that agent should usually do this:

1. clone the repo
2. inspect where OpenClaw runtime data lives
3. edit `~/.config/openclaw-watchdog/config.toml`
4. run `inspect`
5. run `once --dry-run`
6. install/start the service
7. re-check `systemctl --user status openclaw-watchdog`

See also: `docs/agent-handoff.md`

## Files

By default:

- Config: `~/.config/openclaw-watchdog/config.toml`
- Runtime state: `~/.local/state/openclaw-watchdog/state.json`
- Event log: `~/.local/state/openclaw-watchdog/events.jsonl`
- systemd unit: `~/.config/systemd/user/openclaw-watchdog.service`

## Uninstall

```bash
./scripts/uninstall.sh
```

This removes the service but keeps config and runtime state unless you delete them manually.

## Test

```bash
PYTHONPATH=src python3 tests/run_tests.py
```

## Project layout

- `src/openclaw_watchdog/` — runtime code
- `tests/fixtures/` — local interrupted-session fixture
- `scripts/` — install/uninstall helpers
- `examples/systemd/` — manual service example
- `docs/` — architecture, config, recovery policy, integration, testing

## Session-first routing

- If a session is visible in OpenClaw session storage, it is a candidate for watchdog scanning.
- Recovery happens in that same session.
- Repeated failure should alert the related main agent session before any external channel fallback.

## Notes

- This project is a sidecar for OpenClaw, not an OpenClaw core patch.
- It is designed for safe, incremental rollout. Start with `--dry-run`.
- The action layer is intentionally narrow: continue, status request, escalation.
