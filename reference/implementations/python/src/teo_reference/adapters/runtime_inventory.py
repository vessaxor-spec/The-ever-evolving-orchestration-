from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from ..domain.runtime_binding import (
    ExecutionConfigurationIdentity,
    RuntimeImplementation,
)


class RuntimeInventoryAdapterError(RuntimeError):
    """Raised when an installation inventory declaration is internally ambiguous."""


@dataclass(frozen=True, slots=True)
class RuntimeInventoryDeclaration:
    """Provider-neutral declaration of one concrete implementation candidate."""

    configuration: ExecutionConfigurationIdentity
    capabilities: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not self.capabilities:
            raise RuntimeInventoryAdapterError(
                "runtime inventory declaration requires at least one capability"
            )
        if any(not str(capability).strip() for capability in self.capabilities):
            raise RuntimeInventoryAdapterError(
                "runtime inventory declaration capabilities cannot contain empty values"
            )


@dataclass(frozen=True, slots=True)
class InstallationRuntimeInventoryAdapter:
    """Normalize installation-valid inventory surfaces into the RMI domain contract.

    The adapter does not probe networks, authenticate providers, evaluate health,
    infer privacy permission, calibrate models, or grant execution authority. Those
    concerns remain outside RMI-2. Callers supply observations from the installation
    surfaces they are authorized to inspect.
    """

    running: tuple[RuntimeInventoryDeclaration, ...] = ()
    available_local: tuple[RuntimeInventoryDeclaration, ...] = ()
    configured_remote: tuple[RuntimeInventoryDeclaration, ...] = ()
    user_declared: tuple[RuntimeInventoryDeclaration, ...] = ()
    unavailable: tuple[RuntimeInventoryDeclaration, ...] = ()

    def __post_init__(self) -> None:
        seen: dict[str, str] = {}
        for bucket_name, declarations in self._buckets():
            for declaration in declarations:
                if not isinstance(declaration, RuntimeInventoryDeclaration):
                    raise RuntimeInventoryAdapterError(
                        f"{bucket_name} contains a non-RuntimeInventoryDeclaration value"
                    )
                implementation_id = declaration.configuration.implementation_id
                prior = seen.get(implementation_id)
                if prior is not None:
                    raise RuntimeInventoryAdapterError(
                        "implementation_id cannot appear more than once in one installation "
                        f"inventory adapter: {implementation_id} ({prior}, {bucket_name})"
                    )
                seen[implementation_id] = bucket_name

    def _buckets(self) -> tuple[tuple[str, tuple[RuntimeInventoryDeclaration, ...]], ...]:
        return (
            ("running", self.running),
            ("available_local", self.available_local),
            ("configured_remote", self.configured_remote),
            ("user_declared", self.user_declared),
            ("unavailable", self.unavailable),
        )

    @staticmethod
    def _implementation(
        declaration: RuntimeInventoryDeclaration,
        inventory_state: str,
    ) -> RuntimeImplementation:
        return RuntimeImplementation(
            configuration=declaration.configuration,
            inventory_state=inventory_state,  # type: ignore[arg-type]
            capabilities=declaration.capabilities,
        )

    def discover(self) -> Sequence[RuntimeImplementation]:
        implementations: list[RuntimeImplementation] = []
        state_by_bucket = {
            "running": "running",
            "available_local": "available_local",
            "configured_remote": "available_remote",
            "user_declared": "user_declared",
            "unavailable": "unavailable",
        }
        for bucket_name, declarations in self._buckets():
            inventory_state = state_by_bucket[bucket_name]
            implementations.extend(
                self._implementation(declaration, inventory_state)
                for declaration in declarations
            )
        return tuple(implementations)
