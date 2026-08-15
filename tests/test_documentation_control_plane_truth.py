from pathlib import Path

from teo_reference.config import ConfigBundle


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TEAM_COUNT = 10
EXPECTED_WORKER_COUNT = 84
EXPECTED_SPECIALIST_COUNT = 82
EXPECTED_ACCEPTED_SUBSTANTIVE_TESTS = 657
EXPECTED_ACCEPTED_SUBSTANTIVE_TRACKED_FILES = 477
EXPECTED_ACCEPTED_SUBSTANTIVE_CI_RUN = 514
EXPECTED_CURRENT_VALIDATED_TESTS = 915
EXPECTED_CURRENT_VALIDATED_TRACKED_FILES = 535
EXPECTED_CURRENT_VALIDATED_CI_RUN = 710
EXPECTED_RECONCILIATION_CI_RUN = 602
EXPECTED_RECONCILIATION_TESTS = 802
EXPECTED_RECONCILIATION_TRACKED_FILES = 515
EXPECTED_HOST_INTEGRATION_CI_RUN = 720
EXPECTED_HOST_INTEGRATION_TESTS = 941
EXPECTED_HOST_INTEGRATION_TRACKED_FILES = 539
EXPECTED_MISSION_CONTROL_WORKERS = {
    "orchestration",
    "operations",
    "project_delivery",
    "incident_response",
}


def test_control_plane_roster_matches_current_activation() -> None:
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


def test_team_architecture_readme_matches_executable_roster() -> None:
    text = (REPO_ROOT / "community" / "teams" / "README.md").read_text(
        encoding="utf-8"
    )

    for phrase in (
        "**10 teams**",
        "**84 workers**",
        "**82 specialists**",
        "**4 Mission Control workers**",
    ):
        assert phrase in text

    for worker in EXPECTED_MISSION_CONTROL_WORKERS:
        assert f"`{worker}`" in text

    assert "56 specialist" not in text
    assert "## Core teams" not in text

    specialist_text = (
        REPO_ROOT / "community" / "specialists" / "README.md"
    ).read_text(encoding="utf-8")
    bundle = ConfigBundle.load(REPO_ROOT)

    for phrase in (
        "**10 teams**",
        "**84 workers**",
        "**82 active specialists**",
        "**4 Mission Control workers**",
        "**Total active specialists: 82**",
        "principal-engineering-active.yaml",
        "workforce-expansion-active.yaml",
    ):
        assert phrase in specialist_text

    for specialist in bundle.specialist_registry:
        assert f"]({specialist}.md)" in specialist_text

    assert "**Total specialists:** 56" not in specialist_text
    assert "Description column reproduces" not in specialist_text


def test_root_readme_preserves_current_control_plane_truth() -> None:
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for phrase in (
        "ten active organizational teams",
        "82 preserved specialist role cards",
        "dedicated Mission Control workers for orchestration, operations, project delivery, and incident response",
        "community/specialists/workforce-expansion-active.yaml",
        "Shadow Route Evaluation",
        "Qualified-human approval lifecycle",
        f"{EXPECTED_ACCEPTED_SUBSTANTIVE_TESTS} automated tests",
        f"{EXPECTED_ACCEPTED_SUBSTANTIVE_TRACKED_FILES} tracked-file layout checks",
        f"Reference Implementation CI #{EXPECTED_ACCEPTED_SUBSTANTIVE_CI_RUN}",
        "40 JSON Schema",
        f"{EXPECTED_RECONCILIATION_TESTS} automated tests",
        f"{EXPECTED_RECONCILIATION_TRACKED_FILES} tracked-file layout checks",
        f"CI #{EXPECTED_RECONCILIATION_CI_RUN}",
        f"{EXPECTED_HOST_INTEGRATION_TESTS} automated tests",
        f"{EXPECTED_HOST_INTEGRATION_TRACKED_FILES} tracked-file layout checks",
        f"CI #{EXPECTED_HOST_INTEGRATION_CI_RUN}",
        "brokered conformant process-lifetime",
        "static runtime-wired authority-surface reconciliation",
        "process-lifetime recursion resistance",
        "host-integration-cross-process-authority-2026-08-13.md",
        "host-integration-authority-surface-reconciliation-2026-08-14.md",
        "host-integration-recursion-resistance-2026-08-14.md",
        "host-integration-freshness-binding-2026-08-14.md",
        "host-integration-portfolio-authority-separation-2026-08-15.md",
        "host-integration-assimilation-protocol.md",
        "host-integration-integrated-conformance-assimilation-2026-08-15.md",
        "integrated Fresh-AI assimilation/conformance",
        "Assimilation is not installation",
        "exact local freshness binding",
        "portfolio/task-admission separation",
        "red-canary CI #676",
        "final execution provenance",
        "Task Intent & Action Authority",
        "Execution Environment & Recovery",
        "evidence-governed live execution expansion",
        "now at 65%",
        "`documentation` is the first staged candidate",
        "staged replay harness are validated",
        "provider-backed replay evidence is still pending",
        "no live-execution authority",
        "The next gate is provider-backed controlled documentation replay evidence",
        "control-integrity audit",
        "temporal-causality",
        "Control Integrity remains intentionally scored at 90%",
        "Issue #100",
        "is complete",
    ):
        assert phrase in text

    for worker in EXPECTED_MISSION_CONTROL_WORKERS:
        assert f"`{worker}`" in text

    assert "automated qualified-human approval integration" not in text
    assert "source-backed historical cost attribution" not in text
    assert "route-outcome learning and shadow-route evaluation" not in text

    ai_text = (REPO_ROOT / "AI_INSTRUCTIONS.md").read_text(encoding="utf-8")
    for phrase in (
        "## Fresh-AI assimilation rule",
        "Assimilation is not installation",
        "host-integration-assimilation-protocol.md",
        "embedded_orchestration_control_plane",
        "prove continued use on a later distinct admitted task",
        "without relying on a special `use TEO` reminder",
        "Copied files, installed packages, prompts, skills, one successful demo, or a green test suite do not prove assimilation",
        "cannot by itself prove that a fresh session inherited the integration",
        "Assimilation research never widens live execution by itself",
    ):
        assert phrase in ai_text

    live_spec = (
        REPO_ROOT / "docs" / "specification" / "live-independent-verification.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "Primary bounded route:\n\n```text\nGemini 3.5 Flash-Lite execution\n  -> Claude Sonnet 5 verification\n```",
        "Model-specific fallback after Gemini 3.5 Flash-Lite is blocked while Anthropic remains eligible:\n\n```text\nClaude Haiku 4.5 execution\n  -> Gemini 3.6 Flash verification\n```",
        "Google provider-family failure:\n\n```text\nClaude Haiku 4.5 execution\n  -> GPT-5.6 Sol verification\n```",
        "The live verifier does not choose these routes. Routing recomputes eligibility and records the assignment before verification executes.",
    ):
        assert phrase in live_spec

    for stale in (
        "Primary bounded route:\n\n```text\nClaude Haiku 4.5 execution\n  -> Gemini 3.6 Flash verification\n```",
        "Model-specific fallback to Gemini while Anthropic remains eligible:\n\n```text\nGemini 3.6 Flash execution\n  -> Claude Sonnet 5 verification\n```",
        "Anthropic provider-family failure:\n\n```text\nGemini 3.6 Flash execution\n  -> GPT-5.6 Sol verification\n```",
    ):
        assert stale not in live_spec


def test_progress_tracker_matches_executable_roster_and_current_priority() -> None:
    text = (
        REPO_ROOT / "docs" / "stewardship" / "progress-tracker.md"
    ).read_text(encoding="utf-8")

    for phrase in (
        "| Organizational teams | 10 |",
        "| Workers | 84 |",
        "| Active specialists | 82 |",
        "| Mission Control workers | 4 |",
        f"| Current validated scale | {EXPECTED_CURRENT_VALIDATED_TESTS} tests passed, {EXPECTED_CURRENT_VALIDATED_TRACKED_FILES} tracked-file layout checks, 41 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse artifact-bound end-to-end pass; established by CI #{EXPECTED_CURRENT_VALIDATED_CI_RUN} |",
        f"CI #{EXPECTED_RECONCILIATION_CI_RUN}: {EXPECTED_RECONCILIATION_TESTS} tests, {EXPECTED_RECONCILIATION_TRACKED_FILES} tracked-file layout checks",
        f"CI #{EXPECTED_HOST_INTEGRATION_CI_RUN}: {EXPECTED_HOST_INTEGRATION_TESTS} tests, {EXPECTED_HOST_INTEGRATION_TRACKED_FILES} tracked-file layout checks",
        "restrictive host/TEO authority intersection and host execution-scope binding",
        "exact host execution-envelope integrity",
        "verifier-context independence",
        "exact artifact/change-set stale-PASS resistance",
        "brokered conformant process-lifetime cross-process authority/replay resistance",
        "static runtime-wired authority-surface reconciliation",
        "process-lifetime recursion-resistance",
        "exact local freshness-binding",
        "portfolio/task-admission authority-separation",
        "Dynamic executable-hook discovery",
        "Artifact-bound finalization",
        "Task 002 is now closed as a scoped normative remediation",
        "2026-08-14-external-verifier-assessment-artifact-bound-finalization.md",
        "Final execution provenance",
        "Task Intent & Action Authority Contract",
        "Execution Environment & Recovery Contract",
        "host-integration-execution-envelope-integrity-2026-08-12.md",
        "host-integration-verifier-artifact-binding-2026-08-12.md",
        "host-integration-cross-process-authority-2026-08-13.md",
        "host-integration-authority-surface-reconciliation-2026-08-14.md",
        "host-integration-recursion-resistance-2026-08-14.md",
        "host-integration-freshness-binding-2026-08-14.md",
        "host-integration-portfolio-authority-separation-2026-08-15.md",
        "host-integration-assimilation-protocol.md",
        "host-integration-integrated-conformance-assimilation-2026-08-15.md",
        "process-local integrated Fresh-AI assimilation/conformance",
        "assimilation is not installation",
        "two distinct task IDs",
        "| Staged live-scope candidate | `documentation`, evaluation only, not authorized for live execution |",
        "| Control integrity | Operational | 90% |",
        "| Regulated specialist evidence pilot | In progress | 70% |",
        "| Route-outcome evidence | Complete | 100% |",
        "| Benchmark and Outcome Lab | Complete | 100% |",
        "| Source-backed cost attribution | Complete | 100% |",
        "| Shadow route evaluation | Complete | 100% |",
        "| Qualified-human approval lifecycle | Complete | 100% |",
        "| Live execution expansion | In progress | 65% |",
        "`documentation` staged replay harness and operator evidence path validated",
        "Produce provider-backed controlled documentation replay evidence",
        "Formal refresh cycle 1",
        "1 of 2 required formal refresh cycles",
        "30-day scheduled authority-resolution stability",
        "expansion remains unauthorized",
        "## NOW",
        "### Evidence-governed live execution expansion",
        "`documentation` is the first bounded candidate",
        "staged only",
        "The staged documentation replay harness is now implemented",
        "The next material gate is a real provider-backed controlled replay",
        "provider-backed `documentation` replay is intentionally deferred as an open action item",
        "control-integrity audit",
        "temporal-causality",
        "targeted mutation audit",
        "10 of 10 targeted mutants",
        "Control integrity remains intentionally scored at 90%",
        "21-case matrix",
        "Reference Implementation CI #577 passed 788 tests and 509 tracked-file layout checks",
        "canonical `VerificationResult` and `FinalOutcome` schemas remained unchanged",
        "later route-backed final execution provenance change was a separate compatible extension",
        "Reference Implementation CI #626 with **817 tests**, **520 tracked-file layout checks**",
        "CI #643 intentionally failed **2 tests while 840 passed**",
        "Exact corrected head `9cc5694474d310bc50bac1aa342b61f45fb17e10` then passed CI #644",
        "Reference Implementation CI #658 passed **863 tests**, **528 tracked-file layout checks**",
        "Red-canary CI #676",
        "Corrected Reference Implementation CI #678 passed **891 tests**, **532 tracked-file layout checks**",
        "Initial CI #696 preserved a test-assumption canary with **913 passed and 1 failed**",
        "Clean corrected Reference Implementation CI #703 passed **915 tests**, **535 tracked-file layout checks**",
        "production-grade remote or distributed dispatch/exact-action authenticity and replay",
        "## NEXT",
        "No additional workstream is promoted",
        "## LATER",
        "next bounded provider-independent Host Integration gate should be selected from the remaining roadmap evidence",
    ):
        assert phrase in text

    now_section = text.split("## NOW", 1)[1].split("## NEXT", 1)[0]
    next_section = text.split("## NEXT", 1)[1].split("## LATER", 1)[0]
    assert "### Qualified-human approval lifecycle" not in now_section
    assert "### Evidence-governed live execution expansion" in now_section
    assert "do not authorize high or critical live execution" in now_section
    assert "High and critical live execution remains unauthorized" in now_section
    assert "former `runtime-worker-overrides.yaml` behavior" in text
    assert "GPT-5.6 Sol as the provider-diverse non-preview routine fallback" in now_section
    assert "Gemini 3.6 Flash as the fresh provider-diverse verifier" in now_section
    assert "Existing canary wrappers and live-verification task scope remain `high_volume_simple` only" in now_section
    assert "CI uses deterministic fake provider transports" in now_section
    assert "controlled_replay` evidence pointer" in now_section
    assert "No additional workstream is promoted" in next_section
    assert "provider-backed controlled `documentation` replay" in next_section
    assert "Direct outcome-to-self-modifying-routing authority" in text
    assert "Reference Implementation CI run #488" in text
    assert f"Reference Implementation CI run #{EXPECTED_ACCEPTED_SUBSTANTIVE_CI_RUN}" in text
    assert f"{EXPECTED_ACCEPTED_SUBSTANTIVE_TRACKED_FILES} tracked-file layout checks" in text
    assert "78 active specialists" not in text

    benchmark_spec = (
        REPO_ROOT / "docs" / "specification" / "benchmark-outcome-lab.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "completed current milestone",
        "## Multi-verifier disagreement",
        "canonical runtime verifier override: false",
        "## Consequential evaluation conclusions",
        "mission_control_or_maintainer_review",
        "qualified_human_approval_satisfied: false",
        "Reference Implementation CI #429",
    ):
        assert phrase in benchmark_spec
    assert "Two material gates remain" not in benchmark_spec
    assert "does not yet execute or join multiple independent benchmark-verifier observations" not in benchmark_spec

    benchmark_source = (
        REPO_ROOT
        / "reference"
        / "implementations"
        / "python"
        / "src"
        / "teo_reference"
        / "benchmark_lab.py"
    ).read_text(encoding="utf-8")
    assert "Multi-verifier disagreement measurement and live replay execution are not yet implemented." not in benchmark_source
    assert "but does not yet run or join multiple independent benchmark verifier observations." not in benchmark_source
    assert "This report has not been enriched with a declared multi-verifier" in benchmark_source
    assert "Controlled live replay and multi-verifier observation collection are separate executable layers." in benchmark_source

    cost_spec = (
        REPO_ROOT / "docs" / "specification" / "source-backed-cost-attribution.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "A model identity is not a bill.",
        "explicit billable surface",
        "Pricing records are append-only evidence.",
        "every primary attempt;",
        "every retry attempt;",
        "every fallback attempt;",
        "An unperformed verifier is the only case where zero is semantically asserted",
        "Cost is one evaluation dimension",
    ):
        assert phrase in cost_spec

    shadow_spec = (
        REPO_ROOT / "docs" / "specification" / "shadow-route-evaluation.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "Shadow evaluation is a post-run analytical layer",
        "A specialist name is not enough to establish independence.",
        "SHADOW_CHANGE_CANDIDATE",
        "Lower source-backed cost can support a recommendation, but lower cost alone can never create",
        "policy_write_authority",
        "A shadow recommendation does not advance directly to Mission Control review.",
        "mission_control_or_maintainer_review",
        "Direct outcome-to-self-modifying-routing authority is outside TEO's design.",
    ):
        assert phrase in shadow_spec

    qualified_human_spec = (
        REPO_ROOT / "docs" / "specification" / "qualified-human-approval-lifecycle.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "complete at its current declared milestone",
        "A model-verification result cannot satisfy a qualified-human approval requirement.",
        "qualified_human_authority_grant",
        "actor_type: human",
        "Maintainer status by itself is not approval authority.",
        "The original Route-Outcome Evidence remains immutable.",
        "request -> disposition -> finalization temporal causality",
        "model selection;",
        "provider access or authentication method;",
        "billing identity;",
        "Reference Implementation CI #451",
    ):
        assert phrase in qualified_human_spec


def test_roadmap_links_progress_tracker_and_preserves_current_roster_truth() -> None:
    text = (REPO_ROOT / "docs" / "stewardship" / "roadmap.md").read_text(
        encoding="utf-8"
    )

    assert "[`progress-tracker.md`](progress-tracker.md)" in text
    assert "82 active preserved specialist role cards" in text
    assert "prove all 82 active specialists are deterministically spawnable" in text
    assert "`documentation` is the first staged candidate" in text
    assert "live activation is not authorized" in text
    assert "provider-diverse non-preview routine fallback: GPT-5.6 Sol" in text
    assert "fresh redispatch verifier: Gemini 3.6 Flash" in text
    assert "staged replay harness are complete" in text
    assert "The next evidence gate is **provider-backed controlled documentation replay**" in text
    assert "CI conformance with deterministic fake transports does not count as empirical provider-backed evidence" in text
    assert "remains the only accepted live execution scope" in text
    assert "78 preserved specialist" not in text
    assert "78 active specialists" not in text
