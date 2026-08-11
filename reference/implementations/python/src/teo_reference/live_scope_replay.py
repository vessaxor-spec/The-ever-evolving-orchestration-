from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from random import random
from time import monotonic, sleep
from typing import Any, Mapping

from jsonschema import Draft202012Validator

from .anthropic_adapter import AnthropicMessagesAdapter
from .google_verifier import GoogleLiveVerifier
from .live_scope_candidate import LiveScopeExpansionPolicy, evaluate_live_scope_candidate
from .openai_adapter import OpenAIResponsesAdapter
from .openai_verifier import OpenAILiveVerifier
from .provider_adapter import (
    ProviderAdapterContractError,
    ProviderExecutionRequest,
    ProviderExecutionResponse,
    validate_provider_response,
)
from .provider_connection import ProviderConnection
from .route_outcome import (
    RouteOutcomeRecord,
    RouteOutcomeVersionContext,
    build_guarded_canary_route_outcome,
)
from .runtime_canary import CanaryRuntimeOutcome
from .runtime_circuit_breaker import (
    InMemoryCircuitStateStore,
    ProviderCircuitBreaker,
    ProviderCircuitPolicy,
)
from .runtime_retry import (
    AttemptClock,
    RandomSource,
    RetryPolicy,
    Sleeper,
    execute_with_transient_retry,
)
from .runtime_telemetry import InMemoryRuntimeTelemetrySink, RuntimeTelemetryEvent
from .schemas import DispatchRecord, TaskRequest, VerificationResult
from .specialist_routing import SpecialistRoutingEngine
from .verification_adapter import LiveVerificationError, LiveVerificationRequest, read_execution_output
from .verification_policy import LiveVerificationPolicy

LIVE_SCOPE_REPLAY_PLAN_SCHEMA_PATH = "reference/schemas/live-scope-replay-plan.schema.json"
LIVE_SCOPE_REPLAY_RECORD_SCHEMA_PATH = "reference/schemas/live-scope-replay-record.schema.json"

_PRE_REPLAY_REQUIRED_GATES = {
    "active_scope_unchanged",
    "exact_primary_route_matches",
    "exact_initial_fallback_matches",
    "initial_fallback_provider_diverse",
    "primary_verifier_matches",
    "failure_redispatch_route_matches",
    "primary_executor_adapter_supported",
    "failure_redispatch_executor_adapter_supported",
    "primary_verifier_adapter_supported",
    "failure_redispatch_verifier_adapter_supported",
    "fallback_redispatch_verifier_is_fresh",
    "high_and_critical_risk_refusal_proven",
}


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


def _load_schema(repo_root: str | Path, relative_path: str) -> dict[str, Any]:
    path = Path(repo_root) / relative_path
    if not path.is_file():
        raise ProviderAdapterContractError(f"Live-scope replay schema not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProviderAdapterContractError(
            f"Live-scope replay schema could not be loaded: {path}"
        ) from exc
    if not isinstance(payload, dict):
        raise ProviderAdapterContractError("Live-scope replay schema must be an object")
    return payload


def _validate_schema(
    data: dict[str, Any],
    *,
    repo_root: str | Path,
    schema_path: str,
    label: str,
) -> None:
    validator = Draft202012Validator(_load_schema(repo_root, schema_path))
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        path = ".".join(str(item) for item in first.path) or "<root>"
        raise ProviderAdapterContractError(
            f"{label} schema validation failed at {path}: {first.message}"
        )


def _safe_fragment(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-.") or "item"


@dataclass(frozen=True, slots=True)
class LiveScopeReplayPlan:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "LiveScopeReplayPlan":
        _validate_schema(
            data,
            repo_root=repo_root,
            schema_path=LIVE_SCOPE_REPLAY_PLAN_SCHEMA_PATH,
            label="Live-scope replay plan",
        )
        fixture_ids = [str(item["fixture_id"]) for item in data["fixtures"]]
        if len(set(fixture_ids)) != len(fixture_ids):
            raise ProviderAdapterContractError("Live-scope replay fixture IDs must be unique")
        return cls(payload=json.loads(json.dumps(data)))

    @property
    def sha256(self) -> str:
        return _canonical_sha256(self.payload)

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


@dataclass(frozen=True, slots=True)
class LiveScopeReplayRecord:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "LiveScopeReplayRecord":
        _validate_schema(
            data,
            repo_root=repo_root,
            schema_path=LIVE_SCOPE_REPLAY_RECORD_SCHEMA_PATH,
            label="Live-scope replay record",
        )
        expected = str(data["integrity_sha256"])
        actual = _canonical_sha256(data, omit="integrity_sha256")
        if expected != actual:
            raise ProviderAdapterContractError(
                "Live-scope replay record integrity hash does not match content"
            )
        bindings = data["bindings"]
        outcome_ids = [str(item["outcome_id"]) for item in bindings]
        if len(set(outcome_ids)) != len(outcome_ids):
            raise ProviderAdapterContractError(
                "Live-scope replay bindings must reference unique route outcomes"
            )
        summary = data["summary"]
        disposition_total = sum(
            int(summary[key])
            for key in (
                "completed",
                "verification_failed",
                "awaiting_human",
                "verification_missing",
                "execution_failed",
                "abandoned",
            )
        )
        if int(summary["total_trials"]) != len(bindings) or disposition_total != len(bindings):
            raise ProviderAdapterContractError(
                "Live-scope replay summary does not match replay bindings"
            )
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


@dataclass(frozen=True, slots=True)
class LiveScopeReplayExecution:
    plan: LiveScopeReplayPlan
    outcomes: tuple[RouteOutcomeRecord, ...]
    record: LiveScopeReplayRecord


def _route_choice(choice: Any) -> dict[str, Any]:
    return {
        "provider_family": str(choice.provider_family),
        "model": str(choice.model),
        "reasoning_effort": choice.reasoning,
    }


def _expected_route(candidate: dict[str, Any]) -> dict[str, dict[str, Any]]:
    expected = candidate["expected_route"]
    return {
        "primary": dict(expected["primary"]),
        "initial_fallback": dict(expected["initial_fallback"]),
        "primary_verifier": dict(expected["primary_verifier"]),
        "failure_redispatch_executor": dict(expected["failure_redispatch_executor"]),
        "failure_redispatch_verifier": dict(expected["current_failure_redispatch_verifier"]),
    }


def _choice_matches(choice: Any, expected: dict[str, Any]) -> bool:
    return bool(
        choice
        and choice.provider_family == expected["provider_family"]
        and choice.model == expected["model"]
        and choice.reasoning == expected.get("reasoning_effort")
    )


def _assert_pre_replay_candidate_ready(engine: SpecialistRoutingEngine) -> dict[str, Any]:
    policy = LiveScopeExpansionPolicy.load(engine.config.root)
    candidate = policy.candidate("documentation")
    evaluation = evaluate_live_scope_candidate(engine)
    gate_map = {gate.name: gate.passed for gate in evaluation.gates}
    missing = sorted(name for name in _PRE_REPLAY_REQUIRED_GATES if not gate_map.get(name, False))
    if missing:
        raise ProviderAdapterContractError(
            "Documentation replay preflight failed required candidate gates: " + ", ".join(missing)
        )
    if candidate["state"] != "staged" or candidate["activation_authorized"] is not False:
        raise ProviderAdapterContractError(
            "Documentation replay requires a staged, unauthorized live-scope candidate"
        )
    if policy.active_task_types != {"high_volume_simple"}:
        raise ProviderAdapterContractError(
            "Documentation replay refuses any pre-existing widening of active live task scope"
        )
    if policy.active_risk_levels != {"low", "medium"}:
        raise ProviderAdapterContractError(
            "Documentation replay requires the active live risk scope to remain low and medium only"
        )
    return candidate


def _task_for_trial(
    plan: LiveScopeReplayPlan,
    fixture: dict[str, Any],
    trial_index: int,
) -> TaskRequest:
    seed = f"{plan.sha256}|{fixture['fixture_id']}|{trial_index}".encode("utf-8")
    task_id = f"documentation-replay-{hashlib.sha256(seed).hexdigest()[:20]}"
    return TaskRequest.from_dict(
        {
            "task_id": task_id,
            "task": fixture["task"],
            "task_type": "documentation",
            "risk_level": fixture["risk_level"],
            "constraints": {
                "required_capabilities": list(fixture["required_capabilities"]),
                "accepted_preview_models": [],
                "blocked_implementations": [],
                "blocked_providers": [],
            },
        }
    )


def _assert_primary_dispatch(
    dispatch: DispatchRecord,
    *,
    fixture: dict[str, Any],
    candidate: dict[str, Any],
) -> None:
    expected = candidate["expected_route"]
    mismatches: list[str] = []
    if dispatch.task_type != "documentation":
        mismatches.append("task_type")
    if dispatch.risk_level != fixture["risk_level"]:
        mismatches.append("risk_level")
    required = set(str(item) for item in fixture["required_capabilities"])
    if not required.issubset(set(dispatch.required_capabilities)):
        mismatches.append("required_capabilities")
    if not _choice_matches(dispatch.selected_implementation, expected["primary"]):
        mismatches.append("primary")
    if not _choice_matches(dispatch.fallback_implementation, expected["initial_fallback"]):
        mismatches.append("initial_fallback")
    if not _choice_matches(dispatch.verification.implementation, expected["primary_verifier"]):
        mismatches.append("primary_verifier")
    if not dispatch.verification.independent:
        mismatches.append("independent_verification")
    if dispatch.verification.human_approval_required:
        mismatches.append("human_approval_required")
    if dispatch.selected_implementation.provider_family == dispatch.verification.implementation.provider_family:
        mismatches.append("provider_diversity")
    if mismatches:
        raise ProviderAdapterContractError(
            "Documentation controlled replay preflight changed the staged route: "
            + ", ".join(mismatches)
        )


def _execute_staged_documentation_dispatch(
    dispatch: DispatchRecord,
    connections: Mapping[str, ProviderConnection],
    artifact_root: str | Path,
) -> ProviderExecutionResponse:
    if dispatch.task_type != "documentation":
        raise ProviderAdapterContractError(
            "Staged documentation replay executor refuses non-documentation dispatches"
        )
    if dispatch.risk_level not in {"low", "medium"}:
        raise ProviderAdapterContractError(
            "Staged documentation replay executor refuses high and critical risk"
        )
    provider = dispatch.selected_implementation.provider_family
    if provider not in connections:
        raise ProviderAdapterContractError(
            f"No staged replay connection is available for provider {provider}"
        )
    root = Path(artifact_root)
    if provider == "anthropic":
        adapter = AnthropicMessagesAdapter(
            connections[provider],
            artifact_dir=root / "anthropic",
        )
    elif provider == "openai":
        adapter = OpenAIResponsesAdapter(
            connections[provider],
            artifact_dir=root / "openai",
        )
    else:
        raise ProviderAdapterContractError(
            f"Staged documentation replay has no executor implementation for provider {provider}"
        )
    request = ProviderExecutionRequest.from_dispatch(dispatch)
    response = adapter.execute(request)
    validate_provider_response(dispatch, request, response)
    return response


def _telemetry_observer(sink: InMemoryRuntimeTelemetrySink):
    def observe(
        dispatch: DispatchRecord,
        attempt_number: int,
        response: ProviderExecutionResponse,
        duration_seconds: float,
    ) -> None:
        sink.append(
            RuntimeTelemetryEvent.from_attempt(
                dispatch,
                response,
                role="primary",
                attempt_number=attempt_number,
                duration_seconds=duration_seconds,
            )
        )

    return observe


def _verify_staged_documentation_execution(
    engine: SpecialistRoutingEngine,
    dispatch: DispatchRecord,
    execution: ProviderExecutionResponse,
    connections: Mapping[str, ProviderConnection],
    *,
    artifact_root: str | Path,
) -> VerificationResult:
    policy = LiveVerificationPolicy.load(engine.config.root)
    policy.validate()
    if dispatch.task_type != "documentation":
        raise LiveVerificationError("Staged documentation replay verifier refuses other task types")
    if dispatch.risk_level not in {"low", "medium"}:
        raise LiveVerificationError("Staged documentation replay verifier refuses high and critical risk")
    if execution.status != "succeeded" or not execution.output_ref:
        raise LiveVerificationError("Staged documentation replay verification requires successful execution")
    if execution.dispatch_id != dispatch.dispatch_id:
        raise LiveVerificationError("Replay execution artifact does not belong to the active replay dispatch")
    if execution.provider_family != dispatch.selected_implementation.provider_family:
        raise LiveVerificationError("Replay execution provider changed the staged dispatch")
    if execution.model != dispatch.selected_implementation.model:
        raise LiveVerificationError("Replay execution model changed the staged dispatch")
    if dispatch.verification.human_approval_required:
        raise LiveVerificationError(
            "Staged documentation replay cannot satisfy a qualified-human approval requirement"
        )

    output_text = read_execution_output(
        execution.output_ref,
        allowed_root=artifact_root,
        max_bytes=policy.max_output_bytes,
    )
    request = LiveVerificationRequest.from_execution(dispatch, output_text)
    if request.verifier_provider_family == execution.provider_family:
        raise LiveVerificationError(
            "Staged documentation replay requires provider-diverse assigned verification"
        )
    if request.verifier_model == execution.model:
        raise LiveVerificationError(
            "Staged documentation replay requires an independent verifier model"
        )

    if request.verifier_provider_family == "openai":
        response = OpenAILiveVerifier(connections).verify(request)
    elif request.verifier_provider_family == "google":
        response = GoogleLiveVerifier(connections).verify(request)
    else:
        raise LiveVerificationError(
            f"Staged documentation replay has no assigned verifier adapter for {request.verifier_provider_family}"
        )
    if response.provider_family != request.verifier_provider_family:
        raise LiveVerificationError("Replay verifier changed the assigned provider family")
    if response.model != request.verifier_model:
        raise LiveVerificationError("Replay verifier changed the assigned model")
    return response.decision.to_verification_result(
        dispatch,
        evidence=list(response.evidence),
    )


def _version_context(plan: dict[str, Any]) -> RouteOutcomeVersionContext:
    versions = plan["versions"]
    return RouteOutcomeVersionContext(
        runtime_version=str(versions["runtime_version"]),
        repository_revision=str(versions["repository_revision"]),
        routing_policy_revision=(
            str(versions["routing_policy_revision"])
            if versions.get("routing_policy_revision") is not None
            else None
        ),
        registry_revision=(
            str(versions["registry_revision"])
            if versions.get("registry_revision") is not None
            else None
        ),
        tool_versions=dict(versions["tool_versions"]),
    )


def _build_record(
    plan: LiveScopeReplayPlan,
    candidate: dict[str, Any],
    outcomes: list[RouteOutcomeRecord],
    bindings: list[dict[str, Any]],
    *,
    repo_root: str | Path,
) -> LiveScopeReplayRecord:
    disposition_counts = {
        "completed": 0,
        "verification_failed": 0,
        "awaiting_human": 0,
        "verification_missing": 0,
        "execution_failed": 0,
        "abandoned": 0,
    }
    for binding in bindings:
        disposition_counts[str(binding["final_disposition"])] += 1

    plan_data = plan.to_dict()
    payload = {
        "replay_version": "1",
        "record_type": "live_scope_replay_record",
        "replay_id": plan_data["replay_id"],
        "plan_sha256": plan.sha256,
        "task_type": "documentation",
        "candidate_state": "staged",
        "activation_authorized": False,
        "evidence_only": True,
        "live_scope_widened": False,
        "telemetry_persisted": False,
        "active_scope": {
            "task_types": ["high_volume_simple"],
            "risk_levels": ["low", "medium"],
        },
        "candidate_route": _expected_route(candidate),
        "suite_id": plan_data["suite_id"],
        "suite_version": plan_data["suite_version"],
        "trials_per_fixture": plan_data["trials_per_fixture"],
        "bindings": bindings,
        "summary": {
            "total_trials": len(bindings),
            **disposition_counts,
        },
        "limitations": [
            "This record is staged replay evidence and does not authorize documentation live execution.",
            "Replay telemetry is held only in memory for canonical Route-Outcome Evidence construction and is not active runtime telemetry.",
            "Automatic fallback is disabled in this replay milestone. Deliberate rollback and recovery execution remains a separate later gate.",
            "A successful replay does not satisfy Shadow Route Evaluation, rollback, recovery, or independent active-scope review requirements.",
        ],
    }
    payload["integrity_sha256"] = _canonical_sha256(payload)
    return LiveScopeReplayRecord.from_dict(payload, repo_root=repo_root)


def run_staged_documentation_replay(
    plan: LiveScopeReplayPlan,
    engine: SpecialistRoutingEngine,
    connections: Mapping[str, ProviderConnection],
    *,
    repo_root: str | Path,
    artifact_root: str | Path,
    retry_policy: RetryPolicy | None = None,
    sleeper: Sleeper = sleep,
    random_source: RandomSource = random,
    attempt_clock: AttemptClock = monotonic,
) -> LiveScopeReplayExecution:
    """Execute the staged documentation primary route without widening active live scope."""
    repo = Path(repo_root).resolve()
    if repo != Path(engine.config.root).resolve():
        raise ProviderAdapterContractError(
            "Live-scope replay repo_root must match the routing engine configuration root"
        )

    plan_data = plan.to_dict()
    if plan_data["task_type"] != "documentation":
        raise ProviderAdapterContractError("Only documentation is staged for live-scope replay")
    candidate = _assert_pre_replay_candidate_ready(engine)

    policy = retry_policy or RetryPolicy.load(engine.config.root)
    policy.validate()
    if int(plan_data["harness"]["max_attempts"]) != policy.max_attempts_per_dispatch:
        raise ProviderAdapterContractError(
            "Staged replay harness max_attempts must match the active retry policy"
        )

    prepared_trials: list[tuple[dict[str, Any], int, TaskRequest, DispatchRecord]] = []
    for fixture in plan_data["fixtures"]:
        for trial_index in range(1, int(plan_data["trials_per_fixture"]) + 1):
            task = _task_for_trial(plan, fixture, trial_index)
            dispatch = engine.dispatch(task)
            _assert_primary_dispatch(
                dispatch,
                fixture=fixture,
                candidate=candidate,
            )
            prepared_trials.append((fixture, trial_index, task, dispatch))

    outcomes: list[RouteOutcomeRecord] = []
    bindings: list[dict[str, Any]] = []
    circuit_policy = ProviderCircuitPolicy.load(engine.config.root)
    root = Path(artifact_root)

    for fixture, trial_index, task, preflight_dispatch in prepared_trials:
        telemetry = InMemoryRuntimeTelemetrySink()
        circuit = ProviderCircuitBreaker(circuit_policy, InMemoryCircuitStateStore())
        prepared_task = circuit.prepare_task(task)
        dispatch = engine.dispatch(prepared_task)
        _assert_primary_dispatch(
            dispatch,
            fixture=fixture,
            candidate=candidate,
        )
        if _route_choice(dispatch.selected_implementation) != _route_choice(
            preflight_dispatch.selected_implementation
        ):
            raise ProviderAdapterContractError(
                "Documentation replay execution route drifted after no-network preflight"
            )
        circuit.claim_dispatch(dispatch)

        trial_root = (
            root
            / _safe_fragment(str(plan_data["replay_id"]))
            / _safe_fragment(str(fixture["fixture_id"]))
            / f"trial-{trial_index}"
        )
        execution = execute_with_transient_retry(
            dispatch,
            connections,
            trial_root,
            _execute_staged_documentation_dispatch,
            policy,
            sleeper=sleeper,
            random_source=random_source,
            attempt_observer=_telemetry_observer(telemetry),
            attempt_clock=attempt_clock,
        )
        response = execution.response
        circuit_record = circuit.observe(dispatch, response)
        if circuit_record.state not in {"closed", "open", "half_open"}:
            raise ProviderAdapterContractError("Staged replay observed an invalid circuit state")

        runtime_outcome = CanaryRuntimeOutcome(
            status=("primary_executed" if response.status == "succeeded" else "execution_failed"),
            primary_dispatch=dispatch,
            primary_response=response,
            primary_attempts=execution.attempts,
            primary_retry_delays_seconds=execution.delays_seconds,
            primary_provider_circuit_state=circuit_record.state,
        )
        verification = None
        if response.status == "succeeded":
            verification = _verify_staged_documentation_execution(
                engine,
                dispatch,
                response,
                connections,
                artifact_root=trial_root,
            )

        route_outcome = build_guarded_canary_route_outcome(
            runtime_outcome,
            telemetry.events,
            repo_root=repo,
            versions=_version_context(plan_data),
            verification=verification,
        )
        outcomes.append(route_outcome)
        outcome_data = route_outcome.to_dict()
        bindings.append(
            {
                "fixture_id": str(fixture["fixture_id"]),
                "trial_index": trial_index,
                "outcome_id": str(outcome_data["outcome_id"]),
                "final_disposition": str(outcome_data["final_disposition"]),
            }
        )

    record = _build_record(
        plan,
        candidate,
        outcomes,
        bindings,
        repo_root=repo,
    )
    return LiveScopeReplayExecution(
        plan=plan,
        outcomes=tuple(outcomes),
        record=record,
    )
