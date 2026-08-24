from __future__ import annotations

from pathlib import Path

import rmi7_rewire_runtime as base

ROOT = Path(__file__).resolve().parents[1]
AMBIGUOUS_ROUTE_LOOKUP = '        route = self.config.implementation_routes.get(task_type, {})\n'


def guarded_replace(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if old == AMBIGUOUS_ROUTE_LOOKUP and path.endswith("engine.py"):
        if count != 2:
            raise SystemExit(
                f"expected exactly two pre-RMI route lookups in {path}, found {count}"
            )
        target.write_text(text.replace(old, new, 1), encoding="utf-8")
        return
    if count != 1:
        raise SystemExit(f"expected exactly one match in {path}, found {count}: {old[:80]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


base.replace_once = guarded_replace
base.main()
