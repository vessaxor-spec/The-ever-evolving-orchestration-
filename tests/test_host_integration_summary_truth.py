from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_readme_tracks_latest_host_integration_research_truth() -> None:
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for phrase in (
        "seven provider-independent adversarial slices",
        "Reference Implementation CI #626",
        "817 automated tests",
        "520 tracked-file layout checks",
        "brokered conformant process-lifetime cross-process authority/replay",
        "verifier-context independence",
        "exact artifact/change-set stale-PASS resistance",
        "host-integration-verifier-artifact-binding-2026-08-12.md",
        "host-integration-cross-process-authority-2026-08-13.md",
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
        "CI #626",
        "host-integration-verifier-artifact-binding-2026-08-12.md",
        "host-integration-cross-process-authority-2026-08-13.md",
        "Preserve the current Progress Tracker sequencing",
    ):
        assert phrase in text

    assert (
        "especially context economics, dispatch-authorization mutation resistance, adapter integrity, restrictive authority intersection, artifact-bound verification, freshness semantics"
        not in text
    )
