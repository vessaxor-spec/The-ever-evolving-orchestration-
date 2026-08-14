from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_readme_tracks_latest_host_integration_research_truth() -> None:
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for phrase in (
        "ten provider-independent adversarial slices",
        "Reference Implementation CI #678",
        "891 automated tests",
        "532 tracked-file layout checks",
        "brokered conformant process-lifetime cross-process authority/replay",
        "static runtime-wired authority-surface reconciliation",
        "verifier-context independence",
        "exact artifact/change-set stale-PASS resistance",
        "host-integration-verifier-artifact-binding-2026-08-12.md",
        "host-integration-cross-process-authority-2026-08-13.md",
        "host-integration-authority-surface-reconciliation-2026-08-14.md",
        "host-integration-recursion-resistance-2026-08-14.md",
        "host-integration-freshness-binding-2026-08-14.md",
        "process-lifetime recursion resistance",
        "exact local freshness binding",
        "red-canary CI #676",
        "The next gate is provider-backed controlled documentation replay evidence",
    ):
        assert phrase in text

    assert (
        "The next bounded provider-independent adversarial gate is **verifier-context independence plus exact artifact/change-set verification and stale-PASS resistance**."
        not in text
    )
    assert (
        "Remaining promotion evidence includes production and distributed authenticity/provenance controls, provider/model economics and task-adherence evidence, verifier-context independence, exact artifact/change-set verification and stale-PASS resistance"
        not in text
    )
    assert "nine provider-independent adversarial slices" not in text
    assert "eight provider-independent adversarial slices" not in text
    assert "seven provider-independent adversarial slices" not in text


def test_host_integration_roadmap_tracks_current_satisfied_gates() -> None:
    text = (
        REPO_ROOT / "research" / "roadmaps" / "host-integration-contract.md"
    ).read_text(encoding="utf-8")

    for phrase in (
        "**Verifier-context independence:**",
        "**Artifact-bound verification:**",
        "Satisfied at the non-normative research layer by PR #146 and CI #580.",
        "Brokered cross-process authority/replay",
        "Conformant process-lifetime slice satisfied",
        "Authority-surface reconciliation",
        "Static runtime-wired slice satisfied",
        "CI #644",
        "Recursion resistance",
        "Process-lifetime slice satisfied",
        "CI #658",
        "Freshness binding",
        "Exact local classification slice satisfied",
        "CI #678",
        "host-integration-verifier-artifact-binding-2026-08-12.md",
        "host-integration-cross-process-authority-2026-08-13.md",
        "host-integration-authority-surface-reconciliation-2026-08-14.md",
        "host-integration-recursion-resistance-2026-08-14.md",
        "host-integration-freshness-binding-2026-08-14.md",
        "dynamic executable hooks/plugins/transitive code remain open",
    ):
        assert phrase in text

    assert (
        "especially context economics, dispatch-authorization mutation resistance, adapter integrity, restrictive authority intersection, artifact-bound verification, freshness semantics"
        not in text
    )
    assert "Authority-surface reconciliation:** derive or reconcile authority surfaces against executable runtime wiring and fail on omissions. **Open.**" not in text
    assert "Recursion resistance:** mutation-test delegation-depth, spawn-budget, and recovery/re-entry boundaries. **Open.**" not in text
    assert "Registry freshness:** prove stale or mismatched TEO release, policy, registry, overlay, or executable-composition bindings are detected. **Open.**" not in text
    assert "Integration freshness state:** distinguish current, compatible, update-available, unsupported, and mismatched TEO pins/vendorized copies. **Open.**" not in text
