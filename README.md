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

**Current development package:** `teo-reference-router==1.0.1.dev0`

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

Current `main` is post-release development and identifies as `teo-reference-router==1.0.1.dev0`. This development identity does not move, rewrite, or replace the immutable `v1.0.0` release boundary.

The normative release contract is [`docs/releases/v1.0.0.md`](docs/releases/v1.0.0.md), with the canonical readiness boundary in [`docs/releases/v1-readiness.md`](docs/releases/v1-readiness.md) and [`policy/governance/v1-readiness.yaml`](policy/governance/v1-readiness.yaml).

The current control plane has **ten active organizational teams**, **84 workers**, and **82 preserved specialist role cards** with deterministic Team -> Worker -> Specialist spawn paths.

It includes dedicated Mission Control workers for orchestration, operations, project delivery, and incident response.

The repository information-architecture migration **R1 through R5 is complete**. Current authority, historical activation records, research, executable reference code, evidence, registries, and stewardship documentation now have governed canonical locations under [`policy/governance/repository-layout.yaml`](policy/governance/repository-layout.yaml).

The current accepted post-v1 evidence baseline has **Route-Outcome Evidence**, the **Benchmark and Outcome Lab**, **Source-backed Cost Attribution**, **Shadow Route Evaluation**, and the **Qualified-human approval lifecycle** complete at their declared milestones. Reference Implementation CI #514 remains the accepted substantive runtime-control baseline: **657 automated tests**, **477 tracked-file layout checks**, regulated specialist evidence validation, **40 JSON Schema** parses, linked configuration with zero issues, and the provider-diverse end-to-end reference lifecycle. The targeted 2026-08-11 finalization -> authority -> recovery audit closed a proven qualified-human temporal-causality gap and added recovery-authority regression protection without widening routing or execution authority.

The documentation-reconciliation baseline is **802 automated tests**, **515 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse end-to-end reference lifecycle, validated on CI #602 after the then-current Host Integration research chain, route-backed final execution provenance, and Task Intent & Action Authority research direction were reconciled. This historical reconciliation baseline does not replace CI #514 as the substantive runtime-control baseline and does not create empirical provider-backed live-execution evidence.

The latest Host Integration executable research validation is Reference Implementation CI #658: **863 automated tests**, **528 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse artifact-bound end-to-end reference lifecycle. That run validated the process-lifetime recursion-resistance slice after a Security and Authority Boundaries review replaced an unnecessary pending-authorization store with stateless HMAC-bound admission claims. It remains non-normative evidence and does not close restart-durable or distributed recursion state, production scheduler containment, compromised-host bypass, dynamic executable-hook discovery, transitive-code identity, or production authenticity boundaries.

The canonical current priority remains **evidence-governed live execution expansion**, now at 65%. `documentation` is the first staged candidate; its fallback/fresh-verifier topology, direct adapter readiness, and staged replay harness are validated, but provider-backed replay evidence is still pending and it has no live-execution authority. The bounded low or medium risk `high_volume_simple` canary remains the only accepted live execution scope. See [`docs/stewardship/progress-tracker.md`](docs/stewardship/progress-tracker.md).

The current development line also includes an optional **final execution provenance** projection. When canonical Route-Outcome Evidence is supplied to finalization, TEO can revalidate that evidence and expose the observed successful provider/model route through `FinalOutcome.execution_provenance`. The projection is read-only evidence. It cannot reroute a task, nominate a provider, authorize a host action, widen live scope, or replace the complete Route-Outcome Evidence record. See [`docs/specification/final-execution-provenance.md`](docs/specification/final-execution-provenance.md).

The post-v1 hard audit completed on 2026-08-10 without finding a critical control-plane defect. The final audited tree passed **390 tracked-file layout checks**, **519 automated tests**, regulated specialist evidence validation, **18 JSON Schema** parses, linked configuration with zero issues, and the provider-diverse end-to-end reference lifecycle. The durable audit record is [`docs/history/audits/post-v1-hard-audit-2026-08-10.md`](docs/history/audits/post-v1-hard-audit-2026-08-10.md).

The targeted control-integrity audit completed on 2026-08-11 and is preserved at [`docs/history/audits/control-integrity-authority-recovery-audit-2026-08-11.md`](docs/history/audits/control-integrity-authority-recovery-audit-2026-08-11.md). It proved and remediated request -> disposition -> finalization temporal-causality gaps and verified that bounded recovery preparation preserves effective risk and human-approval requirements. Control Integrity remains intentionally scored at 90% because adversarial mutation depth is an ongoing discipline rather than a permanently finishable state.

### Host integration research

TEO is also researching a portable **Host Integration Contract** for embedding Mission Control into pre-existing AI agents and runtimes without replacing host identity, native safety controls, permissions, or execution infrastructure.

Two materially different external-host architectures have completed implementation-backed validation rounds, satisfying the **two-host architecture-diversity research gate**. One pattern uses host-local vendorized TEO material with a capability adapter; the other uses a separate revision-pinned upstream TEO dispatch followed by a downstream host execution adapter. The diversity gate reduces the risk that one host's local design becomes the universal integration contract by accident.

Since those validation rounds, nine provider-independent adversarial slices have converted several previously open integration questions into executable evidence:

- bounded specialist projection reduced the measured active specialist-card payload by **98.7805% on average** and **97.6295% in the worst measured one-card case** against naive loading of all 82 active role cards;
- process-local dispatch provenance rejects tested dispatch tampering before adapter execution, while bundled OpenAI, Anthropic, and Google adapters reject or omit tested payload-driven tool, MCP, web-search, and fallback self-expansion;
- process-local third-party adapter research binds an approved manifest, measured implementation artifact, registered runtime type, provider family, operation, capability scope, and revocation state before execution;
- restrictive host/TEO authority intersection applies deny-wins and more-restrictive-control-wins semantics so host policy may restrict TEO authority but cannot widen it;
- exact execution-envelope research binds the dispatch effective risk, capability, operation, target, canonical parameters, side-effect class, prerequisites, and retry budget to an authority-issued action, with host retry authority limited to the minimum allowed by TEO and host policy;
- verifier-context independence rejects tested executor-derived and verdict-priming context, while exact artifact/change-set stale-PASS resistance binds a PASS to the exact task, dispatch, change, artifact, revision, SHA-256 digest, and target reference it examined;
- brokered conformant process-lifetime cross-process authority/replay research keeps mutable TEO authority outside separate host processes and rejects tested host issuance attempts, dispatch/action mutation, replay, duplicate successful claims, and retry-budget multiplication through the exposed path, while compromised-host bypass, remote/distributed authenticity, host identity, restart persistence, and effect evidence remain open;
- static runtime-wired authority-surface reconciliation derives canonical authority configuration and policy paths from executable Python source, fingerprints present files, retains dormant-but-wired paths, and rejects tested omissions, unwired additions, aliases, stale declarations, content changes, and repository-root escape while dynamic executable hooks, plugins/loaders, constructed paths, and transitive-code identity remain open;
- process-lifetime recursion resistance binds one root dispatch to immutable depth, descendant, specialist-spawn, active-branch, and recovery-generation ceilings; stateless HMAC-bound admission claims reject tested forgery, replay, stale-state claims, cross-root reuse, release-based budget reset, and raced same-revision claims while restart-durable, distributed, production-scheduler, and compromised-host boundaries remain open.

The candidate remains **non-normative research**. These results do not certify an external host, create a normative machine-readable Host Integration schema, authorize third-party adapters, alter Mission Control policy, change the active roster, or widen live execution.

The exact reconciled PR #146 head was validated by Reference Implementation CI #580 with **788 automated tests**, **509 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, linked configuration with zero issues, and the provider-diverse end-to-end reference lifecycle. This validates verifier-context independence and exact artifact/change-set stale-PASS resistance at the research layer and does not replace CI #514 as the accepted substantive runtime baseline.

The later brokered cross-process authority slice merged through PR #156 after exact-head Reference Implementation CI #626 passed **817 automated tests**, **520 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse end-to-end reference lifecycle. That evidence supports only the brokered conformant process-lifetime boundary and does not close production remote/distributed authenticity, compromised-host bypass resistance, host identity, restart-durable replay state, or result/effect receipt authenticity.

The static authority-surface reconciliation slice passed corrected executable Reference Implementation CI #644 with **842 automated tests**, **525 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse artifact-bound end-to-end lifecycle. Red-canary CI #643 first exposed two research-test assumptions, including that the still-present empty `runtime-worker-overrides.yaml` file had been mistaken for an absent surface. The correction followed repository truth and did not change production routing or authority.

The process-lifetime recursion-resistance slice passed corrected executable Reference Implementation CI #658 with **863 automated tests**, **528 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse artifact-bound end-to-end lifecycle. The research authority binds a root dispatch and immutable recursion limits to TEO-side state, uses revision-bound stateless HMAC admission claims, and preserves consumed descendant/spawn budget across release and recovery. This does not prove restart-durable or distributed recursion coordination, remote host authenticity, production scheduler containment, or compromised-host resistance.

Before normative promotion, remaining evidence includes provider/model input economics, end-to-end latency and task adherence, production-grade external-adapter package provenance and authority-controlled loading, dependency/transitive-code identity, revocation/update and downgrade semantics, distributed host/TEO authority synchronization, production resource-target canonicalization and containment, credential/account/tenant scope binding, production-grade remote or distributed dispatch and exact-action authenticity/replay beyond the brokered conformant process-lifetime path, result/effect receipt authenticity, restart-durable and distributed retry-budget coordination, revision freshness and expiry semantics, portfolio/task-admission authority separation, dynamic authority-surface discovery for executable hooks, plugins/loaders, and constructed paths, restart-durable and distributed recursion state, production scheduler recursion/recovery containment, and independent review against a parallel routing or authority plane.

The next bounded provider-independent Host Integration gate should be selected from those remaining evidence requirements after repository recalibration. Host Integration research does not supersede the deferred provider-backed controlled `documentation` replay milestone or change live authority.

See [`research/roadmaps/host-integration-contract.md`](research/roadmaps/host-integration-contract.md), [`research/runtime/2026-08-12-host-integration-validation-round-1.md`](research/runtime/2026-08-12-host-integration-validation-round-1.md), [`research/runtime/2026-08-12-host-integration-validation-round-2.md`](research/runtime/2026-08-12-host-integration-validation-round-2.md), [`research/runtime/host-integration-context-economics-2026-08-12.md`](research/runtime/host-integration-context-economics-2026-08-12.md), [`research/runtime/host-integration-dispatch-adapter-mutation-2026-08-12.md`](research/runtime/host-integration-dispatch-adapter-mutation-2026-08-12.md), [`research/runtime/host-integration-third-party-adapter-trust-2026-08-12.md`](research/runtime/host-integration-third-party-adapter-trust-2026-08-12.md), [`research/runtime/host-integration-authority-intersection-2026-08-12.md`](research/runtime/host-integration-authority-intersection-2026-08-12.md), [`research/runtime/host-integration-execution-envelope-integrity-2026-08-12.md`](research/runtime/host-integration-execution-envelope-integrity-2026-08-12.md), [`research/runtime/host-integration-verifier-artifact-binding-2026-08-12.md`](research/runtime/host-integration-verifier-artifact-binding-2026-08-12.md), [`research/runtime/host-integration-cross-process-authority-2026-08-13.md`](research/runtime/host-integration-cross-process-authority-2026-08-13.md), [`research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md`](research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md), and [`research/runtime/host-integration-recursion-resistance-2026-08-14.md`](research/runtime/host-integration-recursion-resistance-2026-08-14.md).

### Additional accepted architecture research

Two further research directions are accepted without changing current runtime authority or Progress Tracker sequencing:

- [`research/roadmaps/execution-environment-recovery-contract.md`](research/roadmaps/execution-environment-recovery-contract.md) explores vendor-neutral isolated execution, pre-change checkpoints, rollback, recovery verification, and simulation-to-promotion boundaries without making TEO a container, microVM, deployment, or backup runtime.
- [`research/roadmaps/task-intent-action-authority-contract.md`](research/roadmaps/task-intent-action-authority-contract.md) explores a machine-checkable boundary between assessment, recommendation, preparation, execution, and verification authority so downstream routing, delegation, host permissions, fallback, recovery, or exact action envelopes cannot silently widen the authority granted by the originating request or parent task.

Both remain **non-normative**. They do not change the canonical Task Request or Dispatch Record, Mission Control policy, specialist roster, provider routing, qualified-human requirements, live execution, or the stable `v1.0.0` contract.

### Current authority and preserved staged artifacts

TEO deliberately distinguishes an artifact's internal lifecycle label from the authority that activates it.

Direct current routing and worker authority reports `status: active`.

Five worker-definition files are intentionally different. They are cryptographically preserved staged artifacts whose exact Git blob identities are protected by conformance tests:

- `community/workers/extensions/systems-engineering-worker.yaml`
- `community/workers/extensions/platform-reliability-core-workers.yaml`
- `community/workers/extensions/platform-reliability-operations-workers.yaml`
- `community/workers/extensions/physical-systems-workers.yaml`
- `community/workers/extensions/assurance-workers.yaml`

Those files retain their original `public-draft` artifact status. Their current execution authority is conferred by the active [`policy/routing/activation/principal-engineering.yaml`](policy/routing/activation/principal-engineering.yaml) manifest, which records them as `loaded_staged_workers` and records the corresponding teams as activated.

This is intentional. Do not rewrite preserved staged blobs merely to make lifecycle labels visually uniform.

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
- staged live-scope candidate policy and no-network readiness preflight without activation authority
- repaired documentation provider-diverse fallback and fresh-verifier recovery topology
- staged Claude Sonnet 5 and GPT-5.6 Sol executor capability plus GPT-5.6 Terra verifier capability without task-scope activation
- staged documentation replay-plan and replay-record contracts with whole-plan no-network preflight
- an operator-run documentation replay path that preserves assigned routing, retry, circuit, verification, and Route-Outcome Evidence semantics without widening active scope
- bounded transient retry under the same dispatch
- canonical fallback redispatch with a fresh verifier
- persistent provider-family circuit state with Closed, Open, and Half-Open recovery
- abandoned half-open probe recovery
- content-free provider-attempt telemetry
- canonical integrity-protected Route-Outcome Evidence
- optional route-backed final execution provenance projected from revalidated canonical Route-Outcome Evidence without routing or execution authority
- controlled Benchmark and Outcome Lab replay, disagreement measurement, and consequential conclusion handoff
- source-backed effective-dated route-cost attribution with explicit unknown semantics
- governed Shadow Route Evaluation with exact evidence binding, bounded specialist #82 dispositions, independent challenge, and Mission Control or maintainer review handoff
- scoped qualified-human authority grants, evidence-bound approval requests, append-only disposition states, expiry and revocation, temporal-causality enforcement, and terminal human finalization
- recovery-authority regression guards that preserve effective risk and human-approval requirements across fallback and circuit preparation
- strict external JSON Schema boundaries
- verifier-calibration instrumentation
- blinded independent-human review tooling
- a separate provisional provider-diverse machine-panel evidence path
- a six-card regulated evidence/freshness pilot with CI validation and mutation resistance
- an active `orchestration-evaluation-analyst` specialist with bounded shadow-recommendation states and no live routing authority
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
- reviewed route adaptation beyond completed shadow evaluation
- broader evidence-governed live execution beyond the bounded current canary
- TEO-managed API-key provisioning
- TEO-managed OAuth login
- TEO-managed subscription or entitlement management
- a TEO-managed credential broker

Independent human calibration is an optional evidence-enhancement study. It can support specific claims of independent human validation when maintainers choose to run it, but it is not a release, routing, model-selection, live-scope, or architectural gate. It is tracked in [Issue #75](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/issues/75) as optional research rather than an approval authority over TEO.

Repository branch-retention cleanup tracked in [Issue #100](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/issues/100) is complete. Branch hygiene remains repository stewardship only and is not routing or runtime authority.

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

TEO includes **82 public specialist role cards**.

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
- [`community/specialists/workforce-expansion-active.yaml`](community/specialists/workforce-expansion-active.yaml)

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

The canonical routing source is [`policy/routing/core/routing.yaml`](policy/routing/core/routing.yaml). The README summarizes that policy and must not outrank it.

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
- evaluate staged live-scope candidates against actual routing, redispatch, adapter, verification, and evidence gates without making a provider call
- preserve the staged documentation Sonnet 5 -> Sol fallback -> fresh Gemini 3.6 Flash recovery-verifier topology
- expose Sonnet 5 and Sol executor plus Terra verifier adapter capability without widening guarded task scope
- validate and execute the staged documentation replay harness without changing active live authority
- persist integrity-protected staged replay records and canonical Route-Outcome Evidence from operator-run replay execution
- retry bounded transient failures
- perform canonical fallback redispatch
- maintain provider-family circuit state
- record content-free provider-attempt telemetry
- execute the assigned independent verifier on the guarded live path
- build and persist canonical Route-Outcome Evidence
- revalidate a supplied Route-Outcome Evidence record during finalization and optionally project the observed active route into `FinalOutcome.execution_provenance`
- execute controlled Benchmark and Outcome Lab replay and evaluation
- preserve multi-verifier disagreement and consequential conclusion handoffs
- attribute route and verifier cost from explicit source-backed billable surfaces when evidence is sufficient
- build governed shadow-evaluation inputs from immutable evidence
- emit only bounded specialist #82 shadow-recommendation states
- independently challenge model-originated shadow recommendations
- hand verified shadow recommendations only to Mission Control or maintainer review without policy-write authority
- build scoped qualified-human authority grants and exact approval requests for existing human-required outcomes
- record approved, rejected, unable-to-determine, expired, and revoked qualified-human dispositions
- finalize a human-required outcome only when the exact scoped approval remains current, valid, and temporally causal
- finalize evidence-bearing outcomes
- preserve audit records

The live provider adapters are deliberately narrow. The current guarded execution canary is limited to explicit `high_volume_simple` work at low or medium effective risk. `documentation` is only a staged live-scope candidate and remains refused by the guarded runtime until a separate activation change satisfies all declared gates. The staged replay harness is evidence infrastructure, not active execution authority.

That narrow live-execution scope does **not** mean the routing architecture is limited to `high_volume_simple`. TEO's broader routing, risk, specialist, fallback, and verification control plane is active across the supported task taxonomy. The live canary is an execution-scope boundary, not a routing-scope boundary.

### ProviderConnection

Provider adapters receive an **already-selected** operation through the connection boundary. They may translate and execute that authorized operation, but they do not acquire authority to reroute the task.

The integrating runtime may supply API-key, OAuth/subscription-backed, delegated, connector-based, or other provider-supported access without changing TEO routing semantics.

## Verification and evidence

A successful provider call is not automatically a completed TEO outcome.

The active dispatch assigns verification independently. Finalization checks execution and verification identity, provider independence, dispatch identity, verification status, and any human-approval requirement. Where qualified-human authority is required, the model-verification path remains `awaiting_human` until a separate scoped authority record, approval lifecycle, and terminal human finalization prove that the exact gate has been satisfied.

When route-backed execution provenance is requested, finalization additionally revalidates the complete canonical Route-Outcome Evidence record and proves it matches the final dispatch, successful active execution, selected model, assigned verifier, verification status, and final disposition before exposing the compact projection. The projection is evidence only and cannot authorize later work.

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

### Optional independent human calibration

Independent blinded human calibration is an optional evidence-enhancement study. It is not required for the functional reference release and does not authorize or veto releases, routing changes, model selection, live-scope decisions, or architectural evolution.

When maintainers choose to run the study, its blinded protocol can support a specific claim that verifier evidence has been independently human-validated. Without such a study, TEO must simply avoid making that particular claim.

Normal engineering evolution remains governed by reproducible evidence, policy constraints, automated and adversarial testing, CI, public technical review, and maintainer governance. Qualified human approval remains mandatory only where the underlying task or effective-risk policy independently requires it.

The optional study is tracked in [Issue #75](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/issues/75). Public issues, pull requests, technical feedback, and voluntary study contributions remain the normal collaboration mechanisms.

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
- staged live-scope candidate identity, active-scope non-expansion, routing truth, adapter readiness, and premature-activation mutations
- repaired documentation fallback/fresh-verifier topology and staged Sonnet/Sol/Terra adapter capability without activation
- staged documentation replay plan/record integrity, whole-plan preflight, retry/circuit semantics, assigned verification, operator acknowledgement, and continued active-runtime refusal
- preview authorization
- finalization integrity guards
- route-backed final execution provenance validation, active-route binding, verifier consistency, integrity recomputation, stale/replacement rejection, and compatible legacy serialization
- qualified-human request -> disposition -> finalization temporal causality
- recovery preparation preserving effective risk and human-approval requirements
- retry and fallback behavior
- circuit recovery and abandoned half-open probe handling
- content-free telemetry
- canonical Route-Outcome Evidence integrity and lineage
- Benchmark and Outcome Lab comparability, replay, disagreement, and conclusion-control boundaries
- source-backed cost-attribution evidence, arithmetic, unknown-state, and billable-surface controls
- Shadow Route Evaluation evidence binding, bounded states, anti-Goodhart behavior, independent challenge, and authority denials
- qualified-human approval request binding, authority scope, lifecycle transitions, impersonation refusal, expiry, revocation, and finalization integrity
- live verification boundaries
- calibration evidence contracts
- human-review blinding provenance
- machine-panel evidence separation
- model-freshness governance
- provider-access separation governance
- regulated evidence validation and mutation resistance
- external JSON Schema enforcement
- documentation-truth invariants
- repository authority and lifecycle integrity

The reference CI:

1. installs a hash-pinned validation environment on a fixed Python patch version
2. validates the governed repository layout
3. compiles Python sources
4. runs the complete automated test suite
5. validates regulated specialist evidence
6. parses reference schemas
7. validates linked TEO configuration
8. executes the end-to-end reference lifecycle

Reference Implementation CI #514 remains the latest accepted substantive runtime-control baseline: 657 tests passed, 477 tracked files passed layout validation, 40 JSON Schemas parsed, regulated specialist evidence passed, linked configuration reported zero issues, and provider-diverse end-to-end verification passed. It includes the targeted temporal-authority remediation, recovery-authority regression coverage, and durable audit record. It does not create empirical provider-backed documentation replay evidence or widen live execution authority.

The exact reconciled Host Integration PR #146 head passed Reference Implementation CI #580 with 788 tests, 509 tracked files passing layout validation, 41 JSON Schemas parsed, regulated specialist evidence validation, linked configuration with zero issues, and provider-diverse end-to-end verification. This validates the non-normative Host Integration research chain through bounded-context static payload evidence, dispatch provenance, bundled-adapter self-expansion resistance, third-party adapter trust, restrictive host/TEO authority intersection, exact execution-envelope integrity, verifier-context independence, and exact artifact/change-set stale-PASS resistance while leaving CI #514 as the accepted substantive runtime baseline.

The documentation-reconciliation baseline CI #602 passed **802 tests**, **515 tracked-file layout checks**, **41 parsed JSON Schemas**, regulated specialist evidence validation, valid linked configuration, and provider-diverse end-to-end verification. That validation includes the route-backed final execution provenance baseline and accepted Task Intent & Action Authority research record. It does not make non-normative research normative and does not create provider-backed documentation replay evidence.

The later brokered cross-process Host Integration research slice passed exact-head Reference Implementation CI #626 with **817 tests**, **520 tracked-file layout checks**, **41 parsed JSON Schemas**, regulated specialist evidence validation, valid linked configuration, and provider-diverse end-to-end verification before PR #156 was squash-merged. This remains non-normative process-lifetime evidence; production remote/distributed authenticity and effect-evidence gates remain open.

The static runtime-wired authority-surface reconciliation research head passed Reference Implementation CI #644 with **842 tests**, **525 tracked-file layout checks**, **41 parsed JSON Schemas**, regulated specialist evidence validation, valid linked configuration, and the provider-diverse artifact-bound end-to-end reference lifecycle. It remains non-normative evidence and leaves dynamic executable-hook and plugin discovery, transitive-code identity, and production authenticity open.

The corrected process-lifetime recursion-resistance research head passed Reference Implementation CI #658 with **863 tests**, **528 tracked-file layout checks**, **41 parsed JSON Schemas**, regulated specialist evidence validation, valid linked configuration, and the provider-diverse artifact-bound end-to-end reference lifecycle. It remains non-normative evidence and leaves restart-durable and distributed recursion coordination, production scheduler containment, remote host identity/authenticity, and compromised-host bypass resistance open.

The staged documentation replay harness itself was validated earlier in Reference Implementation CI #488 with controlled fake provider transports. Provider-backed replay remains a separate empirical evidence gate.

The 2026-08-10 post-v1 hard audit is recorded in [`docs/history/audits/post-v1-hard-audit-2026-08-10.md`](docs/history/audits/post-v1-hard-audit-2026-08-10.md). The 2026-08-11 authority/recovery control-integrity audit is recorded in [`docs/history/audits/control-integrity-authority-recovery-audit-2026-08-11.md`](docs/history/audits/control-integrity-authority-recovery-audit-2026-08-11.md).

CI validates the control plane. It does not convert provisional or simulated evidence into empirical provider-backed claims.

## Getting started

### For humans

1. Read [`CONSTITUTION.md`](CONSTITUTION.md), [`docs/philosophy/manifesto.md`](docs/philosophy/manifesto.md), and [`docs/specification/lexicon.md`](docs/specification/lexicon.md).
2. Read [`docs/releases/v1-readiness.md`](docs/releases/v1-readiness.md) and the [`v1.0.0 release contract`](docs/releases/v1.0.0.md).
3. Read the canonical [`docs/stewardship/progress-tracker.md`](docs/stewardship/progress-tracker.md) for current post-v1 sequencing.
4. Read [`policy/governance/v1-readiness.yaml`](policy/governance/v1-readiness.yaml).
5. Read [`policy/governance/model-freshness.yaml`](policy/governance/model-freshness.yaml).
6. Read [`policy/governance/provider-access-separation.yaml`](policy/governance/provider-access-separation.yaml).
7. Read [`policy/governance/repository-layout.yaml`](policy/governance/repository-layout.yaml).
8. Review [`community/teams/mission-control.md`](community/teams/mission-control.md).
9. Review canonical routing under [`policy/routing/`](policy/routing/).
10. Review runtime controls under [`policy/runtime/`](policy/runtime/).
11. Review verification policy under [`policy/verification/`](policy/verification/).
12. Review specialists under [`community/specialists/`](community/specialists/).
13. Review current model and provider evidence under [`policy/routing/core/implementation-defaults.yaml`](policy/routing/core/implementation-defaults.yaml) and [`registry/`](registry/).
14. Review the completed evidence and authority contracts in [`docs/specification/route-outcome-evidence.md`](docs/specification/route-outcome-evidence.md), [`docs/specification/final-execution-provenance.md`](docs/specification/final-execution-provenance.md), [`docs/specification/benchmark-outcome-lab.md`](docs/specification/benchmark-outcome-lab.md), [`docs/specification/source-backed-cost-attribution.md`](docs/specification/source-backed-cost-attribution.md), [`docs/specification/shadow-route-evaluation.md`](docs/specification/shadow-route-evaluation.md), and [`docs/specification/qualified-human-approval-lifecycle.md`](docs/specification/qualified-human-approval-lifecycle.md).
15. Review the staged live-scope candidate gate in [`policy/runtime/live-execution-expansion.yaml`](policy/runtime/live-execution-expansion.yaml) and its evidence under [`research/runtime/`](research/runtime/).
16. Review accepted non-normative architecture directions in [`research/roadmaps/`](research/roadmaps/) without treating them as current policy or runtime authority.
17. Review the latest hard-audit record under [`docs/history/audits/`](docs/history/audits/).
18. Run validation and tests.

### For AI agents

Read in this order:

1. [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md)
2. [`docs/stewardship/progress-tracker.md`](docs/stewardship/progress-tracker.md)
3. [`policy/governance/model-freshness.yaml`](policy/governance/model-freshness.yaml)
4. [`policy/governance/provider-access-separation.yaml`](policy/governance/provider-access-separation.yaml)
5. [`policy/routing/core/team-routing.yaml`](policy/routing/core/team-routing.yaml)
6. [`community/teams/`](community/teams/)
7. [`community/workers/`](community/workers/)
8. [`community/specialists/`](community/specialists/)
9. [`policy/routing/core/routing.yaml`](policy/routing/core/routing.yaml)
10. [`policy/runtime/`](policy/runtime/)
11. [`policy/verification/`](policy/verification/)
12. [`policy/routing/core/implementation-defaults.yaml`](policy/routing/core/implementation-defaults.yaml)
13. [`registry/`](registry/)
14. [`reference/datasets/`](reference/datasets/)

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

When canonical Route-Outcome Evidence for the final active dispatch is available, request the compatible execution-provenance projection with:

```bash
teo --repo-root ../../.. finalize \
  /tmp/teo-dispatch.json \
  execution-result.json \
  verification-result.json \
  --route-outcome route-outcome-record.json \
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

Human-required Route-Outcome Evidence remains `awaiting_human`; qualified-human finalization is a separate integrity-protected authority record rather than a rewrite of that historical outcome.

## Repository structure

```text
.
├── README.md
├── CONSTITUTION.md
├── AI_INSTRUCTIONS.md
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── LICENSE
├── pyproject.toml
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
│   ├── stewardship/
│   ├── releases/
│   ├── examples/
│   └── history/
│
├── research/
│   ├── roadmaps/
│   ├── models/
│   └── runtime/
│
├── tests/
├── ci/
└── assets/
```

Repository placement is governed by [`policy/governance/repository-layout.yaml`](policy/governance/repository-layout.yaml) and explained in [`docs/stewardship/repository-layout.md`](docs/stewardship/repository-layout.md).

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

### Repository information architecture

**R1 through R5 complete.**

The repository layout is governed and CI-enforced. Root normalization, documentation lifecycle separation, routing policy topology, worker-extension topology, and implementation-default placement are complete. Historical activation and audit records remain preserved separately from current authority.

### Current development line

Current `main` identifies as `teo-reference-router==1.0.1.dev0`. It contains post-v1 compatible stewardship, repository-organization, integrity, evidence, controlled-evaluation, qualified-human authority, route-backed final execution provenance, and staged live-scope evaluation work while `v1.0.0` remains the immutable stable release.

Route-Outcome Evidence, the Benchmark and Outcome Lab, Source-backed Cost Attribution, Shadow Route Evaluation, and the Qualified-human approval lifecycle have completed their current milestones. The canonical `NOW` workstream is evidence-governed live execution expansion, now at 65%. `documentation` is the first staged candidate and remains `activation_authorized: false`. Its provider-diverse fallback/fresh-verifier topology, direct Sonnet/Sol/Terra adapter readiness, and staged replay harness are validated. The next gate is provider-backed controlled documentation replay evidence. That gate is currently deferred as an open action item, not removed or bypassed. The current low or medium risk `high_volume_simple` canary remains the only accepted live execution scope until the candidate also passes provider-backed replay, shadow, recovery, rollback, and independent-review gates. High and critical live execution remains unauthorized.

The Host Integration Contract remains non-normative after satisfying two-host architecture diversity, static bounded-context payload economics, process-local dispatch provenance, bundled-adapter payload self-expansion resistance, process-local third-party adapter trust, restrictive host/TEO authority intersection and execution-scope binding, exact process-local execution-envelope integrity, verifier-context independence, exact artifact/change-set stale-PASS resistance, brokered conformant process-lifetime cross-process authority/replay resistance, and static runtime-wired authority-surface reconciliation. Reference Implementation CI #644 validated the latest executable research slice with 842 tests, 525 tracked-file layout checks, regulated specialist evidence validation, 41 JSON Schemas, valid linked configuration, and the provider-diverse artifact-bound end-to-end reference lifecycle. Remaining promotion evidence includes production-grade remote/distributed authenticity and provenance controls beyond the brokered conformant path, result/effect receipt authenticity, provider/model economics and task-adherence evidence, revision freshness and expiry semantics, task-admission authority separation, dynamic executable-hook and plugin authority-surface discovery, recursion/recovery failure behavior, host identity and resource/credential/tenant binding, restart/distributed replay and retry coordination, transitive-code identity, and independent review against parallel routing or authority planes. The next bounded provider-independent Host Integration gate should be selected from those remaining evidence requirements after repository recalibration. This research does not alter the canonical `NOW` sequencing or live authority.

The Execution Environment & Recovery Contract and Task Intent & Action Authority Contract are accepted non-normative future research directions. They preserve TEO's vendor-neutral control-plane boundary and do not authorize a specific sandbox, change Task/Dispatch schemas, create a second permissions plane, or widen current live execution.

The 2026-08-10 hard audit reconciled lifecycle, release, and model-evidence metadata and is preserved at [`docs/history/audits/post-v1-hard-audit-2026-08-10.md`](docs/history/audits/post-v1-hard-audit-2026-08-10.md). The 2026-08-11 targeted authority/recovery audit is preserved at [`docs/history/audits/control-integrity-authority-recovery-audit-2026-08-11.md`](docs/history/audits/control-integrity-authority-recovery-audit-2026-08-11.md).

### Post-v1 stewardship and hardening

Current and future work may include:

- evidence-governed live-scope expansion, the current canonical `NOW` workstream
- provider-backed controlled documentation replay followed by shadow, recovery, rollback, and independent-review gates
- continuing adversarial control-integrity hardening and mutation coverage
- remaining adversarial Host Integration Contract research before any normative schema or reference-runtime promotion
- Execution Environment & Recovery Contract research without selecting a mandatory execution substrate prematurely
- Task Intent & Action Authority Contract research before any machine-readable request-authority schema or runtime gate is proposed
- optional independent blinded human calibration research ([Issue #75](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/issues/75))
- distributed circuit-state coordination
- distributed telemetry export and retention controls
- streaming execution paths
- governed route adaptation only after independently challenged shadow evidence and maintainer review
- continued regulated-evidence pilot observation
- ongoing model-freshness reviews as provider catalogs evolve

Repository branch-retention cleanup under [Issue #100](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/issues/100) is complete and is not a control-plane blocker.

These are extensions, evidence-strengthening, or stewardship work. They should not be confused with missing core routing architecture.

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
