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
CURRENT_MAIN = "74c128947f1d98f0e42c595bd1229561ab6dab50"
RMI8_MERGE = "8e5bef0f209f6fe14b46311c7345cea141eb0a4b"
RMI8_FINAL_HEAD = "d5ab4791e7b037bade24e2780a9aaef7df42878f"
RMI8_FINAL_CI = 958
TRANCHE3_HEAD = "504c05f67ee6d89e0144e6d16c11c3a19509e780"
CURRENT_QUALIFIED_TESTS = 1118
CURRENT_QUALIFIED_TRACKED_FILES = 607
CURRENT_QUALIFIED_SCHEMAS = 42
CURRENT_QUALIFIED_CI = 960


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


def test_progress_tracker_matches_current_merged_truth() -> None:
    text = _text("docs/stewardship/progress-tracker.md")

    for phrase in (
        "**Last reconciled:** 2026-08-25",
        f"`{CURRENT_MAIN}` after clean-architecture Tranche 3 / PR #210",
        f"{CURRENT_QUALIFIED_TESTS:,} tests passed",
        f"{CURRENT_QUALIFIED_TRACKED_FILES} tracked-file layout checks",
        f"{CURRENT_QUALIFIED_SCHEMAS} schemas",
        f"Reference Implementation CI #{CURRENT_QUALIFIED_CI}",
        TRANCHE3_HEAD,
        f"PR #209 merged as `{RMI8_MERGE}`",
        f"Reference Implementation CI #{RMI8_FINAL_CI}",
        RMI8_FINAL_HEAD,
        "RMI-1 through RMI-8 merged and reconciled",
        "model/provider neutral",
        "runtime-compatibility-defaults.yaml",
        "specialist-selection-policy.yaml",
        "Discovered -> Eligible -> Calibrated -> Selected",
        "compatibility inputs. It does not claim that those implementations are currently running",
        "Tranches 1–3 merged and qualified",
        "Tranche 4: specialist routing by composition",
        "`documentation`, evaluation only, not authorized for live execution",
        "provider-backed controlled `documentation` replay evidence",
        "High and critical live execution remains unauthorized",
        "Host Integration Contract research",
        "Execution Environment & Recovery Contract",
        "Task Intent & Action Authority Contract",
    ):
        assert phrase in text

    for stale in (
        "before the RMI-8 documentation-only merge",
        "merge of the documentation-only RMI-8 tranche is the remaining closure action",
        "PR #209 candidate qualified",
        "awaiting only final exact-head closure verification/merge",
        "993 tests passed, 558 tracked-file layout checks",
        "established by CI #806",
        "| Runtime model binding | In progress | 95% |",
    ):
        assert stale not in text


def test_roadmap_describes_completed_runtime_binding_and_current_clean_architecture() -> None:
    text = _text("docs/stewardship/roadmap.md")

    for phrase in (
        "runtime-model-binding program through RMI-8",
        "TEO routes capabilities and responsibility, not model brands",
        "Discovered -> Eligible -> Calibrated -> Selected",
        "RMI-1 through RMI-8 are implemented, qualified, and merged",
        "runtime-compatibility-defaults.yaml",
        "specialist-selection-policy.yaml",
        "retired `specialist-model-routing.yaml` is not a current authority surface",
        "Connection mechanism remains separate from runtime fitness and routing",
        f"PR #209 as `{RMI8_MERGE}`",
        f"Reference Implementation CI #{RMI8_FINAL_CI}",
        "Current actionable repository work: clean-architecture migration (#197)",
        f"PR #210 as `{CURRENT_MAIN}`",
        f"CI #{CURRENT_QUALIFIED_CI}",
        "Tranche 4 — specialist routing by composition",
        "High and critical live execution remains outside the current guarded runtime",
        "Assimilation is not installation",
        "routing_continuity_only",
    ):
        assert phrase in text

    assert "RMI-8 candidate qualification" not in text
    assert "required before PR #209 merges" not in text


def test_root_readme_exposes_current_repository_truth() -> None:
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
        f"`main@{CURRENT_MAIN}` after clean-architecture Tranche 3 / PR #210",
        f"Reference Implementation CI #{CURRENT_QUALIFIED_CI}",
        TRANCHE3_HEAD,
        "1,118 tests",
        "607 tracked-file layout checks",
        "42 schemas",
        f"PR #209 as `{RMI8_MERGE}`",
        f"Reference Implementation CI #{RMI8_FINAL_CI}",
        "Tranches 1–3 are merged",
        "Tranche 4 replaces that coupling by composition",
        "The next gate is provider-backed controlled documentation replay evidence",
        "eleven provider-independent adversarial slices",
        "Reference Implementation CI #739",
        "routing_continuity_only",
        "Assimilation is not installation",
    ):
        assert phrase in text

    for stale in (
        "before the documentation-only RMI-8 merge",
        "PR #209 is the documentation-only closure tranche",
        "RMI-8 candidate Reference Implementation CI #954",
        "A final exact-head CI remains the merge gate for PR #209",
    ):
        assert stale not in text


def test_clean_architecture_plan_records_tranche3_and_next_gate() -> None:
    text = _text("docs/architecture/python-clean-architecture-migration.md")

    for phrase in (
        "Tranches 1–3 merged",
        "Tranche 3 — dispatch application service — COMPLETE",
        f"PR #210 as `{CURRENT_MAIN}`",
        TRANCHE3_HEAD,
        f"Reference Implementation CI #{CURRENT_QUALIFIED_CI}",
        "1,118 tests passed",
        "607 tracked files",
        "Tranche 4 — specialist routing by composition — NEXT",
        "SpecialistRoutingEngine",
        "inheritance/refinement/preference bridge for Tranche 4",
    ):
        assert phrase in text


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
        "do not widen live authority",
    ):
        assert phrase in combined

    assert "workers authorize concrete models" not in combined.lower()
