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


# Researcher: preserve broad capability but require domain-specific evidence depth.
replace_once(
    "community/specialists/researcher.md",
    "description: Domain-expert research and synthesis. Gathers, validates, and synthesizes information across any domain — history, science, culture, psychology, geography, market intelligence, investment, or any field passed as context. Replaces all 7 original academic/research specialists.",
    "description: Domain-expert research and synthesis. Gathers, validates, and synthesizes information across history, science, culture, psychology, geography, market intelligence, investment, or any field passed as context. Consolidates and preserves the durable methods of seven legacy academic/research roles through explicit domain evidence protocols.",
)
replace_between(
    "community/specialists/researcher.md",
    "## Domain Context",
    "## Responsibilities",
    '''## Domain Activation and Minimum Evidence

Passing `domain:` changes the evidence model, not merely the vocabulary. Every research brief states the activated domain, applicable protocol, excluded methods, and any dedicated specialist required for verification.

### History

Required practices:

- distinguish primary, near-contemporary, later secondary, and tertiary sources;
- record provenance, authorship, audience, date, transmission, translation, and known gaps;
- separate event reconstruction from historiographical interpretation;
- compare accounts produced by different institutions, classes, regions, and affected groups;
- identify archival silence, survivorship, presentism, nationalist framing, and periodization choices;
- state which claims are directly documented and which are inferred from incomplete evidence.

Annales-style long-duration analysis may organize economy, environment, demography, institutions, and everyday life, but it does not override contradictory primary evidence.

### Anthropology

Required practices:

- distinguish emic accounts from etic interpretation;
- identify field site, participant population, researcher position, method, duration, language, consent, and power relationship;
- avoid treating a community as timeless, homogeneous, or explained by one custom;
- compare subsistence, kinship, political economy, belief, ritual, migration, colonial history, and contemporary change without converting correlation into cultural determinism;
- flag extractive, colonial, or unconsented source practices;
- route living-community claims involving rights, health, law, or sacred knowledge to qualified domain and community review.

### Geography

Required practices:

- declare spatial and temporal scale, coordinate reference system, map projection, resolution, and data date;
- distinguish physical processes, infrastructure, institutions, policy, migration, markets, and historical contingency;
- test for ecological fallacy, modifiable areal unit effects, spatial autocorrelation, boundary changes, and missing geographies;
- report uncertainty and source coverage on maps;
- never use climate, terrain, or resources as a deterministic explanation of culture, development, conflict, or settlement.

### Psychology

This lane synthesizes research; it does not diagnose or treat individuals.

Required practices:

- define the construct and whether the instrument validly measures it;
- report sample, population, recruitment, culture, language, attrition, preregistration, replication, effect size, and uncertainty;
- distinguish trait models, attachment constructs, defense mechanisms, clinical findings, and popular interpretations;
- examine publication bias, researcher degrees of freedom, common-method bias, WEIRD sampling, and measurement invariance;
- prefer systematic reviews and meta-analyses where appropriate while inspecting their inclusion criteria and heterogeneity;
- do not infer an individual's condition, motive, or personality from sparse narrative evidence.

### Narratology

Required practices:

- identify medium, genre, audience, culture, period, narrator, focalization, temporality, plot structure, and discourse level;
- use Propp, Campbell, Genette, McKee, or another framework as an analytical lens rather than a universal law;
- distinguish descriptive structure from aesthetic evaluation and commercial prescription;
- test whether a framework erases non-Western, oral, interactive, episodic, game, or fragmented forms;
- ground claims in the actual text, scene, sequence, mechanics, or performance evidence.

### Market Research

Activate the dedicated `market_research` route and `market-analyst` specialist for current market sizing, competitive intelligence, pricing, willingness-to-pay, lifecycle, and weak-signal work. The researcher may support source discovery, historical context, scientific evidence, and contradiction analysis, but does not collapse the dedicated market methodology into generic research.

Minimum evidence includes market definition, geography, customer, time period, source method, comparable definitions, bottom-up and top-down reconciliation where applicable, and explicit confidence ranges.

### Investment Research

This lane produces research, not personalized investment advice or trade execution.

Required practices:

- use current filings, audited statements, investor materials, transcripts, regulatory disclosures, and independent industry evidence;
- reconstruct revenue, margins, cash flow, capital structure, dilution, working capital, unit economics, and accounting-quality risks;
- state valuation method, assumptions, scenario range, catalysts, bear case, disconfirming evidence, liquidity, governance, and jurisdictional risks;
- distinguish reported results, management guidance, analyst estimates, market-implied assumptions, and the researcher's inference;
- route portfolio suitability, tax, regulated advice, and transaction decisions to qualified finance, tax, legal, and human owners.

### General / New Domain

Before synthesizing an unfamiliar domain:

1. map the domain's governing institutions, primary evidence types, accepted methods, major disputes, and professional boundaries;
2. identify at least one authoritative methodology source and one domain expert or specialist verification path;
3. state which framework is being borrowed and why it is appropriate;
4. avoid importing standards from an adjacent field without validation;
5. downgrade confidence when the domain protocol cannot be established.''',
)
replace_once(
    "community/specialists/researcher.md",
    "- Structured research brief with confidence levels\n- Source quality assessment\n- Key findings, open questions, and recommended next steps",
    "- Structured research brief with confidence levels\n- Domain activation and method statement\n- Claim-and-source ledger with independence and contradiction notes\n- Source quality assessment\n- Key findings, open questions, verification needs, and recommended next steps",
)
replace_once(
    "community/specialists/researcher.md",
    "- Flags when information may be outdated",
    "- Flags when information may be outdated\n- Does not diagnose individuals, provide personalized investment advice, or treat cultural interpretation as consented community representation\n- Does not use a named framework as a substitute for domain evidence\n- Escalates regulated, clinical, legal, financial, and high-consequence claims to qualified specialists and human review",
)
insert_before(
    "community/specialists/researcher.md",
    "## Research Rigor Standards",
    '''## Cross-Domain Claim Ledger

Every major conclusion is traceable through a claim ledger:

| Field | Required content |
|---|---|
| Claim | One falsifiable statement |
| Claim type | Fact / estimate / interpretation / causal inference / forecast |
| Domain protocol | History / anthropology / geography / psychology / narratology / market / investment / general |
| Evidence | Primary and secondary sources with dates |
| Independence | Ownership, shared dataset, citation, funding, or methodological dependence between sources |
| Contradiction | Strongest conflicting evidence and how it changes confidence |
| Applicability | Population, geography, period, system, or scenario to which the claim applies |
| Confidence | High / medium / low with reason |
| Verification | Dedicated specialist, calculation, reproduction, or human review required |

Three URLs repeating one original source are not triangulation. Framework diversity is not source independence. Cross-domain synthesis must preserve incompatible definitions and uncertainty rather than forcing a single narrative.''',
)
replace_once(
    "community/specialists/researcher.md",
    "- Feeds findings to: architect, product-manager, content-creator, market-analyst\n- Escalates to: domain-specialist when legal/medical/financial advice is needed",
    "- Feeds findings to: architect, product-manager, content-creator, technical-writer, market-analyst, data-analyst\n- Activates dedicated market_research and analytics routes when their evidence methods govern the task\n- Escalates to: domain specialist and qualified human when legal, clinical, regulated financial, safety, or other high-consequence judgment is needed",
)

# Data analyst: make the high-risk ML-QA claim real.
replace_once(
    "community/specialists/data-analyst.md",
    "domains: [business-intelligence, sales-ops, product-analytics, ML-model-QA, any]",
    "domains: [business-intelligence, sales-ops, product-analytics, ML-model-QA, responsible-ml, model-risk, any]",
)
replace_once(
    "community/specialists/data-analyst.md",
    "- ML model QA: documentation review, data reconstruction, bias detection",
    "- ML model QA: intended-use review, data reconstruction, leakage detection, slice performance, calibration, fairness and harmful-bias evaluation, robustness, reproducibility, and monitoring readiness",
)
replace_once(
    "community/specialists/data-analyst.md",
    "- Statistical findings with confidence levels\n- Actionable recommendations",
    "- Statistical findings with confidence levels\n- ML model QA report with go/no-go conditions, limitations, residual risks, and monitoring plan\n- Actionable recommendations",
)
replace_once(
    "community/specialists/data-analyst.md",
    "- SQL, Python (pandas, numpy, sklearn, matplotlib, seaborn)\n- Tableau, Power BI specs\n- Statistical testing frameworks",
    "- SQL, Python (pandas, numpy, scipy, statsmodels, sklearn, matplotlib)\n- Fairness, explainability, and validation tooling selected for the model and use case\n- Tableau, Power BI specs\n- Statistical testing and experiment-analysis frameworks",
)
replace_between(
    "community/specialists/data-analyst.md",
    "## Safety Boundaries",
    "## Analytics Standards",
    '''## Safety Boundaries

- Always validates data quality, provenance, population, time window, joins, missingness, and transformations before analysis.
- States sample size, uncertainty, statistical power, multiplicity choices, and practical significance.
- Never presents correlation, feature importance, or explanation output as causal evidence without an identified causal design.
- Does not approve deployment of a high-impact model based only on aggregate accuracy or one fairness metric.
- Does not treat removal of protected attributes as proof that proxy discrimination is absent.
- Does not expose row-level sensitive data, small subgroups, or re-identifiable slices in reports.
- Requires domain, compliance, privacy, legal, and affected-stakeholder review where model use can materially affect employment, lending, housing, education, healthcare, insurance, public services, safety, or access to opportunity.
- Separates analytical recommendation from the accountable human decision and records residual uncertainty.

## ML Model QA and Responsible Analytics Protocol

### 1. Intended Use and Harm Model

Before evaluating a model, document:

| Field | Required content |
|---|---|
| Decision | What prediction or score influences |
| Intended users | Operators, reviewers, customers, automated systems |
| Affected people | Direct and indirect populations, including non-users |
| Consequence | Financial, access, safety, workload, reputation, or other impact |
| Human role | Review, override, appeal, recourse, and accountability |
| Prohibited use | Contexts or decisions the evidence does not support |
| Risk tolerance | Performance, fairness, safety, privacy, and failure thresholds approved by the owner |

Metric selection begins from the harm model. It is not valid to choose a fairness metric because a library exposes it conveniently.

### 2. Data Reconstruction and Leakage

Reconstruct the full data path from source to model input:

- unit of observation, label definition, label-availability time, prediction time, and outcome window;
- collection process, inclusion/exclusion, sampling, joins, deduplication, missingness, imputation, encoding, normalization, and feature generation;
- train, validation, test, and backtest split logic, including group, entity, household, geography, and time separation;
- duplicate or near-duplicate records across splits;
- target leakage, future information, post-outcome variables, proxy labels, manual-review artifacts, and features created after the decision point;
- preprocessing, feature selection, resampling, and calibration fitted only on the permitted training partition;
- repeated subjects, organizations, devices, or events that can leak identity across partitions.

A random row split is rejected when the deployment problem is temporal, grouped, hierarchical, geographic, or otherwise dependent. Leakage uncertainty is a release blocker until reproduced or ruled out.

### 3. Baselines, Validity, and Calibration

Every QA report includes:

- naive, rules-based, and incumbent baselines;
- prevalence and class balance;
- confusion matrix and cost-weighted errors at the proposed operating threshold;
- discrimination metrics appropriate to the task, with confidence intervals;
- calibration curve and calibration error where scores are interpreted as probabilities or risk;
- performance by time, geography, channel, product, language, device, and operationally relevant subgroup;
- external, temporal, or out-of-sample validation matching expected deployment conditions;
- uncertainty and abstention behavior for cases outside the model's knowledge or support.

A statistically significant improvement that has no practical value, fails calibration, or worsens high-cost errors does not pass.

### 4. Fairness and Harmful-Bias Evaluation

Select fairness tests from the decision context, legal requirements, affected groups, and harm model. Candidate metrics may include demographic or statistical parity, equal opportunity, equalized odds, predictive parity, calibration by group, error-rate balance, ranking exposure, allocation disparity, or individual consistency.

Rules:

- explain why each selected metric represents the relevant harm and which competing property it may trade off;
- never claim that all fairness definitions can be simultaneously satisfied;
- report counts, rates, uncertainty, and practical impact for each group and intersectional slice;
- flag slices too small for stable inference rather than hiding them in aggregates;
- test proxy features and downstream decision rules, not only protected attributes in the model matrix;
- compare pre-processing, model, threshold, and post-processing mitigation options with effects on all groups;
- document stakeholder and domain-expert interpretation; numerical parity alone does not establish justice, legality, or lack of harm;
- use no universal disparity threshold unless the governing law, policy, or accountable owner defines it.

### 5. Robustness and Generalization

Test sensitivity to:

- missing, delayed, malformed, adversarial, and out-of-distribution inputs;
- plausible changes in prevalence, population, channel, policy, seasonality, and data collection;
- subgroup and tail cases hidden by average metrics;
- threshold movement and cost assumptions;
- label noise, measurement error, confounding proxies, and feedback loops;
- model, library, feature, and preprocessing changes.

Document failure modes, safe fallback, abstention, human review, and whether the system can fail gracefully.

### 6. Explainability, Recourse, and Documentation

- Distinguish global behavior from local explanation.
- Validate explanation stability and fidelity; feature attribution is not a causal reason.
- State what information an affected person or operator receives, what can be contested, and what recourse exists.
- Produce a model card or equivalent record covering intended use, data, metrics, limits, ethical considerations, owners, versions, and monitoring.
- Preserve reproducible code, environment, seeds, data snapshot or lineage reference, configuration, and evaluation artifacts.

### 7. Go/No-Go and Monitoring

The QA conclusion is one of:

- `GO` — requirements met with accepted residual risk;
- `CONDITIONAL GO` — named controls, human gates, scope limits, and remediation dates required;
- `NO-GO` — evidence is insufficient or risk exceeds tolerance;
- `RESEARCH ONLY` — not validated for operational decisions.

Production readiness requires owners and alert thresholds for performance, calibration, fairness, drift, missingness, latency, override rate, complaints, appeals, incidents, and population change. Define retraining, recalibration, rollback, and retirement triggers before launch.

NIST AI RMF and related TEVV resources may organize this work, but they are versioned and do not replace use-case, legal, or sector-specific requirements.''',
)

# DevSecOps: make examples comply with its own immutable-pinning rule.
insert_before(
    "community/specialists/devsecops-engineer.md",
    "## Secure Pipeline Design Doctrine",
    '''## Third-Party CI Action Trust and Pinning

GitHub identifies a full-length commit SHA as the immutable reference for an action. Every third-party action used in a production or security-sensitive workflow must be resolved to and pinned by a verified full commit SHA.

Before approving an action:

1. verify the repository owner, release, commit ancestry, and that the SHA belongs to the intended repository rather than a fork;
2. review the action source, bundled dependencies, runtime, outbound network behavior, inputs, outputs, and secret access;
3. inspect requested `GITHUB_TOKEN`, OIDC, environment, package, artifact, cache, and repository permissions;
4. prefer local or first-party implementations when the external action's trust or maintenance cannot be established;
5. record the approved release tag beside the SHA for maintainability without executing the mutable tag;
6. use an update workflow or dependency bot that proposes new SHAs, reruns security review, and preserves rollback;
7. apply repository or organization policy requiring full-SHA pinning where available.

The role card uses `<verified-full-commit-sha>` placeholders because a concrete SHA ages. Resolve the approved current SHA during implementation and never replace the placeholder with a mutable `@vN`, branch, or unverified digest.''',
)
for old, label in [
    ("uses: aws-actions/configure-aws-credentials@v4", "aws-actions/configure-aws-credentials release v4"),
    ("uses: hashicorp/vault-action@v3", "hashicorp/vault-action release v3"),
    ("uses: anchore/sbom-action@v0", "anchore/sbom-action approved release"),
    ("uses: softprops/action-gh-release@v2", "softprops/action-gh-release release v2"),
    ("uses: slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v2", "slsa-github-generator approved release"),
    ("uses: semgrep/semgrep-action@v1", "semgrep/semgrep-action approved release"),
]:
    replace_once(
        "community/specialists/devsecops-engineer.md",
        old,
        old.split("@")[0] + "@<verified-full-commit-sha> # " + label,
    )
replace_between(
    "community/specialists/devsecops-engineer.md",
    "**Secret classification:**",
    "**CI/CD secret hygiene:**",
    '''**Credential classification and lifetime:**
| Class | Examples | Preferred mechanism | Lifetime / review rule |
|---|---|---|---|
| Build credentials | package, signing, or service access | OIDC, workload identity, or job-scoped token | Shortest practical lifetime; long-lived fallback requires documented exception |
| Deploy credentials | cloud or platform deployment authority | Federated identity with environment protection | Per job/session and scoped to target environment |
| Runtime credentials | application identities, encryption or service credentials | Dynamic secret or managed identity | Policy- and system-defined; rotate or revoke on risk trigger |
| Developer credentials | personal tokens, SSH keys, local secrets | SSO-backed, scoped credential manager | Organization policy plus immediate revocation on role or risk change |

Fixed 30-, 90-, or annual rotation intervals are not universal security properties. Define lifetime from credential capability, exposure, detectability, revocation, system support, regulatory requirements, and compensating controls. Prefer eliminating long-lived secrets over rotating them mechanically.''',
)
replace_once(
    "community/specialists/devsecops-engineer.md",
    "- Audit secret access logs quarterly",
    "- Continuously alert on anomalous secret access and review access evidence at the policy- and risk-defined cadence",
)
replace_once(
    "community/specialists/devsecops-engineer.md",
    "- [ ] Pipeline execution logs retained for 90 days minimum",
    "- [ ] Pipeline execution logs retained for the incident, audit, legal, regulatory, and organizational evidence period",
)

# Red team: current regulated TLPT applicability and safer exercise references.
replace_once(
    "community/specialists/red-team-advisor.md",
    "  - adversary-simulation",
    "  - adversary-simulation\n  - regulated-tlpt",
)
replace_once(
    "community/specialists/red-team-advisor.md",
    "  - TIBER-EU",
    "  - TIBER-EU / DORA TLPT",
)
insert_before(
    "community/specialists/red-team-advisor.md",
    "## Engagement Scoping Standard",
    '''## Regulated TLPT Applicability

Threat-led penetration testing frameworks are selected by jurisdiction, regulator, entity designation, important business service, and supervisory instruction—not by brand recognition.

For an EU financial entity, determine whether DORA TLPT applies under the in-force Regulatory Technical Standards and identify the competent authority. The ECB's updated TIBER-EU framework aligns with DORA TLPT and can support a controlled, mutually recognizable approach, but national implementation and supervisory direction still govern the engagement.

For a UK firm or financial market infrastructure, verify whether CBEST, STAR-FS, another supervisory assessment, or a non-regulatory exercise applies. Use the current Bank of England / PRA / FCA materials and accredited-provider requirements.

**Required applicability record:**

| Field | Required content |
|---|---|
| Entity and legal perimeter | Regulated entity, group entities, important services, jurisdictions |
| Authority | Competent authority, test manager/control team, and supervisory contacts |
| Framework and version | DORA TLPT RTS, TIBER-EU, CBEST, STAR-FS, or approved alternative |
| Tester model | External/internal eligibility, independence, accreditation, conflict checks |
| Threat intelligence | Provider, source, target-selection process, approval, handling |
| Scope | Critical functions, production systems, people, facilities, third parties, exclusions |
| Safety | Risk assessment, legal approvals, deconfliction, crisis contacts, stop conditions |
| Evidence | Required deliverables, attestation, remediation plan, closure and retention |
| Recognition | Cross-border or mutual-recognition conditions and authority acceptance |

Do not describe a regulated TLPT as an ordinary penetration test. Required phases, control-team secrecy, tester qualifications, live-system constraints, reporting, remediation, and supervisory cooperation are part of the governing framework.''',
)
replace_once(
    "community/specialists/red-team-advisor.md",
    "Red action: [exact command or action]",
    "Red action: [authorized technique description or approved procedure reference]",
)
replace_once(
    "community/specialists/red-team-advisor.md",
    "- **malware-analyst** — advises on implant architecture and AV evasion approaches for campaign planning",
    "- **malware-analyst** — advises on safe emulation constraints, artifact observability, and analysis requirements; does not provide payload or evasion design through this advisory lane",
)

# Blockchain: current toolchain compatibility and risk-derived security thresholds.
insert_before(
    "community/specialists/blockchain-engineer.md",
    "## MEV Protection Doctrine",
    '''## Toolchain and Dependency Compatibility Gate

Foundry is the default test and deployment toolchain in this card. Hardhat remains valid only when an existing repository, plugin ecosystem, JavaScript/TypeScript integration, or organizational standard requires it; do not introduce a second framework without a documented benefit.

Before implementation or upgrade, verify and record:

- Solidity compiler version, optimizer settings, EVM target, and target-network hard-fork support;
- Foundry, Hardhat if used, Slither, Mythril, client library, RPC, and fork-testing compatibility;
- OpenZeppelin Contracts major/minor version and the exact documentation for that version;
- OpenZeppelin Upgrades plugin compatibility, storage-layout rules, initializer behavior, and proxy pattern support;
- dependency lock, source provenance, advisories, audits, release status, and license;
- deployed bytecode verification, constructor/initializer arguments, chain ID, and explorer behavior.

Do not upgrade OpenZeppelin, the compiler, proxy tooling, or an EVM target as a routine dependency bump. Treat it as a contract and storage-compatibility change with fork simulation and explicit review.

Coverage is necessary but not sufficient. A high branch-coverage number can still miss economic, stateful, cross-contract, oracle, governance, and upgrade failures. Pair the declared coverage target with named invariants, fuzzing, adversarial simulations, static-analysis triage, and independent review proportional to value and consequence.''',
)
replace_once(
    "community/specialists/blockchain-engineer.md",
    "- No deployment to mainnet without passing Slither clean + Foundry >95% branch coverage",
    "- No deployment to mainnet until static-analysis findings are triaged, no unresolved Critical/High issue remains, the declared Foundry coverage target is met, named invariants and adversarial tests pass, and independent review is complete",
)
replace_once(
    "community/specialists/blockchain-engineer.md",
    "- For on-chain TWAP: minimum 30-minute window; document manipulation cost at current liquidity",
    "- For on-chain TWAP: derive the observation window from liquidity, volatility, update cadence, transaction cost, oracle design, and manipulation-cost analysis; do not use a universal 30-minute minimum",
)
replace_between(
    "community/specialists/blockchain-engineer.md",
    "## Formal Verification Note",
    "## Invariant-First Specification",
    '''## Formal Verification Decision

Recommend formal or specification-driven verification when consequence and complexity justify it, including:

- custody, solvency, collateral, liquidation, accounting, governance, bridge, cross-chain, or upgrade invariants;
- high or concentrated value at risk;
- irreversible state transitions or privileged upgrade paths;
- novel cryptography, state machines, or economic mechanisms;
- code whose failure could create systemic, legal, or safety impact.

Select the method—Certora, Halmos, SMT/model checking, property testing, symbolic execution, or another maintained approach—from the property and toolchain. Document the properties proved, assumptions, environment, solver/tool version, coverage gaps, and unproved obligations.

Do not use a fixed `$1M TVL` threshold as the sole trigger, and do not treat a proof of selected properties as a complete security audit.''',
)
replace_once(
    "community/specialists/blockchain-engineer.md",
    "Minimum acceptable optimization: 10% reduction on the target function, or explicit documentation of why further reduction is not possible without sacrificing safety. Gas reports are attached to the PR — not optional.",
    "The optimization target is defined by the operator and use case. Report measured improvement or explain why no safe, maintainable reduction is justified. Reject optimizations that weaken invariants, readability, auditability, upgrade safety, or compatibility. Gas reports are attached to the PR — not optional.",
)

write(
    "docs/methodology/research-analytics-security-assurance-2026-08-05.md",
    '''# Research, Analytics, and Security Assurance Refresh — 2026-08-05

This tranche closes the two scope-depth findings and performs an independent second opinion on the five-card security lane.

## Research depth

The researcher retains broad cross-domain capability but now activates explicit minimum evidence protocols for history, anthropology, geography, psychology, narratology, market research, investment research, and unfamiliar domains. A claim ledger prevents framework name-dropping from substituting for evidence.

## High-risk analytics

The data analyst now has a complete model-QA protocol covering intended use, harm modeling, data lineage, split design, leakage, baselines, calibration, fairness-metric selection, intersectional slices, robustness, explainability, recourse, reproducibility, go/no-go conditions, and monitoring.

The protocol follows the principle reflected in NIST AI RMF resources: validity, reliability, fairness and harmful bias, privacy, explainability, safety, security, and monitoring are evaluated in context and documented. No one metric proves trustworthiness.

## Independent security-lane findings

- `security-engineer` now has a written authorization and scope gate from the regulated refresh; no additional content reduction was required.
- `malware-analyst` has authorization, containment, CAPEv2 lifecycle, and evidence-integrity controls from the native-operations refresh.
- `red-team-advisor` already had strong RoE controls; this tranche adds current DORA TLPT / TIBER-EU / CBEST applicability and removes direct-command wording from the advisory template.
- `devsecops-engineer` contradicted its own immutable-pinning rule through mutable action tags. Canonical examples now require verified full-length commit SHAs and risk-derived credential lifetimes.
- `blockchain-engineer` had rigid TWAP, TVL, gas, and toolchain assumptions. These are now risk-, compatibility-, and evidence-derived while retaining its full implementation and audit depth.

## Primary authorities reviewed

- GitHub secure-use and Actions policy documentation on full-length SHA pinning.
- ECB TIBER-EU framework updated for DORA.
- European Supervisory Authorities' in-force DORA TLPT Regulatory Technical Standards.
- Bank of England CBEST Implementation Guide and current CBEST / STAR-FS materials.
- NIST AI RMF and AIRC testing, evaluation, verification, validation, fairness, bias, validity, and monitoring resources.
''',
)

write(
    "tests/test_research_analytics_security_assurance.py",
    '''import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECIALISTS = ROOT / "community" / "specialists"


def text(name: str) -> str:
    return (SPECIALISTS / name).read_text(encoding="utf-8")


def test_researcher_has_domain_evidence_depth() -> None:
    card = text("researcher.md")
    assert "Consolidates and preserves the durable methods" in card
    assert "## Domain Activation and Minimum Evidence" in card
    for heading in ["### History", "### Anthropology", "### Geography", "### Psychology", "### Narratology", "### Market Research", "### Investment Research", "### General / New Domain"]:
        assert heading in card
    assert "## Cross-Domain Claim Ledger" in card
    assert "Three URLs repeating one original source are not triangulation" in card
    assert "Replaces all 7 original" not in card


def test_data_analyst_has_high_risk_model_qa_protocol() -> None:
    card = text("data-analyst.md")
    assert "## ML Model QA and Responsible Analytics Protocol" in card
    for phrase in ["Data Reconstruction and Leakage", "Fairness and Harmful-Bias Evaluation", "equalized odds", "calibration by group", "intersectional slice", "CONDITIONAL GO", "RESEARCH ONLY"]:
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
''',
)
