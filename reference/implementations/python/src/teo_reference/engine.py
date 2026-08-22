from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, Sequence
from uuid import uuid4

from .adapters.configured_runtime_selection import ConfiguredRuntimeSelectionAdapter
from .adapters.filesystem import FilesystemArtifactIntegrityAdapter
from .application.finalization import FinalizationError, FinalizationService
from .config import ConfigBundle
from .domain.routing import RISK_PATTERNS as RISK_PATTERNS
from .domain.routing import TASK_PATTERNS as TASK_PATTERNS
from .domain.routing import RoutingPolicyError, assess_risk, classify_task
from .domain.runtime_binding import CalibrationRequirements, EligibilityRequirements
from .domain.runtime_selection import RuntimeSelectionRequest, RuntimeSelectionScope
from .ports.artifact import ArtifactIntegrityPort
from .ports.runtime_selection import RuntimeSelectionPort
from .schemas import (
    DispatchRecord,
    ExecutionResult,
    FinalOutcome,
    ImplementationChoice,
    RISK_ORDER,
    TaskRequest,
    VerificationPlan,
    VerificationResult,
    utc_now,
)

ROUTE_IMPLEMENTATION_KEYS: dict[str, tuple[str, ...]] = {
    "orchestration": ("primary",),
    "operations": ("primary",),
    "project_delivery": ("primary",),
    "incident_response": ("primary",),
    "user_research": ("primary",),
    "compliance_review": ("primary",),
    "market_research": ("primary",),
    "analytics": ("primary",),
    "architecture_design": ("primary",),
    "daily_coding": ("primary",),
    "deep_debugging": ("primary",),
    "repo_wide_refactor": ("executor",),
    "deep_research": ("primary",),
    "code_review": ("executable_review",),
    "security_review": ("primary",),
    "multimodal_analysis": ("primary",),
    "high_volume_simple": ("primary",),
    "documentation": ("primary",),
}

VERIFIER_KEYS: tuple[str, ...] = (
    "verifier",
    "executable_verifier",
    "semantic_reviewer",
    "technical_verifier",
    "hypothesis_reviewer",
    "engineering_reasoning_review",
    "semantic_review",
    "synthesis",
    "escalation",
)

CAPABILITY_FAMILY: tuple[tuple[set[str], str], ...] = (
    ({"coding", "debugging", "tool_execution", "executable_verification"}, "coding"),
    ({"architecture", "planning", "high_reasoning", "orchestration_reasoning"}, "engineering_reasoning"),
    (
        {
            "statistical_analysis",
            "sql_analysis",
            "experiment_design",
            "data_quality_assessment",
            "causal_reasoning",
            "model_validation",
            "reproducible_analysis",
        },
        "analytics",
    ),
    (
        {
            "market_intelligence",
            "competitive_analysis",
            "trend_analysis",
            "current_information_retrieval",
            "source_validation",
            "qualitative_research",
            "thematic_analysis",
            "evidence_synthesis",
            "interview_transcript_analysis",
            "survey_analysis",
            "usability_research",
            "mixed_methods_reasoning",
            "uncertainty_calibration",
            "privacy_and_research_ethics",
            "user_insight_translation",
            "compliance_reasoning",
            "regulatory_applicability_analysis",
            "control_mapping",
            "evidence_assessment",
            "audit_methodology",
            "privacy_and_data_governance",
            "ai_governance",
            "third_party_risk_analysis",
            "risk_classification",
            "traceable_writing",
        },
        "research",
    ),
    ({"synthesis", "technical_accuracy", "clear_writing"}, "general_reasoning"),
    ({"visual_reasoning", "visual_analysis"}, "multimodal"),
)


class RoutingError(RuntimeError):
    pass


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


class OrchestrationEngine:
    def __init__(
        self,
        config: ConfigBundle,
        *,
        artifact_integrity: ArtifactIntegrityPort | None = None,
        runtime_selector: RuntimeSelectionPort | None = None,
        runtime_calibration_requirements: CalibrationRequirements | None = None,
    ):
        self.config = config
        self._finalization = FinalizationService(
            artifact_integrity or FilesystemArtifactIntegrityAdapter()
        )
        self._runtime_selector = runtime_selector
        self._runtime_calibration_requirements = (
            runtime_calibration_requirements or CalibrationRequirements(required=False)
        )

    @classmethod
    def from_repo(
        cls,
        repo_root: str,
        *,
        runtime_selector: RuntimeSelectionPort | None = None,
        runtime_calibration_requirements: CalibrationRequirements | None = None,
    ) -> "OrchestrationEngine":
        return cls(
            ConfigBundle.load(repo_root),
            runtime_selector=runtime_selector,
            runtime_calibration_requirements=runtime_calibration_requirements,
        )

    def _runtime_selection_port(self) -> RuntimeSelectionPort:
        if self._runtime_selector is not None:
            return self._runtime_selector
        registry = getattr(self.config, "model_registry", None)
        if registry is None:
            raise RoutingError(
                "Runtime dispatch requires model_registry when no runtime selector is injected"
            )
        self._runtime_selector = ConfiguredRuntimeSelectionAdapter(registry)
        return self._runtime_selector

    def dispatch(self, task: TaskRequest) -> DispatchRecord:
        task_type, classification_reason = self._classify_task(task)
        risk, risk_reason = self._assess_risk(task)
        route = self.config.team_routes.get(task_type)
        if not route:
            raise RoutingError(f"No team route for task type: {task_type}")

        team = str(route["primary_team"])
        worker = self._resolve_worker(route, task)
        specialist, specialist_warning = self._resolve_specialist(task, team, worker)
        if specialist:
            specialist_risk = str(specialist[1].get("risk_profile", risk))
            if specialist_risk in RISK_ORDER and RISK_ORDER[specialist_risk] > RISK_ORDER[risk]:
                risk = specialist_risk
                risk_reason += (
                    f" Specialist {specialist[0]} elevated the effective risk to {specialist_risk}."
                )
        specialist_name = specialist[0] if specialist else None
        risk, refinement_reason = self._refine_effective_risk(task, specialist_name, risk)
        if refinement_reason:
            risk_reason += " " + refinement_reason

        capabilities = self._resolve_capabilities(task, worker)
        evaluated_at = utc_now()
        primary = self._select_runtime_choice(
            task=task,
            task_type=task_type,
            worker=worker,
            role="primary",
            risk=risk,
            capabilities=capabilities,
            specialist=specialist_name,
            evaluated_at=evaluated_at,
        )
        primary_policy_warning = self._primary_policy_warning(task_type, worker, task, primary)
        fallback = self._select_fallback_runtime(
            task=task,
            task_type=task_type,
            worker=worker,
            risk=risk,
            capabilities=capabilities,
            specialist=specialist_name,
            primary=primary,
            evaluated_at=evaluated_at,
        )
        verification = self._verification_plan(
            task_type,
            risk,
            task,
            primary,
            worker,
            specialist[1] if specialist else None,
            specialist_name=specialist_name,
            evaluated_at=evaluated_at,
        )

        warnings = [primary_policy_warning] if primary_policy_warning else []
        if specialist_warning:
            warnings.append(specialist_warning)
        worker_entry = self.config.worker_registry.get(worker)
        if worker_entry and worker_entry.get("owning_team") != team:
            warnings.append(
                f"Selected worker {worker} is registered to {worker_entry.get('owning_team')}, not {team}; "
                "the canonical route was preserved and the mismatch was exposed."
            )

        explanation = [classification_reason, risk_reason]
        explanation.append(f"Team route {task_type} selected {team}/{worker}.")
        if specialist:
            explanation.append(
                f"Specialist {specialist[0]} matched team {team} and worker binding {worker}."
            )
        explanation.append(
            f"Runtime binding selected {primary.model} for execution after authority, "
            "eligibility, calibration, and fitness evaluation."
        )
        if fallback:
            explanation.append(
                f"Runtime binding selected {fallback.model} as the constrained fallback."
            )
        explanation.append(
            f"Independent verification assigned to {verification.implementation.model} with "
            f"{', '.join(verification.method)}."
        )

        specialist_entry = specialist[1] if specialist else None
        return DispatchRecord(
            task_id=task.task_id,
            dispatch_id=f"dispatch-{uuid4().hex[:12]}",
            created_at=evaluated_at,
            task=task.task,
            task_type=task_type,
            risk_level=risk,
            selected_team=team,
            selected_worker=worker,
            selected_specialist=specialist_name,
            specialist_source=str(specialist_entry.get("role_card")) if specialist_entry else None,
            specialist_risk_profile=str(specialist_entry.get("risk_profile")) if specialist_entry else None,
            required_capabilities=capabilities,
            selected_implementation=primary,
            fallback_implementation=fallback,
            verification=verification,
            routing_explanation=explanation,
            warnings=warnings,
        )

    def finalize(
        self,
        dispatch: DispatchRecord,
        execution: ExecutionResult,
        verification: VerificationResult,
        *,
        artifact_root: str | Path | None = None,
    ) -> FinalOutcome:
        try:
            return self._finalization.finalize(
                dispatch,
                execution,
                verification,
                artifact_root=artifact_root,
            )
        except FinalizationError as exc:
            raise RoutingError(str(exc)) from exc

    def _classify_task(self, task: TaskRequest) -> tuple[str, str]:
        try:
            return classify_task(task, supported_task_types=self.config.team_routes)
        except RoutingPolicyError as exc:
            raise RoutingError(str(exc)) from None

    def _assess_risk(self, task: TaskRequest) -> tuple[str, str]:
        return assess_risk(task, risk_order=RISK_ORDER)

    def _refine_effective_risk(
        self,
        task: TaskRequest,
        specialist: str | None,
        risk: str,
    ) -> tuple[str, str | None]:
        return risk, None

    def _resolve_worker(self, route: dict[str, Any], task: TaskRequest) -> str:
        worker = str(route["primary_worker"])
        overrides = route.get("worker_override_by_context", {})
        contexts = _unique([task.domain or "", *task.constraints.contexts])
        for context in contexts:
            if context in overrides:
                worker = str(overrides[context])
                break
        if worker not in self.config.worker_registry:
            raise RoutingError(f"Selected worker is not defined in the core registry: {worker}")
        return worker

    def _resolve_specialist(
        self, task: TaskRequest, team: str, worker: str
    ) -> tuple[tuple[str, dict[str, Any]] | None, str | None]:
        registry = self.config.specialist_registry
        if task.specialist:
            entry = registry.get(task.specialist)
            if not entry:
                raise RoutingError(f"Requested specialist is not registered: {task.specialist}")
            if entry.get("primary_team") != team or entry.get("worker_binding") != worker:
                raise RoutingError(
                    f"Requested specialist {task.specialist} does not match selected route {team}/{worker}"
                )
            return (task.specialist, entry), None

        normalized = re.sub(r"[^a-z0-9]+", "-", task.task.lower()).strip("-")
        candidates: list[tuple[str, dict[str, Any]]] = []
        for name, entry in registry.items():
            if entry.get("primary_team") != team or entry.get("worker_binding") != worker:
                continue
            tokens = [
                token
                for token in name.split("-")
                if token not in {"engineer", "specialist", "analyst"}
            ]
            if name in normalized or (tokens and all(token in normalized for token in tokens)):
                candidates.append((name, entry))
        if len(candidates) == 1:
            return candidates[0], None
        if len(candidates) > 1:
            return None, "Multiple specialists matched; no specialist was selected without an explicit hint."
        return None, None

    def _resolve_capabilities(self, task: TaskRequest, worker: str) -> list[str]:
        worker_entry = self.config.worker_registry[worker]
        worker_team = str(worker_entry.get("owning_team") or "")
        registry = self.config.capability_registry
        for capability in task.constraints.required_capabilities:
            entry = registry.get(capability)
            if not entry:
                raise RoutingError(f"Required capability is not registered: {capability}")
            typical_teams = set(str(item) for item in entry.get("typical_teams", []))
            if typical_teams and "all" not in typical_teams and worker_team not in typical_teams:
                raise RoutingError(
                    f"Selected worker {worker} cannot satisfy required capability {capability} for team {worker_team}"
                )
        return _unique(
            [
                *worker_entry.get("required_capabilities", []),
                *task.constraints.required_capabilities,
            ]
        )

    def _worker_allows_model(self, worker: str, choice: ImplementationChoice) -> bool:
        worker_entry = self.config.worker_registry[worker]
        allowed = set(str(item) for item in worker_entry.get("preferred_implementations", []))
        allowed.update(str(item) for item in worker_entry.get("fallbacks", []))
        return choice.model in allowed

    def _primary_policy_warning(
        self,
        task_type: str,
        worker: str,
        task: TaskRequest,
        selected: ImplementationChoice,
    ) -> str | None:
        route = self.config.implementation_routes.get(task_type, {})
        for key in ROUTE_IMPLEMENTATION_KEYS.get(task_type, ("primary",)):
            candidate = route.get(key)
            if not isinstance(candidate, dict) or not candidate.get("model"):
                continue
            choice = self._choice(candidate, f"routing.{task_type}.{key}")
            if choice.model == selected.model:
                return None
            preview_was_only_policy_block = (
                choice.availability == "preview"
                and choice.model not in task.constraints.accepted_preview_models
                and choice.model not in task.constraints.blocked_implementations
                and (
                    not choice.provider_family
                    or choice.provider_family not in task.constraints.blocked_providers
                )
                and self._worker_allows_model(worker, choice)
            )
            if preview_was_only_policy_block:
                return (
                    f"Declared primary {choice.model} was skipped because preview implementations "
                    "require explicit acceptance via constraints.accepted_preview_models."
                )
            return None
        return None

    @staticmethod
    def _candidate(candidate: dict[str, Any], source: str) -> dict[str, Any]:
        return {
            "agent": candidate.get("agent", "registry"),
            "model": candidate.get("model"),
            "profile": candidate.get("profile"),
            "reasoning": candidate.get("reasoning"),
            "source": source,
        }

    def _base_selection_preferences(
        self,
        *,
        task_type: str,
        worker: str,
        role: str,
        capabilities: list[str],
    ) -> list[dict[str, Any]]:
        route = self.config.implementation_routes.get(task_type, {})
        preferences: list[dict[str, Any]] = []
        deferred: list[dict[str, Any]] = []

        def add(candidate: Any, source: str, *, defer_if_worker_disallowed: bool = False) -> None:
            if not isinstance(candidate, dict) or not candidate.get("model"):
                return
            preference = self._candidate(candidate, source)
            if defer_if_worker_disallowed:
                choice = self._choice(preference, source)
                if not self._worker_allows_model(worker, choice):
                    deferred.append(preference)
                    return
            preferences.append(preference)

        if role == "primary":
            for key in ROUTE_IMPLEMENTATION_KEYS.get(task_type, ("primary",)):
                add(route.get(key), f"routing.{task_type}.{key}", defer_if_worker_disallowed=True)
            for key in ("fallback", "local_fallback", "conditional_escalation"):
                add(route.get(key), f"routing.{task_type}.{key}", defer_if_worker_disallowed=True)
            worker_entry = self.config.worker_registry[worker]
            for source_key in ("preferred_implementations", "fallbacks"):
                for model in worker_entry.get(source_key, []):
                    add({"agent": "registry", "model": model}, f"workers.{worker}.{source_key}")
        elif role == "fallback":
            for key in ("fallback", "local_fallback", "conditional_escalation"):
                add(route.get(key), f"routing.{task_type}.{key}", defer_if_worker_disallowed=True)
            for model in self.config.worker_registry[worker].get("fallbacks", []):
                add({"agent": "registry", "model": model}, f"workers.{worker}.fallbacks")
            family = self._fallback_family(capabilities)
            for candidate in self.config.routing.get("fallback_order", {}).get(family, []):
                add(candidate, f"fallback_order.{family}", defer_if_worker_disallowed=True)
        elif role == "verifier":
            for key in VERIFIER_KEYS:
                add(route.get(key), f"routing.{task_type}.{key}")
            for key in ("fallback", "local_fallback", "conditional_escalation"):
                add(route.get(key), f"routing.{task_type}.{key}", defer_if_worker_disallowed=True)
            for model in self.config.worker_registry[worker].get("fallbacks", []):
                add({"agent": "registry", "model": model}, f"workers.{worker}.fallbacks")
            for candidate in self.config.routing.get("fallback_order", {}).get("general_reasoning", []):
                add(candidate, "fallback_order.general_reasoning", defer_if_worker_disallowed=True)
        else:
            raise RoutingError(f"Unsupported runtime selection role: {role}")

        preferences.extend(deferred)
        return self._dedupe_preferences(preferences)

    @staticmethod
    def _dedupe_preferences(preferences: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[str] = set()
        result: list[dict[str, Any]] = []
        for item in preferences:
            model = str(item.get("model") or "")
            if not model or model in seen:
                continue
            seen.add(model)
            result.append(dict(item))
        return result

    def _selection_preferences(
        self,
        *,
        task: TaskRequest,
        task_type: str,
        worker: str,
        role: str,
        risk: str,
        capabilities: list[str],
        specialist: str | None,
    ) -> list[dict[str, Any]]:
        return self._base_selection_preferences(
            task_type=task_type,
            worker=worker,
            role=role,
            capabilities=capabilities,
        )

    @staticmethod
    def _logical_reasoning_effort(encoded_effort: str | None) -> str | None:
        if encoded_effort is None:
            return None
        try:
            value = json.loads(encoded_effort)
        except (TypeError, json.JSONDecodeError) as exc:
            raise RoutingError("Selected runtime reasoning effort is not valid normalized JSON") from exc
        if not isinstance(value, str) or not value.strip():
            raise RoutingError("Selected runtime reasoning effort must decode to a non-empty string")
        return value

    def _select_runtime_choice(
        self,
        *,
        task: TaskRequest,
        task_type: str,
        worker: str,
        role: str,
        risk: str,
        capabilities: list[str],
        specialist: str | None,
        evaluated_at: str,
        exclude_models: set[str] | None = None,
        exclude_providers: set[str] | None = None,
    ) -> ImplementationChoice:
        preferences = self._selection_preferences(
            task=task,
            task_type=task_type,
            worker=worker,
            role=role,
            risk=risk,
            capabilities=capabilities,
            specialist=specialist,
        )
        if not preferences:
            raise RoutingError(
                f"No transitional runtime authority/preferences are defined for {task_type}/{worker}/{role}"
            )

        authorized_models = frozenset(str(item["model"]) for item in preferences)
        blocked_models = set(task.constraints.blocked_implementations)
        blocked_models.update(exclude_models or set())
        for model in authorized_models:
            entry = self._model_entry(model)
            if entry.get("availability") == "preview" and model not in task.constraints.accepted_preview_models:
                blocked_models.add(model)
        blocked_providers = set(task.constraints.blocked_providers)
        blocked_providers.update(exclude_providers or set())

        reasoning_by_model: list[tuple[str, str]] = []
        for item in preferences:
            reasoning = item.get("reasoning")
            if reasoning:
                reasoning_by_model.append((str(item["model"]), str(reasoning)))

        request = RuntimeSelectionRequest(
            scope=RuntimeSelectionScope(
                task_id=task.task_id,
                task_type=task_type,
                worker=worker,
                role=role,
            ),
            eligibility_requirements=EligibilityRequirements(required_capabilities=frozenset(capabilities)),
            calibration_requirements=self._runtime_calibration_requirements,
            evaluated_at=evaluated_at,
            authorized_models=authorized_models,
            excluded_models=frozenset(blocked_models),
            excluded_providers=frozenset(blocked_providers),
            preferred_models=tuple(str(item["model"]) for item in preferences),
            reasoning_effort_by_model=tuple(reasoning_by_model),
        )
        try:
            decision = self._runtime_selection_port().select(request)
        except RuntimeError as exc:
            raise RoutingError(str(exc)) from exc

        selected = decision.selected.implementation
        model = selected.configuration.model
        metadata = next(
            (item for item in preferences if str(item["model"]) == model),
            {"agent": "runtime", "model": model, "source": "runtime-selection"},
        )
        choice = self._choice(metadata, str(metadata.get("source") or "runtime-selection"))
        effort = self._logical_reasoning_effort(
            dict(selected.configuration.reasoning_controls).get("effort")
        )
        if effort:
            choice.reasoning = effort
        return choice

    def _select_fallback_runtime(
        self,
        *,
        task: TaskRequest,
        task_type: str,
        worker: str,
        risk: str,
        capabilities: list[str],
        specialist: str | None,
        primary: ImplementationChoice,
        evaluated_at: str,
    ) -> ImplementationChoice | None:
        try:
            return self._select_runtime_choice(
                task=task,
                task_type=task_type,
                worker=worker,
                role="fallback",
                risk=risk,
                capabilities=capabilities,
                specialist=specialist,
                evaluated_at=evaluated_at,
                exclude_models={primary.model},
                exclude_providers={primary.provider_family} if primary.provider_family else set(),
            )
        except RoutingError:
            return None

    def _verification_plan(
        self,
        task_type: str,
        risk: str,
        task: TaskRequest,
        primary: ImplementationChoice,
        worker: str,
        specialist_entry: dict[str, Any] | None,
        *,
        specialist_name: str | None = None,
        evaluated_at: str | None = None,
    ) -> VerificationPlan:
        policy = self.config.routing.get("verification_policy", {}).get(risk, {})
        methods = list(policy.get("minimum", ["output_validation"]))
        specialist_risk = (specialist_entry or {}).get("risk_profile")
        effective_risk = risk
        if specialist_risk in RISK_ORDER and RISK_ORDER[specialist_risk] > RISK_ORDER[risk]:
            effective_risk = str(specialist_risk)
            methods = list(
                self.config.routing.get("verification_policy", {})
                .get(effective_risk, {})
                .get("minimum", methods)
            )

        when = evaluated_at or utc_now()
        choice = self._select_runtime_choice(
            task=task,
            task_type=task_type,
            worker=worker,
            role="verifier",
            risk=effective_risk,
            capabilities=["high_reasoning"],
            specialist=specialist_name,
            evaluated_at=when,
            exclude_models={primary.model},
            exclude_providers={primary.provider_family} if primary.provider_family else set(),
        )
        if (
            choice.model == primary.model
            or not choice.provider_family
            or not primary.provider_family
            or choice.provider_family == primary.provider_family
        ):
            raise RoutingError("No provider-diverse independent verifier is available for the selected implementation")

        human = task.constraints.require_human_approval or effective_risk == "critical"
        return VerificationPlan(
            team=str(self.config.team_routes[task_type].get("verification_team", "verification")),
            method=_unique(methods),
            implementation=choice,
            independent=True,
            human_approval_required=human,
        )

    def _choice(self, candidate: dict[str, Any], source: str) -> ImplementationChoice:
        model = str(candidate["model"])
        registry_entry = self._model_entry(model)
        profile = candidate.get("profile") or registry_entry.get("profile")
        reasoning = candidate.get("reasoning")
        return ImplementationChoice(
            agent=str(candidate.get("agent", "registry")),
            model=model,
            profile=str(profile) if profile else None,
            provider_family=str(registry_entry.get("provider_family")) if registry_entry.get("provider_family") else None,
            availability=str(registry_entry.get("availability")) if registry_entry.get("availability") else None,
            source=source,
            reasoning=str(reasoning) if reasoning else None,
        )

    def _model_entry(self, model: str) -> dict[str, Any]:
        direct = self.config.model_registry.get(model)
        if direct:
            return direct
        for entry in self.config.model_registry.values():
            if entry.get("concrete_model") == model or model in entry.get("candidate_implementations", []):
                return entry
        return {}

    def _eligible(self, choice: ImplementationChoice, task: TaskRequest) -> bool:
        """Compatibility predicate retained for older outer adapters/tests.

        Production dispatch selection no longer calls this method directly.
        """
        if choice.model in task.constraints.blocked_implementations:
            return False
        if choice.provider_family and choice.provider_family in task.constraints.blocked_providers:
            return False
        if choice.availability == "preview" and choice.model not in task.constraints.accepted_preview_models:
            return False
        return True

    def _resolve_primary(self, task_type: str, worker: str, task: TaskRequest) -> ImplementationChoice:
        capabilities = self._resolve_capabilities(task, worker)
        return self._select_runtime_choice(
            task=task,
            task_type=task_type,
            worker=worker,
            role="primary",
            risk=task.risk_level,
            capabilities=capabilities,
            specialist=task.specialist,
            evaluated_at=utc_now(),
        )

    def _resolve_fallback(
        self,
        task_type: str,
        worker: str,
        capabilities: list[str],
        task: TaskRequest,
        exclude: set[str],
        exclude_providers: set[str] | None = None,
    ) -> ImplementationChoice | None:
        primary_model = next(iter(exclude), "")
        primary = self._choice({"agent": "runtime", "model": primary_model}, "compatibility-exclusion")
        if exclude_providers:
            primary.provider_family = next(iter(exclude_providers), primary.provider_family)
        return self._select_fallback_runtime(
            task=task,
            task_type=task_type,
            worker=worker,
            risk=task.risk_level,
            capabilities=capabilities,
            specialist=task.specialist,
            primary=primary,
            evaluated_at=utc_now(),
        )

    @staticmethod
    def _fallback_family(capabilities: list[str]) -> str:
        capability_set = set(capabilities)
        for triggers, family in CAPABILITY_FAMILY:
            if capability_set.intersection(triggers):
                return family
        return "general_reasoning"
