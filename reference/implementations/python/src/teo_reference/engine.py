from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from .artifact_integrity import ArtifactIntegrityError, revalidate_verified_artifact
from .config import ConfigBundle
from .domain.routing import RISK_PATTERNS as RISK_PATTERNS
from .domain.routing import TASK_PATTERNS as TASK_PATTERNS
from .domain.routing import RoutingPolicyError, assess_risk, classify_task
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
    def __init__(self, config: ConfigBundle):
        self.config = config

    @classmethod
    def from_repo(cls, repo_root: str) -> "OrchestrationEngine":
        return cls(ConfigBundle.load(repo_root))

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
        capabilities = self._resolve_capabilities(task, worker)
        primary = self._resolve_primary(task_type, worker, task)
        primary_policy_warning = self._primary_policy_warning(task_type, worker, task, primary)
        fallback = self._resolve_fallback(task_type, worker, capabilities, task, exclude={primary.model})
        verification = self._verification_plan(
            task_type, risk, task, primary, worker, specialist[1] if specialist else None
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
            f"Implementation {primary.model} selected from the {task_type} implementation route."
        )
        explanation.append(
            f"Independent verification assigned to {verification.implementation.model} with "
            f"{', '.join(verification.method)}."
        )

        specialist_name = specialist[0] if specialist else None
        specialist_entry = specialist[1] if specialist else None
        return DispatchRecord(
            task_id=task.task_id,
            dispatch_id=f"dispatch-{uuid4().hex[:12]}",
            created_at=utc_now(),
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
        if execution.dispatch_id != dispatch.dispatch_id or verification.dispatch_id != dispatch.dispatch_id:
            raise RoutingError("Execution and verification records must reference the dispatch being finalized")
        if verification.verifier_model != dispatch.verification.implementation.model:
            raise RoutingError("Verification was not performed by the assigned verifier")
        if dispatch.verification.independent and verification.verifier_model == dispatch.selected_implementation.model:
            raise RoutingError("Independent verification cannot use the selected execution model")
        if (
            dispatch.verification.independent
            and dispatch.verification.implementation.provider_family
            and dispatch.selected_implementation.provider_family
            and dispatch.verification.implementation.provider_family
            == dispatch.selected_implementation.provider_family
        ):
            raise RoutingError("Independent verification cannot use the selected execution provider family")

        if verification.verified_artifact is not None and not execution.output_ref:
            raise RoutingError("Verification artifact binding has no execution output artifact")
        if execution.status == "succeeded" and verification.status == "passed" and execution.output_ref:
            if verification.verified_artifact is None:
                raise RoutingError(
                    "Artifact-backed passed verification requires exact verified artifact identity"
                )
            if artifact_root is None:
                raise RoutingError(
                    "Artifact-backed passed verification requires an authorized artifact_root"
                )
            try:
                revalidate_verified_artifact(
                    execution.output_ref,
                    verification.verified_artifact,
                    allowed_root=artifact_root,
                )
            except ArtifactIntegrityError as exc:
                raise RoutingError(str(exc)) from exc

        notes: list[str] = []
        escalation_used = False
        if execution.status == "failed":
            if dispatch.fallback_implementation:
                status = "escalated"
                notes.append("Execution failed; an eligible fallback is available but is not recorded as executed.")
            else:
                status = "failed"
                notes.append("Execution failed and no eligible fallback is available.")
        elif verification.status == "failed":
            status = "failed"
            notes.append("Independent verification failed; the outcome is not accepted.")
        elif verification.status == "needs_human" or dispatch.verification.human_approval_required:
            status = "awaiting_human"
            notes.append("The verification gate requires qualified human approval.")
        else:
            status = "completed"
            notes.append("Execution and independent verification passed.")

        return FinalOutcome(
            dispatch_id=dispatch.dispatch_id,
            task_id=dispatch.task_id,
            completed_at=utc_now(),
            status=status,  # type: ignore[arg-type]
            execution_status=execution.status,
            verification_status=verification.status,
            selected_model=dispatch.selected_implementation.model,
            verifier_model=verification.verifier_model,
            evidence=_unique([*execution.evidence, *verification.evidence]),
            failed_attempts=execution.failed_attempts,
            escalation_used=escalation_used,
            notes=notes,
        )

    def _classify_task(self, task: TaskRequest) -> tuple[str, str]:
        try:
            return classify_task(task, supported_task_types=self.config.team_routes)
        except RoutingPolicyError as exc:
            raise RoutingError(str(exc)) from None

    def _assess_risk(self, task: TaskRequest) -> tuple[str, str]:
        return assess_risk(task, risk_order=RISK_ORDER)

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
            tokens = [token for token in name.split("-") if token not in {"engineer", "specialist", "analyst"}]
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
            [*worker_entry.get("required_capabilities", []), *task.constraints.required_capabilities]
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

    def _resolve_primary(self, task_type: str, worker: str, task: TaskRequest) -> ImplementationChoice:
        route = self.config.implementation_routes.get(task_type, {})
        for key in ROUTE_IMPLEMENTATION_KEYS.get(task_type, ("primary",)):
            candidate = route.get(key)
            if isinstance(candidate, dict) and candidate.get("model"):
                choice = self._choice(candidate, f"routing.{task_type}.{key}")
                if self._eligible(choice, task) and self._worker_allows_model(worker, choice):
                    return choice

        for key in ("fallback", "local_fallback", "conditional_escalation"):
            candidate = route.get(key)
            if isinstance(candidate, dict) and candidate.get("model"):
                choice = self._choice(candidate, f"routing.{task_type}.{key}")
                if self._eligible(choice, task) and self._worker_allows_model(worker, choice):
                    return choice

        worker_entry = self.config.worker_registry[worker]
        for source_key in ("preferred_implementations", "fallbacks"):
            for model in worker_entry.get(source_key, []):
                choice = self._choice(
                    {"agent": "registry", "model": model}, f"workers.{worker}.{source_key}"
                )
                if self._eligible(choice, task):
                    return choice
        raise RoutingError(f"No eligible implementation found for {task_type}/{worker}")

    def _resolve_fallback(
        self,
        task_type: str,
        worker: str,
        capabilities: list[str],
        task: TaskRequest,
        exclude: set[str],
        exclude_providers: set[str] | None = None,
    ) -> ImplementationChoice | None:
        blocked_providers = exclude_providers or set()
        route = self.config.implementation_routes.get(task_type, {})
        for key in ("fallback", "local_fallback", "conditional_escalation"):
            candidate = route.get(key)
            if isinstance(candidate, dict) and candidate.get("model"):
                choice = self._choice(candidate, f"routing.{task_type}.{key}")
                if (
                    choice.model not in exclude
                    and choice.provider_family not in blocked_providers
                    and self._eligible(choice, task)
                    and self._worker_allows_model(worker, choice)
                ):
                    return choice

        for model in self.config.worker_registry[worker].get("fallbacks", []):
            choice = self._choice({"agent": "registry", "model": model}, f"workers.{worker}.fallbacks")
            if (
                choice.model not in exclude
                and choice.provider_family not in blocked_providers
                and self._eligible(choice, task)
            ):
                return choice

        family = self._fallback_family(capabilities)
        for candidate in self.config.routing.get("fallback_order", {}).get(family, []):
            choice = self._choice(candidate, f"fallback_order.{family}")
            if (
                choice.model not in exclude
                and choice.provider_family not in blocked_providers
                and self._eligible(choice, task)
                and self._worker_allows_model(worker, choice)
            ):
                return choice
        return None

    def _verification_plan(
        self,
        task_type: str,
        risk: str,
        task: TaskRequest,
        primary: ImplementationChoice,
        worker: str,
        specialist_entry: dict[str, Any] | None,
    ) -> VerificationPlan:
        policy = self.config.routing.get("verification_policy", {}).get(risk, {})
        methods = list(policy.get("minimum", ["output_validation"]))
        route = self.config.implementation_routes.get(task_type, {})
        choice: ImplementationChoice | None = None
        for key in VERIFIER_KEYS:
            candidate = route.get(key)
            if isinstance(candidate, dict) and candidate.get("model"):
                possible = self._choice(candidate, f"routing.{task_type}.{key}")
                if (
                    possible.model != primary.model
                    and possible.provider_family
                    and primary.provider_family
                    and possible.provider_family != primary.provider_family
                    and self._eligible(possible, task)
                ):
                    choice = possible
                    break
        if choice is None:
            capabilities = ["high_reasoning"]
            excluded_providers = {primary.provider_family} if primary.provider_family else set()
            choice = self._resolve_fallback(
                task_type,
                worker,
                capabilities,
                task,
                {primary.model},
                excluded_providers,
            )
        if (
            choice is None
            or choice.model == primary.model
            or not choice.provider_family
            or not primary.provider_family
            or choice.provider_family == primary.provider_family
        ):
            raise RoutingError("No provider-diverse independent verifier is available for the selected implementation")

        specialist_risk = (specialist_entry or {}).get("risk_profile")
        effective_risk = risk
        if specialist_risk in RISK_ORDER and RISK_ORDER[specialist_risk] > RISK_ORDER[risk]:
            effective_risk = specialist_risk
            methods = list(
                self.config.routing.get("verification_policy", {}).get(effective_risk, {}).get("minimum", methods)
            )
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
        return ImplementationChoice(
            agent=str(candidate.get("agent", "registry")),
            model=model,
            profile=str(profile) if profile else None,
            provider_family=str(registry_entry.get("provider_family")) if registry_entry.get("provider_family") else None,
            availability=str(registry_entry.get("availability")) if registry_entry.get("availability") else None,
            source=source,
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
        if choice.model in task.constraints.blocked_implementations:
            return False
        if choice.provider_family and choice.provider_family in task.constraints.blocked_providers:
            return False
        if choice.availability == "preview" and choice.model not in task.constraints.accepted_preview_models:
            return False
        return True

    @staticmethod
    def _fallback_family(capabilities: list[str]) -> str:
        capability_set = set(capabilities)
        for triggers, family in CAPABILITY_FAMILY:
            if capability_set.intersection(triggers):
                return family
        return "general_reasoning"
