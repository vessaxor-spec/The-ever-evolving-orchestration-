from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECIALISTS = ROOT / "community" / "specialists"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    file = ROOT / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match in {path}: {old!r}; found {count}")
    write(path, text.replace(old, new, 1))


def replace_between(path: str, start: str, end: str, replacement: str) -> None:
    text = read(path)
    if text.count(start) != 1 or text.count(end) != 1:
        raise SystemExit(f"Expected one section boundary in {path}: {start!r} -> {end!r}")
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    write(path, before + replacement.rstrip() + "\n\n" + end + after)


def registry_cards() -> list[Path]:
    paths = [
        ROOT / line.strip().split(": ", 1)[1]
        for line in read("community/specialists/specialists.yaml").splitlines()
        if line.strip().startswith("role_card: ")
    ]
    if len(paths) != 56 or len(set(paths)) != 56:
        raise SystemExit(f"Expected 56 unique registry role cards, found {len(paths)}")
    return sorted(paths)


for card in registry_cards():
    text = card.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit(f"Missing frontmatter: {card}")
    frontmatter, body = text[4:].split("\n---\n", 1)
    lines = frontmatter.splitlines()
    if not any(line.startswith("freshness_policy:") for line in lines):
        lines.append("freshness_policy: live-verification-required")
    if not any(line.startswith("tools_last_verified:") for line in lines):
        lines.append("tools_last_verified: 2026-08-05")
    text = f"---\n{'\n'.join(lines)}\n---\n{body}"

    marker = "### What to Search For"
    if marker in text:
        before, remainder = text.split(marker, 1)
        next_heading = re.search(r"\n### |\n## ", remainder)
        if next_heading:
            query_block = remainder[: next_heading.start()]
            after = remainder[next_heading.start() :]
        else:
            query_block, after = remainder, ""
        query_block = re.sub(r"\b(?:2025|2026)\b", "{current_year}", query_block)
        text = before + marker + query_block + after

    card.write_text(text, encoding="utf-8")

replace_once("community/specialists/incident-commander.md", "category: operations", "category: governance")
replace_once("community/specialists/workflow-optimizer.md", "category: automation", "category: engineering-core")
replace_once("community/specialists/spatial-terminal.md", "category: design", "category: engineering-specialized")

replace_between(
    "community/specialists/image-prompt-engineer.md",
    "## Style Reference vs Image Reference (Midjourney)",
    "## Prompt Injection Prevention",
    """## Midjourney Reference Controls

Midjourney parameters and version compatibility are volatile vendor facts. Verify the current official parameter list before recommending or generating production prompts.

As of the card's `tools_last_verified` date:

- `--sref` applies a style reference; `--sw` controls style-reference weight.
- Midjourney V7 uses Omni Reference through `--oref`; `--ow` controls its weight.
- Older V6 workflows may use Character Reference through `--cref`; verify compatibility before use.

Rules:

- Never use or document `--iref`; it is not an official Midjourney parameter.
- Treat parameter names, versions, weights, limits, and incompatibilities as live facts.
- Use official Midjourney documentation as the primary source.
- Record the verified version and parameter set in reusable prompt-library entries.
- If official documentation cannot be checked, describe the intended behavior without asserting a parameter name.""",
)

replace_once(
    "community/specialists/social-media-strategist.md",
    "- **Replies worth 150x likes:** Algorithm heavily weights conversations. High-reply posts get exponentially more distribution.",
    "- **Replies are a positive conversation signal:** exact ranking weights are not treated as public or stable. Verify current official platform documentation or public code before quantifying influence.",
)
replace_between(
    "community/specialists/social-media-strategist.md",
    "## 2026 Platform Research Sources",
    "## Example Tasks",
    """## Source Authority Standard

Platform algorithms, monetization terms, ranking weights, product capabilities, and benchmark statistics are highly volatile. Verify them for the target platform and task date before use.

Use this evidence order:

1. Official platform documentation, policy centers, release notes, transparency reports, or publicly released code.
2. Original measurement studies with disclosed methods and dates.
3. Reputable industry analysis that links to primary evidence.
4. Secondary summaries only as discovery leads.
5. SEO, affiliate, or AI-generated content farms must never be the sole support for a quantitative claim.

Do not present an exact algorithm weight unless the platform has published it and it remains current. Label opaque behavior as inferred, record evidence dates and methods, and state uncertainty when current evidence cannot be verified.""",
)

replace_between(
    "community/specialists/programmatic-buyer.md",
    "## Cookieless Targeting Readiness",
    "## Brand Safety Tier Classification",
    """## Signal and Privacy Readiness

Browser privacy controls, third-party-cookie availability, identity products, consent requirements, and advertising APIs are highly volatile. Verify the current status for the target browser, geography, DSP, SSP, and campaign date before recommending activation.

**Durable targeting stack:**

| Layer | Method | Readiness action |
|---|---|---|
| First-party data | consented CRM, conversion, and customer-match data | Audit lawful collection, consent, normalization, and match quality |
| Contextual targeting | content category, topic, placement, and semantic context | Validate inventory quality without depending on cross-site identity |
| Publisher and identity signals | publisher audiences or supported identity solutions | Verify platform support, contracts, match rates, and privacy obligations |
| Modeled measurement | modeled conversions, incrementality, and aggregate reporting | Document assumptions, uncertainty, and platform limitations |

Rules:

- Do not state that third-party-cookie deprecation is complete without verifying current browser policy.
- Do not instruct users to enable Topics, Protected Audience, Attribution Reporting, or another Privacy Sandbox API without checking Google's official feature-status page and the target DSP's current support.
- Retired, deprecated, experimental, or unavailable APIs must not appear as required activation steps.
- Prefer first-party data quality, contextual relevance, consented publisher signals, experiments, and incrementality over dependence on one identity mechanism.
- State the verification date and source for browser or advertising-platform privacy capabilities.""",
)

replace_between(
    "community/specialists/cross-border-ecommerce.md",
    "## A9/A10 Algorithm Factors (2026)",
    "## FBA Fee Structure Awareness",
    """## Amazon Discovery and Ranking Systems

Do not name an unofficial `A10` algorithm as an Amazon product or specification. Amazon discovery can involve retrieval, ranking, recommendations, advertising, semantic understanding, and conversational shopping systems without one stable public weighting model.

**Durable optimization factors:**

| Factor | Why it matters | Optimization action |
|---|---|---|
| Query and product relevance | Helps systems understand when the product satisfies a need | Use accurate titles, attributes, taxonomy, structured data, and natural-language descriptions |
| Conversion and customer value | Useful listings and strong offers improve purchase outcomes | Improve imagery, detail pages, reviews, price, availability, and fulfillment reliability |
| Sales and availability signals | Consistent demand and stock support discoverability | Plan inventory, launches, promotions, and replenishment without manipulating reviews |
| Customer experience | Returns, defects, delivery, and account health affect performance | Monitor product quality, fulfillment, policy compliance, and post-purchase outcomes |
| Advertising and external demand | Paid and external traffic can create demand but do not guarantee rank | Measure incrementality and conversion instead of asserting a fixed ranking boost |

Verify current Amazon documentation, Seller Central guidance, release notes, and marketplace behavior before asserting system names or ranking weights. Treat external ranking observations as hypotheses unless Amazon confirms them.""",
)

replace_once(
    "community/specialists/devsecops-engineer.md",
    """**SLSA level targets:**
| Level | Requirements | When to target |
|---|---|---|
| SLSA 1 | Provenance generated | Minimum for any project |
| SLSA 2 | Hosted build, signed provenance | Default target for production projects |
| SLSA 3 | Hardened build, non-falsifiable provenance | Security-sensitive or regulated projects |
| SLSA 4 | Two-party review, hermetic build | Critical infrastructure |""",
    """**SLSA track targets:**
| Track / level | Requirements | When to target |
|---|---|---|
| Build L1 | Build provenance exists | Minimum for distributed artifacts |
| Build L2 | Signed provenance from a hosted build platform | Default intermediate target for production projects |
| Build L3 | Hardened build platform with strong tamper resistance | Security-sensitive, regulated, or broadly distributed releases |
| Source track | Version control, preserved history, provenance, enforced controls, and review according to the selected level | Apply where source-governance assurance is required |

SLSA is versioned and track-based. Verify the current official specification before claiming a level; do not use the retired pre-1.0 single-track `SLSA 4` model.""",
)

replace_once(
    "community/specialists/sales-engineer.md",
    "- Applying stable technical discovery frameworks (FIA: Fit/Impact/Authority)",
    "- Applying stable technical discovery frameworks and the card's Feature-Impact-Advantage battlecard format",
)

replace_once("community/specialists/rust-engineer.md", "  - async-std\n", "")
replace_once(
    "community/specialists/rust-engineer.md",
    "- Async Rust: tokio, async-std, runtime selection, executor design, cancellation safety",
    "- Async Rust: tokio, smol, runtime selection, executor design, cancellation safety",
)
replace_once(
    "community/specialists/rust-engineer.md",
    "- `async-std`: simpler API, good for smaller projects; less ecosystem support than tokio\n",
    "",
)
replace_once(
    "community/specialists/rust-engineer.md",
    "- SIMD: use `std::simd` (nightly) or `packed_simd` / `wide` for data-parallel operations",
    "- SIMD: verify current stable support; prefer maintained libraries such as `wide`, or `std::simd` only when its toolchain status is appropriate for the project",
)

replace_once(
    "community/specialists/data-engineer.md",
    "Set Airflow SLA callbacks for freshness breaches. Alert on Slack/PagerDuty. Do not set SLAs you cannot measure — an unmeasured SLA is a false promise.",
    "Implement freshness alerting using the mechanism supported by the installed orchestrator version. In Airflow 3.1+, evaluate Deadline Alerts and document their different firing semantics; in Airflow 3.0 or other environments, use task callbacks or external monitoring. Do not generate legacy SLA-callback code for Airflow 3. Alert through the approved incident channel. Do not set service objectives you cannot measure — an unmeasured objective is a false promise.",
)
replace_once(
    "community/specialists/data-engineer.md",
    "- Write an Airflow DAG with SLA callbacks and automatic Slack alerting on freshness breach",
    "- Write an Airflow DAG with version-compatible deadline or external alerting for freshness breaches",
)

replace_once(
    "tests/test_specialist_roster_hygiene.py",
    'assert "category: operations" in frontmatter("incident-commander.md")',
    'assert "category: governance" in frontmatter("incident-commander.md")',
)
replace_once(
    "tests/test_specialist_roster_hygiene.py",
    'assert "category: automation" in frontmatter("workflow-optimizer.md")',
    'assert "category: engineering-core" in frontmatter("workflow-optimizer.md")',
)

write(
    "policy/specialists/freshness.yaml",
    """version: 0.1
status: public-draft
reviewed_at: 2026-08-05
purpose: Keep durable specialist doctrine intact while volatile facts require current evidence.

principles:
  durable_doctrine:
    includes: [identity, purpose, responsibilities, non_responsibilities, methodologies, decision_frameworks, safety_boundaries, authority_limits, collaboration_and_handoffs, output_contracts]
    rule: Preserve in the specialist role card.
  volatile_facts:
    includes: [laws_and_effective_dates, regulatory_thresholds, standards_and_adopted_editions, product_and_framework_versions, api_and_parameter_availability, model_names_and_capabilities, pricing_and_fees, platform_algorithm_behavior, numerical_benchmarks, tool_maintenance_and_security_status]
    rule: Verify at execution time or through an explicitly dated evidence record.

volatility_classes:
  durable: {verification: normal_role_review}
  slow_moving: {verification: before_consequential_use, maximum_evidence_age_days: 90}
  fast_moving: {verification: per_relevant_task, maximum_evidence_age_days: 30}
  highly_volatile: {verification: live, maximum_evidence_age_days: 0}

source_authority:
  - {tier: 1, sources: [regulator, standards_body, official_vendor_documentation, official_release_notes, primary_law]}
  - {tier: 2, sources: [original_research, maintained_security_advisory, authoritative_technical_publication]}
  - {tier: 3, sources: [reputable_industry_analysis_with_primary_links]}
  - {tier: 4, sources: [secondary_summary], restriction: discovery_only}
  - {tier: 5, sources: [seo_content_farm, affiliate_content, unattributed_ai_generated_summary], restriction: never_sole_support}

risk_overrides:
  high: [verify_current_primary_source, state_evidence_date, state_applicability]
  critical: [verify_current_primary_source, state_evidence_date, state_jurisdiction_or_governing_authority, identify_adopted_edition_or_effective_rule, require_independent_verification]

failure_behavior:
  unavailable_current_evidence: do_not_assert_volatile_fact
  conflicting_authoritative_sources: escalate_and_present_conflict
  unknown_jurisdiction_or_applicability: surface_missing_context
  retired_or_unmaintained_tool: do_not_recommend_without_explicit_exception
""",
)

write(
    "docs/methodology/specialist-freshness.md",
    """# Specialist Freshness and Source Authority

TEO specialist role cards preserve practitioner-grade identity, protocols, responsibilities, safety boundaries, and handoffs. They are not permanent databases of current product behavior, law, pricing, versions, or platform algorithms.

## Two-layer rule

Durable doctrine stays in the role card. Volatile specifics—laws, standards, adopted editions, APIs, versions, model capabilities, prices, fees, ranking behavior, benchmarks, licensing, and tool-maintenance status—require current evidence when the task depends on them.

## Authoring rules

1. Route volatile facts to current verification instead of inlining them as timeless doctrine.
2. Prefer official or primary sources; secondary sources may discover a claim but do not establish it.
3. Do not replace one unsupported precise number with another.
4. State jurisdiction, applicability, product version, platform, and evidence date when they affect correctness.
5. Treat `current`, `latest`, `always`, `required`, and exact percentages as evidence-bearing claims.
6. Remove retired actions rather than merely marking them old.
7. When evidence cannot be verified, preserve the durable method and state uncertainty.

High- and critical-risk specialists must verify current primary authority before consequential legal, tax, lending, compliance, security, safety, or engineering-standard conclusions. For codes and standards, distinguish the latest published edition from the edition adopted by the governing jurisdiction and the edition required by contract.

Each role card declares `freshness_policy: live-verification-required` and `tools_last_verified: YYYY-MM-DD`. The date records the last systematic tool review; it never waives live verification.

Research query templates use `{current_year}`, `latest`, `current stable`, or the task date rather than the year in which the card was authored. Freshness controls are additive and must never compress or weaken the authoritative specialist specification.
""",
)

write(
    "tests/test_specialist_freshness.py",
    '''from __future__ import annotations

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
    for phrase in ["--iref", "Replies worth 150x likes", "Third-party cookie deprecation is complete", "Google's Privacy Sandbox (Topics API)", "## A9/A10 Algorithm Factors", "commonly called A10", "| SLSA 4 |", "Airflow SLA callbacks", "FIA: Fit/Impact/Authority", "  - async-std", "`async-std`:", "packed_simd"]:
        assert phrase not in combined, phrase


def test_freshness_policy_has_required_controls() -> None:
    policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    assert policy["principles"]["durable_doctrine"]
    assert policy["principles"]["volatile_facts"]
    assert policy["source_authority"][0]["tier"] == 1
    assert policy["failure_behavior"]["unavailable_current_evidence"] == "do_not_assert_volatile_fact"
''',
)
