# Architecture

## Overview

`openclaw-watchdog` is a sidecar process for OpenClaw.

It reads local state from the OpenClaw home directory, evaluates whether sessions look interrupted, and performs narrowly-scoped recovery actions.

## Flow

1. Load config
2. Read OpenClaw sessions from `sessions.json`
3. For each session:
   - read transcript tail
   - read lock file
   - evaluate session state
   - apply per-agent policy
4. If eligible:
   - send recovery nudge
   - persist watchdog state
5. If over retry limit:
   - escalate via message.send
6. Append JSONL event log

## Design goals

- Sidecar, not core patch
- Safe by default
- Explainable decisions
- Local-file-first operation
- Narrow action surface

## Future extensions

- Better transcript parsing for more OpenClaw variants
- Progress-stall detection
- Delivery failure heuristics
- systemd service installer
- ClawHub installer skill
