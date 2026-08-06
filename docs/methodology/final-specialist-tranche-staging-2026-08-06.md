# Final Specialist Tranche Staging

Date: 2026-08-06

## Decision

TEO now contains the final four specialist cards approved by the principal-engineering expansion:

- Cloud Architect
- Mobile Engineer
- Compiler and Toolchain Engineer
- Applied Scientist

These specialist cards remain staged. This change does not add new specialist routes, capability mappings, implementation bindings, conformance fixtures, or canonical active-specialist entries.

## Why these specialists remain in different teams

The four roles do not form one responsibility family.

### Cloud Architect

Cloud Architecture remains under the Planning Team because it owns provider-specific structural decisions, landing zones, organizational topology, regional design, service selection, migration, concentration risk, and exit architecture.

The existing Architect remains the whole-system architecture owner. Platform and Reliability specialists remain responsible for implementation, operation, reliability, networks, databases, and cost disciplines.

### Mobile Engineer

Mobile Engineering belongs to the Engineering Team because it implements and operates mobile applications across device lifecycle, local state, offline behavior, platform integration, accessibility, performance, signing, distribution, and release.

It does not replace Product, UX, Backend, Application Security, Privacy, or platform authorities.

TEO already has a basic active `mobile` worker in `community/workers/workers.yaml` and a corresponding context override in `team-routing.yaml`. This tranche does not modify or deactivate that existing worker.

The new Mobile Engineer specialist remains staged. Its richer worker contract is stored in the staged worker file and must later be reconciled into the canonical `mobile` worker without creating a duplicate definition. The specialist still requires a canonical registry entry, capability mapping, provider-diverse route, and conformance evidence before activation.

### Compiler and Toolchain Engineer

Compiler and Toolchain Engineering belongs to the Engineering Team because it builds translation and build systems: frontends, semantics, IRs, optimizers, backends, ABIs, linkers, cross-toolchains, reproducible builds, and language tooling.

It does not replace language governance, Rust systems programming, ordinary application engineering, or the target-domain engineers whose requirements the toolchain must satisfy.

### Applied Scientist

Applied Science belongs to the Research Team because it owns hypotheses, estimands, experimental and observational design, statistical and causal inference, algorithms, simulation, uncertainty, robustness, reproducibility, and translation into engineering evidence.

It does not replace broad research synthesis, quantitative analytics, AI Engineering, MLOps, Product, or domain decision authorities.

## Responsibility preservation

The staging manifest records exact Git blob SHAs for:

- all four new specialist cards
- the shared staged worker contract
- the existing Architect
- the existing AI Engineer
- the existing Researcher

The existing cards are preserved to prevent the new roles from silently absorbing their broader responsibility surfaces.

An intentional amendment must update the affected role card, staging record, and preservation tests together in one reviewed pull request.

## Activation boundary

Completed:

- four full specialist cards
- four staged worker contracts
- independent verification requirements
- high-consequence human-approval boundaries
- freshness policies
- explicit responsibility separation
- canonical preservation locks

Pending:

- active specialist routing policies
- stable capability mappings
- provider-diverse routine fallbacks
- conformance datasets
- canonical active-specialist entries
- reconciliation of the enriched Mobile worker contract into the existing canonical Mobile worker

Until those gates pass, these four specialist cards remain non-routable additions. The pre-existing basic Mobile worker remains active and unchanged.

## Freshness boundary

Cloud services, mobile platforms, stores, SDKs, compiler releases, processor targets, scientific methods, model releases, datasets, benchmarks, and provider behavior change over time.

Each card therefore requires current authoritative verification for consequential volatile claims. Stable engineering and scientific doctrine remains in the role card. Current product, platform, standard, pricing, availability, limit, and policy facts must be checked at use time.

## Evidence-pilot boundary

The regulated evidence pilot remains exactly six specialists:

- legal operations
- tax
- lending
- compliance
- civil engineering
- embedded systems

None of the four specialists in this tranche is added to that pilot before its maintainability gate passes.
