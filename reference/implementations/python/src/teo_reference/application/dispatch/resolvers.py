from __future__ import annotations

import re
from typing import Any, Iterable

from ...schemas import TaskRequest


class DispatchResolutionError(RuntimeError):
    """Raised when dispatch responsibility cannot be resolved from authorized configuration."""


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


class WorkerResolver:
    """Resolve the responsible Worker without selecting an implementation."""

    def __init__(self, config: Any):
        self._config = config

    def resolve(self, route: dict[str, Any], task: TaskRequest) -> str:
        worker = str(route["primary_worker"])
        overrides = route.get("worker_override_by_context", {})
        contexts = _unique([task.domain or "", *task.constraints.contexts])
        for context in contexts:
            if context in overrides:
                worker = str(overrides[context])
                break
        if worker not in self._config.worker_registry:
            raise DispatchResolutionError(
                f"Selected worker is not defined in the core registry: {worker}"
            )
        return worker


class SpecialistResolver:
    """Resolve an optional Specialist constrained by the selected Team/Worker route."""

    def __init__(self, config: Any):
        self._config = config

    def resolve(
        self,
        task: TaskRequest,
        team: str,
        worker: str,
    ) -> tuple[tuple[str, dict[str, Any]] | None, str | None]:
        registry = self._config.specialist_registry
        if task.specialist:
            entry = registry.get(task.specialist)
            if not entry:
                raise DispatchResolutionError(
                    f"Requested specialist is not registered: {task.specialist}"
                )
            if entry.get("primary_team") != team or entry.get("worker_binding") != worker:
                raise DispatchResolutionError(
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
            return (
                None,
                "Multiple specialists matched; no specialist was selected without an explicit hint.",
            )
        return None, None


class CapabilityResolver:
    """Resolve and validate capability requirements for the selected Worker."""

    def __init__(self, config: Any):
        self._config = config

    def resolve(self, task: TaskRequest, worker: str) -> list[str]:
        worker_entry = self._config.worker_registry[worker]
        worker_team = str(worker_entry.get("owning_team") or "")
        registry = self._config.capability_registry
        for capability in task.constraints.required_capabilities:
            entry = registry.get(capability)
            if not entry:
                raise DispatchResolutionError(
                    f"Required capability is not registered: {capability}"
                )
            typical_teams = set(str(item) for item in entry.get("typical_teams", []))
            if typical_teams and "all" not in typical_teams and worker_team not in typical_teams:
                raise DispatchResolutionError(
                    f"Selected worker {worker} cannot satisfy required capability {capability} "
                    f"for team {worker_team}"
                )
        return _unique(
            [
                *worker_entry.get("required_capabilities", []),
                *task.constraints.required_capabilities,
            ]
        )
