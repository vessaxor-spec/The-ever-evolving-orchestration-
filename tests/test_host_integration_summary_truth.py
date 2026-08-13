from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_readme_tracks_latest_host_integration_research_truth() -> None:
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for phrase in (
        "six provider-independent adversarial slices",
        "Reference Implementation CI #580",
        "788 automated tests",
        "509 tracked-file layout checks",
        "verifier-context independence",
        "exact artifact/change-set stale-PASS resistance",
        "host-integration-verifier-artifact-binding-2026-08-12.md",
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


def test_host_integration_roadmap_marks_pr146_gate_satisfied() -> None:
    text = (
        REPO_ROOT / "research" / "roadmaps" / "host-integration-contract.md"
    ).read_text(encoding="utf-8")

    for phrase in (
        "**Verifier-context independence:**",
        "**Artifact-bound verification:**",
        "Satisfied at the non-normative research layer by PR #146 and CI #580.",
        "host-integration-verifier-artifact-binding-2026-08-12.md",
        "Preserve the current Progress Tracker sequencing",
    ):
        assert phrase in text

    assert (
        "especially context economics, dispatch-authorization mutation resistance, adapter integrity, restrictive authority intersection, artifact-bound verification, freshness semantics"
        not in text
    )
