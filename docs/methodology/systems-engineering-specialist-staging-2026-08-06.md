# Systems Engineering Specialist Staging

Date: 2026-08-06

## Decision

TEO now has a staged Systems and Requirements Engineer specialist and a matching `systems_requirements` worker definition.

This addition establishes the responsibility surface but does not activate a routable Systems Engineering Team. Activation remains blocked until the route, capability mapping, provider-diverse fallback, and conformance dataset are implemented and independently validated.

## Why this specialist is distinct

Systems engineering is not interchangeable with software architecture, project planning, product management, Rust systems programming, component testing, or verification.

The specialist owns lifecycle coherence across software, hardware, humans, data, processes, facilities, suppliers, operations, support, and retirement. Its core assets are stakeholder needs, controlled requirements, allocations, interfaces, technical baselines, integration strategy, and verification and validation traceability.

Planning continues to own execution planning and architectural tradeoffs. Engineering and Physical Systems continue to implement allocated elements. Review challenges the requirements and assumptions. Verification independently checks the evidence. Accountable humans retain final acceptance and residual-risk authority.

## Standards posture

The standards statements were checked against official ISO records on 2026-08-06.

### ISO/IEC/IEEE 15288

[ISO/IEC/IEEE 15288:2023](https://www.iso.org/standard/81702.html) is published and defines system life cycle processes across the full lifecycle of human-made systems.

The specialist may use it as a current published reference, but it must still resolve contractual, jurisdictional, certification, organizational, and project-specific applicability before calling any edition governing.

### ISO/IEC/IEEE 29148

[ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) remains the current published requirements-engineering edition. ISO records it as confirmed in 2024 and scheduled for revision.

[ISO/IEC/IEEE DIS 29148 Edition 3](https://www.iso.org/standard/94091.html) is under development. It must not be represented as the published governing edition unless and until it is published or an authorized project explicitly adopts the draft as its contractual basis.

### Application rule

The specialist must distinguish among:

- current published edition
- draft under development
- jurisdiction-adopted edition
- contractual edition
- certification basis
- organizational process baseline
- project-authorized deviation or tailoring

The latest publication does not automatically override a contract, approved baseline, certification basis, law, regulator, or authorized project decision.

## Preservation boundary

The staged manifest records the Git blob SHA for both the specialist card and worker definition. Tests recompute those hashes from repository bytes.

This makes capability reduction, silent compression, or unreviewed responsibility changes visible. An intentional amendment requires an explicit update to the role card, the preservation record, and the relevant tests in the same reviewed change.

## Activation boundary

The following are complete:

- Systems Engineering Team charter
- Systems and Requirements Engineer role card
- `systems_requirements` worker definition
- independent verification requirements
- qualified-human approval boundary for critical and regulated acceptance
- freshness policy
- standards posture
- canonical preservation lock

The following remain required before activation:

- first-class routing policy
- stable capability mapping
- provider-diverse routine fallback
- route and worker conformance dataset

Until those gates pass:

- no task may select `systems_engineering` as an active primary team
- no task may select `systems_requirements` as an active worker
- the specialist must not be inserted into the canonical active specialist registry
- lifecycle systems-engineering work must not fall through to `rust-engineer` because of the former `systems_engineering` binding name

## Evidence-pilot boundary

This specialist is not added to the six-card regulated evidence pilot. The pilot remains limited to legal operations, tax, lending, compliance, civil engineering, and embedded systems until its maintainability gate is satisfied.

The specialist still requires current authoritative evidence for consequential standards claims. That obligation does not imply expansion of the pilot registry.
