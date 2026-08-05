from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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


def insert_before(path: str, marker: str, section: str) -> None:
    text = read(path)
    if text.count(marker) != 1:
        raise SystemExit(f"Expected one insertion marker in {path}: {marker!r}")
    write(path, text.replace(marker, section.rstrip() + "\n\n" + marker, 1))


# SEO: support classic and AI-mediated Search without inventing a separate ranking formula.
replace_once(
    "community/specialists/seo-specialist.md",
    "description: Technical SEO, content SEO, Baidu ecosystem, and App Store Optimization (ASO). Covers crawlability, authority, content strategy, and mobile app discoverability.",
    "description: Technical SEO, content SEO, AI-mediated search discovery, Baidu ecosystem, and App Store Optimization (ASO). Covers crawlability, authority, content strategy, and mobile app discoverability.",
)
replace_once(
    "community/specialists/seo-specialist.md",
    "Maximize organic discoverability across Google, Baidu, App Store, and Google Play. Operates across the full SEO stack — from crawl architecture to content clusters to link authority — and extends into ASO for mobile products.",
    "Maximize organic discoverability across classic search results, AI-mediated search experiences, Google, Baidu, App Store, and Google Play. Operates across crawl architecture, content quality, entity clarity, retrieval eligibility, authority, measurement, and ASO.",
)
replace_once(
    "community/specialists/seo-specialist.md",
    "- Search intent alignment review",
    "- Search intent alignment review\n- AI-mediated discovery review: indexing eligibility, snippet controls, entity clarity, answer support, source authority, and referral measurement",
)
replace_once(
    "community/specialists/seo-specialist.md",
    "- ASO optimization brief with keyword recommendations",
    "- ASO optimization brief with keyword recommendations\n- AI-mediated search visibility review with eligibility, content, source, and measurement findings",
)
insert_before(
    "community/specialists/seo-specialist.md",
    "## Topical Authority Map",
    '''## AI-Mediated Search Visibility

Google Search AI features such as AI Overviews and AI Mode do not require a separate technical optimization layer. The durable requirement remains: pages must be crawlable, indexed, eligible to appear with a snippet, compliant with Search policies, and useful to people.

**Required review:**

| Area | What to verify |
|---|---|
| Eligibility | Indexing, canonicalization, robots controls, snippet eligibility, and Search policy compliance |
| Content usefulness | Direct answers, complete explanations, original experience or evidence, and clear limitations |
| Entity clarity | Unambiguous people, products, organizations, locations, attributes, and relationships |
| Source authority | Primary evidence, named authorship, citations, correction process, and factual consistency |
| Structured data | Matches visible page content and uses currently supported types; no invented AI-specific schema |
| Passage support | Headings and sections make individual claims understandable outside the full-page context |
| Measurement | Search Console Web performance, analytics, conversions, assisted journeys, and referral quality |

Rules:

- Do not sell or claim a secret "AI Overview optimization" formula.
- Do not create synthetic question pages solely to target generated answers.
- Do not add unsupported markup or files claimed to guarantee inclusion in AI answers.
- Optimize for accurate retrieval and citation by making claims explicit, attributable, current, and supported.
- Google currently includes AI Overview and AI Mode activity within the Search Console `Web` search type rather than a separate guaranteed report. Verify current reporting before promising isolated AI-feature metrics.
- For non-Google answer engines, verify their current crawling, indexing, attribution, opt-out, and referral behavior separately.''',
)
replace_once(
    "community/specialists/seo-specialist.md",
    "**Authority threshold rule:** Do not target keywords with KD > 40 until the domain has >80% coverage of the supporting topic cluster. Targeting competitive terms on a thin site wastes crawl budget and produces no ranking.",
    "**Prioritization rule:** Keyword-difficulty scores and coverage percentages are vendor-specific planning signals, not search-engine thresholds. Calibrate them against the site's actual authority, SERP composition, business value, content quality, and observed ranking distribution.",
)
replace_once(
    "community/specialists/seo-specialist.md",
    "General rule: the page must already rank in positions 2-10 before snippet optimization is worth pursuing. Snippet optimization does not substitute for ranking.",
    "General rule: snippet and answer formatting does not substitute for relevance, eligibility, authority, or page quality. Use current SERP evidence rather than assuming a universal prerequisite ranking range.",
)
replace_once(
    "community/specialists/seo-specialist.md",
    "- Algorithm update tasks: check for recent Google core updates, ranking factor changes, or Search Console policy updates before making recommendations",
    "- Algorithm and AI feature tasks: check current Google core updates, AI Overview / AI Mode guidance, ranking-system documentation, Search Console reporting, and Search policies before making recommendations",
)

# Paid search: AI Max and automation governance replace fixed keyword-era formulas.
replace_once(
    "community/specialists/paid-search-strategist.md",
    "description: Google Ads, Microsoft Ads, and Amazon Ads architecture, bidding strategy, and account auditing. Covers search query analysis, negative keyword architecture, and budget pacing.",
    "description: Google Ads, Microsoft Ads, and Amazon Ads architecture, AI-mediated matching, bidding strategy, and account auditing. Covers query analysis, automation controls, creative and URL governance, and budget pacing.",
)
replace_once(
    "community/specialists/paid-search-strategist.md",
    "- Campaign and ad group structure design (SKAG, STAG, hybrid)",
    "- Campaign and ad group structure design across intent, product/service, geography, brand, URL, feed, asset, and control boundaries; SKAG/STAG patterns are optional historical tools, not defaults",
)
replace_once(
    "community/specialists/paid-search-strategist.md",
    "- Match type strategy and keyword taxonomy",
    "- Keyword, broad-match, keywordless, feed, URL, and search-theme strategy with explicit exclusions and reporting controls",
)
replace_once(
    "community/specialists/paid-search-strategist.md",
    "- RSA (Responsive Search Ad) headline and description architecture",
    "- Responsive and generated asset architecture with brand, legal, pinning, URL, and approval constraints",
)
replace_between(
    "community/specialists/paid-search-strategist.md",
    "## Quality Score Decomposition",
    "## Auction Insights Interpretation",
    '''## Quality Score Diagnostic

Quality Score is a diagnostic indicator, not a bidding formula or optimization target. Google exposes three component assessments—expected CTR, ad relevance, and landing-page experience—but does not publish fixed component weights or a universal CPC discount table.

| Component | Evidence to inspect | Typical corrective direction |
|---|---|---|
| Expected CTR | Component status, query intent, ad history, device and market context | Improve message relevance and test genuinely different value propositions |
| Ad relevance | Component status, query-to-ad alignment, asset composition | Tighten themes or improve assets without forcing exact-match repetition |
| Landing-page experience | Component status, page usefulness, speed, clarity, mobile experience | Align promise and page, improve usability, remove friction |

Change one diagnosed constraint at a time where causal learning matters. Do not claim that a specific Quality Score produces a fixed CPC reduction; auction outcomes depend on bids, competition, context, assets, thresholds, and other Ad Rank signals.

## AI Max for Search Governance

AI Max is an optimization layer inside Search campaigns, not a separate campaign type. Its current capabilities can include search-term matching through broad and keywordless technology, text customization, final URL expansion, brand controls, locations of interest, URL inclusions/exclusions, and expanded reporting.

**Pre-activation gate:**

| Control | Required decision |
|---|---|
| Conversion objective | Verified event, value rules, attribution setting, and data quality |
| Bidding | Current Smart Bidding requirement and budget sufficiency |
| Query expansion | Allowed intent boundaries, negatives, brand inclusions/exclusions, regulated terms |
| Generated assets | Approved claims, prohibited language, legal review, and removal process |
| Final URL expansion | Eligible URL set, exclusions, tracking-template compatibility, and landing-page QA |
| Pinned assets | Determine whether pinning must be preserved; final URL expansion or URL inclusions may prevent pinned RSA assets from serving |
| Reporting | Search-term source, generated assets, selected landing pages, spend, conversions, and change log |
| API / Editor | Verify current support before automating management; do not rely on a dated availability assumption |

Run controlled comparisons where volume allows. Evaluate incremental conversion value, query quality, brand safety, landing-page correctness, generated-claim accuracy, and marginal cost—not only platform-reported uplift.''',
)
replace_between(
    "community/specialists/paid-search-strategist.md",
    "## Performance Max Campaign Governance",
    "## First-Party Data Activation",
    '''## Performance Max Campaign Governance

Performance Max eligibility, assets, search themes, brand controls, exclusions, feeds, reporting, and channel controls change frequently. Verify the current account interface and official documentation before specifying counts or settings.

**Governance requirements:**

- Define the conversion and value objective before launch; do not optimize toward unverified or low-value events.
- Group assets and feeds around coherent commercial propositions, not arbitrary product counts.
- Supply high-quality owned images and videos where possible; review any generated or automatically adapted creative.
- Treat audience signals and search themes as system inputs, not deterministic targeting guarantees.
- Separate brand and non-brand measurement using the controls currently available to the account.
- Audit search-category insights, placement/channel reporting, landing pages, asset performance, and cannibalization with other campaigns.
- Record every material automation, feed, exclusion, or conversion-setting change.
- Do not hardcode a universal number of assets or search themes; platform limits and recommendations are volatile.''',
)
replace_between(
    "community/specialists/paid-search-strategist.md",
    "## First-Party Data Activation",
    "## Attribution Model Selection",
    '''## First-Party Data and Consent Controls

First-party data improves measurement and optimization only when it is lawful, accurate, normalized, consented where required, and correctly connected.

**Required controls:**

- Verify Customer Match eligibility, permitted use, source consent, suppression requirements, refresh cadence, and actual match diagnostics.
- Configure Enhanced Conversions using the current supported implementation, hashing, deduplication, and diagnostics; do not promise a fixed recovery percentage.
- Determine the applicable consent and privacy requirements by geography and product. Verify current Consent Mode behavior and platform enforcement rather than relying on a historical launch date.
- Separate modeled, observed, imported, and offline conversions in reporting where the platform permits.
- Test downstream lead quality and incrementality; a larger reported conversion count is not automatically better measurement.''',
)
replace_between(
    "community/specialists/paid-search-strategist.md",
    "## Attribution Model Selection",
    "## Research Protocol",
    '''## Attribution and Incrementality

Attribution options and eligibility change by platform and account. Verify the currently available models before recommending one; do not use a fixed conversion-volume threshold from an old platform rule.

- Use the platform's data-driven model when available and appropriate, while documenting what it can and cannot attribute.
- Use last-click only when it matches the decision need or as an explicit comparison baseline—not as an automatic low-volume fallback.
- Preserve conversion-time, click-time, attribution-window, cross-device, consent, and imported-conversion assumptions in the report.
- Attribution reallocates observed credit; it does not prove causality.
- Use experiments, geo or audience holdouts, conversion lift, marginal ROAS, media-mix modeling, or another approved causal method for budget decisions where feasible.''',
)

# Paid social: align with recommendation-system retrieval and current measurement architecture.
replace_once(
    "community/specialists/paid-social-strategist.md",
    "description: Full-funnel paid social campaigns across Meta, LinkedIn, TikTok, Pinterest, X, and Snapchat. Covers creative strategy, testing frameworks, and Performance Max asset architecture.",
    "description: Full-funnel paid social campaigns across Meta, LinkedIn, TikTok, Pinterest, X, and Snapchat. Covers creative strategy, testing frameworks, AI-mediated delivery, and automation governance.",
)
replace_once(
    "community/specialists/paid-social-strategist.md",
    "- RSA-style headline and description architecture for responsive formats\n- Performance Max asset group strategy (headlines, descriptions, images, videos)",
    "- Platform-native text, image, video, audio, and placement variation architecture\n- Advantage+ and equivalent creative-automation governance, including claim review and variation control",
)
replace_once(
    "community/specialists/paid-social-strategist.md",
    "- Meta: Advantage+ Shopping, Advantage+ Audience, CAPI integration",
    "- Meta: Advantage+ sales, audience, placements, budget, creative, CAPI integration, and Andromeda-aware creative diversity",
)
insert_before(
    "community/specialists/paid-social-strategist.md",
    "## Creative Refresh Cadence",
    '''## AI-Mediated Delivery and Creative Retrieval

Meta Andromeda is a retrieval system inside Meta's ads recommendation stack, not an advertiser setting or a published ranking formula. It selects candidates at large scale before later ranking stages, while Advantage+ can automate or expand audience, budget, placement, and creative decisions.

**Operating implications:**

| Area | Durable practice |
|---|---|
| Audience | Treat interests, lookalikes, CRM lists, and demographics as suggestions or signals unless configured as a supported strict control |
| Controls | Reserve location, minimum age, language, exclusions, legal eligibility, and other current hard constraints for genuine business requirements |
| Creative | Supply materially diverse concepts, offers, formats, and visual treatments rather than superficial copies of one ad |
| Measurement | Verify Pixel/CAPI events, deduplication, attribution, conversion quality, and incrementality before scaling automation |
| Automation | Document which Advantage+ layers are enabled, what can expand, what is fixed, and how to roll back |
| Claims | Review generated or transformed assets for accuracy, rights, disclosure, brand, and regulated-category compliance |

Do not attempt to "optimize for Andromeda" through invented weights. Optimize the inputs the delivery system can evaluate: reliable conversion signals, broad eligible supply where appropriate, strong and diverse creative, clear offers, accurate destinations, and valid constraints.''',
)
replace_between(
    "community/specialists/paid-social-strategist.md",
    "## Creative Refresh Cadence",
    "## Audience Exclusion Architecture",
    '''## Creative Refresh and Fatigue Diagnosis

Refresh decisions use account evidence, not universal frequency cutoffs.

Monitor by audience, placement, geography, creative concept, and time:

- marginal CPA / ROAS and conversion quality;
- reach, frequency, CPM, CTR, hold rate, completion, and landing-page behavior;
- spend concentration by creative and whether the system is starving viable alternatives;
- audience saturation, offer fatigue, seasonal change, and competitive pressure.

Define a fatigue trigger from the account's own baseline—for example, sustained deterioration in marginal outcome at comparable auction conditions. Preserve winning ads when possible, introduce new candidates without unnecessarily resetting learning, and distinguish creative fatigue from offer, tracking, landing-page, or market failure.''',
)
replace_between(
    "community/specialists/paid-social-strategist.md",
    "## Audience Exclusion Architecture",
    "## iOS 14+ Signal Loss Mitigation",
    '''## Audience Controls and Exclusions

Audience architecture must distinguish strict controls from optimization suggestions.

**Common controls to evaluate:**

- current customers or recent converters where acquisition spend should exclude them;
- employees, test users, invalid leads, or internal traffic;
- legal age, geography, language, licensing, and regulated-category restrictions;
- retargeting windows and suppression periods;
- data-source consent, list freshness, match quality, and deletion obligations.

Advantage+ audience can expand beyond suggestions while honoring the strict controls currently supported by the product. Verify the current interface and campaign objective before asserting that an age, interest, custom audience, or lookalike is a hard boundary. Do not rely on a deprecated audience-overlap tool or a universal percentage threshold; diagnose duplication through delivery, reach, auction, and conversion evidence.''',
)
replace_between(
    "community/specialists/paid-social-strategist.md",
    "## iOS 14+ Signal Loss Mitigation",
    "## Creative Performance Diagnosis",
    '''## Measurement and Signal Resilience

Platform measurement changes with operating systems, browser controls, consent, privacy law, product updates, and modeled reporting. Build a resilient measurement stack rather than preserving an old iOS workaround checklist.

1. **Browser/app events:** verify the current Pixel, SDK, and event configuration.
2. **Server-side events:** use Conversions API or the current supported equivalent with event IDs, deduplication, timestamps, consent, and data minimization.
3. **Diagnostics:** monitor platform event diagnostics, match quality, missing parameters, duplicates, delays, and schema drift without treating one score as a universal pass/fail threshold.
4. **Outcome quality:** connect CRM or downstream outcomes where lawful so optimization does not reward low-quality leads or superficial events.
5. **Modeled reporting:** label modeled versus observed results and preserve attribution assumptions.
6. **Causal measurement:** use lift tests, holdouts, or other approved incrementality methods for budget decisions.

Do not instruct users to configure an old fixed number of Aggregated Event Measurement events or claim that only one prioritized event can be recorded without verifying current Meta documentation and account behavior.''',
)
replace_once(
    "community/specialists/paid-social-strategist.md",
    "**Benchmark thresholds (Meta, 2025-2026):**\n- Hook rate (3s video views / impressions): >30% = strong hook\n- CTR (link clicks / impressions): >1.5% = healthy for cold audiences\n- Landing page CVR: benchmark against your own historical baseline, not industry averages",
    "**Benchmark rule:** Use the account's historical distribution, objective, placement, geography, format, attribution window, and downstream outcome quality. External hook-rate or CTR benchmarks require a dated source and comparable population; they are context, not pass/fail thresholds.",
)
replace_once(
    "community/specialists/paid-social-strategist.md",
    '"Write a Performance Max asset group for a SaaS product targeting HR teams"',
    '"Design an Advantage+ creative and audience test for a SaaS product targeting HR teams"',
)

# Cross-border ecommerce: conversational, visual, and agentic product discovery plus live fee/policy controls.
replace_between(
    "community/specialists/cross-border-ecommerce.md",
    "## Listing Quality Score",
    "## Review Velocity Strategy",
    '''## Marketplace Listing Quality Review

Use a marketplace- and category-specific review rather than presenting an internal 100-point rubric as an Amazon standard.

| Area | Evidence to review |
|---|---|
| Product identity | Correct category, brand, model, identifiers, variants, and parent-child relationships |
| Structured attributes | Complete and accurate dimensions, materials, compatibility, use cases, safety data, and category fields |
| Customer-facing content | Clear title, bullets, description, enhanced content, comparison information, and localized language |
| Visual evidence | Current image/video requirements, accurate product depiction, dimensions, use in context, and rights |
| Trust and compliance | Claims support, certifications, warnings, reviews, returns, seller identity, and restricted-product rules |
| Discoverability | Query relevance, natural-language needs, product attributes, visual similarity, and conversational comparison support |
| Conversion and operations | Price, availability, delivery promise, reviews, returns, defects, and offer competitiveness |

Platform field limits, image counts, backend fields, enhanced-content eligibility, and scoring tools are volatile. Verify them in the target marketplace's current Seller Central or official policy documentation. Any internal scorecard must be labeled as the operator's prioritization tool, not an Amazon ranking score.''',
)
replace_between(
    "community/specialists/cross-border-ecommerce.md",
    "## Review Velocity Strategy",
    "## Amazon Discovery and Ranking Systems",
    '''## Review Integrity and Voice-of-Customer Strategy

Reviews support customer trust and product understanding, but acquisition methods, messaging rules, Vine eligibility, enrollment limits, and review-display behavior change by marketplace.

Rules:

- Use only review-request mechanisms currently permitted by the marketplace.
- Never incentivize, gate, buy, manipulate, suppress, or coordinate reviews.
- Verify current Vine eligibility, cost, review-count rules, and market availability before recommending enrollment.
- Treat inserts, follow-up messages, and third-party tools as policy-sensitive; verify current Buyer-Seller Messaging and communication rules.
- Analyze review themes for product defects, missing information, compatibility issues, and language customers use.
- Do not set a universal target such as a fixed number of reviews per week. Track legitimate review rate, rating distribution, recency, verified-purchase mix, return reasons, and conversion against the category baseline.''',
)
insert_before(
    "community/specialists/cross-border-ecommerce.md",
    "## FBA Fee Structure Awareness",
    '''## AI-Mediated Marketplace Discovery

Amazon's conversational shopping assistant, historically called Rufus and renamed Alexa for Shopping in May 2026, can support natural-language discovery, comparisons, product questions, personalized guidance, visual search, price monitoring, and agentic shopping actions. Names, availability, and behavior vary by market and change rapidly; verify the current experience before advising.

Amazon describes the assistant as using product-catalog data, customer reviews, community Q&A, information from the web, Stores APIs, retrieval-augmented generation, and multiple models. Product content must therefore support more than exact keyword matching.

**Required content review:**

| Evidence surface | Optimization requirement |
|---|---|
| Catalog and attributes | Accurate, complete, normalized product facts and variant relationships |
| Product detail page | Explicit use cases, limitations, compatibility, dimensions, materials, care, safety, and included items |
| Comparisons | Clear differentiators and suitability for common customer needs without unsupported superiority claims |
| Reviews and Q&A | Monitor recurring questions and defects; correct listing gaps instead of manufacturing answers |
| Images and video | Make visual attributes, scale, configuration, and use context clear for visual and multimodal discovery |
| Price and availability | Keep offers, inventory, delivery, and promotions accurate; conversational systems can surface live changes |

Do not claim a direct optimization switch or ranking formula for Alexa for Shopping. Improve the authoritative product evidence available to retrieval, comparison, and recommendation systems, then measure search, detail-page, conversion, return, and customer-question outcomes.''',
)
replace_between(
    "community/specialists/cross-border-ecommerce.md",
    "## FBA Fee Structure Awareness",
    "## Account Health Monitoring",
    '''## FBA and Marketplace Fee Verification

Every landed-cost model must use the current target marketplace, category, fulfillment program, size/weight tier, storage profile, inventory age, returns, inbound placement, low-inventory or other applicable surcharges, taxes, and seller-plan fees.

**Required fee schedule:**

| Fee / cost | Current source | Basis | Assumption | Sensitivity |
|---|---|---|---|---|
| Referral / commission | Official marketplace fee page or Seller Central | Category and sale price | | |
| Fulfillment | Current rate card / revenue calculator | Size, weight, dangerous goods, market | | |
| Inbound and placement | Current program rules | Shipment configuration | | |
| Storage and inventory age | Current rate card | Volume, season, age | | |
| Returns / removals / disposal | Current rate card and historical data | Units and category | | |
| Advertising / promotions | Actual plan or campaign evidence | Spend, coupons, deals | | |
| Duties / tax / compliance | Governing authority and specialist review | Product and route | | |

Do not embed a dated US fee table or universal 20% margin floor in the role card. Calculate contribution margin, cash conversion, return sensitivity, and break-even using current official fees and the operator's commercial threshold.''',
)
replace_between(
    "community/specialists/cross-border-ecommerce.md",
    "## Account Health Monitoring",
    "## Research Protocol",
    '''## Account Health and Policy Monitoring

Marketplace account-health metrics, thresholds, response windows, appeal processes, and score displays vary by marketplace and can change without notice.

- Identify the current official policy metrics for the seller's marketplace and fulfillment model.
- Record actual status, threshold, measurement window, source, and next action for each metric.
- Prioritize product safety, authenticity, intellectual property, restricted products, customer harm, unresolved policy notices, and fulfillment failures.
- Respond within the official case or appeal deadline; do not use a generic 24-hour or numeric trigger unless verified.
- Preserve evidence: invoices, certifications, test reports, tracking, customer communication, corrective actions, and root-cause analysis.
- Do not claim a fixed reinstatement duration. Escalate material enforcement risk to compliance, legal, and the accountable business owner.''',
)

write(
    "docs/methodology/ai-mediated-discovery-refresh-2026-08-05.md",
    '''# AI-Mediated Discovery Specialist Refresh — 2026-08-05

This tranche updates four connected specialists as one retrieval-system change rather than four independent platform edits.

## Durable shift

Keyword research, audience knowledge, product data, creative testing, technical eligibility, and conversion measurement remain important. They now operate inside systems that increasingly use semantic retrieval, recommendation models, generated answers, automated matching, dynamic assets, visual understanding, and conversational or agentic interfaces.

## Primary authorities reviewed

- Google Search Central: AI features and website eligibility for AI Overviews and AI Mode.
- Google Ads Help: AI Max search-term matching, asset optimization, final URL expansion, controls, reporting, pinning interactions, and setup requirements.
- Meta Engineering: Andromeda personalized ads retrieval architecture and its relationship to Advantage+ automation and creative scale.
- Meta for Business: Advantage+ audience, creative, placement, budget, sales, app, and lead campaign behavior.
- Amazon Science and About Amazon: Rufus technology, RAG evidence sources, conversational shopping, visual search, agentic actions, and the 2026 Alexa for Shopping name.

## Authoring rule

The cards describe what practitioners can control and verify. They do not invent algorithm weights, marketplace scores, secret AI optimization techniques, fixed benchmark thresholds, or permanent product limits.
''',
)

write(
    "tests/test_ai_mediated_discovery_refresh.py",
    '''from pathlib import Path

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
    methodology = (ROOT / "docs" / "methodology" / "ai-mediated-discovery-refresh-2026-08-05.md").read_text(encoding="utf-8")
    for name in ["Google Search Central", "Google Ads Help", "Meta Engineering", "Amazon Science"]:
        assert name in methodology
''',
)
