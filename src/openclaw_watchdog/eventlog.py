from __future__ import annotations

import json
import time
from pathlib import Path


class EventLog:
    def __init__(self, path: Path) -> None:
        self.path = path

    def write(self, event: str, **fields) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        doc = {"ts": int(time.time() * 1000), "event": event, **fields}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
