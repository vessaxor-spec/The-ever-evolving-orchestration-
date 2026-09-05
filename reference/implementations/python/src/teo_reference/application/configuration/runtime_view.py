from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator


_IMMUTABLE_MESSAGE = "runtime configuration view is immutable"


class FrozenDict(dict):
    """Dictionary-compatible immutable mapping for runtime configuration snapshots."""

    @staticmethod
    def _immutable(*args: Any, **kwargs: Any) -> None:
        del args, kwargs
        raise TypeError(_IMMUTABLE_MESSAGE)

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    setdefault = _immutable
    update = _immutable
    __ior__ = _immutable


class FrozenList(list):
    """List-compatible immutable sequence for runtime configuration snapshots."""

    @staticmethod
    def _immutable(*args: Any, **kwargs: Any) -> None:
        del args, kwargs
        raise TypeError(_IMMUTABLE_MESSAGE)

    __setitem__ = _immutable
    __delitem__ = _immutable
    append = _immutable
    clear = _immutable
    extend = _immutable
    insert = _immutable
    pop = _immutable
    remove = _immutable
    reverse = _immutable
    sort = _immutable
    __iadd__ = _immutable
    __imul__ = _immutable


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return FrozenDict({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return FrozenList(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


@dataclass(frozen=True, slots=True)
class RuntimeConfigurationView:
    """Deeply immutable runtime snapshot of the accepted repository configuration.

    The view deliberately preserves ``dict``/``list`` compatibility through immutable
    subclasses because existing dispatch policy performs concrete container checks.
    The mutable ``ConfigBundle`` remains the compatibility and validation surface;
    runtime execution consumes one detached snapshot per dispatch.
    """

    root: Path
    team_routing: FrozenDict
    routing: FrozenDict
    runtime_compatibility: FrozenDict
    workers: FrozenDict
    specialists: FrozenDict
    models: FrozenDict
    capabilities: FrozenDict
    model_evidence: FrozenDict
    capability_registry: FrozenDict

    @property
    def team_routes(self) -> FrozenDict:
        return self.team_routing["team_routes"]

    @property
    def implementation_routes(self) -> FrozenDict:
        return self.routing["routing"]

    @property
    def worker_registry(self) -> FrozenDict:
        return self.workers["workers"]

    @property
    def runtime_compatibility_defaults(self) -> FrozenDict:
        return self.runtime_compatibility

    @property
    def worker_runtime_defaults(self) -> FrozenDict:
        return self.runtime_compatibility["worker_defaults"]

    @property
    def runtime_task_routes(self) -> FrozenDict:
        return self.runtime_compatibility["task_routes"]

    @property
    def runtime_task_routing_defaults(self) -> FrozenDict:
        return self.runtime_compatibility["task_routing_defaults"]

    @property
    def runtime_fallback_order(self) -> FrozenDict:
        return self.runtime_compatibility["fallback_order"]

    @property
    def runtime_specialist_profiles(self) -> FrozenDict:
        return self.runtime_compatibility["specialist_profiles"]

    @property
    def specialist_registry(self) -> FrozenDict:
        return self.specialists["specialists"]

    @property
    def model_registry(self) -> FrozenDict:
        return self.models["models"]

    @property
    def model_evidence_registry(self) -> FrozenDict:
        return self.model_evidence["models"]


def build_runtime_configuration_view(source: Any) -> RuntimeConfigurationView:
    """Detach and deeply freeze the runtime-facing state of a configuration source."""

    return RuntimeConfigurationView(
        root=Path(source.root),
        team_routing=_freeze(source.team_routing),
        routing=_freeze(source.routing),
        runtime_compatibility=_freeze(source.runtime_compatibility),
        workers=_freeze(source.workers),
        specialists=_freeze(source.specialists),
        models=_freeze(source.models),
        capabilities=_freeze(source.capabilities),
        model_evidence=_freeze(source.model_evidence),
        capability_registry=_freeze(source.capability_registry),
    )


class RuntimeConfigurationBinding:
    """Context-local bridge from a mutable compatibility source to a runtime snapshot."""

    def __init__(
        self,
        source: Any,
        *,
        view_factory: Callable[[], Any] | None = None,
    ) -> None:
        self._source = source
        self._view_factory = view_factory or (lambda: source)
        self._active: ContextVar[Any | None] = ContextVar(
            f"teo_runtime_configuration_{id(self)}",
            default=None,
        )

    @property
    def current(self) -> Any:
        active = self._active.get()
        return active if active is not None else self._source

    @contextmanager
    def activate(self) -> Iterator[Any]:
        view = self._view_factory()
        token = self._active.set(view)
        try:
            yield view
        finally:
            self._active.reset(token)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.current, name)
