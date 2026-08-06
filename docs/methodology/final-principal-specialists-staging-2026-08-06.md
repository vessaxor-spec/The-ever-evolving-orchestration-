# Final Principal Specialist Staging

Date: 2026-08-06
Status: staged, not active

## Decision

The final specialist-card tranche adds:

- Cloud Architect to the Planning Team
- Mobile Engineer to the Engineering Team
- Compiler and Toolchain Engineer to the Engineering Team
- Applied Scientist to the Research Team

After this tranche, all 22 specialists approved in the principal-engineering expansion have complete staged role cards and worker contracts. Active routing, capability resolution, conformance, provider-diverse fallback, and existing-card allocation changes remain a separate completion phase.

## Why these specialists remain distinct

### Cloud Architect

Cloud Architecture owns cloud-specific placement, landing zones, provider service mapping, regional design, migration, operating model, economics, lock-in, and exit strategy.

The general Architect continues to own cross-domain system architecture and structural tradeoffs. Platform and Reliability owns implementation and operation. Network, Security, Privacy, Database Reliability, SRE, and FinOps retain their own technical authority.

### Mobile Engineer

Mobile Engineering owns mobile application implementation under platform lifecycle, state, offline, permission, accessibility, performance, device, signing, distribution, and store constraints.

It does not absorb Product, UX, Backend, Platform, Security, Privacy, or Release authority.

### Compiler and Toolchain Engineer

Compiler and Toolchain Engineering owns language translation, IR transformations, code generation, linking, runtimes, build systems, target support, cross-compilation, compatibility, reproducibility, bootstrap, provenance, and toolchain release evidence.

It does not replace language standards, architecture decisions, target owners, language-specific engineers, or application ownership. Rust Engineering remains a full language and systems-programming specialist.

### Applied Scientist

Applied Science owns scientific questions, hypotheses, experiment and measurement design, models, simulation, uncertainty, robustness, reproduction, and research-to-engineering handoff.

It does not replace Product decisions, production AI implementation, Data Engineering, MLOps, quantitative business analysis, domain authority, or independent methodological verification.

## Methodology checkpoint

The role design was checked against primary technical guidance.

| Area | Engineering implication | Primary reference |
|---|---|---|
| Cloud architecture | Required properties, governance, operating model, resilience, cost, and migration must be resolved before product selection | AWS Well-Architected Framework, Azure Cloud Adoption Framework, and Google Cloud Architecture Framework official documentation |
| Android application architecture | Separation of concerns, lifecycle-aware state, persistent data models, a single source of truth, unidirectional data flow, adaptive layouts, and testable boundaries are first-class | https://developer.android.com/topic/architecture |
| Apple application security | Platform security services should be used for identity, authorization, protected data, and code trust rather than custom cryptography | https://developer.apple.com/documentation/security/ |
| Compiler testing | Unit tests, regression tests, and whole-program suites provide distinct evidence categories | https://llvm.org/docs/TestingGuide.html |
| Applied science and AI evaluation | Evaluation must be context- and risk-appropriate across design, development, deployment, and use | https://www.nist.gov/itl/ai-risk-management-framework |

These sources provide guidance, not universal project requirements. Current provider services, mobile platforms, compilers, toolchains, models, datasets, benchmarks, APIs, regulations, and standards must be verified for the actual task and decision date.

## Cross-role authority boundaries

### Cloud and general architecture

```text
Architect
  -> owns cross-domain architecture and structural tradeoffs

Cloud Architect
  -> owns cloud-specific placement, provider mapping, migration, and exit design

Platform and Reliability
  -> implements and operates the selected cloud and platform capabilities
```

### Applied science and production AI

```text
Applied Scientist
  -> produces research evidence and prototype conclusions

AI Engineer
  -> implements production AI applications and inference behavior

MLOps Engineer
  -> owns model, data, artifact, deployment, monitoring, retraining, and retirement lifecycle

Data Analyst
  -> owns decision-focused quantitative analysis and model QA
```

### Compiler and language engineering

```text
Architect
  -> approves language and platform commitments

Compiler and Toolchain Engineer
  -> owns translation, build, target, compatibility, reproducibility, and toolchain evidence

Rust Engineer and other language specialists
  -> own language-specific production implementation
```

## Staged activation

This tranche completes:

- four specialist cards
- four worker contracts
- responsibility and handoff boundaries
- independent verification requirements
- risk-based qualified human approval requirements
- freshness policies
- exact canonical preservation controls

It does not add active routes. Activation remains blocked until TEO has:

- all 22 cards added to the active specialist registry
- capability mappings
- provider-diverse fallback rules
- conformance datasets
- deterministic team, worker, and specialist routing
- DevOps, DevSecOps, Embedded, and Civil allocation changes
- the Rust worker-binding correction

## Preservation

The four new cards and their worker contracts are locked to exact Git blob SHAs.

The existing Architect, AI Engineer, Data Analyst, and Rust Engineer cards are also locked so this expansion cannot silently absorb or weaken their capabilities.

The six-card regulated evidence pilot remains unchanged. Completing specialist cards does not authorize expansion of the evidence registry.
