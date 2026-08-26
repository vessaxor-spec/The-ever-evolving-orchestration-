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
CURRENT_MAIN = "6528be6e54b5acc8c37ef8ab1f5198ab1e61d20f"
RMI8_MERGE = "8e5bef0f209f6fe14b46311c7345cea141eb0a4b"
RMI8_FINAL_HEAD = "d5ab4791e7b037bade24e2780a9aaef7df42878f"
RMI8_FINAL_CI = 958
TRANCHE3_MERGE = "74c128947f1d98f0e42c595bd1229561ab6dab50"
TRANCHE3_HEAD = "504c05f67ee6d89e0144e6d16c11c3a19509e780"
TRANCHE3_QUALIFIED_TESTS = 1118
TRANCHE3_QUALIFIED_TRACKED_FILES = 607
TRANCHE3_QUALIFIED_SCHEMAS = 42
TRANCHE3_QUALIFIED_CI = 960
TRANCHE4_MERGE = "2f4df9d1124be91473e346ddb926f5d93c93de3e"
TRANCHE4_HEAD = "176217f9803c2ec274d2b225c52cf1f4d5c0f27f"
TRANCHE4_QUALIFIED_TESTS = 1120
TRANCHE4_QUALIFIED_TRACKED_FILES = 610
TRANCHE4_QUALIFIED_SCHEMAS = 42
TRANCHE4_QUALIFIED_CI = 968
TRANCHE5A_MERGE = "1ba1a4b0a83e403b422b47f2e7b7cef733ccb201"
TRANCHE5A_HEAD = "17afc5d5ff3b74897e6c2bcd534ccb6158fbc2cb"
TRANCHE5A_QUALIFIED_TESTS = 1127
TRANCHE5A_QUALIFIED_TRACKED_FILES = 612
TRANCHE5A_QUALIFIED_SCHEMAS = 42
TRANCHE5A_PR_CI = 977
TRANCHE5A_MAIN_CI = 978
TRANCHE5B_HEAD = "d52a834509dd04f141550806871a203b0d850560"
TRANCHE5B_QUALIFIED_TESTS = 1135
TRANCHE5B_QUALIFIED_TRACKED_FILES = 615
TRANCHE5B_QUALIFIED_SCHEMAS = 42
TRANCHE5B_PR_CI = 982
TRANCHE5B_MAIN_CI = 983
CURRENT_VALIDATED_TESTS = TRANCHE5B_QUALIFIED_TESTS
CURRENT_VALIDATED_TRACKED_FILES = TRANCHE5B_QUALIFIED_TRACKED_FILES
CURRENT_VALIDATED_SCHEMAS = TRANCHE5B_QUALIFIED_SCHEMAS
CURRENT_VALIDATED_CI = TRANCHE5B_MAIN_CI


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
        "**Last reconciled:** 2026-08-26",
        f"`{CURRENT_MAIN}` after clean-architecture Tranche 5B / PR #219",
        f"{CURRENT_VALIDATED_TESTS:,} tests passed",
        f"{CURRENT_VALIDATED_TRACKED_FILES} tracked-file layout checks",
        f"{CURRENT_VALIDATED_SCHEMAS} schemas",
        f"Reference Implementation CI #{CURRENT_VALIDATED_CI}",
        f"Reference Implementation CI #{TRANCHE3_QUALIFIED_CI}",
        TRANCHE3_HEAD,
        f"Reference Implementation CI #{TRANCHE4_QUALIFIED_CI}",
        TRANCHE4_HEAD,
        f"Reference Implementation CI #{TRANCHE5A_PR_CI}",
        TRANCHE5A_HEAD,
        f"Reference Implementation CI #{TRANCHE5A_MAIN_CI}",
        f"Reference Implementation CI #{TRANCHE5B_PR_CI}",
        TRANCHE5B_HEAD,
        f"Reference Implementation CI #{TRANCHE5B_MAIN_CI}",
        f"PR #209 merged as `{RMI8_MERGE}`",
        f"Reference Implementation CI #{RMI8_FINAL_CI}",
        RMI8_FINAL_HEAD,
        "RMI-1 through RMI-8 merged and reconciled",
        "model/provider neutral",
        "runtime-compatibility-defaults.yaml",
        "specialist-selection-policy.yaml",
        "Discovered -> Eligible -> Calibrated -> Selected",
        "compatibility inputs. It does not claim that those implementations are currently running",
        "Tranches 1–4 plus Tranche 5A and Tranche 5B merged and qualified",
        "T5C: invariant validation boundary",
        "`documentation`, evaluation only, not authorized for live execution",
        "provider-backed controlled `documentation` replay evidence",
        "High and critical live execution remains unauthorized",
        "Host Integration Contract research",
        "Execution Environment & Recovery Contract",
        "Task Intent & Action Authority Contract",
    ):
        assert phrase in text

    for stale in (
        "T5B configuration composition and explicit manifest is the next actionable repository gate",
        "T5B: configuration composition and explicit manifest",
        "Tranches 1–4 merged and qualified; Tranche 5 configuration-boundary separation is the next actionable repository gate",
        "Tranche 5: configuration boundary separation",
        "Tranches 1–3 merged and qualified",
        "Tranche 4: specialist routing by composition",
        "specialist inheritance bridge remains intentionally present for Tranche 4",
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
        f"PR #210 as `{TRANCHE3_MERGE}`",
        f"CI #{TRANCHE3_QUALIFIED_CI}",
        f"PR #212 as `{TRANCHE4_MERGE}`",
        f"CI #{TRANCHE4_QUALIFIED_CI}",
        f"PR #214 merged as `{TRANCHE5A_MERGE}`",
        f"CI #{TRANCHE5A_MAIN_CI}",
        f"PR #219 merged as `{CURRENT_MAIN}`",
        f"CI #{TRANCHE5B_MAIN_CI}",
        "Tranche 5A — configuration source I/O — COMPLETE",
        "Tranche 5B — configuration composition and explicit manifest — COMPLETE",
        "Tranche 5C — invariant validation boundary — NEXT",
        "High and critical live execution remains outside the current guarded runtime",
        "Assimilation is not installation",
        "routing_continuity_only",
    ):
        assert phrase in text

    for stale in (
        "Tranche 5B — configuration composition and explicit manifest — NEXT",
        "The behavior-preserving Python clean-architecture migration has completed Tranches 1–4; Tranche 5 configuration-boundary separation is next.",
        "Tranche 5 — configuration boundary separation** is the next clean-architecture gate",
        "inheritance bridge in `SpecialistRoutingEngine` is deliberately retained",
        "RMI-8 candidate qualification",
        "required before PR #209 merges",
    ):
        assert stale not in text


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
        f"`main@{CURRENT_MAIN}` after clean-architecture Tranche 5B / PR #219",
        f"Reference Implementation CI #{CURRENT_VALIDATED_CI}",
        f"{CURRENT_VALIDATED_TESTS:,} tests",
        f"{CURRENT_VALIDATED_TRACKED_FILES} tracked-file layout checks",
        f"{CURRENT_VALIDATED_SCHEMAS} schemas",
        f"PR #209 as `{RMI8_MERGE}`",
        f"Reference Implementation CI #{RMI8_FINAL_CI}",
        "Tranches 1–4 plus Tranche 5A and Tranche 5B are merged",
        f"Tranche 3 exact-head CI #{TRANCHE3_QUALIFIED_CI}",
        f"{TRANCHE3_QUALIFIED_TESTS:,} tests",
        f"Tranche 4 exact-head CI #{TRANCHE4_QUALIFIED_CI}",
        f"{TRANCHE4_QUALIFIED_TESTS:,} tests",
        f"Tranche 5A merged-main CI #{TRANCHE5A_MAIN_CI}",
        f"{TRANCHE5A_QUALIFIED_TESTS:,} tests",
        f"Tranche 5B merged-main CI #{TRANCHE5B_MAIN_CI}",
        f"{TRANCHE5B_QUALIFIED_TESTS:,} tests",
        "`SpecialistRoutingEngine` remains the public compatibility façade but no longer subclasses `OrchestrationEngine`",
        "Tranche 5C invariant validation boundary is the next clean-architecture gate",
        "The next gate is provider-backed controlled documentation replay evidence",
        "eleven provider-independent adversarial slices",
        "Reference Implementation CI #739",
        "routing_continuity_only",
        "Assimilation is not installation",
    ):
        assert phrase in text

    for stale in (
        "Tranches 1–4 plus Tranche 5A are merged",
        "Tranche 5B configuration composition and explicit manifest is the next clean-architecture gate",
        "Tranches 1–4 are merged",
        "Tranche 5 configuration-boundary separation is the next clean-architecture gate",
        "inheritance bridge is intentionally retained until Tranche 4",
        "before the documentation-only RMI-8 merge",
        "PR #209 is the documentation-only closure tranche",
        "RMI-8 candidate Reference Implementation CI #954",
        "A final exact-head CI remains the merge gate for PR #209",
    ):
        assert stale not in text


def test_clean_architecture_plan_records_tranche5b_and_next_gate() -> None:
    text = _text("docs/architecture/python-clean-architecture-migration.md")

    for phrase in (
        "Tranches 1–4 plus Tranche 5A and Tranche 5B merged",
        "Tranche 3 — dispatch application service — COMPLETE",
        f"PR #210 as `{TRANCHE3_MERGE}`",
        TRANCHE3_HEAD,
        f"Reference Implementation CI #{TRANCHE3_QUALIFIED_CI}",
        f"{TRANCHE3_QUALIFIED_TESTS:,} tests passed",
        f"{TRANCHE3_QUALIFIED_TRACKED_FILES} tracked files",
        "Tranche 4 — specialist routing by composition — COMPLETE",
        f"PR #212 as `{TRANCHE4_MERGE}`",
        TRANCHE4_HEAD,
        f"Reference Implementation CI #{TRANCHE4_QUALIFIED_CI}",
        f"{TRANCHE4_QUALIFIED_TESTS:,} tests passed",
        f"{TRANCHE4_QUALIFIED_TRACKED_FILES} tracked files",
        "SpecialistRoutingEngine",
        "no longer subclasses",
        "Tranche 5A — configuration source I/O — COMPLETE",
        f"PR #214 as `{TRANCHE5A_MERGE}`",
        TRANCHE5A_HEAD,
        f"Reference Implementation CI #{TRANCHE5A_PR_CI}",
        f"Reference Implementation CI #{TRANCHE5A_MAIN_CI}",
        f"{TRANCHE5A_QUALIFIED_TESTS:,} tests passed",
        f"{TRANCHE5A_QUALIFIED_TRACKED_FILES} tracked files",
        "Tranche 5B — configuration composition and explicit manifest — COMPLETE",
        f"PR #219 as `{CURRENT_MAIN}`",
        TRANCHE5B_HEAD,
        f"Reference Implementation CI #{TRANCHE5B_PR_CI}",
        f"Reference Implementation CI #{TRANCHE5B_MAIN_CI}",
        f"{TRANCHE5B_QUALIFIED_TESTS:,} tests passed",
        f"{TRANCHE5B_QUALIFIED_TRACKED_FILES} tracked files",
        "Tranche 5C — invariant validation — NEXT",
    ):
        assert phrase in text

    for stale in (
        "Tranche 5B — configuration composition and explicit manifest — NEXT",
        "Configuration source I/O is separated; composition is the next coupling target",
        "Tranche 5 — configuration boundary — NEXT",
        "`config.py` is now the next coupling target",
        "Tranche 4 — specialist routing by composition — NEXT",
        "specialist_routing.py` remains the next coupling target",
        "inheritance/refinement/preference bridge for Tranche 4",
    ):
        assert stale not in text


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
