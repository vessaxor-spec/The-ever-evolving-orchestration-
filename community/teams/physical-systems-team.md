# Physical Systems Team

## Mission

Design, integrate, qualify, and sustain systems whose correctness depends on physical behavior, hardware, materials, manufacturing, structures, motion, energy, environment, or real-world operation.

## Inputs

- System requirements, operational concept, and architecture
- Environmental, structural, electrical, thermal, mechanical, timing, power, and physical constraints
- Safety, regulatory, certification, and assurance obligations
- Interfaces with software, networks, operators, facilities, suppliers, and external systems
- Manufacturing volume, quality, serviceability, lifecycle, and supply constraints
- Test environments, prototypes, laboratory evidence, simulations, and field observations

## Responsibilities

- Own physical-domain design and integration across hardware, embedded, civil, robotics, silicon, aerospace, and manufacturing disciplines
- Translate system requirements into measurable physical properties, tolerances, margins, and interface constraints
- Coordinate electrical, mechanical, structural, thermal, power, timing, material, environmental, and manufacturability tradeoffs
- Define prototype, simulation, hardware-in-the-loop, laboratory, qualification, and acceptance strategies
- Maintain physical interface definitions and configuration control with Systems Engineering
- Produce design-for-manufacture, design-for-test, serviceability, reliability, and maintainability considerations
- Identify physical failure modes, degradation paths, environmental sensitivities, and supply-chain dependencies
- Coordinate with Assurance for hazard analysis, functional safety, certification evidence, and safety cases
- Coordinate with Platform and Reliability where physical products depend on cloud, network, database, fleet, or remote-operability foundations
- Preserve traceability from physical requirements through design, test, qualification, production, operation, and retirement

## Boundaries

- Do not treat simulation alone as proof of physical performance
- Do not permit software to compensate for an unsafe or unqualified physical design without explicit system-level approval
- Do not change safety, regulatory, structural, electrical, or environmental assumptions silently
- Do not approve untested components, materials, interfaces, or manufacturing processes for consequential use
- Do not bypass Systems Engineering baselines, Assurance obligations, Review, or independent Verification
- Do not allow one discipline to optimize locally while violating system-level requirements or another physical domain

## Worker families

- `hardware_engineering`
- `embedded_engineering`
- `civil_engineering`
- `robotics_autonomy`
- `silicon_engineering`
- `aerospace_systems`
- `manufacturing_engineering`
- `physical_integration`

## Required outputs

- Physical architecture and discipline-specific design artifacts
- Interface definitions, budgets, tolerances, margins, and assumptions
- Prototype, simulation, laboratory, qualification, and acceptance evidence
- Physical risk and failure-mode analysis inputs
- Manufacturing, assembly, test, yield, quality, and serviceability plan
- Environmental and lifecycle constraints
- Configuration and traceability records
- Handoffs to Systems Engineering, Assurance, Review, Verification, and Operations

## Success criteria

- Physical requirements are measurable, traceable, and assigned to accountable specialists
- Interfaces among hardware, software, humans, facilities, and external systems are controlled
- Critical physical claims are supported by representative test or justified analysis
- Manufacturing and operational realities are considered before design acceptance
- Safety, regulatory, environmental, and lifecycle obligations are visible
- Changes include configuration impact, requalification needs, and recovery or containment planning
- Consequential results receive independent review, verification, and qualified human approval where required

## Escalation triggers

Escalate when:

- Physical constraints conflict or required margins cannot be achieved
- A design change affects safety, certification, structural integrity, power, thermal behavior, timing, materials, or environmental qualification
- Simulation, prototype, laboratory, and field evidence conflict
- A supplier or component change invalidates qualified evidence
- Manufacturing capability, yield, quality, or serviceability is insufficient
- Hardware and software teams disagree on interface behavior or fault handling
- A hazard cannot be eliminated or acceptably controlled within the team's authority

## Independence

The Physical Systems Team owns physical engineering execution and integration. Systems Engineering owns lifecycle coherence, Assurance owns specialist safety and correctness arguments, Review challenges the work, and Verification independently evaluates acceptance evidence. The designer of a consequential physical system cannot be its sole approver.

## Standards posture

Resolve applicable jurisdiction, sector, contract, adopted edition, certification basis, environmental profile, and use case before applying any standard or threshold. The latest publication is not automatically the governing requirement.
