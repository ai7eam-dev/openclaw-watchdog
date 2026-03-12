# Recovery Policy

## Interrupted

A session is recoverable when:

- no `.lock` file exists
- `abortedLastRun=true`
- the last user message is newer than the last assistant message

## Resume gating

The watchdog resumes only if:

- the policy is enabled
- auto-resume count is still below `max_auto_resume`
- cooldown has expired

## Escalation

If a session is still interrupted after the allowed number of auto-resume attempts, the watchdog can send a manual inspection alert via `openclaw message send`.

## Current action templates

- `continue`
- `progress`
- `finalize`
