import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECIALISTS = ROOT / "community" / "specialists"


def text(name: str) -> str:
    return (SPECIALISTS / name).read_text(encoding="utf-8")


def test_researcher_has_domain_evidence_depth() -> None:
    card = text("researcher.md")
    assert "Consolidates and preserves the durable methods" in card
    assert "## Domain Activation and Minimum Evidence" in card
    for heading in [
        "### History",
        "### Anthropology",
        "### Geography",
        "### Psychology",
        "### Narratology",
        "### Market Research",
        "### Investment Research",
        "### General / New Domain",
    ]:
        assert heading in card
    assert "## Cross-Domain Claim Ledger" in card
    assert "Three URLs repeating one original source are not triangulation" in card
    assert "Replaces all 7 original" not in card


def test_data_analyst_has_high_risk_model_qa_protocol() -> None:
    card = text("data-analyst.md")
    assert "## ML Model QA and Responsible Analytics Protocol" in card
    for phrase in [
        "Data Reconstruction and Leakage",
        "Fairness and Harmful-Bias Evaluation",
        "equalized odds",
        "calibration by group",
        "intersectional slice",
        "CONDITIONAL GO",
        "RESEARCH ONLY",
    ]:
        assert phrase in card
    assert "Does not treat removal of protected attributes as proof" in card
    assert "A random row split is rejected" in card
    assert "no universal disparity threshold" in card


def test_devsecops_examples_follow_full_sha_policy() -> None:
    card = text("devsecops-engineer.md")
    assert "## Third-Party CI Action Trust and Pinning" in card
    assert "<verified-full-commit-sha>" in card
    assert not re.search(r"uses:\s+[^\n]+@v\d", card)
    assert "Fixed 30-, 90-, or annual rotation intervals are not universal" in card
    assert "retained for 90 days minimum" not in card


def test_red_team_regulated_tlpt_is_applicability_based() -> None:
    card = text("red-team-advisor.md")
    assert "## Regulated TLPT Applicability" in card
    assert "DORA TLPT" in card
    assert "TIBER-EU" in card
    assert "CBEST" in card
    assert "STAR-FS" in card
    assert "authorized technique description or approved procedure reference" in card
    assert "Red action: [exact command or action]" not in card
    assert "does not provide payload or evasion design" in card


def test_blockchain_security_thresholds_are_risk_derived() -> None:
    card = text("blockchain-engineer.md")
    assert "## Toolchain and Dependency Compatibility Gate" in card
    assert "Coverage is necessary but not sufficient" in card
    assert "do not use a universal 30-minute minimum" in card
    assert "Do not use a fixed `$1M TVL` threshold" in card
    assert "Minimum acceptable optimization: 10%" not in card
    assert "no unresolved Critical/High issue remains" in card


def test_security_lane_retains_authorization_and_containment() -> None:
    security = text("security-engineer.md")
    malware = text("malware-analyst.md")
    red_team = text("red-team-advisor.md")
    devsecops = text("devsecops-engineer.md")
    blockchain = text("blockchain-engineer.md")

    assert "Requires documented asset-owner authorization" in security
    assert "Without authorization and scope, limit work to passive review" in security
    assert "No live malware execution" in malware
    assert "isolated sandbox" in malware
    assert "Authorization chain" in red_team
    assert "Pipeline changes are advisory" in devsecops
    assert "explicit operator confirmation before execution" in blockchain
