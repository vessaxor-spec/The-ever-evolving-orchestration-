from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from .audit import append_jsonl
from .config import ConfigBundle, ConfigurationError
from .engine import OrchestrationEngine, RoutingError
from .schemas import (
    DispatchRecord,
    ExecutionResult,
    ImplementationChoice,
    TaskRequest,
    VerificationPlan,
    VerificationResult,
)


def _load(path: str) -> dict[str, Any]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    data = json.loads(text) if source.suffix.lower() == ".json" else yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"Input must contain a mapping: {source}")
    return data


def _choice(data: dict[str, Any]) -> ImplementationChoice:
    return ImplementationChoice(**data)


def _dispatch(data: dict[str, Any]) -> DispatchRecord:
    verification = dict(data["verification"])
    verification["implementation"] = _choice(verification["implementation"])
    payload = dict(data)
    payload["selected_implementation"] = _choice(payload["selected_implementation"])
    payload["fallback_implementation"] = (
        _choice(payload["fallback_implementation"]) if payload.get("fallback_implementation") else None
    )
    payload["verification"] = VerificationPlan(**verification)
    return DispatchRecord(**payload)


def _print(data: dict[str, Any]) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="teo", description="TEO Phase 5 reference router")
    parser.add_argument("--repo-root", default=".", help="TEO repository root")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate linked TEO configuration")
    validate.set_defaults(action="validate")

    plan = sub.add_parser("plan", help="Create a structured dispatch record")
    plan.add_argument("task")
    plan.add_argument("--output")
    plan.add_argument("--audit-log")
    plan.set_defaults(action="plan")

    finalize = sub.add_parser("finalize", help="Record execution and independent verification")
    finalize.add_argument("dispatch")
    finalize.add_argument("execution")
    finalize.add_argument("verification")
    finalize.add_argument("--output")
    finalize.add_argument("--audit-log")
    finalize.set_defaults(action="finalize")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        bundle = ConfigBundle.load(args.repo_root)
        if args.action == "validate":
            issues = bundle.validate()
            status = "valid" if not any(issue.startswith("ERROR:") for issue in issues) else "invalid"
            _print({"status": status, "issues": issues})
            return 0

        engine = OrchestrationEngine(bundle)
        if args.action == "plan":
            dispatch = engine.dispatch(TaskRequest.from_dict(_load(args.task)))
            result = dispatch.to_dict()
            if args.output:
                Path(args.output).write_text(
                    json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
                )
            if args.audit_log:
                append_jsonl(args.audit_log, "dispatch", result)
            _print(result)
            return 0

        dispatch = _dispatch(_load(args.dispatch))
        execution = ExecutionResult.from_dict(_load(args.execution))
        verification = VerificationResult.from_dict(_load(args.verification))
        outcome = engine.finalize(dispatch, execution, verification)
        result = outcome.to_dict()
        if args.output:
            Path(args.output).write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
        if args.audit_log:
            append_jsonl(args.audit_log, "final_outcome", result)
        _print(result)
        return 0
    except (ConfigurationError, RoutingError, ValueError, OSError) as exc:
        parser = build_parser()
        parser.error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
