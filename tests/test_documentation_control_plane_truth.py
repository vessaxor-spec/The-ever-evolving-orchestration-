from pathlib import Path

from teo_reference.config import ConfigBundle


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TEAM_COUNT = 10
EXPECTED_WORKER_COUNT = 84
EXPECTED_SPECIALIST_COUNT = 82
EXPECTED_MISSION_CONTROL_WORKERS = {
    "orchestration",
    "operations",
    "project_delivery",
    "incident_response",
}
CURRENT_PRE_RMI8_MAIN = "3d121fde56f840bbfaa6bcb240c262f045525786"
RMI7_QUALIFIED_TESTS = 1113
RMI7_QUALIFIED_TRACKED_FILES = 602
RMI7_QUALIFIED_SCHEMAS = 42
RMI7_QUALIFIED_CI = 951


def _text(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_control_plane_roster_matches_executable_configuration() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    teams = {
        str(worker.get("owning_team"))
        for worker in bundle.worker_registry.values()
    }
    mission_control_workers = {
        name
        for name, worker in bundle.worker_registry.items()
        if worker.get("owning_team") == "mission_control"
    }

    assert len(teams) == EXPECTED_TEAM_COUNT
    assert len(bundle.worker_registry) == EXPECTED_WORKER_COUNT
    assert len(bundle.specialist_registry) == EXPECTED_SPECIALIST_COUNT
    assert mission_control_workers == EXPECTED_MISSION_CONTROL_WORKERS


def test_runtime_binding_current_authority_surfaces_exist() -> None:
    required = (
        "policy/routing/core/routing.yaml",
        "policy/routing/core/specialist-selection-policy.yaml",
        "policy/routing/core/runtime-compatibility-defaults.yaml",
        "tests/test_runtime_binding_contract.py",
        "tests/test_runtime_binding_state_integrity.py",
        "tests/test_runtime_inventory_composition.py",
        "tests/test_runtime_eligibility_service.py",
        "tests/test_runtime_calibration_service.py",
        "tests/test_runtime_selection_service.py",
        "tests/test_runtime_dispatch_binding.py",
        "tests/test_runtime_observed_identity.py",
        "tests/test_runtime_model_neutral_responsibility.py",
    )
    for path in required:
        assert (REPO_ROOT / path).is_file(), path

    assert not (
        REPO_ROOT / "policy/routing/core/specialist-model-routing.yaml"
    ).exists()


def test_progress_tracker_matches_post_rmi7_executable_truth() -> None:
    text = _text("docs/stewardship/progress-tracker.md")

    for phrase in (
        "**Last reconciled:** 2026-08-24",
        f"`{CURRENT_PRE_RMI8_MAIN}` after RMI-7 / PR #208",
        f"{RMI7_QUALIFIED_TESTS:,} tests passed",
        f"{RMI7_QUALIFIED_TRACKED_FILES} tracked-file layout checks",
        f"{RMI7_QUALIFIED_SCHEMAS} schemas",
        f"Reference Implementation CI #{RMI7_QUALIFIED_CI}",
        "RMI-1 through RMI-7 executable and merged",
        "model/provider neutral",
        "runtime-compatibility-defaults.yaml",
        "specialist-selection-policy.yaml",
        "Discovered -> Eligible -> Calibrated -> Selected",
        "compatibility inputs. It does not claim that those implementations are currently running",
        "RMI-8 — reconcile canonical documentation",
        "| Live execution expansion | In progress | 65% |",
        "`documentation`, evaluation only, not authorized for live execution",
        "provider-backed controlled documentation replay evidence",
        "High and critical live execution remains unauthorized",
        "Clean-architecture migration (#197)",
        "Host Integration Contract research",
        "Execution Environment & Recovery Contract",
        "Task Intent & Action Authority Contract",
    ):
        assert phrase in text

    for stale in (
        "993 tests passed, 558 tracked-file layout checks",
        "established by CI #806",
        "specialist-model-routing.yaml` is the current",
    ):
        assert stale not in text


def test_roadmap_describes_capability_first_runtime_binding() -> None:
    text = _text("docs/stewardship/roadmap.md")

    for phrase in (
        "TEO routes capabilities and responsibility, not model brands",
        "Discovered -> Eligible -> Calibrated -> Selected",
        "runtime-compatibility-defaults.yaml",
        "specialist-selection-policy.yaml",
        "retired `specialist-model-routing.yaml` is not a current authority surface",
        "Connection mechanism remains separate from runtime fitness and routing",
        "Current: RMI-8 truth reconciliation",
        "High and critical live execution remains outside the current guarded runtime",
        "Clean-architecture migration (#197)",
        "Assimilation is not installation",
        "routing_continuity_only",
    ):
        assert phrase in text

    assert "The repaired staged route is:" not in text


def test_root_readme_exposes_current_runtime_binding_truth() -> None:
    text = _text("README.md")

    for phrase in (
        "TEO routes capabilities and responsibility, not model brands",
        "Discovered -> Eligible -> Calibrated -> Selected",
        "Responsibility is model-neutral",
        "Runtime inventory does not equal runtime truth",
        "Observed identity matters",
        "runtime-compatibility-defaults.yaml",
        "specialist-selection-policy.yaml",
        "retired `specialist-model-routing.yaml` is not a current authority surface",
        f"`{CURRENT_PRE_RMI8_MAIN}` after RMI-7 / PR #208",
        f"Reference Implementation CI #{RMI7_QUALIFIED_CI}",
        "1,113 tests",
        "602 tracked-file layout checks",
        "42 schemas",
        "The next gate is provider-backed controlled documentation replay evidence",
        "eleven provider-independent adversarial slices",
        "Reference Implementation CI #739",
        "routing_continuity_only",
        "Assimilation is not installation",
    ):
        assert phrase in text

    assert "accepted substantive runtime-control baseline remains **Reference Implementation CI #514**" not in text


def test_ai_instructions_use_runtime_binding_not_static_model_authority() -> None:
    text = _text("AI_INSTRUCTIONS.md")

    for phrase in (
        "policy/routing/core/specialist-selection-policy.yaml",
        "policy/routing/core/runtime-compatibility-defaults.yaml",
        "retired `policy/routing/core/specialist-model-routing.yaml` is not a current authority surface",
        "Discovered -> Eligible -> Calibrated -> Selected",
        "TEO routes capabilities and responsibility, not model brands",
        "Do not claim that TEO automatically discovers every arbitrary local or cloud model",
        "## Connection neutrality",
        "Connection mechanism is separate from routing semantics",
        "API keys, OAuth or subscription-backed sessions, delegated identity",
        "service accounts, connector sessions",
        "must not change the selected Team, Worker, Specialist, model role, fallback, verifier, or reasoning effort",
        "Pretrained, cached, remembered, or previously documented model information is not authoritative",
        "A newer model does not automatically replace an existing route",
        "Observed runtime identity",
        "Routing continuity is not full end-to-end assimilation",
        "Research simulation may support `routing_continuity_only`",
        "Assimilation research never widens live execution by itself",
        "Issue #197 is behavior-preserving and separate from runtime-model binding",
    ):
        assert phrase in text

    assert "Specialist-model policy may perform additive specialist-specific refinement" not in text


def test_current_docs_do_not_turn_compatibility_or_access_into_authority() -> None:
    combined = "\n".join(
        _text(path)
        for path in (
            "README.md",
            "AI_INSTRUCTIONS.md",
            "docs/stewardship/progress-tracker.md",
            "docs/stewardship/roadmap.md",
        )
    )

    for phrase in (
        "compatibility/default evidence",
        "does not create authority",
        "connection",
        "does not widen live authority",
    ):
        assert phrase in combined

    assert "workers authorize concrete models" not in combined.lower()
