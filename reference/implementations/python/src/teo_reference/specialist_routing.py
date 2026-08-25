from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters.specialist_selection_policy import (
    SpecialistSelectionPolicyLoadError,
    YamlSpecialistSelectionPolicyAdapter,
)
from .application.dispatch.specialist_policy import (
    SpecialistRoutingPolicy,
    SpecialistRoutingPolicyError,
)
from .config import ConfigBundle
from .engine import OrchestrationEngine as BaseOrchestrationEngine, RoutingError
from .ports.configuration import SpecialistSelectionPolicyPort
from .schemas import DispatchRecord, ExecutionResult, FinalOutcome, TaskRequest, VerificationResult


class SpecialistRoutingError(RoutingError):
    pass


class SpecialistRoutingEngine:
    """Compatibility façade that composes specialist refinement into the base engine.

    The public class remains available, but specialist policy no longer subclasses or
    overrides base-engine internals. Unknown attributes are delegated to the composed
    engine to preserve the existing compatibility surface during the migration.
    """

    def __init__(
        self,
        config: ConfigBundle,
        *,
        specialist_selection_policy_source: SpecialistSelectionPolicyPort | None = None,
        **engine_kwargs: Any,
    ):
        self.config = config
        self._specialist_selection_policy_source = (
            specialist_selection_policy_source
            or YamlSpecialistSelectionPolicyAdapter(config.root)
        )
        try:
            self._specialist_selection_policy = (
                self._specialist_selection_policy_source.load()
            )
            self._specialist_policy = SpecialistRoutingPolicy(
                selection_policy=self._specialist_selection_policy,
                specialist_registry=config.specialist_registry,
                runtime_specialist_profiles=config.runtime_specialist_profiles,
                worker_runtime_defaults=config.worker_runtime_defaults,
                model_registry=config.model_registry,
            )
        except (SpecialistSelectionPolicyLoadError, SpecialistRoutingPolicyError) as exc:
            raise SpecialistRoutingError(str(exc)) from exc

        self._engine = BaseOrchestrationEngine(
            config,
            risk_refiner=self._specialist_policy.refine_effective_risk,
            selection_preference_refiner=self._specialist_policy.refine_selection_preferences,
            **engine_kwargs,
        )

    @classmethod
    def from_repo(
        cls,
        repo_root: str | Path,
        **kwargs: Any,
    ) -> "SpecialistRoutingEngine":
        return cls(ConfigBundle.load(repo_root), **kwargs)

    def dispatch(self, task: TaskRequest) -> DispatchRecord:
        try:
            return self._engine.dispatch(task)
        except SpecialistRoutingPolicyError as exc:
            raise SpecialistRoutingError(str(exc)) from exc

    def finalize(
        self,
        dispatch: DispatchRecord,
        execution: ExecutionResult,
        verification: VerificationResult,
        *,
        artifact_root: str | Path | None = None,
    ) -> FinalOutcome:
        return self._engine.finalize(
            dispatch,
            execution,
            verification,
            artifact_root=artifact_root,
        )

    def _load_specialist_selection_policy(self) -> dict[str, Any]:
        try:
            return self._specialist_selection_policy_source.load()
        except SpecialistSelectionPolicyLoadError as exc:
            raise SpecialistRoutingError(str(exc)) from exc

    def _validate_specialist_selection_policy(self) -> None:
        try:
            self._specialist_policy._validate()
        except SpecialistRoutingPolicyError as exc:
            raise SpecialistRoutingError(str(exc)) from exc

    def _provider_for_model(self, model: str) -> str | None:
        return self._specialist_policy.provider_for_model(model)

    def _selection_profile_for(self, specialist: str) -> tuple[str, dict[str, Any]]:
        try:
            return self._specialist_policy.selection_profile_for(specialist)
        except SpecialistRoutingPolicyError as exc:
            raise SpecialistRoutingError(str(exc)) from exc

    def _refine_effective_risk(
        self,
        task: TaskRequest,
        specialist: str | None,
        risk: str,
    ) -> tuple[str, str | None]:
        try:
            return self._specialist_policy.refine_effective_risk(task, specialist, risk)
        except SpecialistRoutingPolicyError as exc:
            raise SpecialistRoutingError(str(exc)) from exc

    def _selection_preferences(self, **kwargs: Any) -> list[dict[str, Any]]:
        try:
            return self._engine._selection_preferences(**kwargs)
        except SpecialistRoutingPolicyError as exc:
            raise SpecialistRoutingError(str(exc)) from exc

    def _documentation_recovery_verifier_preferences(
        self,
        worker: str,
    ) -> list[dict[str, Any]]:
        return self._specialist_policy._documentation_recovery_verifier_preferences(
            worker=worker
        )

    def __getattr__(self, name: str) -> Any:
        return getattr(self._engine, name)
