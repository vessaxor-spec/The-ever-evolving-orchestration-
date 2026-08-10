from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from .anthropic_adapter import CANARY_MODELS as ANTHROPIC_EXECUTOR_MODELS
from .anthropic_verifier import SUPPORTED_MODELS as ANTHROPIC_VERIFIER_MODELS
from .engine import RoutingError
from .google_adapter import CANARY_MODELS as GOOGLE_EXECUTOR_MODELS
from .google_verifier import SUPPORTED_MODEL_EFFORTS as GOOGLE_VERIFIER_MODEL_EFFORTS
from .openai_adapter import CANARY_MODELS as OPENAI_EXECUTOR_MODELS
from .openai_verifier import SUPPORTED_MODELS as OPENAI_VERIFIER_MODELS
from .provider_adapter import ProviderAdapterContractError
from .runtime_canary import _copy_task_for_redispatch
from .runtime_telemetry import RuntimeTelemetryPolicy
from .schemas import DispatchRecord, TaskRequest
from .specialist_routing import SpecialistRoutingEngine
from .verification_policy import LiveVerificationPolicy

LIVE_SCOPE_EXPANSION_POLICY_PATH = "policy/runtime/live-execution-expansion.yaml"


@dataclass(frozen=True, slots=True)
class LiveScopeCandidateGate:
    name: str
    passed: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class LiveScopeCandidateEvaluation:
    task_type: str
    state: str
    activation_authorized: bool
    primary_dispatch: dict[str, Any]
    model_failure_redispatch: dict[str, Any] | None
    provider_failure_redispatch: dict[str, Any] | None
    gates: tuple[LiveScopeCandidateGate, ...]
    ready_for_activation: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_type": self.task_type,
            "state": self.state,
            "activation_authorized": self.activation_authorized,
            "primary_dispatch": self.primary_dispatch,
            "model_failure_redispatch": self.model_failure_redispatch,
            "provider_failure_redispatch": self.provider_failure_redispatch,
            "gates": [gate.to_dict() for gate in self.gates],
            "ready_for_activation": self.ready_for_activation,
        }


class LiveScopeExpansionPolicy:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.validate()

    @classmethod
    def load(cls, repo_root: str | Path) -> "LiveScopeExpansionPolicy":
        path = Path(repo_root) / LIVE_SCOPE_EXPANSION_POLICY_PATH
        if not path.is_file():
            raise ProviderAdapterContractError(f"Live execution expansion policy not found: {path}")
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ProviderAdapterContractError("Live execution expansion policy must be a mapping")
        return cls(raw)

    @property
    def active_task_types(self) -> frozenset[str]:
        active = self.payload["active_scope"]
        return frozenset(str(item) for item in active["task_types"])

    @property
    def active_risk_levels(self) -> frozenset[str]:
        active = self.payload["active_scope"]
        return frozenset(str(item) for item in active["risk_levels"])

    def candidate(self, task_type: str) -> dict[str, Any]:
        candidate = self.payload["candidates"].get(task_type)
        if not isinstance(candidate, dict):
            raise ProviderAdapterContractError(f"Unknown live execution candidate: {task_type}")
        return candidate

    def validate(self) -> None:
        if self.payload.get("status") != "active":
            raise ProviderAdapterContractError("Live execution expansion policy must be active")
        active = self.payload.get("active_scope")
        candidates = self.payload.get("candidates")
        if not isinstance(active, dict) or not isinstance(candidates, dict):
            raise ProviderAdapterContractError(
                "Live execution expansion policy requires active_scope and candidates mappings"
            )
        if frozenset(str(item) for item in active.get("task_types", [])) != {"high_volume_simple"}:
            raise ProviderAdapterContractError(
                "Staged expansion policy must not widen the currently authorized live task scope"
            )
        if frozenset(str(item) for item in active.get("risk_levels", [])) != {"low", "medium"}:
            raise ProviderAdapterContractError(
                "Live execution expansion policy must keep high and critical risk unauthorized"
            )
        documentation = candidates.get("documentation")
        if not isinstance(documentation, dict):
            raise ProviderAdapterContractError("Documentation must be the declared staged candidate")
        if documentation.get("state") != "staged" or documentation.get("activation_authorized") is not False:
            raise ProviderAdapterContractError(
                "Documentation candidate must remain staged and unauthorized before activation evidence"
            )
        if documentation.get("task_type") != "documentation":
            raise ProviderAdapterContractError("Documentation candidate task identity drifted")
        if frozenset(str(item) for item in documentation.get("risk_levels", [])) != {"low", "medium"}:
            raise ProviderAdapterContractError(
                "Documentation candidate must remain restricted to low and medium risk"
            )
        expected = documentation.get("expected_route")
        probe = documentation.get("probe")
        evidence = documentation.get("evidence")
        requirements = documentation.get("activation_requirements")
        if not isinstance(expected, dict) or not isinstance(probe, dict) or not isinstance(evidence, dict):
            raise ProviderAdapterContractError(
                "Documentation candidate requires expected_route, probe, and evidence mappings"
            )
        if not isinstance(requirements, list) or not requirements:
            raise ProviderAdapterContractError("Documentation candidate requires activation requirements")
        for key in (
            "primary",
            "initial_fallback",
            "primary_verifier",
            "failure_redispatch_executor",
            "current_failure_redispatch_verifier",
        ):
            route = expected.get(key)
            if not isinstance(route, dict) or not route.get("provider_family") or not route.get("model"):
                raise ProviderAdapterContractError(f"Documentation candidate expected_route.{key} is incomplete")
        if evidence.get("controlled_replay") is not None or evidence.get("shadow_evaluation") is not None:
            raise ProviderAdapterContractError(
                "Staged candidate cannot claim replay or shadow evidence before those records exist"
            )


def _executor_supported(provider_family: str | None, model: str) -> bool:
    support = {
        "anthropic": ANTHROPIC_EXECUTOR_MODELS,
        "google": GOOGLE_EXECUTOR_MODELS,
        "openai": OPENAI_EXECUTOR_MODELS,
    }
    return bool(provider_family and model in support.get(provider_family, set()))


def _verifier_supported(provider_family: str | None, model: str) -> bool:
    if provider_family == "anthropic":
        return model in ANTHROPIC_VERIFIER_MODELS
    if provider_family == "google":
        return model in GOOGLE_VERIFIER_MODEL_EFFORTS
    if provider_family == "openai":
        return model in OPENAI_VERIFIER_MODELS
    return False


def _redispatch(
    engine: SpecialistRoutingEngine,
    task: TaskRequest,
    dispatch: DispatchRecord,
    failure_scope: str,
) -> tuple[DispatchRecord | None, str | None]:
    prepared = _copy_task_for_redispatch(task, dispatch, failure_scope)
    try:
        return engine.dispatch(prepared), None
    except RoutingError as exc:
        return None, str(exc)


def _route_matches(choice: Any, expected: dict[str, Any]) -> bool:
    return bool(
        choice
        and choice.provider_family == expected["provider_family"]
        and choice.model == expected["model"]
        and choice.reasoning == expected.get("reasoning_effort")
    )


def _dispatch_summary(dispatch: DispatchRecord | None, error: str | None = None) -> dict[str, Any] | None:
    if dispatch is None:
        return {"error": error or "redispatch unavailable"}
    return {
        "dispatch_id": dispatch.dispatch_id,
        "task_type": dispatch.task_type,
        "risk_level": dispatch.risk_level,
        "primary_provider_family": dispatch.selected_implementation.provider_family,
        "primary_model": dispatch.selected_implementation.model,
        "primary_reasoning_effort": dispatch.selected_implementation.reasoning,
        "fallback_provider_family": (
            dispatch.fallback_implementation.provider_family if dispatch.fallback_implementation else None
        ),
        "fallback_model": dispatch.fallback_implementation.model if dispatch.fallback_implementation else None,
        "verifier_provider_family": dispatch.verification.implementation.provider_family,
        "verifier_model": dispatch.verification.implementation.model,
        "verifier_reasoning_effort": dispatch.verification.implementation.reasoning,
        "human_approval_required": dispatch.verification.human_approval_required,
    }


def evaluate_live_scope_candidate(
    engine: SpecialistRoutingEngine,
    *,
    task_type: str = "documentation",
) -> LiveScopeCandidateEvaluation:
    """Evaluate one staged live-scope candidate without invoking a provider."""
    policy = LiveScopeExpansionPolicy.load(engine.config.root)
    candidate = policy.candidate(task_type)
    probe = candidate["probe"]
    expected = candidate["expected_route"]
    task = TaskRequest.from_dict(
        {
            "task_id": str(probe["task_id"]),
            "task": str(probe["task"]),
            "task_type": task_type,
            "risk_level": str(probe["risk_level"]),
        }
    )
    primary = engine.dispatch(task)
    model_redispatch, model_error = _redispatch(engine, task, primary, "model")
    provider_redispatch, provider_error = _redispatch(engine, task, primary, "provider")

    telemetry_policy = RuntimeTelemetryPolicy.load(engine.config.root)
    verification_policy = LiveVerificationPolicy.load(engine.config.root)
    active_scope_unchanged = (
        policy.active_task_types == {"high_volume_simple"}
        and telemetry_policy.task_types == {"high_volume_simple"}
        and verification_policy.task_types == {"high_volume_simple"}
    )

    redispatches = (model_redispatch, provider_redispatch)
    redispatch_route_matches = all(
        dispatch is not None
        and _route_matches(dispatch.selected_implementation, expected["failure_redispatch_executor"])
        and _route_matches(
            dispatch.verification.implementation,
            expected["current_failure_redispatch_verifier"],
        )
        and dispatch.verification.implementation.provider_family
        != dispatch.selected_implementation.provider_family
        for dispatch in redispatches
    )
    fallback_verifier_fresh = all(
        dispatch is not None
        and dispatch.verification.implementation.model
        != primary.verification.implementation.model
        for dispatch in redispatches
    )

    gates = (
        LiveScopeCandidateGate(
            "active_scope_unchanged",
            active_scope_unchanged,
            "Current telemetry and live-verification policy still authorize only high_volume_simple.",
        ),
        LiveScopeCandidateGate(
            "exact_primary_route_matches",
            _route_matches(primary.selected_implementation, expected["primary"]),
            "Candidate must preserve the canonical documentation primary route.",
        ),
        LiveScopeCandidateGate(
            "exact_initial_fallback_matches",
            _route_matches(primary.fallback_implementation, expected["initial_fallback"]),
            "Candidate must report the fallback currently recorded by the canonical initial dispatch.",
        ),
        LiveScopeCandidateGate(
            "initial_fallback_provider_diverse",
            bool(
                primary.fallback_implementation
                and primary.fallback_implementation.provider_family
                != primary.selected_implementation.provider_family
            ),
            "The initial dispatch fallback must be provider-diverse before live activation.",
        ),
        LiveScopeCandidateGate(
            "primary_verifier_matches",
            _route_matches(primary.verification.implementation, expected["primary_verifier"]),
            "Candidate must preserve the canonical independent primary verifier.",
        ),
        LiveScopeCandidateGate(
            "failure_redispatch_route_matches",
            redispatch_route_matches,
            "Model- and provider-failure redispatch must be measured against actual canonical routing.",
        ),
        LiveScopeCandidateGate(
            "primary_executor_adapter_supported",
            _executor_supported(
                primary.selected_implementation.provider_family,
                primary.selected_implementation.model,
            ),
            "The guarded executor must support the canonical primary model before activation.",
        ),
        LiveScopeCandidateGate(
            "failure_redispatch_executor_adapter_supported",
            all(
                dispatch is not None
                and _executor_supported(
                    dispatch.selected_implementation.provider_family,
                    dispatch.selected_implementation.model,
                )
                for dispatch in redispatches
            ),
            "Every measured failure redispatch executor must have guarded adapter support.",
        ),
        LiveScopeCandidateGate(
            "primary_verifier_adapter_supported",
            _verifier_supported(
                primary.verification.implementation.provider_family,
                primary.verification.implementation.model,
            ),
            "The guarded verifier must support the canonical primary verifier before activation.",
        ),
        LiveScopeCandidateGate(
            "failure_redispatch_verifier_adapter_supported",
            all(
                dispatch is not None
                and _verifier_supported(
                    dispatch.verification.implementation.provider_family,
                    dispatch.verification.implementation.model,
                )
                for dispatch in redispatches
            ),
            "Every measured failure redispatch verifier must have guarded verifier adapter support.",
        ),
        LiveScopeCandidateGate(
            "fallback_redispatch_verifier_is_fresh",
            fallback_verifier_fresh,
            "Fallback redispatch cannot reuse the primary dispatch verifier implementation.",
        ),
        LiveScopeCandidateGate(
            "controlled_replay_evidence_present",
            bool(candidate["evidence"].get("controlled_replay")),
            "Activation requires a reproducible controlled replay record for documentation.",
        ),
        LiveScopeCandidateGate(
            "shadow_evaluation_evidence_present",
            bool(candidate["evidence"].get("shadow_evaluation")),
            "Activation requires bounded shadow evaluation of the replay evidence.",
        ),
        LiveScopeCandidateGate(
            "high_and_critical_risk_refusal_proven",
            set(candidate["risk_levels"]) == {"low", "medium"},
            "The candidate policy excludes high and critical risk.",
        ),
    )

    return LiveScopeCandidateEvaluation(
        task_type=task_type,
        state=str(candidate["state"]),
        activation_authorized=bool(candidate["activation_authorized"]),
        primary_dispatch=_dispatch_summary(primary) or {},
        model_failure_redispatch=_dispatch_summary(model_redispatch, model_error),
        provider_failure_redispatch=_dispatch_summary(provider_redispatch, provider_error),
        gates=gates,
        ready_for_activation=bool(candidate["activation_authorized"]) and all(
            gate.passed for gate in gates
        ),
    )
