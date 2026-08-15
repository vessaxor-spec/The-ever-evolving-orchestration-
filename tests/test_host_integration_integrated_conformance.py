from __future__ import annotations

import runpy
from dataclasses import replace
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "research" / "runtime" / "host_integration_integrated_conformance.py"
INTEGRATED = runpy.run_path(str(HARNESS))
ACTIVATION_SEQUENCE = INTEGRATED["ACTIVATION_SEQUENCE"]
AssimilationLease = INTEGRATED["AssimilationLease"]
FreshAIAssimilationDeclaration = INTEGRATED["FreshAIAssimilationDeclaration"]
IntegratedHostConformanceError = INTEGRATED["IntegratedHostConformanceError"]
IntegratedHostConformanceSandbox = INTEGRATED["IntegratedHostConformanceSandbox"]
REQUIRED_OPEN_SURFACES = INTEGRATED["REQUIRED_OPEN_SURFACES"]
StandingIntegrationHook = INTEGRATED["StandingIntegrationHook"]
derive_assimilation_truth = INTEGRATED["derive_assimilation_truth"]

TEST_REVISION = "1" * 40


@pytest.fixture(scope="session")
def truth():
    return derive_assimilation_truth(ROOT, revision=TEST_REVISION)


def declaration(truth, **overrides):
    values = {
        "host_id": "fresh-ai-host",
        "integration_role": "embedded_orchestration_control_plane",
        "host_identity_preserved": True,
        "portfolio_authority_owner": "host",
        "routing_authority_owner": "teo_mission_control",
        "connection_semantics": "connection_after_routing",
        "responsibility_chain": truth.responsibility_chain,
        "specialist_context_mode": "selected_only_bounded_projection",
        "verification_mode": "independent_provider_diverse_when_required",
        "activation_sequence": ACTIVATION_SEQUENCE,
        "stable_release": truth.stable_release,
        "runtime_version": truth.runtime_version,
        "revision": truth.revision,
        "binding_id": truth.binding_id,
        "team_count": truth.team_count,
        "worker_count": truth.worker_count,
        "specialist_count": truth.specialist_count,
        "active_live_task_types": truth.active_live_task_types,
        "staged_live_task_types": truth.staged_live_task_types,
        "unsupported_surfaces": tuple(sorted(REQUIRED_OPEN_SURFACES)),
    }
    values.update(overrides)
    return FreshAIAssimilationDeclaration(**values)


def make_sandbox(truth, **overrides):
    return IntegratedHostConformanceSandbox.create(
        ROOT,
        declaration=declaration(truth, **overrides),
        revision=TEST_REVISION,
    )


def register_hook(sandbox):
    sandbox.register_standing_hook(
        StandingIntegrationHook(
            hook_id="standing-teo-control-plane",
            host_id=sandbox.host_id,
            binding_id=sandbox.truth.binding_id,
        )
    )


def active_task(task_id: str) -> dict:
    return {
        "task_id": task_id,
        "task": "Classify a bounded record through the integrated TEO path.",
        "task_type": "high_volume_simple",
        "risk_level": "low",
    }


@pytest.mark.parametrize("role", ["plugin", "sdk", "library", "finished_product"])
def test_fresh_ai_cannot_frame_teo_as_installable_plugin_or_product(truth, role) -> None:
    with pytest.raises(IntegratedHostConformanceError, match="control plane"):
        make_sandbox(truth, integration_role=role)


def test_assimilation_preserves_host_identity(truth) -> None:
    with pytest.raises(IntegratedHostConformanceError, match="preserve the host identity"):
        make_sandbox(truth, host_identity_preserved=False)


def test_assimilation_preserves_host_portfolio_authority(truth) -> None:
    with pytest.raises(IntegratedHostConformanceError, match="host-owned"):
        make_sandbox(truth, portfolio_authority_owner="teo")


def test_assimilation_rejects_parallel_host_routing_plane(truth) -> None:
    with pytest.raises(IntegratedHostConformanceError, match="parallel host routing plane"):
        make_sandbox(truth, routing_authority_owner="host_router")


def test_assimilation_rejects_collapsed_responsibility_chain(truth) -> None:
    collapsed = ("agent", "specialist", "model")
    with pytest.raises(IntegratedHostConformanceError, match="responsibility chain"):
        make_sandbox(truth, responsibility_chain=collapsed)


def test_assimilation_rejects_full_specialist_corpus_loading(truth) -> None:
    with pytest.raises(IntegratedHostConformanceError, match="bounded selected specialist"):
        make_sandbox(truth, specialist_context_mode="load_all_active_specialists")


def test_assimilation_rejects_same_session_verification_roleplay(truth) -> None:
    with pytest.raises(IntegratedHostConformanceError, match="actual independence"):
        make_sandbox(truth, verification_mode="same_session_persona_shift")


def test_assimilation_rejects_big_bang_activation(truth) -> None:
    with pytest.raises(IntegratedHostConformanceError, match="shadow mode"):
        make_sandbox(
            truth,
            activation_sequence=("full_enforcement",),
        )


def test_assimilation_rejects_stale_executable_truth(truth) -> None:
    with pytest.raises(IntegratedHostConformanceError, match="team_count"):
        make_sandbox(truth, team_count=truth.team_count + 1)


def test_assimilation_rejects_false_live_scope_claim(truth) -> None:
    with pytest.raises(IntegratedHostConformanceError, match="active_live_task_types"):
        make_sandbox(
            truth,
            active_live_task_types=("high_volume_simple", "documentation"),
        )


def test_assimilation_must_declare_open_integration_boundaries(truth) -> None:
    with pytest.raises(IntegratedHostConformanceError, match="hides unresolved"):
        make_sandbox(truth, unsupported_surfaces=("production_remote_authenticity",))


def test_assimilation_lease_tampering_is_rejected(truth) -> None:
    sandbox = make_sandbox(truth)
    forged = AssimilationLease(
        lease_id=sandbox.lease.lease_id,
        host_id=sandbox.lease.host_id,
        binding_id="0" * 64,
        revision=sandbox.lease.revision,
        declaration_digest=sandbox.lease.declaration_digest,
        authorization_token=sandbox.lease.authorization_token,
    )
    with pytest.raises(IntegratedHostConformanceError, match="signature"):
        sandbox.assimilation_authority.verify(forged)


def test_one_time_install_without_standing_hook_cannot_activate(truth, tmp_path) -> None:
    sandbox = make_sandbox(truth)
    sandbox.shadow_route(active_task("shadow-install-only"))
    with pytest.raises(IntegratedHostConformanceError, match="persistent TEO control-plane hook"):
        sandbox.governed_execute(active_task("install-only"), artifact_root=tmp_path)


def test_standing_hook_must_bind_exact_teo_truth(truth) -> None:
    sandbox = make_sandbox(truth)
    with pytest.raises(IntegratedHostConformanceError, match="stale or mismatched"):
        sandbox.register_standing_hook(
            StandingIntegrationHook(
                hook_id="stale-hook",
                host_id=sandbox.host_id,
                binding_id="0" * 64,
            )
        )


def test_bounded_activation_requires_real_shadow_dispatch(truth, tmp_path) -> None:
    sandbox = make_sandbox(truth)
    register_hook(sandbox)
    with pytest.raises(IntegratedHostConformanceError, match="shadow-routing evidence"):
        sandbox.governed_execute(active_task("no-shadow"), artifact_root=tmp_path)


def test_shadow_dispatch_preserves_teo_responsibility_and_verification(truth) -> None:
    sandbox = make_sandbox(truth)
    dispatch = sandbox.shadow_route(active_task("shadow-proof"))

    assert dispatch.selected_team == "research"
    assert dispatch.selected_worker == "documentation"
    assert dispatch.selected_implementation.model
    assert dispatch.verification.independent is True
    assert (
        dispatch.selected_implementation.provider_family
        != dispatch.verification.implementation.provider_family
    )


def test_integrated_active_scope_executes_and_finalizes(truth, tmp_path) -> None:
    sandbox = make_sandbox(truth)
    register_hook(sandbox)
    sandbox.shadow_route(active_task("shadow-before-active"))

    outcome = sandbox.governed_execute(
        active_task("governed-active"),
        artifact_root=tmp_path,
    )

    assert outcome.status == "completed"
    assert outcome.execution_status == "succeeded"
    assert outcome.verification_status == "passed"


def test_integrated_negative_controls_fail_closed(truth, tmp_path) -> None:
    sandbox = make_sandbox(truth)
    register_hook(sandbox)
    sandbox.shadow_route(active_task("shadow-before-negative-controls"))

    sandbox.prove_staged_scope_refusal()
    sandbox.prove_revoked_admission_refusal()
    sandbox.prove_artifact_mutation_refusal(artifact_root=tmp_path)
    sandbox.prove_autonomy_and_human_authority()
    sandbox.prove_recursion_refusal()

    assert sandbox._negative_controls == {
        "staged_scope_refusal",
        "revoked_admission_refusal",
        "artifact_mutation_refusal",
        "critical_human_gate_preserved",
        "high_risk_autonomy_preserved",
        "recursive_reentry_refusal",
    }


def test_one_governed_demo_is_not_continued_integration(truth, tmp_path) -> None:
    sandbox = make_sandbox(truth)
    register_hook(sandbox)
    sandbox.shadow_route(active_task("shadow-before-one-use"))
    sandbox.governed_execute(active_task("only-one-use"), artifact_root=tmp_path)
    sandbox.prove_staged_scope_refusal()
    sandbox.prove_revoked_admission_refusal()
    sandbox.prove_artifact_mutation_refusal(artifact_root=tmp_path)
    sandbox.prove_autonomy_and_human_authority()
    sandbox.prove_recursion_refusal()

    with pytest.raises(IntegratedHostConformanceError, match="repeated post-assimilation TEO use"):
        sandbox.claim_process_local_conformance()


def test_full_process_local_assimilation_and_integrated_premortem_replay(truth, tmp_path) -> None:
    sandbox = make_sandbox(truth)
    register_hook(sandbox)

    sandbox.shadow_route(active_task("shadow-baseline"))
    first = sandbox.governed_execute(active_task("activation-probe"), artifact_root=tmp_path)
    second = sandbox.governed_execute(active_task("continuity-probe"), artifact_root=tmp_path)
    sandbox.prove_staged_scope_refusal()
    sandbox.prove_revoked_admission_refusal()
    sandbox.prove_artifact_mutation_refusal(artifact_root=tmp_path)
    sandbox.prove_autonomy_and_human_authority()
    sandbox.prove_recursion_refusal()

    report = sandbox.claim_process_local_conformance()

    assert first.status == "completed"
    assert second.status == "completed"
    assert report.passed is True
    assert report.shadow_dispatches == 1
    assert report.governed_executions == 2
    assert all(report.premortem_replay.values())
    assert set(report.residual_boundaries) == REQUIRED_OPEN_SURFACES


def test_assimilation_protocol_explicitly_prevents_install_and_forget() -> None:
    text = (
        ROOT
        / "research"
        / "roadmaps"
        / "host-integration-assimilation-protocol.md"
    ).read_text(encoding="utf-8")

    for phrase in (
        "Assimilation is not installation.",
        "TEO is an orchestration control plane",
        "install a persistent control-plane hook",
        "Run TEO in shadow mode",
        "Prove continued use on a later task",
        "one successful integration demo is insufficient",
        "Fresh-AI bootstrap directive",
        "do not give the host a special \"use TEO now\" reminder",
        "Do not claim 'TEO integrated' merely because files, prompts, skills, or packages are present.",
    ):
        assert phrase in text


def test_assimilation_protocol_preserves_host_and_teo_separation() -> None:
    text = (
        ROOT
        / "research"
        / "roadmaps"
        / "host-integration-assimilation-protocol.md"
    ).read_text(encoding="utf-8")

    for phrase in (
        "The host remains the host. TEO remains TEO.",
        "Host backlog, priority, and task admission",
        "Routing of admitted TEO-governed work",
        "Provider connection mechanism",
        "Host/runtime after routing",
        "TEO Mission Control must own routing for work explicitly admitted into the TEO-governed boundary",
    ):
        assert phrase in text
