# Configuration

## Default path

`~/.config/openclaw-watchdog/config.toml`

## Sections

This file is meant to be the main per-user adjustment point. For most installations, users only need to edit this file.

### [openclaw]
- `root`: OpenClaw home directory
- `openclaw_bin`: CLI binary name or absolute path

### [watch]
- `interval_seconds`: polling interval for `watch`

### [defaults]
- `enabled`
- `max_auto_resume`
- `cooldown_seconds`
- `nudge_template`
- `require_pending_reply`

### [notify]
- `enabled`
- `channel`
- `target`
- `silent`

This block is fallback-only. The preferred escalation path is parent/main session alerting inside OpenClaw session space.

### [agents."..."]
Per-agent override block.

## Example

```toml
[openclaw]
root = "~/.openclaw"
openclaw_bin = "openclaw"

[notify]
enabled = true
channel = "telegram"
target = "<your-target>"

[agents."my-agent"]
enabled = true
max_auto_resume = 3
cooldown_seconds = 180
nudge_template = "continue"
```

## Most common user-specific changes

- change `openclaw.root` if OpenClaw data is not under `~/.openclaw`
- change `openclaw.openclaw_bin` if the CLI is not on PATH
- change `[notify]` to the right channel/target
- add per-agent overrides only for agents that need custom retry behavior
- optionally override `[paths]` on shared machines or in tests
