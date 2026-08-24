from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ...schemas import ImplementationChoice, TaskRequest, VerificationPlan


PrimarySelector = Callable[..., ImplementationChoice]
FallbackSelector = Callable[..., ImplementationChoice | None]
VerificationPlanner = Callable[..., VerificationPlan]
PrimaryPolicyWarning = Callable[[str, str, TaskRequest, ImplementationChoice], str | None]


class ImplementationSelector:
    """Application-facing implementation-selection seam.

    Tranche 3 keeps runtime selection behavior behind bound engine callbacks so the
    existing SpecialistRoutingEngine polymorphic preference hooks remain intact.
    Tranche 4 may replace that temporary inheritance bridge without changing the
    DispatchService contract.
    """

    def __init__(
        self,
        *,
        select_runtime: PrimarySelector,
        select_fallback: FallbackSelector,
        plan_verification: VerificationPlanner,
        primary_policy_warning: PrimaryPolicyWarning,
    ):
        self._select_runtime = select_runtime
        self._select_fallback = select_fallback
        self._plan_verification = plan_verification
        self._primary_policy_warning = primary_policy_warning

    def select_primary(
        self,
        *,
        task: TaskRequest,
        task_type: str,
        worker: str,
        risk: str,
        capabilities: list[str],
        specialist: str | None,
        evaluated_at: str,
    ) -> ImplementationChoice:
        return self._select_runtime(
            task=task,
            task_type=task_type,
            worker=worker,
            role="primary",
            risk=risk,
            capabilities=capabilities,
            specialist=specialist,
            evaluated_at=evaluated_at,
        )

    def select_fallback(
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
        return self._select_fallback(
            task=task,
            task_type=task_type,
            worker=worker,
            risk=risk,
            capabilities=capabilities,
            specialist=specialist,
            primary=primary,
            evaluated_at=evaluated_at,
        )

    def primary_policy_warning(
        self,
        task_type: str,
        worker: str,
        task: TaskRequest,
        selected: ImplementationChoice,
    ) -> str | None:
        return self._primary_policy_warning(task_type, worker, task, selected)

    def verification_plan(
        self,
        task_type: str,
        risk: str,
        task: TaskRequest,
        primary: ImplementationChoice,
        worker: str,
        specialist_entry: dict[str, Any] | None,
        *,
        specialist_name: str | None,
        evaluated_at: str,
    ) -> VerificationPlan:
        return self._plan_verification(
            task_type,
            risk,
            task,
            primary,
            worker,
            specialist_entry,
            specialist_name=specialist_name,
            evaluated_at=evaluated_at,
        )
