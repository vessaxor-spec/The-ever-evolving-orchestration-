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


# Civil engineering: distinguish latest publication from governing adoption.
replace_between(
    "community/specialists/civil-engineer.md",
    "## Code Edition Awareness",
    "## Load Path Tracing",
    '''## Governing Code and Edition Protocol

The latest published standard is not automatically the governing standard. Before any calculation, resolve all four layers:

1. **Governing jurisdiction** — authority having jurisdiction, permit authority, national annex, and local amendments.
2. **Adopted edition** — the edition legally adopted for this project location and date.
3. **Contractual edition** — the edition named in the contract, basis of design, or owner requirements.
4. **Latest published edition** — use as a change and risk reference; do not silently substitute it for the adopted edition.

Every calculation header records:

| Field | Required value |
|---|---|
| Jurisdiction / authority | Country, state, city, permitting authority, or owner standard |
| Adopted code and edition | Exact standard identifier and adoption source |
| Contractual code and edition | Exact identifier, or `not specified` |
| Latest published edition checked | Exact identifier and verification date |
| Local amendments / national annex | Document identifier and effective date |
| Conflict resolution | Which requirement governs and who approved the decision |

As of `tools_last_verified`, ACI publishes ACI CODE-318-25. Second-generation Eurocodes are in a staged national transition: availability to National Standards Bodies, national publication, national annexes, and withdrawal of conflicting first-generation standards occur on different dates. These facts are context only. Verify the adopted edition and transition rules for the project jurisdiction before use.

If the adopted and contractual editions conflict, stop and escalate to the Engineer of Record, authority having jurisdiction, and contract owner. Do not blend provisions across editions without an approved code-comparison memo.''',
)

# Embedded systems: edition-aware MISRA compliance rather than a 2012 mandate.
replace_between(
    "community/specialists/embedded-engineer.md",
    "## MISRA C Compliance Declaration",
    "## Stack Overflow Detection",
    '''## MISRA Compliance Declaration

Every firmware project declares the coding-standard edition actually required by its safety case, certification plan, contract, regulator, and toolchain. Do not default to MISRA C:2012 merely because an older template used it.

```text
Coding standard: [MISRA C / MISRA C++ / project standard]
Edition and amendments: [exact licensed publication identifiers]
Governing basis: [contract / certification plan / regulator / internal safety standard]
Compliance posture: [Mandatory / Required / Advisory]
Deviation record: [file] — rule, rationale, risk, approver, review date
Enforcement tools and versions: [tool + supported standard edition]
Evidence date: [YYYY-MM-DD]
```

Rules:

- Verify the current official MISRA publication set and the edition required by the project before generating a compliance declaration.
- Verify that the selected static-analysis tool supports the exact edition, amendments, and rule interpretations being claimed.
- Safety-critical targets require zero undocumented deviations and independent review of deviation permits.
- Consumer or non-certified targets may use an advisory posture only when the operator approves the reduced assurance level.
- A newer publication does not automatically override the edition incorporated by a certification plan; document any migration analysis.
- All reported violations are triaged before release and are never suppressed silently.

As of `tools_last_verified`, official MISRA publications include MISRA C:2025 materials. This is a freshness checkpoint, not a universal project mandate.''',
)

# UX: align the design authority with the repository's WCAG 2.2 baseline.
ux_path = "community/specialists/ux-designer.md"
ux_text = read(ux_path)
if ux_text.count("WCAG 2.1 AA") < 5:
    raise SystemExit("Expected multiple WCAG 2.1 AA references in ux-designer.md")
ux_text = ux_text.replace("WCAG 2.1 AA", "WCAG 2.2 AA")
write(ux_path, ux_text)
insert_before(
    ux_path,
    "## Heuristic Evaluation Protocol",
    '''## Accessibility Standard Applicability

WCAG 2.2 AA is the default TEO design baseline because it is backward-compatible with WCAG 2.1 and adds current interaction and cognitive-accessibility requirements. The governing legal or contractual standard may still incorporate another WCAG version or EN 301 549 edition; document that mapping rather than lowering the design baseline silently.

Every accessibility handoff records:

| Field | Required value |
|---|---|
| Design baseline | WCAG 2.2 AA unless explicitly approved otherwise |
| Governing law / contract | Jurisdiction, regulation, procurement requirement, or `none identified` |
| Incorporated standard | Exact WCAG / EN 301 549 / ISO edition and verification date |
| Additional platform guidance | Mobile, desktop, kiosk, XR, or assistive-technology requirements |
| Exceptions | Criterion, rationale, compensating measure, owner, and remediation date |

WCAG 2.2 additions that must be represented in component and flow specifications include focus visibility and non-obscuration, dragging alternatives, target size, consistent help, redundant-entry reduction, and accessible authentication. The UX baseline may be stricter than the minimum incorporated by a local rule, but it must never be weaker than the implementation and QA acceptance criteria.''',
)

# Tax: current terminology, Pillar Two, and jurisdiction-specific reporting thresholds.
replace_once(
    "community/specialists/tax-strategist.md",
    "  - international tax (BEPS, GILTI, FDII)",
    "  - international tax (BEPS, Pillar Two, NCTI/GILTI, FDDEI/FDII transitions)",
)
insert_before(
    "community/specialists/tax-strategist.md",
    "## BEPS Action Plan Applicability",
    '''## Current International Tax Regime Verification

International tax terminology, deductions, foreign-tax-credit mechanics, effective dates, and transition rules are volatile. Before using GILTI, FDII, NCTI, FDDEI, QBAI, Section 250, or related labels in a recommendation:

1. identify the taxpayer type and tax year;
2. verify the enacted statute and current Treasury / IRS guidance;
3. identify whether legacy forms or instructions still use earlier terminology during transition;
4. model the current calculation rather than applying a historical percentage from this card;
5. record unresolved guidance and require tax counsel for implementation.

For tax years affected by Public Law 119-21, verify the current Section 250 and Section 951A terminology and calculations, including any changes to deductions, QBAI treatment, and foreign-tax-credit mechanics. Do not treat a dated summary as a substitute for the statute, regulations, notices, forms, and instructions applicable to the return year.''',
)
insert_before(
    "community/specialists/tax-strategist.md",
    "## Substance Requirements",
    '''## Pillar Two / Global Minimum Tax Applicability

BEPS Actions 1–15 do not replace the separate Pillar Two analysis. For every multinational group, determine whether the Global Anti-Base Erosion rules or a domestic implementation applies.

| Area | Required determination |
|---|---|
| Scope | Consolidated-revenue test, excluded entities, ownership period, and jurisdiction-specific implementation |
| Charging rules | IIR, UTPR, and any domestic minimum top-up tax or QDMTT |
| Effective dates | Fiscal-year start, transition rules, safe harbours, and local enactment status |
| Computation | GloBE income or loss, covered taxes, effective tax rate, substance-based income exclusion, top-up tax |
| Filing | GloBE Information Return, local notifications, central filing / exchange eligibility, and local deadlines |
| Governance | Data owner, calculation owner, review, controls, and sign-off |

The OECD model and information-return materials are authoritative references, but obligations and deadlines arise through implementing jurisdictions. Never state a universal first-filing deadline without verifying the fiscal year and each relevant jurisdiction.''',
)
replace_between(
    "community/specialists/tax-strategist.md",
    "## Country-by-Country Reporting (CbCR)",
    "## Research Protocol",
    '''## Country-by-Country Reporting (CbCR)

CbCR scope and filing thresholds are jurisdiction-specific. The OECD model commonly uses a EUR 750 million consolidated-revenue threshold or a domestic-currency equivalent, while domestic rules, exchange relationships, surrogate-parent rules, and local-filing triggers differ.

For every engagement approaching a relevant threshold:

- verify the ultimate-parent jurisdiction's enacted threshold and currency;
- identify reporting fiscal year, filing deadline, notification deadline, and exchange relationships;
- determine whether parent, surrogate-parent, or local filing applies;
- reconcile revenue, profit, tax, employees, and assets with transfer-pricing documentation and financial statements;
- flag inconsistent CbCR, master-file, local-file, and Pillar Two data as an audit risk.

Do not use `$750M` as a universal threshold. State the governing jurisdiction, currency, threshold, source, and verification date.''',
)

# AI compliance: add the missing legal and management-system lane.
replace_once(
    "community/specialists/compliance-auditor.md",
    "  - risk assessment",
    "  - risk assessment\n  - AI regulatory classification and governance",
)
replace_once(
    "community/specialists/compliance-auditor.md",
    "  - NIST CSF",
    "  - NIST CSF\n  - EU AI Act\n  - ISO/IEC 42001\n  - NIST AI RMF",
)
replace_once(
    "community/specialists/compliance-auditor.md",
    "- Verify agentic identity and trust in multi-agent systems: who can invoke what, with what authority, and how is it verified",
    "- Verify agentic identity and trust in multi-agent systems: who can invoke what, with what authority, and how is it verified\n- Classify AI-system roles, risk, transparency, governance, and evidence obligations under applicable law and policy",
)
insert_before(
    "community/specialists/compliance-auditor.md",
    "## NIST CSF 2.0 — Govern Function",
    '''## AI Governance Applicability Protocol

For every AI or agentic-system review, identify the organization, system, use case, affected people, geography, and lifecycle role before mapping controls.

**Required classification:**

| Dimension | Required determination |
|---|---|
| Legal role | Provider, deployer, importer, distributor, product manufacturer, GPAI provider, or other applicable role |
| Risk / use category | Prohibited, transparency-regulated, high-risk, product-integrated, limited/minimal risk, or outside scope |
| Affected obligations | Data governance, technical documentation, logging, human oversight, accuracy, robustness, cybersecurity, transparency, registration, post-market duties |
| Effective date | Exact provision, transition rule, grandfathering rule, and verification date |
| Management system | Whether ISO/IEC 42001 or another AIMS framework is required or voluntarily adopted |
| Risk framework | Current NIST AI RMF version/profile or another approved framework; note when revision is pending |
| Evidence | System inventory, impact assessment, model/system card, evaluation results, incident log, change record, accountability owner |

The EU AI Act is phased and has been amended. As of `tools_last_verified`, Article 50 transparency obligations apply from 2 August 2026; high-risk timelines differ for Annex III use cases and AI embedded in regulated products. Verify the current Commission timeline and the exact use case before asserting an obligation.

ISO/IEC 42001 is an AI management-system standard, not proof that a specific AI system complies with law. NIST AI RMF is voluntary and versioned. Use these frameworks to organize governance and evidence, but do not substitute them for legal applicability analysis or sector-specific requirements.''',
)

# Supply chain: add CBAM only when goods and thresholds are in scope.
replace_once(
    "community/specialists/supply-chain-strategist.md",
    "- Customs duties and tariffs (current rate + tariff risk premium)",
    "- Customs duties, tariffs, and applicable border measures (including CBAM when goods, origin, importer, and thresholds are in scope)",
)
insert_before(
    "community/specialists/supply-chain-strategist.md",
    "## Supplier Financial Health Monitoring",
    '''## EU CBAM Applicability Check

For an EU import flow, determine CBAM scope before finalizing total landed cost. CBAM does not apply to every EU-bound product.

| Check | Required evidence |
|---|---|
| Goods scope | CN code and whether the product is a covered CBAM good |
| Importer role | EU importer or indirect customs representative responsible for compliance |
| Threshold / exemption | Annual imported mass, applicable exemption, and verification date |
| Authorisation | Whether authorised CBAM declarant status is required and held |
| Embedded emissions | Supplier data, methodology, verifier requirements, and data-quality gaps |
| Certificate exposure | Forecast quantity, certificate-price assumption, timing, and sensitivity |
| Filing | Registry, declaration, surrender, record-retention, and responsible owner |

As of `tools_last_verified`, the definitive regime applies from 1 January 2026 and the Commission describes a 50-tonne mass threshold for covered goods. Verify current legislation, product scope, thresholds, transitional measures, certificate mechanics, and competent-authority guidance for the actual import flow. Show CBAM as a separate landed-cost and compliance line rather than hiding it inside customs duty.''',
)

# Lending: remove universal eligibility cutoffs and route decisions through current guides/AUS.
replace_between(
    "community/specialists/loan-officer-assistant.md",
    "## Loan Program Decision Tree",
    "## Condition Triage",
    '''## Loan Program Eligibility and Cost Protocol

Program eligibility is determined from current agency, investor, lender-overlay, AUS, and jurisdiction-specific requirements. Credit-score, down-payment, DTI, mortgage-insurance, funding-fee, and loan-limit values in historical templates must not be used as universal approval rules.

**Required comparison:**

| Program | Current authoritative guide | AUS / manual path | Borrower eligibility | Property eligibility | Cash requirement | Insurance / guarantee cost | Key overlays |
|---|---|---|---|---|---|---|---|
| Conventional | Current Fannie Mae / Freddie Mac selling guide and lender overlays | DU / LPA / manual as permitted | Verify | Verify | Calculate | Verify current PMI terms | Record |
| FHA | Current HUD handbook, mortgagee letters, and lender overlays | TOTAL / manual as permitted | Verify | Verify | Calculate | Verify current upfront and annual MIP | Record |
| VA | Current VA lender handbook, circulars, and lender overlays | AUS / manual | Verify service and entitlement | Verify | Calculate | Verify funding-fee and exemption status | Record |
| USDA | Current USDA handbook, notices, eligibility map, and lender overlays | GUS / manual as permitted | Verify income and program eligibility | Verify rural eligibility | Calculate | Verify guarantee fees | Record |

Show trade-offs and route the final credit decision to the authorized underwriter.

## DTI and Ability-to-Repay Analysis

Calculate and display:

```text
Front-end DTI = monthly housing payment / gross monthly income
Back-end DTI = all recurring monthly debt / gross monthly income
```

DTI remains an underwriting and affordability input, but it is not a universal legal approval cutoff. The General QM definition no longer uses a universal 43% DTI ceiling; it uses price-based thresholds together with ability-to-repay requirements. Agency programs, AUS findings, manual-underwriting guides, lender overlays, residual-income tests, and compensating factors can produce different limits.

Rules:

- verify the current General QM rule and applicable loan-program guide;
- use current DU, LPA, TOTAL, GUS, or authorized manual-underwriting findings;
- distinguish regulatory QM status from investor eligibility and lender overlays;
- do not disqualify a borrower solely because back-end DTI exceeds 43%;
- do not guarantee approval from an AUS result;
- present monthly affordability, reserves, payment shock, residual income, and layered risk alongside DTI.

## Mortgage Insurance and Program Fee Verification

Calculate PMI, MIP, guarantee fees, and funding fees from the current program, insurer, borrower profile, LTV, term, and exemption status. Do not use a generic percentage range as a quote. State the source and date, show the monthly and cash-to-close effect, and require LO review before communicating the result.''',
)

# Real estate: add the post-settlement buyer-agreement and MLS compensation rules with scope qualifiers.
insert_before(
    "community/specialists/real-estate-agent.md",
    "## CMA Output Format",
    '''## Buyer Representation and MLS Compensation Protocol

Before the first property tour, identify the jurisdiction, brokerage policy, MLS participation, agency relationship, and applicable written-agreement requirements.

For MLS Participants subject to the NAR settlement practice changes, unless inconsistent with state or federal law:

- enter into a written buyer agreement before an in-person or live-virtual tour;
- disclose services, agreement term, and compensation in an objectively ascertainable manner;
- state conspicuously that broker fees and commissions are negotiable and not set by law;
- do not accept compensation above the amount or rate agreed with the buyer;
- do not place or rely on offers of buyer-broker compensation in the MLS;
- document any seller concession or off-MLS compensation discussion separately and consistently with law, MLS rules, and brokerage policy.

These are association / MLS practice requirements, not a substitute for state licensing law, agency law, contract review, or brokerage supervision. Verify the current MLS rules and approved forms before advising or drafting transaction documents.''',
)
replace_once(
    "community/specialists/real-estate-agent.md",
    "- Does not represent both buyer and seller in the same transaction without disclosed dual agency consent",
    "- Does not represent both buyer and seller in the same transaction without disclosed dual agency consent\n- Does not begin buyer tours until any applicable written buyer-representation agreement and compensation disclosures are completed",
)

# Security: require authorization and add public-company disclosure applicability.
replace_once(
    "community/specialists/security-engineer.md",
    "- Does not access production systems, live credentials, or customer data",
    "- Does not access production systems, live credentials, or customer data\n- Requires documented asset-owner authorization, written scope, permitted techniques, testing window, data-handling rules, and stop conditions before any active security testing or audit execution",
)
insert_before(
    "community/specialists/security-engineer.md",
    "## Threat Intelligence Doctrine",
    '''## Authorization and Scope Gate

Before any security assessment, record:

| Field | Required value |
|---|---|
| Authorizing owner | Named asset owner or delegated authority |
| In-scope assets | Repositories, applications, contracts, accounts, environments, ranges |
| Out-of-scope assets | Explicit exclusions and third-party systems |
| Permitted actions | Review-only, scanning, fuzzing, test transactions, or other approved techniques |
| Environment and window | Non-production / production, dates, rate limits, maintenance window |
| Data handling | Credentials, logs, PII, secrets, evidence storage, retention, deletion |
| Stop conditions | Instability, unexpected access, sensitive-data exposure, scope ambiguity |
| Escalation contacts | Operator, incident commander, legal/compliance, system owner |

Without authorization and scope, limit work to passive review of operator-provided material. Do not probe, scan, exploit, transact, or access systems based solely on a public endpoint or repository URL.''',
)
replace_once(
    "community/specialists/security-engineer.md",
    "4. **Regulatory notification triggers** — GDPR: 72h to supervisory authority if personal data affected; HIPAA: 60 days to HHS if PHI affected; PCI DSS: notify card brands and acquirer immediately",
    "4. **Regulatory and contractual notification triggers** — identify jurisdiction, entity type, affected data, materiality, discovery/determination time, regulator, customer, insurer, law-enforcement, and contract obligations. Examples requiring applicability checks include GDPR supervisory-authority notification, HIPAA breach notification, payment-card obligations, and—for SEC-reporting companies—Form 8-K Item 1.05 generally within four business days after determining that a cybersecurity incident is material, subject to the rule's exceptions and delay process",
)

# Source-backed methodology note for this tranche.
write(
    "docs/methodology/regulated-specialist-refresh-2026-08-05.md",
    '''# Regulated and Life-Safety Specialist Refresh — 2026-08-05

This tranche updates high-risk specialist content without turning the cards into static legal or standards databases.

## Governing rule

A current publication is not automatically the governing requirement. Each specialist now resolves jurisdiction, legal role, adopted edition, contract, effective date, transition rule, applicability, and approving authority before issuing consequential guidance.

## Primary authorities reviewed

- American Concrete Institute: ACI CODE-318-25 and the ACI 318 Building Code Portal.
- European Commission Joint Research Centre: second-generation Eurocode availability, national publication, and withdrawal timeline.
- MISRA official publications and addenda for current MISRA C materials.
- W3C: WCAG 2.2 and ISO/IEC 40500:2025 status.
- IRS / enacted U.S. law materials for Section 250 and international-tax transitions.
- OECD: Pillar Two GloBE Model Rules and GloBE Information Return materials.
- European Commission: AI Act and AI Omnibus implementation timeline.
- ISO: ISO/IEC 42001:2023 AI management systems.
- NIST: AI RMF 1.0 and current revision status.
- European Commission Taxation and Customs Union: CBAM definitive regime.
- Consumer Financial Protection Bureau: General QM price-based definition replacing the 43% DTI limit.
- National Association of REALTORS®: written buyer agreements and 2024 MLS practice changes.
- U.S. Securities and Exchange Commission: Form 8-K Item 1.05 material cybersecurity incident disclosure.

## Preservation

The refresh adds applicability, evidence, authorization, and escalation controls. It does not replace licensed engineering, legal, tax, lending, real-estate, compliance, or security professionals and does not authorize execution outside each role card's existing boundaries.
''',
)

write(
    "tests/test_regulated_specialist_refresh.py",
    '''from pathlib import Path

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
    assert "2 December 2027" in card
    assert "2 August 2028" in card


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
''',
)
