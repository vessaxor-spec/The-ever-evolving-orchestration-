from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECIALISTS = ROOT / "community" / "specialists"


def text(name: str) -> str:
    return (SPECIALISTS / name).read_text(encoding="utf-8")


def test_seo_supports_ai_features_without_secret_formula() -> None:
    card = text("seo-specialist.md")
    assert "## AI-Mediated Search Visibility" in card
    assert "AI Overviews and AI Mode do not require a separate technical optimization layer" in card
    assert "no invented AI-specific schema" in card
    assert "KD > 40" not in card
    assert ">80% coverage" not in card
    assert "positions 2-10" not in card


def test_paid_search_governs_ai_max_and_removes_fixed_qs_formula() -> None:
    card = text("paid-search-strategist.md")
    assert "## AI Max for Search Governance" in card
    assert "broad and keywordless technology" in card
    assert "final URL expansion" in card
    assert "fixed component weights" in card
    assert "Expected CTR** | ~40%" not in card
    assert "QS of 10 vs. 4" not in card
    assert ">300 conversions/month" not in card
    assert "25 search themes per asset group" not in card


def test_paid_social_uses_retrieval_and_automation_model() -> None:
    card = text("paid-social-strategist.md")
    assert "## AI-Mediated Delivery and Creative Retrieval" in card
    assert "Meta Andromeda is a retrieval system" in card
    assert "Advantage+ sales" in card
    assert "Performance Max asset group strategy" not in card
    assert "up to 8 conversion events" not in card
    assert "frequency > 3.0" not in card.lower()
    assert "CTR (link clicks / impressions): >1.5%" not in card


def test_ecommerce_supports_conversational_and_agentic_discovery() -> None:
    card = text("cross-border-ecommerce.md")
    assert "## AI-Mediated Marketplace Discovery" in card
    assert "renamed Alexa for Shopping" in card
    assert "retrieval-augmented generation" in card
    assert "Do not claim a direct optimization switch or ranking formula" in card
    assert "Amazon US, 2025-2026 rates" not in card
    assert "$3.22–$6.92" not in card
    assert "Minimum acceptable net margin" not in card
    assert "Target 1-3 organic reviews per week" not in card


def test_refresh_is_documented_as_one_systemic_theme() -> None:
    historical_record = (
        ROOT / "docs" / "history" / "audits" / "ai-mediated-discovery-refresh-2026-08-05.md"
    ).read_text(encoding="utf-8")
    for name in ["Google Search Central", "Google Ads Help", "Meta Engineering", "Amazon Science"]:
        assert name in historical_record
