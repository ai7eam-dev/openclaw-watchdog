from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from test_watchdog import test_run_once_detects_and_resumes_interrupted_session, test_second_run_escalates_after_limit


def main() -> None:
    test_run_once_detects_and_resumes_interrupted_session()
    test_second_run_escalates_after_limit()
    print("ok")


if __name__ == "__main__":
    main()
