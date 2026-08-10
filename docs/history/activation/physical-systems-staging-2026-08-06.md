# Physical Systems Specialist Staging

Date: 2026-08-06
Status: staged, not active

## Decision

The Physical Systems Team receives five new specialist specifications:

- Hardware Engineer
- Robotics and Autonomous Systems Engineer
- Silicon and ASIC Engineer
- Aerospace and Satellite Engineer
- Manufacturing Engineer

Embedded Engineering and Civil Engineering are intended to move into this team later as TEO allocation changes. Their existing role cards remain unchanged in this tranche.

## Why a separate team is required

The Engineering Team is defined around software implementation. The Planning Team owns architecture and executable planning. Neither team should be made solely accountable for work whose correctness depends on physical behavior, electronics, materials, manufacturing, environment, dynamics, mission constraints, production processes, or operation in the real world.

The Physical Systems Team creates a stable responsibility boundary for those disciplines while retaining required handoffs to Systems Engineering, Planning, Engineering, Platform and Reliability, Assurance, Review, and Verification.

## Specialist boundaries

### Hardware Engineering

Owns electronic hardware architecture, components, schematics, PCB implementation, power, signal, thermal, EMC, DFM, DFT, bring-up, and qualification evidence.

It does not absorb firmware, manufacturing-process ownership, system requirements, safety approval, or final release authority.

### Robotics and Autonomous Systems

Owns sensing, estimation, perception, planning, control, actuation, simulation, degraded modes, human supervision, and operational-domain evidence.

It does not own functional-safety approval or unbounded autonomous authority.

### Silicon and ASIC Engineering

Owns microarchitecture, RTL, verification, clocks and reset, timing, CDC, synthesis, physical implementation, DFT, characterization, yield, and silicon lifecycle evidence.

It does not self-approve tapeout or production release.

### Aerospace and Satellite Engineering

Owns mission and spacecraft architecture, payload, orbit and trajectory constraints, avionics, communications, ground interfaces, environmental qualification, launch, commissioning, operations, and mission evidence.

It does not replace launch, flight, mission, certification, or safety authority.

### Manufacturing Engineering

Owns manufacturing process design, tooling, instructions, measurement, capability, yield, quality controls, supplier manufacturing interfaces, nonconformance, corrective action, and production-readiness evidence.

It does not replace product design authority, Quality, Safety, Regulatory, or customer acceptance.

## Systems Engineering handoff

Physical Systems work must hand off to Systems Engineering when it changes:

- stakeholder needs or intended use
- system requirements or allocation
- internal or external interfaces
- configuration or technical baseline
- integration sequence
- verification or validation strategy
- lifecycle, support, maintenance, or retirement assumptions

## Assurance handoff

Safety-related, security-relevant, privacy-relevant, high-consequence, regulated, or formally constrained physical-system work requires the appropriate Assurance specialist and independent Verification Team review.

## Staged activation

This tranche completes:

- the team charter
- five specialist cards
- five worker contracts
- responsibility and authority boundaries
- independent-verification requirements
- critical human-approval requirements
- freshness policies
- exact canonical preservation controls

This tranche does not add an active route. Activation remains blocked until TEO has:

- capability mappings
- provider-diverse fallback policy
- conformance datasets
- deterministic classification and routing
- completed Embedded and Civil allocation changes

## Preservation

The five new specialist cards are locked to their recorded Git blob SHAs. Existing Embedded and Civil role cards are also locked and must not be rewritten merely to change TEO allocation.

The six-card regulated evidence pilot remains unchanged. Physical Systems expansion does not authorize an evidence-registry rollout.
