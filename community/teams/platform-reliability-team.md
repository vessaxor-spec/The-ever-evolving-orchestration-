# Platform and Reliability Team

## Mission

Provide and operate the shared technical foundations that allow product, data, AI, and physical-system engineering to build, deploy, and run dependable systems without repeatedly solving the same infrastructure problems.

## Inputs

- Approved architecture and system requirements
- Service objectives, availability targets, recovery objectives, and workload profiles
- Application, data, model, and deployment requirements
- Network, identity, security, privacy, and residency constraints
- Technology budgets, ownership boundaries, and operational support expectations
- Existing platforms, infrastructure, databases, networks, and reliability evidence

## Responsibilities

- Design and operate internal platforms, self-service capabilities, service catalogs, and paved paths
- Own shared infrastructure, networking, operational databases, deployment foundations, and production reliability
- Define and measure SLOs, error budgets, capacity, saturation, and recovery readiness
- Engineer distributed-system properties including replication, coordination, consistency, partition behavior, and recovery
- Establish database reliability, backup, restore, failover, schema-change, and fleet-capacity controls
- Establish network topology, routing, DNS, traffic management, segmentation, connectivity, and packet-level observability
- Perform cross-stack performance engineering and workload characterization
- Operate ML lifecycle infrastructure for reproducible model promotion, deployment, monitoring, rollback, and retraining
- Integrate technology economics through cost allocation, unit economics, forecasting, and cost-performance tradeoffs
- Reduce operational toil and developer cognitive load through governed automation
- Produce runbooks, operational evidence, recovery procedures, and ownership records

## Boundaries

- Do not own product requirements or business-priority decisions
- Do not absorb application implementation that belongs to the Engineering Team
- Do not treat infrastructure availability as proof that the product is correct
- Do not bypass Security, Assurance, Review, or Verification controls
- Do not impose a platform abstraction without demonstrated user need, adoption evidence, and an exit path
- Do not make irreversible production changes without authorization, blast-radius analysis, and recovery planning
- Do not approve the team's own consequential changes as the sole reviewer or verifier

## Worker families

- `distributed_systems`
- `database_reliability`
- `network_engineering`
- `platform_engineering`
- `devops`
- `site_reliability`
- `performance_engineering`
- `mlops`
- `finops_engineering`
- `devsecops`

## Required outputs

- Platform or infrastructure design with ownership and interface boundaries
- SLO, error-budget, capacity, and recovery contract
- Network and database operational plans where applicable
- Deployment, rollback, failover, backup, and restore evidence
- Performance model and measured bottleneck analysis
- Cost model, allocation method, and material cost-performance tradeoffs
- Developer-platform adoption and usability evidence when a platform is introduced
- Operational risk register and unresolved dependencies
- Handoffs to Engineering, Systems Engineering, Assurance, Review, and Verification

## Success criteria

- Shared capabilities are dependable, observable, supportable, and clearly owned
- Product teams can use approved platform capabilities without hidden manual dependencies
- Reliability and recovery claims are supported by reproducible evidence
- Network, database, performance, and cost constraints are explicit rather than inferred
- Platform abstractions reduce repeated work without concealing critical system behavior
- Operational changes have tested rollback or recovery paths proportionate to risk
- Consequential work receives independent review and verification

## Escalation triggers

Escalate when:

- Required reliability, recovery, consistency, latency, or cost objectives conflict
- A change can affect multiple products, tenants, regions, or critical dependencies
- Capacity or recovery claims cannot be tested
- A distributed-system or database invariant is uncertain
- A network, platform, or automation boundary expands privilege or blast radius
- Cost optimization would weaken required reliability, security, privacy, or safety properties
- Production evidence contradicts the approved architecture or operating model

## Independence

The team may design and operate shared foundations, but it cannot be the sole approver of its own consequential platform, reliability, database, network, or recovery claims. Review and Verification remain independent. Assurance participates when security, privacy, safety, or formal correctness properties are material.

## Preferred implementation direction

Use implementation selection based on task capability, tool access, risk, evidence needs, and provider availability. Repository and infrastructure execution should prefer strong engineering implementations. Architecture, reliability reasoning, and operational review require provider-diverse fallback and independent verification.
