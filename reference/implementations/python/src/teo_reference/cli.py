from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from .audit import append_jsonl
from .config import ConfigBundle, ConfigurationError
from .engine import RoutingError
from .final_execution_provenance import attach_execution_provenance
from .provider_adapter import ProviderAdapterContractError
from .schemas import (
    DispatchRecord,
    ExecutionResult,
    ImplementationChoice,
    TaskRequest,
    VerificationPlan,
    VerificationResult,
)
from .specialist_routing import SpecialistRoutingEngine


def _load(path: str) -> dict[str, Any]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    data = json.loads(text) if source.suffix.lower() == ".json" else yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"Input must contain a mapping: {source}")
    return data


def _validate_schema(
    repo_root: str | Path,
    schema_name: str,
    data: dict[str, Any],
    label: str,
) -> None:
    path = Path(repo_root).resolve() / "reference" / "schemas" / schema_name
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    failures = sorted(
        validator.iter_errors(data),
        key=lambda error: tuple(str(item) for item in error.absolute_path),
    )
    if failures:
        failure = failures[0]
        location = ".".join(str(item) for item in failure.absolute_path) or "$"
        raise ValueError(f"{label} failed schema validation at {location}: {failure.message}")


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
    parser = argparse.ArgumentParser(prog="teo", description="TEO reference router")
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
    finalize.add_argument(
        "--artifact-root",
        help=(
            "Authorized local artifact root required when a passed verification finalizes "
            "an artifact-backed execution."
        ),
    )
    finalize.add_argument(
        "--route-outcome",
        help="Optional canonical Route-Outcome Evidence record used to project validated active execution provenance.",
    )
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
            return 0 if status == "valid" else 2

        engine = SpecialistRoutingEngine(bundle)
        if args.action == "plan":
            task_data = _load(args.task)
            _validate_schema(args.repo_root, "task.schema.json", task_data, "task input")
            dispatch = engine.dispatch(TaskRequest.from_dict(task_data))
            result = dispatch.to_dict()
            _validate_schema(args.repo_root, "dispatch-record.schema.json", result, "dispatch output")
            if args.output:
                Path(args.output).write_text(
                    json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
                )
            if args.audit_log:
                append_jsonl(args.audit_log, "dispatch", result)
            _print(result)
            return 0

        dispatch_data = _load(args.dispatch)
        execution_data = _load(args.execution)
        verification_data = _load(args.verification)
        _validate_schema(args.repo_root, "dispatch-record.schema.json", dispatch_data, "dispatch input")
        _validate_schema(args.repo_root, "execution-result.schema.json", execution_data, "execution input")
        _validate_schema(args.repo_root, "verification-result.schema.json", verification_data, "verification input")
        dispatch = _dispatch(dispatch_data)
        execution = ExecutionResult.from_dict(execution_data)
        verification = VerificationResult.from_dict(verification_data)
        outcome = engine.finalize(
            dispatch,
            execution,
            verification,
            artifact_root=args.artifact_root,
        )
        if args.route_outcome:
            route_outcome_data = _load(args.route_outcome)
            outcome = attach_execution_provenance(
                outcome,
                route_outcome_data,
                repo_root=args.repo_root,
            )
        result = outcome.to_dict()
        _validate_schema(args.repo_root, "final-outcome.schema.json", result, "final outcome")
        if args.output:
            Path(args.output).write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
        if args.audit_log:
            append_jsonl(args.audit_log, "final_outcome", result)
        _print(result)
        return 0
    except (
        ConfigurationError,
        ProviderAdapterContractError,
        RoutingError,
        ValueError,
        OSError,
        json.JSONDecodeError,
    ) as exc:
        parser = build_parser()
        parser.error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
