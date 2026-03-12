# Testing

## Run

```bash
PYTHONPATH=src python3 tests/run_tests.py
```

## What is covered

- interrupted-session detection
- auto-resume decision path
- repeated-run behavior up to escalation boundary

## Notes

Tests use a local fixture under `tests/fixtures/` and do not need a live OpenClaw gateway.
