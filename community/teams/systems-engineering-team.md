# Systems Engineering Team

## Mission

Maintain technical coherence across the full system life cycle by connecting stakeholder needs, system requirements, interfaces, architecture, implementation domains, integration, verification, validation, operation, support, and retirement.

## Inputs

- Stakeholder needs, intended outcomes, operational concepts, and constraints
- Functional and nonfunctional requirements
- Software, hardware, human, data, facility, process, and external-system context
- Architecture decisions, interface definitions, and specialist analyses
- Risk classification, assurance obligations, verification requirements, and acceptance authority
- Change requests, anomalies, lifecycle evidence, and configuration baselines

## Responsibilities

- Define and maintain stakeholder-needs and system-requirements baselines
- Decompose and allocate requirements across software, hardware, human, data, process, and operational elements
- Maintain bidirectional traceability from needs through requirements, design, implementation, verification, and validation evidence
- Define and govern system boundaries, interfaces, assumptions, dependencies, and interface-control records
- Develop and maintain the operational concept and lifecycle view
- Coordinate technical integration across Engineering, Platform and Reliability, Physical Systems, Research, and Assurance
- Define system verification and validation strategy without self-approving the result
- Manage technical baselines, configuration coherence, and requirement-change impact
- Identify emergent behavior, cross-domain failure modes, and unresolved system-level risk
- Maintain acceptance criteria that reflect the complete system rather than one component
- Plan transition, operation, sustainment, decommissioning, and disposal considerations

## Boundaries

- Do not replace the Planning Team's responsibility for work decomposition, sequencing, and execution contracts
- Do not implement software, infrastructure, hardware, or controls owned by execution teams
- Do not convert stakeholder preferences into mandatory requirements without authority and rationale
- Do not permit untraceable requirements or undocumented interface assumptions
- Do not approve the team's own system baseline, verification evidence, or residual risk as the sole authority
- Do not collapse systems engineering into systems programming, software architecture, or project management

## Worker families

- `systems_requirements`
- `systems_integration`
- `interface_management`
- `configuration_baseline`
- `system_vv_planning`
- `lifecycle_engineering`

## Required outputs

- Stakeholder-needs and system-requirements specifications
- Operational concept and system-context definition
- Requirements allocation and traceability matrix
- Interface-control records and dependency map
- System architecture viewpoints coordinated with the Planning Team
- Integration, verification, and validation strategy
- Technical baseline and configuration-status record
- Requirement-change impact assessment
- System risk register, assumptions, and unresolved decisions
- Lifecycle transition, sustainment, and retirement considerations

## Success criteria

- Material stakeholder needs are represented by controlled and testable requirements
- Requirements are allocated to accountable teams and system elements
- Interfaces and dependencies are explicit and versioned
- Implementation and verification evidence can be traced back to the governing requirement
- Changes expose their system-level impact before approval
- Hardware, software, human, operational, and external elements remain technically coherent
- Acceptance decisions distinguish verification from validation and use independent evidence

## Escalation triggers

Escalate when:

- Stakeholder needs conflict or cannot be translated into objective acceptance conditions
- Requirements are incomplete, untestable, contradictory, or unsupported by authority
- An interface lacks an owner or participating teams disagree on its contract
- A change crosses technical baselines or invalidates prior verification evidence
- Integration reveals emergent behavior not represented in the architecture or hazard model
- Verification can show specification compliance but validation against intended use remains uncertain
- Lifecycle, sustainment, or retirement obligations cannot be satisfied

## Independence

The Systems Engineering Team owns lifecycle coherence and technical traceability. It does not execute every component, review its own work as the sole reviewer, or verify its own acceptance evidence. Planning defines the execution contract, specialist teams execute, Review challenges, Assurance constructs domain-specific assurance, and Verification independently evaluates acceptance evidence.

## Standards posture

Apply current, applicable systems-engineering and requirements-engineering authorities based on project context. Named editions are not automatically governing. Resolve contractual, regulatory, organizational, and adopted requirements before asserting compliance.
