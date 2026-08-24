from __future__ import annotations

from collections.abc import Callable
from typing import Any
from uuid import uuid4

from ...schemas import DispatchRecord, RISK_ORDER, TaskRequest, utc_now
from .resolvers import CapabilityResolver, DispatchResolutionError, SpecialistResolver, WorkerResolver
from .selectors import ImplementationSelector


class DispatchServiceError(RuntimeError):
    """Raised when the dispatch application service cannot produce a valid dispatch."""


TaskClassifier = Callable[[TaskRequest], tuple[str, str]]
RiskAssessor = Callable[[TaskRequest], tuple[str, str]]
RiskRefiner = Callable[[TaskRequest, str | None, str], tuple[str, str | None]]


class DispatchService:
    """Application service coordinating responsibility resolution and implementation selection."""

    def __init__(
        self,
        config: Any,
        *,
        classify_task: TaskClassifier,
        assess_risk: RiskAssessor,
        refine_risk: RiskRefiner,
        worker_resolver: WorkerResolver,
        specialist_resolver: SpecialistResolver,
        capability_resolver: CapabilityResolver,
        implementation_selector: ImplementationSelector,
    ):
        self._config = config
        self._classify_task = classify_task
        self._assess_risk = assess_risk
        self._refine_risk = refine_risk
        self._worker_resolver = worker_resolver
        self._specialist_resolver = specialist_resolver
        self._capability_resolver = capability_resolver
        self._implementation_selector = implementation_selector

    def dispatch(self, task: TaskRequest) -> DispatchRecord:
        task_type, classification_reason = self._classify_task(task)
        risk, risk_reason = self._assess_risk(task)
        route = self._config.team_routes.get(task_type)
        if not route:
            raise DispatchServiceError(f"No team route for task type: {task_type}")

        try:
            team = str(route["primary_team"])
            worker = self._worker_resolver.resolve(route, task)
            specialist, specialist_warning = self._specialist_resolver.resolve(task, team, worker)
            if specialist:
                specialist_risk = str(specialist[1].get("risk_profile", risk))
                if (
                    specialist_risk in RISK_ORDER
                    and RISK_ORDER[specialist_risk] > RISK_ORDER[risk]
                ):
                    risk = specialist_risk
                    risk_reason += (
                        f" Specialist {specialist[0]} elevated the effective risk to {specialist_risk}."
                    )
            specialist_name = specialist[0] if specialist else None
            risk, refinement_reason = self._refine_risk(task, specialist_name, risk)
            if refinement_reason:
                risk_reason += " " + refinement_reason

            capabilities = self._capability_resolver.resolve(task, worker)
        except DispatchResolutionError as exc:
            raise DispatchServiceError(str(exc)) from exc

        evaluated_at = utc_now()
        primary = self._implementation_selector.select_primary(
            task=task,
            task_type=task_type,
            worker=worker,
            risk=risk,
            capabilities=capabilities,
            specialist=specialist_name,
            evaluated_at=evaluated_at,
        )
        primary_policy_warning = self._implementation_selector.primary_policy_warning(
            task_type,
            worker,
            task,
            primary,
        )
        fallback = self._implementation_selector.select_fallback(
            task=task,
            task_type=task_type,
            worker=worker,
            risk=risk,
            capabilities=capabilities,
            specialist=specialist_name,
            primary=primary,
            evaluated_at=evaluated_at,
        )
        verification = self._implementation_selector.verification_plan(
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
        worker_entry = self._config.worker_registry.get(worker)
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
            specialist_source=(
                str(specialist_entry.get("role_card")) if specialist_entry else None
            ),
            specialist_risk_profile=(
                str(specialist_entry.get("risk_profile")) if specialist_entry else None
            ),
            required_capabilities=capabilities,
            selected_implementation=primary,
            fallback_implementation=fallback,
            verification=verification,
            routing_explanation=explanation,
            warnings=warnings,
        )
