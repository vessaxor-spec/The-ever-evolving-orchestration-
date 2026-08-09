<p align="center">
  <img src="assets/banner/teo-banner.svg" alt="The Ever-Evolving Orchestration banner" width="100%">
</p>

<div align="center">

# The Ever-Evolving Orchestration

### Models evolve. Responsibilities endure.

A vendor-neutral orchestration specification and runnable reference control plane for deciding **which intelligence should do the work, under what authority, with which fallback, and with what verification**.

**Navigate by principles. Adapt by evidence.**

[![Reference Implementation CI](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/actions/workflows/reference-ci.yml/badge.svg)](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/actions/workflows/reference-ci.yml)
[![Release](https://img.shields.io/github/v/release/vessaxor-spec/The-ever-evolving-orchestration-?label=release)](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/releases/tag/v1.0.0)

**Latest stable release:** [`v1.0.0`](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/releases/tag/v1.0.0) · **State:** `reference_operational` · **Reference package:** `teo-reference-router==1.0.0`

</div>

---

AI models change quickly. Responsibilities, risk boundaries, and the need for accountable verification change much more slowly.

TEO is built around one enduring premise:

> **The model is not the architecture.**

The architecture resolves responsibility before implementation. A task is interpreted, risk-assessed, assigned to an accountable team and worker, optionally narrowed through a specialist, translated into required capabilities, routed to an eligible implementation, given a capability-valid fallback, and independently verified.

That structure is designed to survive model releases, provider changes, new access mechanisms, and future implementations without repeatedly redesigning how work is understood and governed.

## What TEO owns

TEO owns orchestration decisions:

```text
Task
  -> Effective risk
  -> Team
  -> Worker
  -> Optional Specialist
  -> Required capabilities
  -> Primary implementation
  -> Reasoning effort
  -> Routine fallback
  -> Conditional escalation
  -> Independent verification
  -> Evidence-bearing outcome
```

TEO decides **which implementation should perform the task**, which fallback remains valid if that route fails, and which independent verifier should assess the result.

TEO does **not** own the user's provider account, subscription, authentication session, API key, billing relationship, credential broker, OAuth login, or connector session.

### Provider access is deliberately outside routing

A user or integrating runtime is responsible for having legitimate access to a selected implementation through any provider-supported mechanism, including:

- API keys
- OAuth or subscription-backed sessions
- delegated identity
- service accounts
- connector sessions
- credential brokers
- SDK-managed identity
- local runtime connections
- future provider-supported access mechanisms

Authentication method, subscription type, account tier, credential presence, billing method, and connector type are **not model-fitness signals** and must not change TEO's selected Team, Worker, Specialist, model role, reasoning effort, fallback, or verifier.

Provider-level model availability remains relevant to routing. A particular user's access state does not.

The normative boundary is defined in [`policy/governance/provider-access-separation.yaml`](policy/governance/provider-access-separation.yaml) and [`docs/specification/provider-access-boundary.md`](docs/specification/provider-access-boundary.md).

## Current state

**TEO v1.0.0 is released.** The project has crossed the functional-v1 boundary and is now in post-v1 stewardship and evolution.

The `v1.0.0` tag is governed as an immutable historical reference to the exact repository state accepted as the first functional release. The GitHub Release is published in the `reference_operational` state and aligns with `teo-reference-router==1.0.0`.

The normative release contract is [`docs/releases/v1.0.0.md`](docs/releases/v1.0.0.md), with the canonical readiness boundary in [`V1_READINESS.md`](V1_READINESS.md) and [`policy/governance/v1-readiness.yaml`](policy/governance/v1-readiness.yaml).

The current control plane has **ten active organizational teams**, **84 workers**, and **78 preserved specialist role cards** with deterministic Team -> Worker -> Specialist spawn paths.

It includes dedicated Mission Control workers for orchestration, operations, project delivery, and incident response.

The repository currently implements:

- non-lowerable effective-risk assessment
- specialist-driven risk elevation
- capability-aware implementation eligibility
- effort-aware specialist model routing
- preview-model authorization gates
- provider-diverse routine fallback
- independent provider-diverse verification
- conditional escalation separated from ordinary fallback
- guarded live provider execution for the bounded canary route
- bounded transient retry under the same dispatch
- canonical fallback redispatch with a fresh verifier
- persistent provider-family circuit state with Closed, Open, and Half-Open recovery
- abandoned half-open probe recovery
- content-free provider-attempt telemetry
- strict external JSON Schema boundaries
- verifier-calibration instrumentation
- blinded independent-human review tooling
- a separate provisional provider-diverse machine-panel evidence path
- a six-card regulated evidence/freshness pilot with CI validation and mutation resistance
- model-freshness governance based on current authoritative evidence
- provider-access separation governance
- reproducible CI with pinned dependencies and artifact hashes

### Functional v1 means

TEO v1.0.0 establishes a **credible vendor-neutral orchestration specification with a runnable reference control plane**.

It does not require TEO to become a production distributed orchestration platform before v1 can exist.

The functional-v1 boundary includes:

- architecture and governance
- deterministic routing and risk controls
- team, worker, and specialist resolution
- model and reasoning-effort routing
- provider-diverse fallback and verification
- guarded live provider execution
- retry, fallback, circuit-breaker, and telemetry controls
- calibration instrumentation
- provisional operational-evidence machinery
- reproducible green CI
- model-freshness governance
- provider-access separation governance

The authoritative release boundary is defined in [`policy/governance/v1-readiness.yaml`](policy/governance/v1-readiness.yaml).

### What is intentionally not a functional-v1 blocker

The following remain valuable post-v1 work and were explicitly not required for the `v1.0.0` `reference_operational` release:

- independent blinded human calibration
- a human-ground-truth verifier-quality claim
- distributed circuit-state coordination
- distributed telemetry export and retention infrastructure
- streaming runtime support
- source-backed historical cost attribution
- route-outcome learning
- automated qualified-human approval integration
- TEO-managed API-key provisioning
- TEO-managed OAuth login
- TEO-managed subscription or entitlement management
- a TEO-managed credential broker

Independent human calibration remains the stronger evidence tier and is required before claims or scope changes that policy explicitly reserves for human acceptance. It is tracked as a community stewardship path rather than a blocker to the functional reference release.

## Mission Control

Mission Control is the orchestration authority at the top of the active control plane.

It owns:

- task intake and intent preservation
- task classification
- effective-risk assessment
- primary and supporting team selection
- worker and specialist activation
- capability resolution
- execution order and dependencies
- implementation assignment
- routine fallback assignment
- verification assignment
- escalation triggers
- final completion status

Mission Control does not absorb specialist work and does not route directly to a model before responsibility, capability, and risk are resolved.

Its dedicated workers are:

| Worker | Responsibility |
|---|---|
| `orchestration` | governed multi-agent pipelines, handoffs, state, recovery, and termination |
| `operations` | operational controls, dependencies, vendors, approvals, and accountable execution |
| `project_delivery` | scope, capacity, sequencing, critical path, change control, and delivery commitments |
| `incident_response` | severity, roles, communications, timeline, recovery readiness, and blameless learning |

The canonical team definition is [`community/teams/mission-control.md`](community/teams/mission-control.md).

## Teams and responsibility domains

TEO currently organizes work through ten active teams:

| Team | Primary responsibility |
|---|---|
| **Mission Control** | intake, orchestration, coordination, dispatch, verification assignment, completion |
| **Planning** | architecture, decomposition, sequencing, tradeoffs, irreversible-choice review |
| **Engineering** | application and product implementation, debugging, testing, refactoring, migrations |
| **Platform and Reliability** | distributed systems, databases, networking, platforms, performance, SRE, MLOps, DevOps, DevSecOps, FinOps |
| **Systems Engineering** | stakeholder needs, requirements, interfaces, baselines, integration, lifecycle coherence, V&V planning |
| **Physical Systems** | hardware, embedded, civil, robotics, silicon, aerospace, manufacturing, physical integration |
| **Research** | broad research, user research, market research, analytics, applied science, documentation |
| **Assurance** | privacy engineering, functional safety, formal methods, application security |
| **Review** | code review, compliance review, semantic and adversarial challenge |
| **Verification** | evidence sufficiency, output validation, executable checks, independent acceptance gates |

The architecture is organizational before it is model-selective. Implementations can change without redefining responsibility.

## Specialist layer

TEO includes **78 public specialist role cards**.

Each specialist preserves its complete identity, responsibilities, protocols, capabilities, safety boundaries, collaboration rules, outputs, and examples. TEO allocation adds orchestration context. It does not compress, generalize, weaken, or replace the specialist.

Each active specialist has:

- a primary team
- supporting teams where required
- a stable worker binding
- a deterministic Team -> Worker -> Specialist spawn path
- activation and handoff rules
- a risk profile
- verification requirements
- authority and safety boundaries

The human-readable roster is in [`community/specialists/`](community/specialists/).

The canonical allocation registries are:

- [`community/specialists/specialists.yaml`](community/specialists/specialists.yaml)
- [`community/specialists/principal-engineering-active.yaml`](community/specialists/principal-engineering-active.yaml)

Specialists do not bypass Mission Control, self-assign authority, or approve their own consequential work.

## Routing principles

### Team-first

Resolve accountable responsibility before selecting an implementation.

### Capability-first

Determine what the task requires before considering a provider or model.

### Risk cannot be lowered by convenience

Effective risk is a non-lowerable floor derived from task content, caller declaration, specialist profile, and policy.

### Evidence-first

Change routing through current provider evidence, measured outcomes, documented limitations, and conformance updates rather than preference or model novelty.

### Independent verification

Consequential work must not rely on one implementation or one provider family as sole planner, executor, reviewer, and verifier.

### Failure-aware recovery

Retry, fallback, escalation, circuit state, and provider health are distinct controls. A failure must be classified before recovery is chosen.

### Connection neutrality

Provider access is an execution concern after routing. Authentication mechanics must not become routing authority.

## Current executable routing directions

These are **active routing directions**, not a permanent model ranking. Mission Control resolves responsibility, capability, effective risk, specialist context, and verification requirements before applying them.

A model being newer or stronger in aggregate does not automatically make it the correct route.

| Workload shape | Active primary | Routine fallback / support | Verification / escalation | Mission Control rationale |
|---|---|---|---|---|
| Orchestration, coordination, and general semantic planning | **Claude Sonnet 5** | GPT-5.6 Sol for engineering-heavy orchestration; Gemini 3.1 Pro Preview for research-heavy context only when explicitly accepted | Claude Opus 5 for unresolved high-consequence tradeoffs; route-specific independent verification | Sonnet is the coordination workhorse. Supporting models are selected by the dominant constraint rather than provider preference. |
| Bounded engineering implementation | **GPT-5.6 Terra** | **Gemini 3.6 Flash** as the stable routine cross-provider coding fallback; GPT-5.6 Sol for planning or cross-component reasoning | Claude Sonnet 5 semantic review where required | Terra owns inspect, edit, test, debug, and verify work where implementation is the dominant problem. Stable Gemini 3.6 Flash avoids making routine coding resilience depend on preview acceptance. |
| Difficult engineering reasoning, deep debugging, and refactor planning | **GPT-5.6 Sol** | Claude Sonnet 5 cross-provider reasoning fallback; Gemini 3.1 Pro Preview for independent research where explicitly accepted | Route-specific independent verifier | Sol is reserved for cross-system reasoning, hidden invariants, root-cause synthesis, and implementation-aware planning. |
| High-consequence specialist reasoning | **Claude Opus 5** | GPT-5.6 Sol cross-provider fallback | Gemini research/verification path where capability-valid; qualified human approval remains mandatory at critical effective risk | Opus remains the established routed high-consequence specialist implementation. Capability never removes human authority requirements. |
| Frontier unresolved reasoning | **Claude Fable 5**, conditional only | Entered only after established Opus/Sol paths remain materially inconclusive | Existing Mission Control escalation and verification controls remain in force | Fable is a narrow frontier escalation lane, not a global Opus replacement or routine fallback. |
| Broad research and grounded synthesis | **Gemini 3.1 Pro Preview**, only with explicit preview acceptance | Gemini 3.6 Flash for faster collection; Claude Sonnet 5 for cross-provider synthesis and contradiction challenge; GPT-5.6 Sol for technical validation | Independent source grounding and route-specific verification | Research separates collection, synthesis, contradiction analysis, and technical verification rather than forcing one model to own the whole evidence chain. |
| Multimodal, spatial, and rapid agentic interpretation | **Gemini 3.6 Flash** | Claude Sonnet 5 when the fallback remains modality-capable; GPT-5.6 Sol for technical follow-up | Gemini 3.1 Pro Preview may be used for ambiguous long-context synthesis only when explicitly accepted | Gemini 3.6 Flash is the stable multimodal and stronger bounded agentic lane. Fallback must preserve actual modality requirements. |
| Economical high-volume bounded work | **Gemini 3.5 Flash-Lite** | **Claude Haiku 4.5** first cross-provider fallback; GPT-5.6 Luna independent economical alternative; Gemini 3.6 Flash for stronger bounded agentic or multimodal work | **Claude Sonnet 5** verifies the primary Flash-Lite route; **Gemini 3.6 Flash** becomes the fresh verifier when Haiku is the executor and Google remains eligible; **GPT-5.6 Sol** verifies when Google is provider-blocked or stronger technical review is required | Throughput routing optimizes boundedness, latency, cost, and validation while maintaining provider-diverse recovery and fresh-verifier rotation. |
| Executable and semantic verification | **Route-specific independent verifier** | Provider-diverse semantic, research, executable, deterministic, or qualified-human verification according to risk and evidence type | Fresh verifier assignment follows every canonical fallback redispatch | Verification is a separate responsibility. TEO intentionally does not maintain one universal verifier model. |

### Active throughput topology

The bounded `high_volume_simple` canary now uses this executable topology:

```text
Primary execution
Gemini 3.5 Flash-Lite (Google)
  -> verifier: Claude Sonnet 5 (Anthropic)

Model-scoped Flash-Lite failure
Claude Haiku 4.5 (Anthropic)
  -> fresh verifier: Gemini 3.6 Flash (Google)

Google provider-scoped failure
Claude Haiku 4.5 (Anthropic)
  -> fresh verifier: GPT-5.6 Sol (OpenAI)

Independent economical alternative
GPT-5.6 Luna (OpenAI)
```

This topology is intentionally asymmetric. Executor fallback and verifier rotation are selected together so provider diversity remains meaningful after redispatch.

### Interpretation rules

- **Terra and Sol are not interchangeable engineering labels.** Terra is the bounded execution lane; Sol is the difficult-reasoning and cross-system lane.
- **Opus 5 and Fable 5 are not interchangeable escalation labels.** Opus 5 remains the established high-consequence specialist route. Fable 5 is a narrow frontier escalation after established paths remain materially inconclusive.
- **Gemini 3.6 Flash and Gemini 3.5 Flash-Lite solve different optimization problems.** Flash is the stronger stable agentic and multimodal lane. Flash-Lite is the active high-throughput bounded route.
- **Haiku 4.5 is no longer the primary throughput executor.** It is the first cross-provider fallback for the bounded throughput route.
- **Preview models do not become defaults by being stronger.** Gemini 3.1 Pro Preview remains task-ineligible unless that exact preview implementation is explicitly accepted.
- **Fallback must remain capability-valid.** Provider diversity does not excuse modality, tooling, context, or reasoning mismatch.
- **Fallback gets a fresh verifier.** Canonical redispatch cannot silently inherit an invalid or same-provider verifier.
- **Authentication never changes these directions.** API keys, OAuth or subscription-backed sessions, delegated identity, and other provider-supported access mechanisms belong to the execution boundary after routing.

Reasoning effort is part of the executable dispatch contract where the selected implementation supports a corresponding control. Mission Control may raise effort when risk or complexity justifies it, but maximum effort and premium modes are conditional tools rather than routine defaults.

Model freshness is governed by [`policy/governance/model-freshness.yaml`](policy/governance/model-freshness.yaml). Newer triggers evaluation; it does not automatically trigger replacement.

The canonical routing source is [`policy/routing/routing.yaml`](policy/routing/routing.yaml). The README summarizes that policy and must not outrank it.

## Provider-aware fallback and recovery

A different model name is not automatically a meaningful fallback.

TEO distinguishes request-specific, transient, model-specific, provider-scoped, and capability-scoped failures.

Core rules:

1. Prefer a capable routine fallback from another provider family.
2. Block only the failed implementation after a model-specific failure.
3. Block the provider family for provider-scoped task recovery when policy identifies provider-level unavailability.
4. Keep bounded transient retry under the same dispatch, model, provider, reasoning effort, and verifier.
5. Treat fallback as a new orchestration decision with a new dispatch and fresh verifier.
6. Do not use frontier or high-cost escalation capacity as an ordinary availability fallback.
7. Keep circuit state separate from route selection. Circuit state constrains eligibility; canonical routing chooses the alternative.
8. Do not poison provider-family health because one user has invalid credentials, missing entitlement, billing failure, account quota exhaustion, or a local connection problem.
9. Execute only the verifier assigned by the active dispatch.
10. Fail closed when no eligible independent verifier remains.

### Circuit semantics

Provider-family circuit state is a reliability constraint, not routing authority.

- service-health failures can accumulate toward opening a circuit
- tenant/account and local-connection failures do not poison global provider health
- Half-Open probes use recoverable ownership rather than permanent in-flight state
- a local connection error during Half-Open is inconclusive and does not count as provider recovery
- canonical routing selects the next eligible implementation after circuit constraints are applied

See [`docs/methodology/provider-aware-fallbacks.md`](docs/methodology/provider-aware-fallbacks.md) and [`policy/runtime/`](policy/runtime/).

## Reference runtime

The Python reference implementation is a runnable control plane that can:

- load and validate linked TEO policy and registries
- classify supported tasks deterministically
- calculate effective risk
- select teams, workers, specialists, capabilities, implementations, fallbacks, and verifiers
- produce structured dispatch records
- execute the guarded live canary path
- retry bounded transient failures
- perform canonical fallback redispatch
- maintain provider-family circuit state
- record content-free provider-attempt telemetry
- execute the assigned independent verifier on the guarded live path
- finalize evidence-bearing outcomes
- preserve audit records

The live provider adapters are deliberately narrow. The current guarded execution canary is limited to explicit `high_volume_simple` work at low or medium effective risk.

That narrow live-execution scope does **not** mean the routing architecture is limited to `high_volume_simple`. TEO's broader routing, risk, specialist, fallback, and verification control plane is active across the supported task taxonomy. The live canary is an execution-scope boundary, not a routing-scope boundary.

### ProviderConnection

Provider adapters receive an **already-selected** operation through the connection boundary. They may translate and execute that authorized operation, but they do not acquire authority to reroute the task.

The integrating runtime may supply API-key, OAuth/subscription-backed, delegated, connector-based, or other provider-supported access without changing TEO routing semantics.

## Verification and evidence

A successful provider call is not automatically a completed TEO outcome.

The active dispatch assigns verification independently. Finalization checks execution and verification identity, provider independence, dispatch identity, verification status, and any human-approval requirement.

The verifier-calibration system includes:

- a fixed eight-case control corpus
- deterministic pre-verifier checks where objective validation is possible
- strict observation contracts
- blinded human-review packet generation
- two-reviewer minimum for the human-backed evidence tier
- adjudication on human-review disagreement
- a three-provider, three-run-per-case empirical verifier protocol
- route-specific false-pass, false-failure, escalation, criterion, repeatability, disagreement, latency, and usage metrics
- a separate provisional machine-panel tier when independent human reviewers are unavailable
- strict evidence labeling that prevents machine-panel evidence from being presented as human ground truth

### Human stewardship

Independent blinded human calibration is **not required to tag the functional reference v1**.

It remains required before:

- claiming human-ground-truth verifier quality
- evidence-based scope expansion where policy requires human acceptance
- route changes that require explicit human acceptance
- replacing the independent-human evidence tier

The preferred path is public GitHub community stewardship. The machine-panel path does not remove or impersonate that human tier.

### Provisional operational evidence

TEO includes a manually executable provisional study that can collect:

- 24 blinded judgments from three provider-diverse machine-panel routes
- 72 repeated live verifier observations
- 96 live calls in total

The GitHub Actions workflow uses API-key secrets because GitHub-hosted automation cannot inherit an end user's interactive provider session. This is an **API-key convenience harness**, not a TEO provider-access requirement.

Alternative runtimes may execute the same selected models through OAuth/subscription-backed or other legitimate provider-supported access.

Provisional evidence may inform readiness and future review. It cannot automatically authorize quality claims, route changes, or broader live execution.

## Model and policy freshness

TEO explicitly rejects the assumption that a model registry remains correct merely because it was correct when written.

Model-sensitive work must establish current provider reality from authoritative evidence before changing routing.

Freshness review considers:

- current model identity
- provider-level availability
- lifecycle state such as stable, generally available, preview, deprecated, or retired
- supported reasoning or thinking controls where relevant
- capability changes that materially affect routing
- current provider documentation and release evidence

User authentication method, subscription entitlement, billing state, and credential availability are not model-freshness properties.

A new model release triggers evaluation, not automatic promotion.

Current model evidence belongs in the model registry and evidence records, not as permanent truth embedded in README prose. The README should describe active routing roles and governance boundaries; provider catalogs remain independently refreshable.

## Regulated evidence pilot

TEO maintains a six-card evidence-backed freshness pilot for high-consequence specialist domains:

- Legal Operations
- Tax Strategist
- Loan Officer Assistant
- Compliance Auditor
- Civil Engineer
- Embedded Engineer

The pilot requires dated authoritative claims, structural evidence validation, non-expired consequential evidence, authority resolution, and mutation resistance.

The pilot remains intentionally bounded. It is not permission to claim that every specialist card has completed the same evidence lifecycle.

## Conformance and CI

TEO treats silent routing drift as a defect.

The repository test and validation system covers, among other controls:

- team, worker, specialist, and capability integrity
- all active specialist spawn paths
- routing and risk behavior
- specialist model refinement and reasoning effort
- provider-diverse fallback and verifier assignment
- active throughput primary/fallback/verifier topology
- preview authorization
- finalization integrity guards
- retry and fallback behavior
- circuit recovery and abandoned half-open probe handling
- content-free telemetry
- live verification boundaries
- calibration evidence contracts
- human-review blinding provenance
- machine-panel evidence separation
- model-freshness governance
- provider-access separation governance
- regulated evidence validation and mutation resistance
- external JSON Schema enforcement
- documentation-truth invariants

The reference CI:

1. installs a hash-pinned validation environment on a fixed Python patch version
2. compiles Python sources
3. runs the complete automated test suite
4. validates regulated specialist evidence
5. parses reference schemas
6. validates linked TEO configuration
7. executes the end-to-end reference lifecycle

CI validates the control plane. It does not convert provisional evidence into human-ground-truth claims.

## Getting started

### For humans

1. Read [`CONSTITUTION.md`](CONSTITUTION.md), [`MANIFESTO.md`](MANIFESTO.md), and [`LEXICON.md`](LEXICON.md).
2. Read [`V1_READINESS.md`](V1_READINESS.md) and the [`v1.0.0 release contract`](docs/releases/v1.0.0.md).
3. Read [`policy/governance/v1-readiness.yaml`](policy/governance/v1-readiness.yaml).
4. Read [`policy/governance/model-freshness.yaml`](policy/governance/model-freshness.yaml).
5. Read [`policy/governance/provider-access-separation.yaml`](policy/governance/provider-access-separation.yaml).
6. Review [`community/teams/mission-control.md`](community/teams/mission-control.md).
7. Review canonical routing under [`policy/routing/`](policy/routing/).
8. Review runtime controls under [`policy/runtime/`](policy/runtime/).
9. Review verification policy under [`policy/verification/`](policy/verification/).
10. Review specialists under [`community/specialists/`](community/specialists/).
11. Review current model and provider evidence under [`models.yaml`](models.yaml) and [`registry/`](registry/).
12. Run validation and tests.

### For AI agents

Read in this order:

1. [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md)
2. [`policy/governance/model-freshness.yaml`](policy/governance/model-freshness.yaml)
3. [`policy/governance/provider-access-separation.yaml`](policy/governance/provider-access-separation.yaml)
4. [`policy/routing/team-routing.yaml`](policy/routing/team-routing.yaml)
5. [`community/teams/`](community/teams/)
6. [`community/workers/`](community/workers/)
7. [`community/specialists/`](community/specialists/)
8. [`policy/routing/routing.yaml`](policy/routing/routing.yaml)
9. [`policy/runtime/`](policy/runtime/)
10. [`policy/verification/`](policy/verification/)
11. [`models.yaml`](models.yaml)
12. [`registry/`](registry/)
13. [`reference/datasets/`](reference/datasets/)

Do not route from remembered provider assumptions when current evidence is materially relevant.

Do not make API availability, OAuth state, subscription tier, billing, or credentials part of model selection.

## Reference commands

Install the Python reference implementation:

```bash
cd reference/implementations/python
python -m pip install -e '.[test]'
```

Validate linked configuration:

```bash
teo --repo-root ../../.. validate
```

Create a dispatch:

```bash
teo --repo-root ../../.. plan \
  ../../examples/phase5-task.yaml \
  --output /tmp/teo-dispatch.json \
  --audit-log /tmp/teo-audit.jsonl
```

Finalize an externally executed and independently verified result:

```bash
teo --repo-root ../../.. finalize \
  /tmp/teo-dispatch.json \
  execution-result.json \
  verification-result.json \
  --audit-log /tmp/teo-audit.jsonl
```

Run the end-to-end example:

```bash
python reference/examples/run_example.py
```

Run the complete test suite:

```bash
pytest
```

The final outcome contract supports:

- `completed`
- `failed`
- `escalated`
- `awaiting_human`

## Repository structure

```text
.
├── README.md
├── CONSTITUTION.md
├── MANIFESTO.md
├── LEXICON.md
├── AI_INSTRUCTIONS.md
├── STEWARDSHIP.md
├── ROADMAP.md
├── CHANGELOG.md
├── models.yaml
│
├── policy/
│   ├── governance/
│   ├── routing/
│   ├── runtime/
│   ├── escalation/
│   └── verification/
│
├── registry/
│   ├── providers/
│   ├── models/
│   ├── capabilities/
│   └── benchmarks/
│
├── community/
│   ├── teams/
│   ├── workers/
│   ├── specialists/
│   ├── capsules/
│   ├── discussions/
│   └── proposals/
│
├── reference/
│   ├── configs/
│   ├── schemas/
│   ├── implementations/
│   ├── examples/
│   └── datasets/
│
├── docs/
│   ├── philosophy/
│   ├── specification/
│   ├── architecture/
│   ├── methodology/
│   ├── examples/
│   └── history/
│
├── research/
├── tests/
├── ci/
└── assets/
```

## Roadmap state

### Phase 1: Repository credibility

**Complete.**

### Phase 2: Core organizational architecture

**Complete.**

### Phase 3: Routing validation

**Complete.**

### Phase 4: Registry and evidence structure

**Complete.**

### Phase 5: Reference control plane

**Complete.**

### Functional v1: reference operational

**Released as `v1.0.0` on 2026-08-09.**

The architecture, governance, deterministic routing, risk controls, specialist bindings, model refinement, Mission Control routing assignments, provider-diverse fallback, fresh-verifier rotation, guarded live execution, recovery controls, telemetry, calibration instrumentation, model freshness, provider-access separation, and reproducible CI are operational as a reference system.

The release is governed by [`docs/releases/v1.0.0.md`](docs/releases/v1.0.0.md). Future compatible fixes and extensions advance through semantic release versions rather than moving or rewriting the `v1.0.0` tag.

### Post-v1 stewardship and hardening

Future work may include:

- independent blinded human calibration through community stewardship
- evidence-governed live-scope expansion
- distributed circuit-state coordination
- distributed telemetry export and retention controls
- streaming execution paths
- source-backed historical cost attribution
- route-outcome evaluation and learning
- qualified-human approval integration
- continued regulated-evidence pilot observation
- ongoing model-freshness reviews as provider catalogs evolve

These are extensions and evidence-strengthening work. They should not be confused with missing core routing architecture.

## Community stewardship

TEO is designed to evolve through publicly reviewable stewardship.

Useful contributions include:

- evidence-backed routing challenges
- verification research
- model-freshness updates
- capability definitions
- worker and specialist binding improvements
- provider-resilience research
- reference implementation improvements
- documentation corrections
- independent human calibration and residual-risk review

A newer model should not replace an existing route solely because it is newer or stronger on one benchmark. Proposed route changes should identify the responsibility affected, current evidence, limitations, fallback implications, verifier independence, and rollback path.

The repository owner is `vessaxor-spec`. The project was initiated by Sylvester Roxas in 2026.

## Capsules

Capsules preserve accepted historical states of TEO.

Accepted capsule files are immutable. When the system changes, future stewards add a new capsule rather than rewriting the past.

The capsule index is [`community/capsules/README.md`](community/capsules/README.md).

> If this repository still exists years from now, it belongs to every steward who chose to improve it rather than restart it.

## Public scope

This repository is intended for public review and must not contain:

- private prompts
- proprietary workflows
- credentials or secrets
- employer-specific processes
- personal infrastructure
- confidential benchmarks
- identifying operational data

## License

No open-source license has been selected yet.

Until a license is added, the repository is publicly viewable but is not yet offered for reuse, modification, or redistribution. External code contributions should wait until licensing and contribution terms are finalized.

---

<div align="center">

**The best orchestration specification is not the one that predicts the future. It is the one that remains useful when the future arrives.**

</div>
