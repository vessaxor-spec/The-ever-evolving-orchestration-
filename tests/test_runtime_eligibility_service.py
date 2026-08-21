from __future__ import annotations

import ast
from pathlib import Path

import pytest

from teo_reference.adapters.runtime_eligibility import (
    DeclaredRuntimeEligibilityEvidenceAdapter,
    RuntimeEligibilityEvidenceAdapterError,
)
from teo_reference.application.runtime_eligibility import (
    RuntimeEligibilityEvaluationError,
    RuntimeEligibilityService,
)
from teo_reference.domain.runtime_binding import (
    AuthorityScope,
    EligibilityEvidence,
    EligibilityRequirements,
    ExecutionConfigurationIdentity,
    RuntimeImplementation,
)
from teo_reference.ports.runtime_eligibility import (
    RuntimeEligibilityEvidenceUnavailable,
)


def _implementation(
    implementation_id: str,
    *,
    inventory_state: str = "running",
    capabilities: frozenset[str] = frozenset({"coding", "testing"}),
    runtime: str = "runtime-a",
) -> RuntimeImplementation:
    return RuntimeImplementation(
        configuration=ExecutionConfigurationIdentity.from_runtime(
            implementation_id=implementation_id,
            model=f"model-{implementation_id}",
            runtime=runtime,
            provider_family="provider-neutral-test",
            version="1",
            context_window=32768,
            hardware="test-hardware",
            serving_stack="test-stack",
        ),
        inventory_state=inventory_state,  # type: ignore[arg-type]
        capabilities=capabilities,
    )


class StaticInventory:
    def __init__(self, *implementations: RuntimeImplementation) -> None:
        self._implementations = implementations

    def discover(self):
        return self._implementations


def _full_evidence(**overrides: bool | None) -> EligibilityEvidence:
    values: dict[str, bool | None] = {
        "reachable": True,
        "healthy": True,
        "privacy_allowed": True,
        "runtime_constraints_satisfied": True,
    }
    values.update(overrides)
    return EligibilityEvidence(**values)


def _requirements(**overrides: object) -> EligibilityRequirements:
    values: dict[str, object] = {
        "required_capabilities": frozenset({"coding"}),
        "require_reachable": True,
        "require_healthy": True,
        "require_privacy_allowed": True,
        "require_runtime_constraints": True,
    }
    values.update(overrides)
    return EligibilityRequirements(**values)  # type: ignore[arg-type]


def test_full_policy_admits_only_candidate_satisfying_every_gate() -> None:
    candidates = (
        _implementation("good"),
        _implementation("unauthorized"),
        _implementation("missing-capability", capabilities=frozenset({"testing"})),
        _implementation("unreachable"),
        _implementation("unhealthy"),
        _implementation("privacy-denied"),
        _implementation("runtime-denied"),
        _implementation("unavailable", inventory_state="unavailable"),
    )
    evidence = DeclaredRuntimeEligibilityEvidenceAdapter(
        {
            "good": _full_evidence(),
            "unauthorized": _full_evidence(),
            "missing-capability": _full_evidence(),
            "unreachable": _full_evidence(reachable=False),
            "unhealthy": _full_evidence(healthy=False),
            "privacy-denied": _full_evidence(privacy_allowed=False),
            "runtime-denied": _full_evidence(runtime_constraints_satisfied=False),
            "unavailable": _full_evidence(),
        }
    )
    service = RuntimeEligibilityService(StaticInventory(*candidates), evidence)

    snapshot = service.evaluate(
        authority=AuthorityScope(
            frozenset(
                {
                    "good",
                    "missing-capability",
                    "unreachable",
                    "unhealthy",
                    "privacy-denied",
                    "runtime-denied",
                    "unavailable",
                }
            )
        ),
        requirements=_requirements(),
    )

    assert [item.implementation.implementation_id for item in snapshot.eligible] == [
        "good"
    ]
    assert snapshot.get("unauthorized") is not None
    assert "implementation is outside the authorized set" in snapshot.get(
        "unauthorized"
    ).decision.reasons  # type: ignore[union-attr]
    assert "missing required capabilities: coding" in snapshot.get(
        "missing-capability"
    ).decision.reasons  # type: ignore[union-attr]
    assert "mandatory eligibility constraint failed: reachable" in snapshot.get(
        "unreachable"
    ).decision.reasons  # type: ignore[union-attr]
    assert "mandatory eligibility constraint failed: healthy" in snapshot.get(
        "unhealthy"
    ).decision.reasons  # type: ignore[union-attr]
    assert "mandatory eligibility constraint failed: privacy_allowed" in snapshot.get(
        "privacy-denied"
    ).decision.reasons  # type: ignore[union-attr]
    assert (
        "mandatory eligibility constraint failed: runtime_constraints_satisfied"
        in snapshot.get("runtime-denied").decision.reasons  # type: ignore[union-attr]
    )
    assert "implementation is unavailable" in snapshot.get(
        "unavailable"
    ).decision.reasons  # type: ignore[union-attr]


def test_missing_declared_evidence_fails_closed() -> None:
    implementation = _implementation("remote", inventory_state="available_remote")
    service = RuntimeEligibilityService(
        StaticInventory(implementation),
        DeclaredRuntimeEligibilityEvidenceAdapter(),
    )

    snapshot = service.evaluate(
        authority=AuthorityScope(frozenset({"remote"})),
        requirements=_requirements(),
    )

    assessment = snapshot.get("remote")
    assert assessment is not None
    assert assessment.permitted is False
    assert set(assessment.decision.reasons) == {
        "missing mandatory eligibility evidence: reachable",
        "missing mandatory eligibility evidence: healthy",
        "missing mandatory eligibility evidence: privacy_allowed",
        "missing mandatory eligibility evidence: runtime_constraints_satisfied",
    }


def test_user_declared_inventory_does_not_gain_authority_from_presence() -> None:
    implementation = _implementation("declared", inventory_state="user_declared")
    service = RuntimeEligibilityService(
        StaticInventory(implementation),
        DeclaredRuntimeEligibilityEvidenceAdapter({"declared": _full_evidence()}),
    )

    snapshot = service.evaluate(
        authority=AuthorityScope(frozenset()),
        requirements=_requirements(),
    )

    assessment = snapshot.get("declared")
    assert assessment is not None
    assert assessment.permitted is False
    assert "implementation is outside the authorized set" in assessment.decision.reasons


def test_optional_evidence_checks_do_not_become_implicit_mandatory_checks() -> None:
    implementation = _implementation("bounded")
    evidence = EligibilityEvidence(reachable=True)
    service = RuntimeEligibilityService(
        StaticInventory(implementation),
        DeclaredRuntimeEligibilityEvidenceAdapter({"bounded": evidence}),
    )

    snapshot = service.evaluate(
        authority=AuthorityScope(frozenset({"bounded"})),
        requirements=_requirements(
            require_healthy=False,
            require_privacy_allowed=False,
            require_runtime_constraints=False,
        ),
    )

    assessment = snapshot.get("bounded")
    assert assessment is not None
    assert assessment.permitted is True


def test_local_and_remote_candidates_are_policy_peers() -> None:
    local = _implementation("local", inventory_state="available_local", runtime="local")
    remote = _implementation(
        "remote", inventory_state="available_remote", runtime="remote"
    )
    service = RuntimeEligibilityService(
        StaticInventory(local, remote),
        DeclaredRuntimeEligibilityEvidenceAdapter(
            {"local": _full_evidence(), "remote": _full_evidence()}
        ),
    )

    snapshot = service.evaluate(
        authority=AuthorityScope(frozenset({"local", "remote"})),
        requirements=_requirements(),
    )

    assert [item.implementation.implementation_id for item in snapshot.eligible] == [
        "local",
        "remote",
    ]


def test_typed_evidence_source_unavailability_fails_closed_and_is_auditable() -> None:
    implementation = _implementation("offline-evidence")

    class UnavailableEvidence:
        def observe(self, candidate: RuntimeImplementation) -> EligibilityEvidence:
            raise RuntimeEligibilityEvidenceUnavailable("health probe unavailable")

    service = RuntimeEligibilityService(StaticInventory(implementation), UnavailableEvidence())
    snapshot = service.evaluate(
        authority=AuthorityScope(frozenset({"offline-evidence"})),
        requirements=_requirements(),
    )

    assessment = snapshot.get("offline-evidence")
    assert assessment is not None
    assert assessment.permitted is False
    assert assessment.evidence_error == "health probe unavailable"
    assert "missing mandatory eligibility evidence: healthy" in assessment.decision.reasons


def test_evidence_source_failure_cannot_override_authority_even_when_checks_optional() -> None:
    implementation = _implementation("not-authorized")

    class UnavailableEvidence:
        def observe(self, candidate: RuntimeImplementation) -> EligibilityEvidence:
            raise RuntimeEligibilityEvidenceUnavailable("observation unavailable")

    service = RuntimeEligibilityService(StaticInventory(implementation), UnavailableEvidence())
    snapshot = service.evaluate(
        authority=AuthorityScope(frozenset()),
        requirements=_requirements(
            require_reachable=False,
            require_healthy=False,
            require_privacy_allowed=False,
            require_runtime_constraints=False,
        ),
    )

    assessment = snapshot.get("not-authorized")
    assert assessment is not None
    assert assessment.permitted is False
    assert "implementation is outside the authorized set" in assessment.decision.reasons


def test_empty_inventory_is_valid_and_produces_no_eligibility() -> None:
    service = RuntimeEligibilityService(
        StaticInventory(),
        DeclaredRuntimeEligibilityEvidenceAdapter(),
    )

    snapshot = service.evaluate(
        authority=AuthorityScope(frozenset()),
        requirements=_requirements(),
    )

    assert snapshot.assessments == ()
    assert snapshot.eligible == ()
    assert snapshot.rejected == ()


def test_duplicate_inventory_ids_fail_closed_before_eligibility_snapshot() -> None:
    first = _implementation("duplicate")
    second = _implementation("duplicate")
    service = RuntimeEligibilityService(
        StaticInventory(first, second),
        DeclaredRuntimeEligibilityEvidenceAdapter({"duplicate": _full_evidence()}),
    )

    with pytest.raises(
        RuntimeEligibilityEvaluationError,
        match="requires unique implementation ids: duplicate",
    ):
        service.evaluate(
            authority=AuthorityScope(frozenset({"duplicate"})),
            requirements=_requirements(),
        )


def test_non_evidence_value_from_port_is_rejected() -> None:
    implementation = _implementation("bad-evidence")

    class BadEvidence:
        def observe(self, candidate: RuntimeImplementation):
            return {"healthy": True}

    service = RuntimeEligibilityService(StaticInventory(implementation), BadEvidence())
    with pytest.raises(
        RuntimeEligibilityEvaluationError,
        match="non-EligibilityEvidence value",
    ):
        service.evaluate(
            authority=AuthorityScope(frozenset({"bad-evidence"})),
            requirements=_requirements(),
        )


def test_declared_evidence_adapter_rejects_structurally_invalid_entries() -> None:
    with pytest.raises(
        RuntimeEligibilityEvidenceAdapterError,
        match="implementation_id cannot be empty",
    ):
        DeclaredRuntimeEligibilityEvidenceAdapter({" ": _full_evidence()})

    with pytest.raises(
        RuntimeEligibilityEvidenceAdapterError,
        match="must be EligibilityEvidence",
    ):
        DeclaredRuntimeEligibilityEvidenceAdapter({"impl": object()})  # type: ignore[dict-item]


def test_rmi3_layers_do_not_import_routing_config_or_provider_execution_surfaces() -> None:
    root = (
        Path(__file__).resolve().parents[1]
        / "reference"
        / "implementations"
        / "python"
        / "src"
        / "teo_reference"
    )
    targets = {
        root / "application" / "runtime_eligibility.py": {
            "__future__",
            "dataclasses",
            "domain",
            "ports",
        },
        root / "adapters" / "runtime_eligibility.py": {
            "__future__",
            "types",
            "typing",
            "domain",
        },
        root / "ports" / "runtime_eligibility.py": {
            "__future__",
            "typing",
            "domain",
        },
    }

    for path, allowed_roots in targets.items():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported_roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(
                    alias.name.split(".", 1)[0] for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])
        assert imported_roots <= allowed_roots
