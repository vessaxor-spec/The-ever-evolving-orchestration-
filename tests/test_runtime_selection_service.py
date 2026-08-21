from __future__ import annotations

import ast
from pathlib import Path

import pytest

from teo_reference.adapters.runtime_calibration import DeclaredRuntimeCalibrationAdapter
from teo_reference.adapters.runtime_eligibility import (
    DeclaredRuntimeEligibilityEvidenceAdapter,
)
from teo_reference.adapters.runtime_selection import (
    DeclaredRuntimeFitnessAdapter,
    PreferenceRuntimeFitnessAdapter,
    RuntimeFitnessAdapterError,
)
from teo_reference.application.runtime_selection import RuntimeSelectionService
from teo_reference.domain.runtime_binding import (
    CalibrationRecord,
    CalibrationRequirements,
    EligibilityEvidence,
    EligibilityRequirements,
    ExecutionConfigurationIdentity,
    RuntimeImplementation,
)
from teo_reference.domain.runtime_selection import (
    RuntimeSelectionError,
    RuntimeSelectionPin,
    RuntimeSelectionRequest,
    RuntimeSelectionScope,
)

EVALUATED_AT = "2026-08-21T20:00:00+00:00"
CALIBRATED_AT = "2026-08-21T18:00:00+00:00"
VALID_UNTIL = "2026-08-21T22:00:00+00:00"


class StaticInventory:
    def __init__(self, *implementations: RuntimeImplementation) -> None:
        self.implementations = tuple(implementations)
        self.calls = 0

    def discover(self):
        self.calls += 1
        return self.implementations


def _implementation(
    implementation_id: str,
    *,
    model: str | None = None,
    provider: str = "provider-a",
    inventory_state: str = "running",
    capabilities: frozenset[str] = frozenset({"coding", "debugging"}),
    quantization: str | None = None,
) -> RuntimeImplementation:
    return RuntimeImplementation(
        configuration=ExecutionConfigurationIdentity.from_runtime(
            implementation_id=implementation_id,
            model=model or implementation_id,
            runtime=f"runtime-{implementation_id}",
            provider_family=provider,
            version="2026-08-21",
            digest=f"sha256:{implementation_id}",
            quantization=quantization,
            context_window=32768,
            hardware="test-hardware",
            serving_stack="test-stack",
            tools=("tool-a",),
            reasoning_controls={"effort": "high"},
            material_settings={"temperature": 0},
        ),
        inventory_state=inventory_state,  # type: ignore[arg-type]
        capabilities=capabilities,
    )


def _evidence(*implementations: RuntimeImplementation):
    return DeclaredRuntimeEligibilityEvidenceAdapter(
        {
            item.implementation_id: EligibilityEvidence(
                reachable=True,
                healthy=True,
                privacy_allowed=True,
                runtime_constraints_satisfied=True,
            )
            for item in implementations
        }
    )


def _calibrations(*implementations: RuntimeImplementation):
    return DeclaredRuntimeCalibrationAdapter(
        tuple(
            CalibrationRecord(
                configuration_fingerprint=item.configuration.fingerprint,
                status="passed",
                evidence_ref=f"benchmark://{item.implementation_id}",
                calibrated_at=CALIBRATED_AT,
                valid_until=VALID_UNTIL,
            )
            for item in implementations
        )
    )


def _request(
    *,
    authorized_ids: frozenset[str] = frozenset(),
    authorized_models: frozenset[str] = frozenset(),
    excluded_ids: frozenset[str] = frozenset(),
    excluded_models: frozenset[str] = frozenset(),
    excluded_providers: frozenset[str] = frozenset(),
    preferred_models: tuple[str, ...] = (),
    evaluated_at: str = EVALUATED_AT,
    removal_conditions: frozenset[str] = frozenset(),
) -> RuntimeSelectionRequest:
    return RuntimeSelectionRequest(
        scope=RuntimeSelectionScope(
            task_id="task-a",
            task_type="daily_coding",
            worker="backend",
            role="primary",
        ),
        eligibility_requirements=EligibilityRequirements(
            required_capabilities=frozenset({"coding"})
        ),
        calibration_requirements=CalibrationRequirements(
            required=True,
            max_age_seconds=10800,
            require_valid_until=True,
        ),
        evaluated_at=evaluated_at,
        authorized_implementation_ids=authorized_ids,
        authorized_models=authorized_models,
        excluded_implementation_ids=excluded_ids,
        excluded_models=excluded_models,
        excluded_providers=excluded_providers,
        preferred_models=preferred_models,
        satisfied_pin_removal_conditions=removal_conditions,
    )


def _service(
    inventory: StaticInventory,
    *,
    scores: dict[str, float],
    calibrations=None,
    evidence=None,
    pins: tuple[RuntimeSelectionPin, ...] = (),
) -> RuntimeSelectionService:
    implementations = inventory.implementations
    return RuntimeSelectionService(
        inventory=inventory,
        eligibility_evidence=evidence or _evidence(*implementations),
        calibration_records=calibrations or _calibrations(*implementations),
        fitness=DeclaredRuntimeFitnessAdapter(scores),
        pins=pins,
    )


def test_best_fit_selects_highest_score_only_after_lifecycle_gates() -> None:
    first = _implementation("impl-a")
    second = _implementation("impl-b")
    service = _service(
        StaticInventory(first, second),
        scores={"impl-a": 0.4, "impl-b": 0.9},
    )

    decision = service.select(
        _request(authorized_ids=frozenset({"impl-a", "impl-b"}))
    )

    assert decision.selected.implementation.implementation_id == "impl-b"
    assert decision.eligible_candidate_count == 2
    assert decision.calibrated_candidate_count == 2
    assert decision.pin_id is None


def test_unauthorized_high_score_cannot_enter_selection() -> None:
    allowed = _implementation("allowed")
    unauthorized = _implementation("unauthorized")
    service = _service(
        StaticInventory(allowed, unauthorized),
        scores={"allowed": 0.1, "unauthorized": 999.0},
    )

    decision = service.select(_request(authorized_ids=frozenset({"allowed"})))

    assert decision.selected.implementation.implementation_id == "allowed"
    assert decision.eligible_candidate_count == 1


def test_model_and_implementation_authority_intersect_instead_of_union() -> None:
    first = _implementation("impl-a", model="model-a")
    second = _implementation("impl-b", model="model-b")
    service = _service(
        StaticInventory(first, second),
        scores={"impl-a": 0.1, "impl-b": 1.0},
    )

    decision = service.select(
        _request(
            authorized_ids=frozenset({"impl-a", "impl-b"}),
            authorized_models=frozenset({"model-a"}),
        )
    )

    assert decision.selected.implementation.implementation_id == "impl-a"
    assert decision.eligible_candidate_count == 1


def test_explicit_exclusions_are_deny_wins() -> None:
    first = _implementation("impl-a", model="model-a", provider="provider-a")
    second = _implementation("impl-b", model="model-b", provider="provider-b")
    service = _service(
        StaticInventory(first, second),
        scores={"impl-a": 10.0, "impl-b": 1.0},
    )

    decision = service.select(
        _request(
            authorized_ids=frozenset({"impl-a", "impl-b"}),
            excluded_providers=frozenset({"provider-a"}),
        )
    )

    assert decision.selected.implementation.implementation_id == "impl-b"


def test_missing_mandatory_eligibility_evidence_fails_closed_before_fitness() -> None:
    candidate = _implementation("impl-a")
    service = _service(
        StaticInventory(candidate),
        scores={"impl-a": 1.0},
        evidence=DeclaredRuntimeEligibilityEvidenceAdapter({}),
    )

    with pytest.raises(
        RuntimeSelectionError,
        match="missing mandatory eligibility evidence",
    ):
        service.select(_request(authorized_ids=frozenset({"impl-a"})))


def test_stale_calibration_fails_closed_before_fitness() -> None:
    candidate = _implementation("impl-a")
    stale = DeclaredRuntimeCalibrationAdapter(
        (
            CalibrationRecord(
                configuration_fingerprint=candidate.configuration.fingerprint,
                status="passed",
                evidence_ref="benchmark://stale",
                calibrated_at="2026-08-21T12:00:00+00:00",
                valid_until="2026-08-21T19:00:00+00:00",
            ),
        )
    )
    service = _service(
        StaticInventory(candidate),
        scores={"impl-a": 1.0},
        calibrations=stale,
    )

    with pytest.raises(RuntimeSelectionError, match="stale"):
        service.select(_request(authorized_ids=frozenset({"impl-a"})))


def test_pin_overrides_fitness_only_for_lifecycle_valid_target() -> None:
    first = _implementation("impl-a")
    second = _implementation("impl-b")
    pin = RuntimeSelectionPin(
        pin_id="pin-1",
        implementation_id="impl-a",
        role="primary",
        reason="controlled incident mitigation",
        task_type="daily_coding",
        expires_at="2026-08-21T21:00:00+00:00",
    )
    service = _service(
        StaticInventory(first, second),
        scores={"impl-a": 0.1, "impl-b": 99.0},
        pins=(pin,),
    )

    decision = service.select(
        _request(authorized_ids=frozenset({"impl-a", "impl-b"}))
    )

    assert decision.selected.implementation.implementation_id == "impl-a"
    assert decision.pin_id == "pin-1"


def test_pin_cannot_widen_authority() -> None:
    allowed = _implementation("allowed")
    pinned = _implementation("pinned")
    pin = RuntimeSelectionPin(
        pin_id="pin-unauthorized",
        implementation_id="pinned",
        role="primary",
        reason="must not widen authority",
        task_id="task-a",
        removal_conditions=frozenset({"owner-clears-pin"}),
    )
    service = _service(
        StaticInventory(allowed, pinned),
        scores={"allowed": 1.0, "pinned": 2.0},
        pins=(pin,),
    )

    with pytest.raises(RuntimeSelectionError, match="target is not currently authorized"):
        service.select(_request(authorized_ids=frozenset({"allowed"})))


def test_expired_pin_is_ignored_and_best_fit_resumes() -> None:
    first = _implementation("impl-a")
    second = _implementation("impl-b")
    pin = RuntimeSelectionPin(
        pin_id="expired-pin",
        implementation_id="impl-a",
        role="primary",
        reason="temporary incident pin",
        task_type="daily_coding",
        expires_at="2026-08-21T19:59:59+00:00",
    )
    service = _service(
        StaticInventory(first, second),
        scores={"impl-a": 0.1, "impl-b": 0.9},
        pins=(pin,),
    )

    decision = service.select(
        _request(authorized_ids=frozenset({"impl-a", "impl-b"}))
    )

    assert decision.selected.implementation.implementation_id == "impl-b"
    assert decision.pin_id is None


def test_satisfied_removal_condition_disables_pin() -> None:
    first = _implementation("impl-a")
    second = _implementation("impl-b")
    pin = RuntimeSelectionPin(
        pin_id="condition-pin",
        implementation_id="impl-a",
        role="primary",
        reason="until provider incident clears",
        worker="backend",
        removal_conditions=frozenset({"provider-incident-cleared"}),
    )
    service = _service(
        StaticInventory(first, second),
        scores={"impl-a": 0.1, "impl-b": 0.9},
        pins=(pin,),
    )

    decision = service.select(
        _request(
            authorized_ids=frozenset({"impl-a", "impl-b"}),
            removal_conditions=frozenset({"provider-incident-cleared"}),
        )
    )

    assert decision.selected.implementation.implementation_id == "impl-b"
    assert decision.pin_id is None


def test_multiple_matching_active_pins_fail_closed() -> None:
    candidate = _implementation("impl-a")
    pins = tuple(
        RuntimeSelectionPin(
            pin_id=f"pin-{index}",
            implementation_id="impl-a",
            role="primary",
            reason="ambiguous by construction",
            task_type="daily_coding",
            removal_conditions=frozenset({f"remove-{index}"}),
        )
        for index in (1, 2)
    )
    service = _service(
        StaticInventory(candidate),
        scores={"impl-a": 1.0},
        pins=pins,
    )

    with pytest.raises(RuntimeSelectionError, match="multiple runtime pins"):
        service.select(_request(authorized_ids=frozenset({"impl-a"})))


def test_pin_requires_scope_and_removal_mechanism() -> None:
    with pytest.raises(RuntimeSelectionError, match="must be scoped"):
        RuntimeSelectionPin(
            pin_id="pin-a",
            implementation_id="impl-a",
            role="primary",
            reason="invalid global permanent pin",
            expires_at="2026-08-21T21:00:00+00:00",
        )

    with pytest.raises(RuntimeSelectionError, match="expires_at or at least one removal"):
        RuntimeSelectionPin(
            pin_id="pin-b",
            implementation_id="impl-a",
            role="primary",
            reason="invalid permanent pin",
            task_type="daily_coding",
        )


def test_missing_fitness_evidence_fails_closed() -> None:
    candidate = _implementation("impl-a")
    service = RuntimeSelectionService(
        inventory=StaticInventory(candidate),
        eligibility_evidence=_evidence(candidate),
        calibration_records=_calibrations(candidate),
        fitness=DeclaredRuntimeFitnessAdapter({}),
    )

    with pytest.raises(RuntimeFitnessAdapterError, match="missing runtime fitness evidence"):
        service.select(_request(authorized_ids=frozenset({"impl-a"})))


def test_nonfinite_fitness_is_rejected_at_adapter_boundary() -> None:
    with pytest.raises(RuntimeFitnessAdapterError, match="must be finite"):
        DeclaredRuntimeFitnessAdapter({"impl-a": float("inf")})


def test_local_and_remote_candidates_are_policy_peers_for_best_fit() -> None:
    local = _implementation("local", inventory_state="available_local")
    remote = _implementation("remote", inventory_state="available_remote")
    service = _service(
        StaticInventory(local, remote),
        scores={"local": 0.5, "remote": 0.8},
    )

    decision = service.select(
        _request(authorized_ids=frozenset({"local", "remote"}))
    )

    assert decision.selected.implementation.implementation_id == "remote"


def test_inventory_is_snapshotted_once_per_selection() -> None:
    candidate = _implementation("impl-a")
    inventory = StaticInventory(candidate)
    service = _service(inventory, scores={"impl-a": 1.0})

    service.select(_request(authorized_ids=frozenset({"impl-a"})))

    assert inventory.calls == 1


def test_transitional_preference_is_fitness_not_authority() -> None:
    allowed = _implementation("allowed", model="model-low")
    unauthorized = _implementation("blocked", model="model-preferred")
    inventory = StaticInventory(allowed, unauthorized)
    service = RuntimeSelectionService(
        inventory=inventory,
        eligibility_evidence=_evidence(allowed, unauthorized),
        calibration_records=_calibrations(allowed, unauthorized),
        fitness=PreferenceRuntimeFitnessAdapter(),
    )

    decision = service.select(
        _request(
            authorized_ids=frozenset({"allowed"}),
            preferred_models=("model-preferred", "model-low"),
        )
    )

    assert decision.selected.implementation.implementation_id == "allowed"


def test_preference_adapter_ranks_known_good_models_after_lifecycle() -> None:
    first = _implementation("impl-a", model="model-a")
    second = _implementation("impl-b", model="model-b")
    service = RuntimeSelectionService(
        inventory=StaticInventory(first, second),
        eligibility_evidence=_evidence(first, second),
        calibration_records=_calibrations(first, second),
        fitness=PreferenceRuntimeFitnessAdapter(),
    )

    decision = service.select(
        _request(
            authorized_ids=frozenset({"impl-a", "impl-b"}),
            preferred_models=("model-b", "model-a"),
        )
    )

    assert decision.selected.implementation.implementation_id == "impl-b"


def test_runtime_selection_layers_do_not_import_engine_config_or_provider_execution() -> None:
    root = Path(__file__).resolve().parents[1] / "reference" / "implementations" / "python" / "src" / "teo_reference"
    paths = (
        root / "domain" / "runtime_selection.py",
        root / "ports" / "runtime_selection.py",
        root / "application" / "runtime_selection.py",
        root / "adapters" / "runtime_selection.py",
    )
    forbidden_fragments = {
        "teo_reference.engine",
        "teo_reference.config",
        "provider_adapter",
        "openai_adapter",
        "anthropic_adapter",
        "google_adapter",
    }

    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        joined = "\n".join(imported)
        assert all(fragment not in joined for fragment in forbidden_fragments), path
