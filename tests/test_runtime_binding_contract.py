from __future__ import annotations

import ast
from pathlib import Path

import pytest

from teo_reference.domain.runtime_binding import (
    AuthorityScope,
    CalibrationRecord,
    CalibrationRequirements,
    CalibratedImplementation,
    DiscoveredImplementation,
    EligibilityEvidence,
    EligibilityRequirements,
    ExecutionConfigurationIdentity,
    RuntimeBindingError,
    RuntimeImplementation,
    apply_calibration,
    discover,
    evaluate_eligibility,
    select_best,
)
from teo_reference.ports.runtime_inventory import RuntimeInventoryPort

_EVALUATED_AT = "2026-08-21T12:00:00+00:00"


def _configuration(
    *,
    implementation_id: str = "impl-a",
    model: str = "model-a",
    runtime: str = "runtime-a",
    quantization: str | None = None,
    context_window: int | None = 32768,
) -> ExecutionConfigurationIdentity:
    return ExecutionConfigurationIdentity.from_runtime(
        implementation_id=implementation_id,
        model=model,
        runtime=runtime,
        provider_family="provider-a",
        version="2026-08-21",
        digest="sha256:abc",
        quantization=quantization,
        context_window=context_window,
        hardware="test-hardware",
        serving_stack="test-stack",
        tools=("tool-a",),
        reasoning_controls={"effort": "high"},
        material_settings={"temperature": 0},
    )


def _implementation(
    *,
    implementation_id: str = "impl-a",
    inventory_state: str = "running",
    capabilities: frozenset[str] = frozenset({"coding", "debugging"}),
) -> RuntimeImplementation:
    return RuntimeImplementation(
        configuration=_configuration(implementation_id=implementation_id),
        inventory_state=inventory_state,  # type: ignore[arg-type]
        capabilities=capabilities,
    )


def _eligible(implementation: RuntimeImplementation | None = None):
    implementation = implementation or _implementation()
    result = evaluate_eligibility(
        discover(implementation),
        authority=AuthorityScope(frozenset({implementation.implementation_id})),
        requirements=EligibilityRequirements(
            required_capabilities=frozenset({"coding"})
        ),
        evidence=EligibilityEvidence(
            reachable=True,
            healthy=True,
            privacy_allowed=True,
            runtime_constraints_satisfied=True,
        ),
    )
    assert result.eligible is not None
    return result.eligible


def _calibrated(
    implementation: RuntimeImplementation | None = None,
) -> CalibratedImplementation:
    eligible = _eligible(implementation)
    return apply_calibration(
        eligible,
        CalibrationRecord(
            configuration_fingerprint=(
                eligible.implementation.configuration.fingerprint
            ),
            status="passed",
            evidence_ref="benchmark://runtime-binding/test",
            calibrated_at="2026-08-21T11:00:00+00:00",
            valid_until="2026-08-22T11:00:00+00:00",
        ),
        requirements=CalibrationRequirements(
            required=True,
            max_age_seconds=86400,
        ),
        evaluated_at=_EVALUATED_AT,
    )


def test_discovery_records_presence_without_granting_eligibility() -> None:
    discovered = discover(_implementation())

    assert isinstance(discovered, DiscoveredImplementation)
    assert discovered.state == "discovered"
    assert discovered.implementation.inventory_state == "running"


def test_eligibility_cannot_widen_authority() -> None:
    decision = evaluate_eligibility(
        discover(_implementation()),
        authority=AuthorityScope(frozenset()),
        requirements=EligibilityRequirements(
            required_capabilities=frozenset({"coding"})
        ),
        evidence=EligibilityEvidence(
            reachable=True,
            healthy=True,
            privacy_allowed=True,
            runtime_constraints_satisfied=True,
        ),
    )

    assert decision.permitted is False
    assert decision.eligible is None
    assert "implementation is outside the authorized set" in decision.reasons


def test_missing_mandatory_eligibility_evidence_fails_closed() -> None:
    implementation = _implementation()
    decision = evaluate_eligibility(
        discover(implementation),
        authority=AuthorityScope(frozenset({implementation.implementation_id})),
        requirements=EligibilityRequirements(
            required_capabilities=frozenset({"coding"})
        ),
        evidence=EligibilityEvidence(
            reachable=True,
            healthy=None,
            privacy_allowed=True,
            runtime_constraints_satisfied=True,
        ),
    )

    assert decision.permitted is False
    assert "missing mandatory eligibility evidence: healthy" in decision.reasons


def test_unavailable_inventory_entry_cannot_become_eligible() -> None:
    implementation = _implementation(inventory_state="unavailable")
    decision = evaluate_eligibility(
        discover(implementation),
        authority=AuthorityScope(frozenset({implementation.implementation_id})),
        requirements=EligibilityRequirements(
            required_capabilities=frozenset({"coding"})
        ),
        evidence=EligibilityEvidence(
            reachable=True,
            healthy=True,
            privacy_allowed=True,
            runtime_constraints_satisfied=True,
        ),
    )

    assert decision.permitted is False
    assert "implementation is unavailable" in decision.reasons


def test_calibration_is_bound_to_exact_execution_configuration() -> None:
    eligible = _eligible()
    changed_configuration = _configuration(quantization="q4")

    assert (
        changed_configuration.fingerprint
        != eligible.implementation.configuration.fingerprint
    )

    with pytest.raises(
        RuntimeBindingError,
        match="calibration fingerprint does not match",
    ):
        apply_calibration(
            eligible,
            CalibrationRecord(
                configuration_fingerprint=changed_configuration.fingerprint,
                status="passed",
                evidence_ref="benchmark://wrong-configuration",
                calibrated_at="2026-08-21T11:00:00+00:00",
            ),
            requirements=CalibrationRequirements(required=True),
            evaluated_at=_EVALUATED_AT,
        )


def test_explicit_not_required_calibration_still_binds_configuration_identity() -> None:
    eligible = _eligible()

    calibrated = apply_calibration(
        eligible,
        CalibrationRecord(
            configuration_fingerprint=(
                eligible.implementation.configuration.fingerprint
            ),
            status="not_required",
            evidence_ref="policy://calibration/not-required",
        ),
        requirements=CalibrationRequirements(required=False),
        evaluated_at=_EVALUATED_AT,
    )

    assert calibrated.state == "calibrated"
    assert calibrated.calibration.status == "not_required"


def test_selection_requires_calibrated_candidates() -> None:
    eligible = _eligible()

    with pytest.raises(
        RuntimeBindingError,
        match="selection requires calibrated candidates",
    ):
        select_best(  # type: ignore[list-item]
            [eligible],
            fitness_scores={eligible.implementation.implementation_id: 1.0},
            selection_reason="test",
            evaluated_at=_EVALUATED_AT,
        )


def test_selection_chooses_best_fit_only_after_calibration() -> None:
    first = _calibrated(_implementation(implementation_id="impl-a"))
    second = _calibrated(_implementation(implementation_id="impl-b"))

    selected = select_best(
        [first, second],
        fitness_scores={"impl-a": 0.7, "impl-b": 0.9},
        selection_reason="highest policy-constrained fitness",
        evaluated_at=_EVALUATED_AT,
    )

    assert selected.state == "selected"
    assert selected.implementation.implementation_id == "impl-b"
    assert selected.fitness_score == 0.9
    assert selected.evaluated_at == _EVALUATED_AT


def test_execution_configuration_fingerprint_changes_with_material_runtime_settings() -> None:
    base = _configuration()
    quantized = _configuration(quantization="q4")
    reduced_context = _configuration(context_window=8192)

    assert len(base.fingerprint) == 64
    assert base.fingerprint != quantized.fingerprint
    assert base.fingerprint != reduced_context.fingerprint


def test_runtime_inventory_port_is_provider_independent() -> None:
    implementation = _implementation()

    class StaticInventory:
        def discover(self):
            return (implementation,)

    inventory: RuntimeInventoryPort = StaticInventory()
    assert inventory.discover() == (implementation,)


def test_runtime_binding_domain_has_no_outer_layer_imports() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "reference"
        / "implementations"
        / "python"
        / "src"
        / "teo_reference"
        / "domain"
        / "runtime_binding.py"
    )
    tree = ast.parse(path.read_text(encoding="utf-8"))
    allowed_roots = {
        "__future__",
        "dataclasses",
        "datetime",
        "hashlib",
        "json",
        "math",
        "typing",
    }

    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(
                alias.name.split(".", 1)[0] for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])

    assert imported_roots <= allowed_roots
