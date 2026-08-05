from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def append_jsonl(path: str | Path, record_type: str, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    envelope = {"record_type": record_type, "payload": payload}
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(envelope, sort_keys=True) + "\n")
