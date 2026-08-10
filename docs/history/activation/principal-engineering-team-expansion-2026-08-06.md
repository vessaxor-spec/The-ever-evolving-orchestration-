# Principal Engineering Team Expansion

Date: 2026-08-06
Status: approved foundation

## Decision

TEO expands from six teams to a target of ten teams and from 56 specialists to a target of 78 specialists.

The expansion adds four responsibility-owning teams:

1. Platform and Reliability
2. Systems Engineering
3. Physical Systems
4. Assurance

It also approves 22 new specialist roles and four existing-specialist reallocations. The new teams are established by charter in this change, but their routes remain inactive until their workers, specialists, capabilities, fallbacks, verification rules, and conformance fixtures exist.

## Why the six-team structure was insufficient

The original six teams established a sound control plane for coordination, planning, software execution, research, review, and verification. They did not provide sufficiently precise ownership for several principal-engineering disciplines.

The main structural problems were:

- shared platforms, networks, operational databases, reliability, performance, ML operations, and technology economics were compressed into general Engineering;
- systems engineering was confused with systems programming through the `rust-engineer` worker binding;
- physical engineering domains were split between Planning and Engineering despite requiring physical integration, qualification, and lifecycle controls;
- technical privacy, functional safety, formal correctness, and application security lacked a team that owns assurance claims and evidence construction;
- Review and Verification were at risk of becoming catch-all teams rather than preserving their independent challenge and acceptance missions.

## Responsibility model

### Planning

Planning owns architecture, decomposition, tradeoffs, sequencing, and execution contracts.

### Systems Engineering

Systems Engineering owns stakeholder needs, system requirements, interfaces, allocation, integration, technical baselines, verification and validation planning, and lifecycle coherence.

### Engineering

Engineering owns software and product implementation.

### Platform and Reliability

Platform and Reliability owns shared technical foundations, distributed systems, operational databases, networks, internal platforms, deployment systems, production reliability, cross-stack performance, ML lifecycle infrastructure, and technology economics.

### Physical Systems

Physical Systems owns engineering where correctness depends on hardware, materials, structures, motion, power, environment, manufacturing, or real-world operation.

### Research

Research owns evidence discovery, user and market research, analytics, and applied scientific investigation.

### Assurance

Assurance owns specialist claims and evidence requirements for privacy, functional safety, formal correctness, application security, and assurance cases.

### Review

Review independently challenges plans, implementations, claims, assumptions, evidence, and residual risk.

### Verification

Verification independently determines whether acceptance criteria and evidence are sufficient.

### Mission Control

Mission Control owns classification, dispatch, sequencing, fallback, escalation, and completion control.

## Approved new specialists

### Planning

- cloud-architect

### Engineering

- mobile-engineer
- compiler-toolchain-engineer

### Platform and Reliability

- distributed-systems-engineer
- database-reliability-engineer
- network-engineer
- platform-engineer
- performance-engineer
- finops-engineer
- site-reliability-engineer
- mlops-engineer

### Systems Engineering

- systems-requirements-engineer

### Physical Systems

- hardware-engineer
- robotics-autonomous-systems-engineer
- silicon-asic-engineer
- aerospace-satellite-engineer
- manufacturing-engineer

### Research

- applied-scientist

### Assurance

- privacy-engineer
- functional-safety-engineer
- formal-methods-engineer
- application-security-engineer

## Existing specialist migration map

The following are allocation changes only. Their practitioner-grade role cards must remain intact.

| Specialist | Current primary team | Approved primary team |
|---|---|---|
| devops-engineer | Engineering | Platform and Reliability |
| devsecops-engineer | Engineering | Platform and Reliability |
| embedded-engineer | Engineering | Physical Systems |
| civil-engineer | Planning | Physical Systems |

The `rust-engineer` worker binding changes from `systems_engineering` to `rust_systems_programming`. This prevents language and runtime expertise from being mistaken for system-lifecycle engineering.

## Non-duplication boundaries

The approved specialists remain distinct through explicit ownership boundaries:

- DevOps owns infrastructure-as-code and delivery automation. Site Reliability Engineering owns production reliability, SLOs, error budgets, toil, and production readiness.
- AI Engineering owns product AI and inference systems. MLOps owns reproducible model lifecycle infrastructure and operations.
- Data Engineering owns pipelines, warehouses, streaming, and analytical data quality. Database Reliability owns operational database fleets, replication, failover, restore, and database SLOs.
- The general Architect owns cross-domain architecture. Cloud Architecture owns cloud-specific topology, landing zones, service selection, residency, and cloud migration.
- Security Engineering owns broad security architecture and review. Application Security Engineering owns application-layer control design and regression assurance.
- Compliance determines legal and framework applicability. Privacy Engineering implements and assures technical privacy properties.
- QA executes broad quality testing. Performance Engineering owns cross-stack workload models, diagnosis, saturation analysis, capacity, and benchmark validity.
- Systems Engineering owns lifecycle coherence. Rust Systems Programming owns Rust language, runtime, unsafe-code, FFI, and low-level implementation expertise.

## Activation boundary

This decision does not create active routes merely by naming teams or specialists.

A team or worker route becomes active only after all required artifacts exist:

- team charter;
- worker definition;
- specialist card;
- capability mapping;
- implementation route;
- provider-diverse routine fallback;
- independent verification;
- conformance fixture;
- critical-risk human approval where applicable;
- freshness and canonical-preservation controls.

Until then, the new team is an accepted organizational responsibility with staged activation.

## Evidence-pilot boundary

The six-card evidence-backed freshness pilot remains exactly scoped to legal operations, tax, lending, compliance, civil engineering, and embedded systems.

The 22 new specialist cards must use freshness-aware authoring and primary-authority research where consequential claims are involved. They must not be added to the evidence-pilot registry until the pilot's maintainability gate has passed.

## Implementation sequence

1. Establish team charters, routing taxonomy, activation gates, and migration map.
2. Add Platform and Reliability plus Systems Engineering workers and specialists.
3. Add Physical Systems workers and specialists and reallocate Civil and Embedded.
4. Add Assurance workers and specialists.
5. Add Cloud Architecture, Mobile, Compiler and Toolchain, and Applied Science.
6. Complete deterministic routing, capability mappings, provider-diverse fallbacks, conformance, and verification controls.
7. Create an immutable completion capsule only after the full architecture is implemented and validated.

## Authoritative reference basis

The team separation is informed by current primary or discipline-authoritative sources:

- ISO/IEC/IEEE 15288:2023, system life cycle processes: https://www.iso.org/standard/81702.html
- ISO/IEC/IEEE 24748-2:2024, application guidance for system life cycle processes: https://www.iso.org/standard/84661.html
- NASA Systems Engineering Handbook: https://www.nasa.gov/reference/systems-engineering-handbook/
- CNCF platform-engineering overview: https://www.cncf.io/blog/2025/11/19/what-is-platform-engineering/
- Google Site Reliability Engineering books: https://sre.google/books/
- FinOps Framework: https://www.finops.org/framework/
- NIST Privacy Engineering Program: https://www.nist.gov/privacy-engineering
- NIST formal-methods guidance: https://www.nist.gov/publications/formal-methods-statistical-software
- IEC 61508 functional-safety series overview: https://webstore.iec.ch/en/publication/5514
- MLOps principles: https://ml-ops.org/content/mlops-principles

These references establish discipline boundaries. They do not make every named standard universally applicable. Each consequential specialist must resolve current applicability, adopted or contractual edition, jurisdiction, use case, authority, and effective date.
