from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from .config import ConfigBundle
from .live_scope_replay import LiveScopeReplayPlan, run_staged_documentation_replay
from .provider_adapter import ProviderAdapterContractError
from .provider_connection import HeaderProviderConnection, ProviderConnection
from .specialist_routing import SpecialistRoutingEngine


def connections_from_environment() -> dict[str, ProviderConnection]:
    """Build the staged documentation replay connections from optional operator env vars.

    This is a convenience bridge only. Provider access remains outside routing and the
    library replay API continues to accept provider-neutral ProviderConnection objects.
    """
    connections: dict[str, ProviderConnection] = {}
    if os.environ.get("ANTHROPIC_API_KEY"):
        connections["anthropic"] = HeaderProviderConnection(
            provider_family="anthropic",
            authorization_headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"]},
        )
    if os.environ.get("OPENAI_API_KEY"):
        connections["openai"] = HeaderProviderConnection(
            provider_family="openai",
            authorization_headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
            },
        )
    missing = sorted({"anthropic", "openai"} - set(connections))
    if missing:
        raise ProviderAdapterContractError(
            "Missing environment-backed staged replay connections: " + ", ".join(missing)
        )
    return connections


def load_plan(path: str | Path, *, repo_root: str | Path) -> LiveScopeReplayPlan:
    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProviderAdapterContractError(
            f"Documentation replay plan could not be loaded: {source}"
        ) from exc
    if not isinstance(payload, dict):
        raise ProviderAdapterContractError("Documentation replay plan must be a JSON object")
    return LiveScopeReplayPlan.from_dict(payload, repo_root=repo_root)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def persist_execution(output_dir: str | Path, execution) -> dict[str, str]:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    plan_path = target / "replay-plan.json"
    record_path = target / "replay-record.json"
    outcomes_path = target / "route-outcomes.jsonl"

    _write_json(plan_path, execution.plan.to_dict())
    _write_json(record_path, execution.record.to_dict())
    with outcomes_path.open("w", encoding="utf-8") as handle:
        for outcome in execution.outcomes:
            handle.write(
                json.dumps(outcome.to_dict(), sort_keys=True, separators=(",", ":"))
                + "\n"
            )

    return {
        "plan": str(plan_path),
        "record": str(record_path),
        "route_outcomes": str(outcomes_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate or run the staged TEO documentation controlled replay"
    )
    parser.add_argument("--repo-root", default=".")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate", help="Validate the replay plan without provider calls"
    )
    validate_parser.add_argument("--plan", required=True)

    run_parser = subparsers.add_parser(
        "run", help="Run the staged documentation replay with operator provider access"
    )
    run_parser.add_argument("--plan", required=True)
    run_parser.add_argument(
        "--output-dir",
        default=".teo/runtime/live-scope-replay/documentation",
    )
    run_parser.add_argument(
        "--execute-live",
        action="store_true",
        help="Required acknowledgement that this command makes live provider calls",
    )

    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    plan = load_plan(args.plan, repo_root=repo_root)

    if args.command == "validate":
        print(
            json.dumps(
                {
                    "status": "valid",
                    "replay_id": plan.to_dict()["replay_id"],
                    "plan_sha256": plan.sha256,
                    "provider_calls": 0,
                    "activation_authorized": False,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if not args.execute_live:
        raise ProviderAdapterContractError(
            "Staged documentation replay requires explicit --execute-live acknowledgement"
        )

    engine = SpecialistRoutingEngine(ConfigBundle.load(repo_root))
    execution = run_staged_documentation_replay(
        plan,
        engine,
        connections_from_environment(),
        repo_root=repo_root,
        artifact_root=Path(args.output_dir) / "artifacts",
    )
    paths = persist_execution(args.output_dir, execution)
    print(
        json.dumps(
            {
                "status": "completed",
                "replay_id": execution.record.to_dict()["replay_id"],
                "summary": execution.record.to_dict()["summary"],
                "activation_authorized": False,
                "live_scope_widened": False,
                "evidence_paths": paths,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
