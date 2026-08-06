# Assurance Specialist Staging

Date: 2026-08-06
Status: staged, not active

## Decision

The Assurance Team receives four specialist specifications:

- Privacy Engineer
- Functional Safety Engineer
- Formal Methods Engineer
- Application Security Engineer

The team owns construction and maintenance of selected assurance claims, technical controls, requirements, methods, and evidence. It does not approve its own consequential work.

## Why a separate team is required

Review challenges claims and decisions. Verification determines whether evidence satisfies requirements. Compliance determines applicability, control mapping, and audit evidence. Broad Security owns enterprise and cross-domain security architecture.

Technical privacy, functional safety, formal correctness, and application-layer security each require deep engineering work before independent review and verification can occur. Placing these responsibilities entirely inside Review or Verification would make those teams both producer and assessor of the same assurance evidence.

## Specialist boundaries

### Privacy Engineering

Owns technical privacy properties, data and inference flows, minimization, purpose enforcement, de-identification, privacy-enhancing technologies, consent and preference controls, retention, deletion, privacy-safe telemetry, and control verification.

It does not issue legal opinions or compliance conclusions.

### Functional Safety

Owns safety lifecycle, hazard analysis, safety goals and requirements, integrity allocation, architecture constraints, independence, fault analysis, verification and validation planning, safety case, and production and operational safety evidence.

It does not replace regulator, certification, product, mission, flight, operator, or release authority.

### Formal Methods

Owns precise specifications, assumptions, invariants, model checking, theorem proving, refinement, implementation correspondence, proof-supported testing, and formal-evidence maintenance for selected critical properties.

It does not convert bounded or assumption-dependent evidence into an unlimited correctness claim and does not replace testing or system validation.

### Application Security

Owns application trust boundaries, authentication, authorization, sessions, input and output handling, file processing, integrations, business-logic abuse, secure code review, vulnerability remediation, and security regression evidence.

It does not replace broad Security architecture and does not conduct active testing without written authorization.

## Standards and authority checkpoint

The staging decision was checked against primary sources on 2026-08-06.

| Area | Current checkpoint | Primary source |
|---|---|---|
| Privacy engineering | NIST defines privacy engineering as a systems-engineering specialty focused on reducing problems caused by data processing | https://www.nist.gov/itl/applied-cybersecurity/privacy-engineering/about |
| Privacy Framework | Version 1.0 remains published; Version 1.1 remains an Initial Public Draft and is not governing by default | https://www.nist.gov/privacy-framework and https://www.nist.gov/privacy-framework/new-projects/privacy-framework-version-11 |
| Functional safety | IEC 61508 remains the horizontal functional-safety reference; IEC 61508-6:2010 is Edition 2.0 with a 2027 stability date | https://webstore.iec.ch/en/publication/5520 |
| Automotive safety | ISO 26262:2018 Edition 2 remains published; Edition 3 material is still in working-draft development | https://www.iso.org/publication/PUB200262.html and https://www.iso.org/standard/90021.html |
| Formal methods | Formal methods are mathematically based, useful for selected problem classes, and still require testing because assumptions and implementation mappings can fail | https://csrc.nist.gov/projects/automated-combinatorial-testing-for-software/autonomous-systems-assurance/formal-methods |
| Application security | OWASP ASVS 5.0.0 is the latest stable ASVS and versioned requirement references are recommended | https://owasp.org/www-project-application-security-verification-standard/ |

Latest publication does not automatically mean governing edition. Applicability must resolve jurisdiction, sector, contract, certification basis, organizational adoption, lifecycle, effective date, transition rule, and accountable authority.

## Independence model

```text
Assurance Team
  -> defines technical assurance requirements
  -> builds controls, analyses, and assurance arguments
  -> assembles traceable evidence

Review Team
  -> challenges scope, assumptions, claims, and residual risk

Verification Team
  -> independently reproduces checks and determines evidence sufficiency

Qualified human authority
  -> accepts critical residual risk or authorizes release
```

The same worker and implementation cannot be the sole producer, reviewer, verifier, and approver.

## Staged activation

This tranche completes:

- four specialist cards
- four worker contracts
- standards and draft-status checkpoints
- authority and independence boundaries
- critical human-approval requirements
- freshness policies
- exact canonical preservation controls

This tranche does not add an active route. Activation remains blocked until TEO has:

- capability mappings
- provider-diverse fallback policy
- conformance datasets
- deterministic classification and routing

## Preservation

The four new specialist cards and their worker contracts are locked to exact Git blob SHAs.

The existing Compliance Auditor and Security Engineer cards are also locked to prevent the new team from rewriting or reducing their established capabilities.

The six-card regulated evidence pilot remains unchanged. Assurance expansion does not authorize an evidence-registry rollout.
