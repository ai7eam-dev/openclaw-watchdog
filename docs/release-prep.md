# Release Prep

## Before first public push

- replace `git clone <repo-url>` in `README.md` with the real repository URL
- ensure `scripts/install.sh` and `scripts/uninstall.sh` are executable in git
- run tests: `PYTHONPATH=src python3 tests/run_tests.py`
- do one real local smoke check:
  - `PYTHONPATH=src python3 -m openclaw_watchdog inspect`
  - `PYTHONPATH=src python3 -m openclaw_watchdog once --dry-run`
- review `config.example.toml` defaults
- review systemd unit path assumptions

## Suggested first tags

- `v0.1.0` for initial MVP release
