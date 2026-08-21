from __future__ import annotations

import ast
from pathlib import Path

import pytest

from teo_reference.adapters.runtime_inventory import (
    InstallationRuntimeInventoryAdapter,
    RuntimeInventoryAdapterError,
    RuntimeInventoryDeclaration,
)
from teo_reference.application.runtime_inventory import (
    RuntimeInventoryCompositionError,
    RuntimeInventoryService,
)
from teo_reference.domain.runtime_binding import ExecutionConfigurationIdentity


def _declaration(
    implementation_id: str,
    *,
    model: str | None = None,
    runtime: str = "test-runtime",
    capabilities: frozenset[str] = frozenset({"coding"}),
) -> RuntimeInventoryDeclaration:
    configuration = ExecutionConfigurationIdentity.from_runtime(
        implementation_id=implementation_id,
        model=model or f"model-{implementation_id}",
        runtime=runtime,
        provider_family="test-provider",
        version="1",
        digest=f"sha256:{implementation_id}",
        context_window=32768,
        hardware="test-hardware",
        serving_stack="test-stack",
        tools=("tool-a",),
        reasoning_controls={"effort": "medium"},
        material_settings={"temperature": 0},
    )
    return RuntimeInventoryDeclaration(
        configuration=configuration,
        capabilities=capabilities,
    )


def test_installation_adapter_normalizes_all_inventory_classes() -> None:
    adapter = InstallationRuntimeInventoryAdapter(
        running=(_declaration("running"),),
        available_local=(_declaration("local"),),
        configured_remote=(_declaration("remote"),),
        user_declared=(_declaration("declared"),),
        unavailable=(_declaration("missing"),),
    )

    discovered = {item.implementation_id: item for item in adapter.discover()}

    assert discovered["running"].inventory_state == "running"
    assert discovered["local"].inventory_state == "available_local"
    assert discovered["remote"].inventory_state == "available_remote"
    assert discovered["declared"].inventory_state == "user_declared"
    assert discovered["missing"].inventory_state == "unavailable"


def test_configured_remote_inventory_does_not_claim_reachability_or_eligibility() -> None:
    adapter = InstallationRuntimeInventoryAdapter(
        configured_remote=(_declaration("remote"),),
    )

    discovered = adapter.discover()

    assert len(discovered) == 1
    assert discovered[0].inventory_state == "available_remote"
    assert not hasattr(discovered[0], "reachable")
    assert not hasattr(discovered[0], "eligible")


def test_user_declared_inventory_remains_distinct_from_running_inventory() -> None:
    adapter = InstallationRuntimeInventoryAdapter(
        user_declared=(_declaration("declared"),),
    )

    discovered = adapter.discover()

    assert discovered[0].inventory_state == "user_declared"


def test_adapter_rejects_ambiguous_duplicate_ids_across_buckets() -> None:
    declaration = _declaration("same")

    with pytest.raises(
        RuntimeInventoryAdapterError,
        match="cannot appear more than once",
    ):
        InstallationRuntimeInventoryAdapter(
            running=(declaration,),
            available_local=(declaration,),
        )


def test_composition_collects_multiple_sources_deterministically() -> None:
    first = InstallationRuntimeInventoryAdapter(
        running=(_declaration("zeta"),),
    )
    second = InstallationRuntimeInventoryAdapter(
        available_local=(_declaration("alpha"),),
    )

    snapshot = RuntimeInventoryService((first, second)).discover_snapshot()

    assert [item.implementation_id for item in snapshot.implementations] == [
        "alpha",
        "zeta",
    ]
    assert snapshot.source_count == 2
    assert snapshot.exact_duplicate_count == 0


def test_composition_deduplicates_exact_observations_only() -> None:
    declaration = _declaration("shared")
    first = InstallationRuntimeInventoryAdapter(running=(declaration,))
    second = InstallationRuntimeInventoryAdapter(running=(declaration,))

    snapshot = RuntimeInventoryService((first, second)).discover_snapshot()

    assert len(snapshot.implementations) == 1
    assert snapshot.implementations[0].implementation_id == "shared"
    assert snapshot.exact_duplicate_count == 1


def test_composition_fails_closed_on_same_id_with_different_configuration() -> None:
    first = InstallationRuntimeInventoryAdapter(
        running=(_declaration("shared", model="model-a"),),
    )
    second = InstallationRuntimeInventoryAdapter(
        running=(_declaration("shared", model="model-b"),),
    )

    with pytest.raises(
        RuntimeInventoryCompositionError,
        match="conflicting runtime inventory observations",
    ):
        RuntimeInventoryService((first, second)).discover_snapshot()


def test_composition_fails_closed_on_same_id_with_different_state() -> None:
    declaration = _declaration("shared")
    first = InstallationRuntimeInventoryAdapter(running=(declaration,))
    second = InstallationRuntimeInventoryAdapter(available_local=(declaration,))

    with pytest.raises(
        RuntimeInventoryCompositionError,
        match="conflicting runtime inventory observations",
    ):
        RuntimeInventoryService((first, second)).discover_snapshot()


def test_composition_fails_closed_on_same_id_with_different_capabilities() -> None:
    first = InstallationRuntimeInventoryAdapter(
        running=(_declaration("shared", capabilities=frozenset({"coding"})),),
    )
    second = InstallationRuntimeInventoryAdapter(
        running=(
            _declaration(
                "shared",
                capabilities=frozenset({"coding", "visual_reasoning"}),
            ),
        ),
    )

    with pytest.raises(
        RuntimeInventoryCompositionError,
        match="conflicting runtime inventory observations",
    ):
        RuntimeInventoryService((first, second)).discover_snapshot()


def test_empty_installation_inventory_is_a_valid_snapshot() -> None:
    snapshot = RuntimeInventoryService(()).discover_snapshot()

    assert snapshot.implementations == ()
    assert snapshot.source_count == 0
    assert snapshot.exact_duplicate_count == 0


def test_composed_service_itself_conforms_to_inventory_discovery_shape() -> None:
    source = InstallationRuntimeInventoryAdapter(
        available_local=(_declaration("local"),),
    )
    service = RuntimeInventoryService((source,))

    discovered = service.discover()

    assert len(discovered) == 1
    assert discovered[0].implementation_id == "local"


def test_runtime_inventory_layers_do_not_import_routing_or_provider_execution() -> None:
    root = (
        Path(__file__).resolve().parents[1]
        / "reference"
        / "implementations"
        / "python"
        / "src"
        / "teo_reference"
    )
    paths = (
        root / "application" / "runtime_inventory.py",
        root / "adapters" / "runtime_inventory.py",
    )
    forbidden_roots = {
        "engine",
        "config",
        "provider_adapter",
        "provider_connection",
        "runtime_execution",
        "runtime_canary",
    }

    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported_modules: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module)

        assert not any(
            module.split(".")[-1] in forbidden_roots
            for module in imported_modules
        )
