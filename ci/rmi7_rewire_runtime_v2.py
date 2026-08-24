from __future__ import annotations

from pathlib import Path

import rmi7_rewire_runtime as base

ROOT = Path(__file__).resolve().parents[1]
AMBIGUOUS_ROUTE_LOOKUP = '        route = self.config.implementation_routes.get(task_type, {})\n'
AMBIGUOUS_DEFERRED_ADD = (
    '                add(route.get(key), f"routing.{task_type}.{key}", '
    'defer_if_worker_disallowed=True)\n'
)


def guarded_replace(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if path.endswith("engine.py") and old == AMBIGUOUS_ROUTE_LOOKUP:
        if count != 2:
            raise SystemExit(
                f"expected exactly two pre-RMI route lookups in {path}, found {count}"
            )
        target.write_text(text.replace(old, new, 1), encoding="utf-8")
        return
    if path.endswith("engine.py") and old == AMBIGUOUS_DEFERRED_ADD:
        if count != 4:
            raise SystemExit(
                f"expected exactly four pre-RMI deferred route additions in {path}, found {count}"
            )
        target.write_text(text.replace(old, new, 1), encoding="utf-8")
        return
    if count != 1:
        raise SystemExit(f"expected exactly one match in {path}, found {count}: {old[:80]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


base.replace_once = guarded_replace
base.main()
