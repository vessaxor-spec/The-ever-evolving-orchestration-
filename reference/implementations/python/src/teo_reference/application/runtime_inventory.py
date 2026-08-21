from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ..domain.runtime_binding import RuntimeImplementation
from ..ports.runtime_inventory import RuntimeInventoryPort


class RuntimeInventoryCompositionError(RuntimeError):
    """Raised when installation inventory sources cannot be reconciled safely."""


@dataclass(frozen=True, slots=True)
class RuntimeInventorySnapshot:
    """Deterministic provider-independent view of installation inventory.

    A snapshot records what inventory sources report. It carries no eligibility,
    calibration, selection, connection, or execution authority.
    """

    implementations: tuple[RuntimeImplementation, ...]
    source_count: int
    exact_duplicate_count: int = 0

    def __post_init__(self) -> None:
        if self.source_count < 0:
            raise RuntimeInventoryCompositionError("source_count cannot be negative")
        if self.exact_duplicate_count < 0:
            raise RuntimeInventoryCompositionError(
                "exact_duplicate_count cannot be negative"
            )
        implementation_ids = [item.implementation_id for item in self.implementations]
        if len(implementation_ids) != len(set(implementation_ids)):
            raise RuntimeInventoryCompositionError(
                "runtime inventory snapshot cannot contain duplicate implementation ids"
            )

    def get(self, implementation_id: str) -> RuntimeImplementation | None:
        for implementation in self.implementations:
            if implementation.implementation_id == implementation_id:
                return implementation
        return None


class RuntimeInventoryService:
    """Compose one or more runtime inventory sources without widening authority."""

    def __init__(self, sources: Sequence[RuntimeInventoryPort]):
        self._sources = tuple(sources)

    def discover_snapshot(self) -> RuntimeInventorySnapshot:
        by_id: dict[str, RuntimeImplementation] = {}
        exact_duplicate_count = 0

        for source_index, source in enumerate(self._sources):
            discovered = source.discover()
            for implementation in discovered:
                if not isinstance(implementation, RuntimeImplementation):
                    raise RuntimeInventoryCompositionError(
                        "runtime inventory source "
                        f"{source_index} returned a non-RuntimeImplementation value"
                    )
                implementation_id = implementation.implementation_id
                existing = by_id.get(implementation_id)
                if existing is None:
                    by_id[implementation_id] = implementation
                    continue
                if existing == implementation:
                    exact_duplicate_count += 1
                    continue
                raise RuntimeInventoryCompositionError(
                    "conflicting runtime inventory observations for implementation_id "
                    f"{implementation_id}; sources must not silently reconcile material "
                    "configuration, capability, or inventory-state differences"
                )

        implementations = tuple(by_id[key] for key in sorted(by_id))
        return RuntimeInventorySnapshot(
            implementations=implementations,
            source_count=len(self._sources),
            exact_duplicate_count=exact_duplicate_count,
        )

    def discover(self) -> Sequence[RuntimeImplementation]:
        """Implement RuntimeInventoryPort so composed inventory can be nested."""

        return self.discover_snapshot().implementations
