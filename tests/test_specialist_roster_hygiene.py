from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPECIALISTS = ROOT / "community" / "specialists"


def text(name: str) -> str:
    return (SPECIALISTS / name).read_text(encoding="utf-8")


def frontmatter(name: str) -> str:
    return text(name).split("---", 2)[1]


def test_corrected_specialist_categories() -> None:
    assert "category: operations" in frontmatter("incident-commander.md")
    assert "category: automation" in frontmatter("workflow-optimizer.md")
    assert "category: testing" in frontmatter("qa-engineer.md")


def test_xr_and_terminal_ownership_is_explicitly_split() -> None:
    xr = text("xr-developer.md")
    terminal = text("spatial-terminal.md")

    assert "routes those to **spatial-terminal**" in xr
    assert "Retains Swift CLI tooling, process spawning" in xr
    assert "routes those to **xr-developer**" in terminal
    assert "Owns terminal emulation, PTY/view integration" in terminal


def test_social_strategy_has_no_dangling_influencer_specialist() -> None:
    social = text("social-media-strategist.md")

    assert "influencer-strategist" not in social
    assert "Owns platform-specific creator and influencer partnership mechanics directly" in social


def test_zettelkasten_steward_slug_remains_stable() -> None:
    steward = text("zk-steward.md")

    assert "name: zk-steward" in steward
    assert "Zettelkasten" in steward
