from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPECIALISTS = ROOT / "community" / "specialists"
POLICY = ROOT / "policy" / "specialists" / "freshness.yaml"


def cards() -> list[Path]:
    registry = yaml.safe_load((SPECIALISTS / "specialists.yaml").read_text(encoding="utf-8"))
    return sorted(ROOT / entry["role_card"] for entry in registry["specialists"].values())


def frontmatter(path: Path) -> dict[str, object]:
    return yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])


def search_block(raw: str) -> str:
    marker = "### What to Search For"
    if marker not in raw:
        return ""
    block = raw.split(marker, 1)[1]
    match = re.search(r"\n### |\n## ", block)
    return block[: match.start()] if match else block


def test_every_specialist_declares_freshness_metadata() -> None:
    roster = cards()
    assert len(roster) == 56
    for card in roster:
        metadata = frontmatter(card)
        assert metadata["freshness_policy"] == "live-verification-required"
        verified = metadata["tools_last_verified"]
        if isinstance(verified, str):
            verified = dt.date.fromisoformat(verified)
        assert isinstance(verified, dt.date)


def test_search_templates_do_not_freeze_authoring_year() -> None:
    for card in cards():
        block = search_block(card.read_text(encoding="utf-8"))
        assert "2025" not in block, card.name
        assert "2026" not in block, card.name


def test_corrected_categories_use_existing_taxonomy() -> None:
    assert frontmatter(SPECIALISTS / "incident-commander.md")["category"] == "governance"
    assert frontmatter(SPECIALISTS / "workflow-optimizer.md")["category"] == "engineering-core"
    assert frontmatter(SPECIALISTS / "spatial-terminal.md")["category"] == "engineering-specialized"


def test_known_false_or_retired_instructions_are_absent() -> None:
    combined = "\n".join(card.read_text(encoding="utf-8") for card in cards())
    banned = [
        "Replies worth 150x likes",
        "Third-party cookie deprecation is complete",
        "Google's Privacy Sandbox (Topics API)",
        "## A9/A10 Algorithm Factors",
        "commonly called A10",
        "| SLSA 4 |",
        "Airflow SLA callbacks",
        "FIA: Fit/Impact/Authority",
        "  - async-std",
        "`async-std`:",
        "packed_simd",
    ]
    for phrase in banned:
        assert phrase not in combined, phrase

    image_prompt = (SPECIALISTS / "image-prompt-engineer.md").read_text(encoding="utf-8")
    assert "Never use or document `--iref`" in image_prompt
    assert "| `--iref" not in image_prompt


def test_freshness_policy_has_required_controls() -> None:
    policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    assert policy["principles"]["durable_doctrine"]
    assert policy["principles"]["volatile_facts"]
    assert policy["source_authority"][0]["tier"] == 1
    assert policy["failure_behavior"]["unavailable_current_evidence"] == "do_not_assert_volatile_fact"
