from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from random import random
from time import monotonic, sleep
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator

from .benchmark_lab import (
    BENCHMARK_LAB_VERSION,
    BenchmarkExperimentManifest,
    BenchmarkExperimentReport,
    BenchmarkFixtureRecord,
    evaluate_benchmark,
)
from .provider_adapter import ProviderAdapterContractError
from .provider_connection import ProviderConnection
from .route_outcome import (
    RouteOutcomeRecord,
    RouteOutcomeVersionContext,
    build_guarded_canary_route_outcome,
)
from .runtime_canary import execute_guarded_canary
from .runtime_circuit_breaker import (
    InMemoryCircuitStateStore,
    ProviderCircuitBreaker,
    ProviderCircuitPolicy,
)
from .runtime_retry import AttemptClock, RandomSource, RetryPolicy, Sleeper
from .runtime_telemetry import InMemoryRuntimeTelemetrySink
from .runtime_verification import verify_guarded_canary_outcome
from .schemas import DispatchRecord, TaskRequest
from .specialist_routing import SpecialistRoutingEngine
from .verification_policy import LiveVerificationPolicy

BENCHMARK_REPLAY_PLAN_SCHEMA_PATH = "reference/schemas/benchmark-replay-plan.schema.json"
LIVE_REPLAY_TASK_TYPES = {"high_volume_simple"}
LIVE_REPLAY_RISK_LEVELS = {"low", "medium"}


def _canonical_sha256(data: Mapping[str, Any], *, omit: str | None = None) -> str:
    canonical = dict(data)
    if omit is not None:
        canonical.pop(omit, None)
    encoded = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_schema(repo_root: str | Path) -> dict[str, Any]:
    path = Path(repo_root) / BENCHMARK_REPLAY_PLAN_SCHEMA_PATH
    if not path.is_file():
        raise ProviderAdapterContractError(f"Benchmark replay schema not found: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProviderAdapterContractError(
            f"Benchmark replay schema could not be loaded: {path}"
        ) from exc
    if not isinstance(raw, dict):
        raise ProviderAdapterContractError("Benchmark replay schema must be an object")
    return raw


def _validate_plan_schema(data: dict[str, Any], repo_root: str | Path) -> None:
    validator = Draft202012Validator(_load_schema(repo_root))
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        path = ".".join(str(item) for item in first.path) or "<root>"
        raise ProviderAdapterContractError(
            f"Benchmark replay plan schema validation failed at {path}: {first.message}"
        )


def _validate_plan_semantics(data: dict[str, Any]) -> None:
    candidates = data["candidates"]
    candidate_ids = [str(item["candidate_id"]) for item in candidates]
    if len(set(candidate_ids)) != len(candidate_ids):
        raise ProviderAdapterContractError("Benchmark replay candidate IDs must be unique")

    route_identities: set[tuple[str, str, str | None]] = set()
    for candidate in candidates:
        candidate_id = str(candidate["candidate_id"])
        provider = str(candidate["provider_family"])
        model = str(candidate["model"])
        verifier_provider = str(candidate["verifier_provider_family"])
        identity = (
            provider,
            model,
            str(candidate["reasoning_effort"])
            if candidate.get("reasoning_effort") is not None
            else None,
        )
        if identity in route_identities:
            raise ProviderAdapterContractError(
                "Benchmark replay candidates must declare distinct execution route identities"
            )
        route_identities.add(identity)
        if provider == verifier_provider:
            raise ProviderAdapterContractError(
                f"Benchmark replay candidate {candidate_id} must preserve provider-diverse verification"
            )

        isolation = candidate["isolation"]
        if model in isolation["blocked_implementations"]:
            raise ProviderAdapterContractError(
                f"Benchmark replay candidate {candidate_id} cannot block its declared model"
            )
        if provider in isolation["blocked_providers"]:
            raise ProviderAdapterContractError(
                f"Benchmark replay candidate {candidate_id} cannot block its declared provider"
            )


@dataclass(frozen=True, slots=True)
class BenchmarkReplayPlan:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "BenchmarkReplayPlan":
        _validate_plan_schema(data, repo_root)
        _validate_plan_semantics(data)
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))

    @property
    def sha256(self) -> str:
        return _canonical_sha256(self.payload)


@dataclass(frozen=True, slots=True)
class ControlledReplayExecution:
    plan: BenchmarkReplayPlan
    manifest: BenchmarkExperimentManifest
    outcomes: tuple[RouteOutcomeRecord, ...]


def _safe_fragment(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-.") or "item"


def _fixture_map(
    plan: dict[str, Any],
    fixtures: Sequence[BenchmarkFixtureRecord],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in fixtures:
        fixture = record.to_dict()
        fixture_id = str(fixture["fixture_id"])
        if fixture_id in result:
            raise ProviderAdapterContractError(
                f"Duplicate controlled replay fixture {fixture_id}"
            )
        if fixture["suite_id"] != plan["suite_id"]:
            raise ProviderAdapterContractError(
                f"Controlled replay fixture {fixture_id} is from a different suite"
            )
        if fixture["suite_version"] != plan["suite_version"]:
            raise ProviderAdapterContractError(
                f"Controlled replay fixture {fixture_id} has a different suite version"
            )
        if fixture["task_type"] not in LIVE_REPLAY_TASK_TYPES:
            raise ProviderAdapterContractError(
                f"Controlled live replay does not authorize task type {fixture['task_type']}"
            )
        if fixture["risk_level"] not in LIVE_REPLAY_RISK_LEVELS:
            raise ProviderAdapterContractError(
                f"Controlled live replay refuses {fixture['risk_level']} risk fixtures"
            )
        result[fixture_id] = fixture
    if not result:
        raise ProviderAdapterContractError("Controlled live replay requires at least one fixture")
    return result


def _task_for_trial(
    *,
    plan: BenchmarkReplayPlan,
    candidate: dict[str, Any],
    fixture: dict[str, Any],
    trial_index: int,
) -> TaskRequest:
    identity = (
        f"{plan.sha256}|{candidate['candidate_id']}|"
        f"{fixture['fixture_id']}|{trial_index}"
    )
    task_id = f"replay-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:20]}"
    isolation = candidate["isolation"]
    return TaskRequest.from_dict(
        {
            "task_id": task_id,
            "task": fixture["controlled_input"],
            "task_type": fixture["task_type"],
            "risk_level": fixture["risk_level"],
            "constraints": {
                "required_capabilities": list(fixture["required_capabilities"]),
                "blocked_implementations": list(isolation["blocked_implementations"]),
                "blocked_providers": list(isolation["blocked_providers"]),
            },
        }
    )


def _dispatch_mismatches(
    dispatch: DispatchRecord,
    *,
    candidate: dict[str, Any],
    fixture: dict[str, Any],
) -> list[str]:
    mismatches: list[str] = []
    if dispatch.task_type != fixture["task_type"]:
        mismatches.append("task_type")
    if dispatch.risk_level != fixture["risk_level"]:
        mismatches.append("risk_level")
    if sorted(dispatch.required_capabilities) != sorted(fixture["required_capabilities"]):
        mismatches.append("required_capabilities")

    implementation = dispatch.selected_implementation
    if implementation.provider_family != candidate["provider_family"]:
        mismatches.append("provider_family")
    if implementation.model != candidate["model"]:
        mismatches.append("model")
    if implementation.reasoning != candidate["reasoning_effort"]:
        mismatches.append("reasoning_effort")

    verifier = dispatch.verification.implementation
    if verifier.provider_family != candidate["verifier_provider_family"]:
        mismatches.append("verifier_provider_family")
    if verifier.model != candidate["verifier_model"]:
        mismatches.append("verifier_model")
    if not dispatch.verification.independent:
        mismatches.append("independent_verification")
    if dispatch.verification.human_approval_required:
        mismatches.append("human_approval_required")
    return mismatches


def _assert_dispatch_matches(
    dispatch: DispatchRecord,
    *,
    candidate: dict[str, Any],
    fixture: dict[str, Any],
    phase: str,
) -> None:
    mismatches = _dispatch_mismatches(
        dispatch,
        candidate=candidate,
        fixture=fixture,
    )
    if mismatches:
        raise ProviderAdapterContractError(
            "Controlled replay "
            f"{phase} did not resolve the declared candidate {candidate['candidate_id']}: "
            + ", ".join(mismatches)
        )


def _manifest_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": candidate["candidate_id"],
        "provider_family": candidate["provider_family"],
        "model": candidate["model"],
        "reasoning_effort": candidate["reasoning_effort"],
        "verifier_provider_family": candidate["verifier_provider_family"],
        "verifier_model": candidate["verifier_model"],
        "runtime_version": candidate["runtime_version"],
        "routing_policy_revision": candidate["routing_policy_revision"],
        "registry_revision": candidate["registry_revision"],
        "tool_versions": dict(candidate["tool_versions"]),
    }


def _version_context(candidate: dict[str, Any]) -> RouteOutcomeVersionContext:
    return RouteOutcomeVersionContext(
        runtime_version=str(candidate["runtime_version"]),
        repository_revision=str(candidate["repository_revision"]),
        routing_policy_revision=(
            str(candidate["routing_policy_revision"])
            if candidate.get("routing_policy_revision") is not None
            else None
        ),
        registry_revision=(
            str(candidate["registry_revision"])
            if candidate.get("registry_revision") is not None
            else None
        ),
        tool_versions=dict(candidate["tool_versions"]),
    )


def run_controlled_replay(
    plan: BenchmarkReplayPlan,
    fixtures: Sequence[BenchmarkFixtureRecord],
    engine: SpecialistRoutingEngine,
    connections: Mapping[str, ProviderConnection],
    *,
    repo_root: str | Path,
    artifact_root: str | Path,
    retry_policy: RetryPolicy | None = None,
    verification_policy: LiveVerificationPolicy | None = None,
    sleeper: Sleeper = sleep,
    random_source: RandomSource = random,
    attempt_clock: AttemptClock = monotonic,
) -> ControlledReplayExecution:
    """Execute a declared replay without granting Benchmark Lab route-selection authority.

    Candidate isolation is additive only: a plan may block implementations or provider
    families, but it cannot directly select, unblock, or rewrite a route. A no-network
    preflight must resolve the declared candidate through normal TEO routing before the
    guarded canary is allowed to execute.
    """
    plan_data = plan.to_dict()
    fixture_by_id = _fixture_map(plan_data, fixtures)
    policy = retry_policy or RetryPolicy.load(engine.config.root)
    policy.validate()
    if int(plan_data["harness"]["max_attempts"]) != policy.max_attempts_per_dispatch:
        raise ProviderAdapterContractError(
            "Controlled replay harness max_attempts must match the active canary retry policy"
        )
    if plan_data["harness"]["max_wall_time_seconds"] is not None:
        raise ProviderAdapterContractError(
            "Controlled replay does not claim a wall-time deadline until preemptive cancellation exists"
        )

    circuit_policy = ProviderCircuitPolicy.load(engine.config.root)
    outcomes: list[RouteOutcomeRecord] = []
    bindings: list[dict[str, Any]] = []
    root = Path(artifact_root)

    for candidate in plan_data["candidates"]:
        candidate_id = str(candidate["candidate_id"])
        for fixture_id in sorted(fixture_by_id):
            fixture = fixture_by_id[fixture_id]
            for trial_index in range(1, int(plan_data["trials_per_fixture"]) + 1):
                task = _task_for_trial(
                    plan=plan,
                    candidate=candidate,
                    fixture=fixture,
                    trial_index=trial_index,
                )

                preflight = engine.dispatch(task)
                _assert_dispatch_matches(
                    preflight,
                    candidate=candidate,
                    fixture=fixture,
                    phase="preflight",
                )

                telemetry = InMemoryRuntimeTelemetrySink()
                circuit = ProviderCircuitBreaker(
                    circuit_policy,
                    InMemoryCircuitStateStore(),
                )
                trial_root = (
                    root
                    / _safe_fragment(str(plan_data["replay_id"]))
                    / _safe_fragment(candidate_id)
                    / _safe_fragment(fixture_id)
                    / f"trial-{trial_index}"
                )
                runtime_outcome = execute_guarded_canary(
                    engine,
                    task,
                    connections,
                    artifact_root=trial_root,
                    retry_policy=policy,
                    circuit_breaker=circuit,
                    telemetry_sink=telemetry,
                    sleeper=sleeper,
                    random_source=random_source,
                    attempt_clock=attempt_clock,
                )
                _assert_dispatch_matches(
                    runtime_outcome.primary_dispatch,
                    candidate=candidate,
                    fixture=fixture,
                    phase="execution",
                )

                verification = None
                if runtime_outcome.execution_succeeded:
                    verification = verify_guarded_canary_outcome(
                        engine,
                        runtime_outcome,
                        connections,
                        artifact_root=trial_root,
                        verification_policy=verification_policy,
                    )

                route_outcome = build_guarded_canary_route_outcome(
                    runtime_outcome,
                    telemetry.events,
                    repo_root=repo_root,
                    versions=_version_context(candidate),
                    verification=verification,
                )
                outcomes.append(route_outcome)
                bindings.append(
                    {
                        "fixture_id": fixture_id,
                        "candidate_id": candidate_id,
                        "trial_index": trial_index,
                        "outcome_id": route_outcome.to_dict()["outcome_id"],
                    }
                )

    manifest_data = {
        "benchmark_lab_version": BENCHMARK_LAB_VERSION,
        "record_type": "benchmark_experiment",
        "experiment_id": f"replay-{plan.sha256}",
        "study_type": "replay",
        "claim_scope": plan_data["claim_scope"],
        "suite_id": plan_data["suite_id"],
        "suite_version": plan_data["suite_version"],
        "trials_per_fixture": plan_data["trials_per_fixture"],
        "primary_metric": plan_data["primary_metric"],
        "stopping_rule": plan_data["stopping_rule"],
        "harness": {
            "harness_id": plan_data["harness"]["harness_id"],
            "harness_version": plan_data["harness"]["harness_version"],
            "tool_access_profile": plan_data["harness"]["tool_access_profile"],
            "max_attempts": plan_data["harness"]["max_attempts"],
            "max_wall_time_seconds": plan_data["harness"]["max_wall_time_seconds"],
        },
        "candidates": [
            _manifest_candidate(candidate) for candidate in plan_data["candidates"]
        ],
        "bindings": bindings,
        "regression_baseline_candidate_id": None,
    }
    manifest = BenchmarkExperimentManifest.from_dict(
        manifest_data,
        repo_root=repo_root,
    )
    return ControlledReplayExecution(
        plan=plan,
        manifest=manifest,
        outcomes=tuple(outcomes),
    )


def _validate_replay_bundle(bundle: ControlledReplayExecution) -> None:
    plan = bundle.plan.to_dict()
    manifest = bundle.manifest.to_dict()
    expected_experiment_id = f"replay-{bundle.plan.sha256}"
    if manifest["experiment_id"] != expected_experiment_id:
        raise ProviderAdapterContractError(
            "Controlled replay manifest does not preserve the replay plan digest"
        )
    if manifest["study_type"] != "replay":
        raise ProviderAdapterContractError("Controlled replay bundle requires replay study_type")

    plan_candidates = {
        str(candidate["candidate_id"]): candidate for candidate in plan["candidates"]
    }
    manifest_candidates = {
        str(candidate["candidate_id"]): candidate for candidate in manifest["candidates"]
    }
    if set(plan_candidates) != set(manifest_candidates):
        raise ProviderAdapterContractError(
            "Controlled replay manifest candidate set does not match the replay plan"
        )
    for candidate_id, candidate in plan_candidates.items():
        if _manifest_candidate(candidate) != manifest_candidates[candidate_id]:
            raise ProviderAdapterContractError(
                f"Controlled replay manifest changed candidate {candidate_id}"
            )

    outcomes = {record.to_dict()["outcome_id"]: record.to_dict() for record in bundle.outcomes}
    bound_ids = [str(binding["outcome_id"]) for binding in manifest["bindings"]]
    if len(outcomes) != len(bundle.outcomes) or set(bound_ids) != set(outcomes):
        raise ProviderAdapterContractError(
            "Controlled replay outcome set does not exactly match manifest bindings"
        )
    for binding in manifest["bindings"]:
        candidate_id = str(binding["candidate_id"])
        outcome = outcomes[str(binding["outcome_id"])]
        expected_revision = str(plan_candidates[candidate_id]["repository_revision"])
        if outcome["versions"]["repository_revision"] != expected_revision:
            raise ProviderAdapterContractError(
                f"Controlled replay outcome repository revision drifted for {candidate_id}"
            )


def evaluate_controlled_replay(
    bundle: ControlledReplayExecution,
    fixtures: Sequence[BenchmarkFixtureRecord],
    *,
    repo_root: str | Path,
    generated_at: str | None = None,
) -> BenchmarkExperimentReport:
    """Evaluate a completed live replay through the existing Benchmark Lab report contract."""
    _validate_replay_bundle(bundle)
    report = evaluate_benchmark(
        bundle.manifest,
        fixtures,
        bundle.outcomes,
        repo_root=repo_root,
        generated_at=generated_at,
    )
    payload = report.to_dict()
    limitations: list[str] = []
    stale = (
        "Multi-verifier disagreement measurement and live replay execution are not yet implemented."
    )
    for item in payload["limitations"]:
        if item == stale:
            limitations.append("Multi-verifier disagreement measurement is not yet implemented.")
        else:
            limitations.append(item)
    limitations.append(
        "Controlled live replay used normal TEO routing with additive isolation, isolated per-trial circuit state, and the assigned live verifier; Benchmark Lab did not acquire route-selection authority."
    )
    payload["limitations"] = limitations
    payload["integrity_sha256"] = _canonical_sha256(
        payload,
        omit="integrity_sha256",
    )
    return BenchmarkExperimentReport.from_dict(payload, repo_root=repo_root)
