# GitHub Publish Checklist

Before publishing:

- [ ] README includes install, configure, verify, uninstall, and agent handoff steps
- [ ] scripts/install.sh and scripts/uninstall.sh are executable in git
- [ ] config.example.toml documents user-specific values
- [ ] tests pass: `PYTHONPATH=src python3 tests/run_tests.py`
- [ ] systemd example matches the intended repository location assumptions
- [ ] user-facing claims stay aligned with current implementation (polling sidecar, not event-driven core hook)
