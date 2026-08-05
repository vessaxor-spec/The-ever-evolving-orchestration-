from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECIALISTS = ROOT / "community" / "specialists"


def text(name: str) -> str:
    return (SPECIALISTS / name).read_text(encoding="utf-8")


def test_civil_engineering_selects_governing_edition() -> None:
    card = text("civil-engineer.md")
    assert "## Governing Code and Edition Protocol" in card
    assert "Adopted edition" in card
    assert "Latest published edition" in card
    assert "ACI 318-14 vs 318-19" not in card
    assert "Eurocode 2004 vs 2023 amendments" not in card


def test_embedded_misra_is_edition_aware() -> None:
    card = text("embedded-engineer.md")
    assert "## MISRA Compliance Declaration" in card
    assert "Do not default to MISRA C:2012" in card
    assert "MISRA C: 2012 — Compliance Level" not in card


def test_ux_uses_wcag_22_baseline() -> None:
    card = text("ux-designer.md")
    assert "## Accessibility Standard Applicability" in card
    assert "WCAG 2.2 AA" in card
    assert "WCAG 2.1 AA" not in card


def test_tax_covers_current_regimes_without_universal_thresholds() -> None:
    card = text("tax-strategist.md")
    assert "## Current International Tax Regime Verification" in card
    assert "## Pillar Two / Global Minimum Tax Applicability" in card
    assert "Do not use `$750M` as a universal threshold" in card
    assert "CbCR threshold: **$750M" not in card


def test_ai_compliance_has_current_governance_lane() -> None:
    card = text("compliance-auditor.md")
    assert "## AI Governance Applicability Protocol" in card
    assert "EU AI Act" in card
    assert "ISO/IEC 42001" in card
    assert "NIST AI RMF" in card
    assert "Annex III" in card
    assert "AI embedded in regulated products" in card
    assert "Verify the current Commission timeline" in card


def test_cbam_is_scoped_not_universal() -> None:
    card = text("supply-chain-strategist.md")
    assert "## EU CBAM Applicability Check" in card
    assert "CBAM does not apply to every EU-bound product" in card
    assert "50-tonne" in card


def test_lending_does_not_use_43_percent_as_universal_cutoff() -> None:
    card = text("loan-officer-assistant.md")
    assert "## Loan Program Eligibility and Cost Protocol" in card
    assert "General QM definition no longer uses a universal 43% DTI ceiling" in card
    assert "back-end ≤43%" not in card
    assert "do not disqualify a borrower solely because back-end DTI exceeds 43%" in card


def test_real_estate_has_buyer_agreement_and_mls_rules() -> None:
    card = text("real-estate-agent.md")
    assert "## Buyer Representation and MLS Compensation Protocol" in card
    assert "written buyer agreement before an in-person or live-virtual tour" in card
    assert "offers of buyer-broker compensation in the MLS" in card


def test_security_requires_authorization_and_sec_applicability() -> None:
    card = text("security-engineer.md")
    assert "## Authorization and Scope Gate" in card
    assert "documented asset-owner authorization" in card
    assert "Form 8-K Item 1.05" in card
    assert "four business days" in card
