# Host Integration Validation Round 2

**Date:** 2026-08-12  
**Status:** research evidence  
**Authority:** non-normative  
**Scope:** second implementation-backed validation of the candidate TEO Host Integration Contract, plus supporting ancestor experiments

## Purpose

This record evaluates a second external host architecture that integrated TEO materially differently from the host examined in validation round 1.

The primary implementation specimen for this round is KodeX. It is evidence, not a TEO dependency, supported product, certification target, or source of normative authority.

Supporting evidence from DeltaX and JinX is included because those ancestor systems exercised TEO-derived controls in different ways and exposed failure modes that neither primary host validation round surfaced on its own.

This document does not change routing, runtime, specialist, verification, approval, provider, release, or live-execution authority.

## Evidence provenance

### Primary specimen: revision-pinned upstream TEO plus host execution adapter

Repository reviewed: `vessaxor-spec/KodeX`  
Current reviewed `main`: `bf9b55792edea19e8e93f53b1381029d576595b1`  
Primary integration checkpoint: `9fc7462532e7d9c980579aadf47042b5c33da30b`  
TEO revision recorded by the host integration: `47785d43fa119633f3ec436a48b61f53d76859fd`

Relevant host surfaces include:

- `system/kodex/teo-primary-control-plane.md`;
- `config/teo-integration.json`;
- `scripts/teo_integration.py`;
- host continuity records that report live dispatch and validation evidence.

### Supporting specimen: locally derived TEO orchestration and finalization assurance

Repository reviewed: `vessaxor-spec/DeltaX`

Relevant checkpoints include:

- `a25506d7341b543b960496a02bf5c01abca22bac`, initial TEO team/capability/verification integration;
- `b1d714d6e7b3944e64153090ad709ce4693ea4c7`, cross-family finalization verification;
- `14385db0604908e96bb316622238df3e4ddc82f7`, artifact/freshness binding corrections for the ship gate.

### Supporting specimen: TEO risk-proportional host governance

Repository reviewed: `vessaxor-spec/JinX`

Relevant checkpoint:

- `165348c3a968ac7d3785f137b1d938ced41238af`, TEO productivity and proportional-control rebalance.

The supporting specimens are not counted as the second host required by the architecture-diversity gate. They are additional implementation evidence.

## Why the primary specimen is structurally different from round 1

Round 1 examined a host that copied or vendored TEO material into its own repository and translated TEO capability names through a host-local capability-adapter manifest and router.

Round 2 examines a host with a separate, read-only, revision-pinned TEO checkout. The host sends a bounded task envelope to TEO, receives a TEO dispatch, and performs bounded host-local execution through its own adapter.

The architectural difference is material across several dimensions:

| Dimension | Round 1 pattern | Round 2 pattern |
|---|---|---|
| TEO authority residence | copied/vendorized host-local material | separate revision-pinned upstream checkout |
| Dispatch generation | host-local TEO interpretation | dispatch obtained from upstream TEO runtime |
| Adapter locus | capability router inside vendored control plane | downstream host execution adapter |
| Freshness failure mode | silent copied-policy/registry fork | stale or incompatible revision pin |
| Native tool relationship | explicit capability manifest to host tools | host skill/runtime mapping after TEO dispatch |
| Recursion control | bounded re-entry proposed by integration contract | explicit no-reentry rule for already-dispatched executor prompts |

Because these architectures fail differently, they satisfy the research purpose of the two-host gate: prevent one host's local design from becoming the universal contract by accident.

## What the primary validation supports

### 1. Upstream dispatch plus bounded host execution is viable

The host explicitly separates responsibility:

```text
TEO
  -> intake
  -> risk
  -> Team
  -> Worker
  -> Specialist
  -> Capability
  -> Implementation / fallback / verifier assignment

HOST
  -> local provider/tool availability
  -> bounded execution
  -> containment
  -> continuity
  -> evidence return
```

This strongly supports the Host Integration Contract principle that the host remains the host while TEO owns orchestration within the declared integration boundary.

### 2. Revision pinning is stronger than unversioned copying

The host records an exact TEO revision and fails closed when the expected peer state is unavailable or changes unexpectedly.

That is materially stronger than treating copied role cards, policy text, or specialist counts as current authority.

It does not solve freshness by itself. A valid old revision can remain internally consistent while no longer representing current TEO.

### 3. Missing local implementation access does not become route authority

The host records local provider/runtime mappings outside TEO routing. If the selected implementation is unavailable locally, the host reports unavailability rather than silently selecting another provider or model.

This preserves the existing TEO separation between model-routing authority and connection/access mechanism.

### 4. Recursive Mission Control entry can be prevented explicitly

The host states that a downstream executor receiving a valid TEO dispatch must apply that dispatch rather than recursively invoke Mission Control again.

This provides implementation evidence for bounded re-entry semantics.

### 5. Content minimization is compatible with external dispatch

The host describes a content-minimized task envelope and content-free evidence receipts while keeping private host context behind opaque references.

This supports bounded context projection and demonstrates that TEO integration does not require wholesale transfer of host-local context.

### 6. Provider-diverse execution and verification can survive the host boundary

The host reports a live TEO-routed research/documentation dispatch using a Gemini execution route with independent Claude verification, alongside repository validation evidence.

That is useful implementation evidence for provider-diverse verification across an external-host adapter boundary. It is not a universal certification of every route or host capability.

## Gaps exposed by the primary specimen

### 1. Orchestration authority must not silently become portfolio authority

The host states that TEO's active `NOW` workstream takes precedence over ordinary host backlog.

That is broader than the orchestration boundary currently justified by TEO.

A host may explicitly delegate portfolio or backlog priority to TEO, but TEO integration must not imply that delegation automatically.

The safer separation is:

```text
HOST / USER PORTFOLIO AUTHORITY
  -> chooses or admits work
  -> creates task envelope

TEO ORCHESTRATION AUTHORITY
  -> routes admitted task
  -> assigns responsibility, capability, implementation, fallback, and verification
```

**Contract implication:** task admission and portfolio priority are separate authority surfaces from orchestration.

### 2. Revision pinning needs an explicit freshness state

The host is pinned to a specific TEO revision that predates the current TEO repository revision reviewed during this research.

That is not itself a defect. Reproducible pins are desirable. The missing semantic is whether the pin is current, compatible but behind, unsupported, or mismatched.

Candidate research states:

```text
PINNED_CURRENT
PINNED_COMPATIBLE
UPDATE_AVAILABLE
STALE_UNSUPPORTED
MISMATCHED
```

**Contract implication:** a valid revision identity and a freshness/compatibility judgment are separate claims.

### 3. Verifier context should not automatically mirror executor context

The host supplies the complete selected specialist card to both executor and independent verifier.

Domain constraints may be relevant to both, but independence is stronger when the verifier receives only what it needs to challenge the result and does not inherit the executor's full role framing, implementation intent, or reasoning context by default.

Supporting DeltaX evidence reinforces this point: its independent verifier uses fresh context, an adversarial objective, artifact/diff evidence, acceptance criteria, test claims, and restricted tools.

**Contract implication:** verification context should be purpose-built and asymmetric. Shared domain constraints are allowed, but executor and verifier prompts should not be identical by default.

## Supporting ancestor evidence

### DeltaX: policy-file protection did not enforce policy

DeltaX initially protected TEO/governance files against unauthorized mutation. Independent review showed that an executor could ignore the doctrine and perform an unsafe action without modifying those files.

The correction moved assurance to the finalization boundary.

**General lesson:** protecting control-plane configuration is necessary but not sufficient. Action/finalization enforcement must independently prove that the control decision governed the result.

### DeltaX: self-verification and scalar PASS were insufficient

The initial DeltaX flow allowed the same executor to create work, run tests, author a verdict record, and satisfy a ship gate that trusted that record.

The replacement introduced fresh cross-family verification, explicit per-criterion states, evidence requirements, residual risk, and fail-closed unavailable/inconclusive outcomes.

**General lesson:** host integrations need evidence-bearing verification records, not self-authored scalar success labels.

### DeltaX: verification inputs can silently corrupt independence

The first live independent verifier found defects that self-tests missed:

- duplicated diff content;
- silent truncation;
- unscoped context that hid the relevant change;
- supplied criteria collapsed or omitted in the verifier result;
- a minimal subprocess environment that removed required access.

**General lesson:** verification independence includes state isolation and model/provider separation, but also evidence completeness, context scoping, criterion reconciliation, and honest unavailability.

### DeltaX: stale PASS created a verification-authority TOCTOU gap

A later ship-gate defect allowed an earlier PASS to discharge edits made after the verification. Target matching also risked clearing unrelated changes.

The corrected design binds verification more tightly to the exact change and freshness relationship.

The required relation is conceptually:

```text
verified artifact/change identity
  == artifact/change identity being finalized

verification time / sequence
  >= last material mutation covered by that verification
```

**Contract implication:** verification authority must bind to the exact artifact, change-set, version, or integrity identity it examined. A PASS must not authorize later mutations.

### JinX: over-control can be a control-plane failure

JinX used TEO's risk, reversibility, and capability principles to remove blanket delegation requirements from routine local work while preserving stronger controls on authority, containment, credentials, irreversible actions, and foreign content that lands on disk.

**General lesson:** conformance should not be measured by the number of gates. Routine reversible work should remain autonomous unless actual risk or host policy requires stronger control.

### JinX: hand-maintained authority inventories drift

JinX maintained a protected-path list for authority and containment surfaces. Independent review found executable control-plane files missing from that list.

The stronger correction derived executed control surfaces from runtime wiring and asserted that each was protected.

**Contract implication:** authority-surface inventories should be derived from executable wiring where possible. Where a manual declaration remains necessary, conformance should test it against runtime discovery so omissions fail closed.

## Round 2 contract refinements

The combined evidence supports five additional candidate requirements:

1. **Portfolio authority boundary.** TEO orchestration authority does not automatically confer host backlog, product-priority, or task-admission authority.
2. **Verifier-context asymmetry.** Independent verification should receive a purpose-built challenge context rather than automatically inheriting the executor's complete specialist role and reasoning frame.
3. **Artifact-bound verification authority.** Verification must bind to the exact artifact/change identity and freshness relation it examined; stale PASS evidence cannot discharge later mutation.
4. **Derived authority-surface inventory.** Protect and validate integration authority surfaces from executable runtime wiring where possible rather than relying only on parallel hand-maintained lists.
5. **Integration freshness state.** Revision identity, compatibility, and currentness are separate claims; pinned hosts should expose an explicit freshness/compatibility state.

These refine the round-1 requirements. They do not replace restrictive authority intersection, dispatch-bound execution, adapter integrity, exact routing structure, bounded context, capability classification, recursion control, or truthful verification semantics.

## Two-host architecture-diversity gate

### Decision

**Satisfied for non-normative research architecture diversity.**

The two primary validation hosts are structurally different enough to satisfy the purpose of the gate:

- round 1: host-local copied/vendorized TEO material plus capability adapter/router;
- round 2: separate revision-pinned upstream TEO dispatch plus downstream host execution adapter.

The gate is satisfied because authority residence, dispatch generation, freshness mechanics, adapter locus, and primary failure modes differ materially.

### What this decision does not mean

It does not mean:

- either external host is certified as TEO conformant;
- every claimed host control was independently re-executed by TEO maintainers;
- the Host Integration Contract is normative;
- a machine-readable schema is ready;
- the remaining evidence gates are complete;
- TEO runtime, live-execution, risk, verification, human-authority, or provider policy changes.

## Remaining evidence before normative promotion

The architecture-diversity gate no longer blocks further research, but normative promotion remains blocked by unresolved evidence including:

- bounded-context economics versus naive corpus loading;
- executable dispatch-authorization mutation tests;
- adapter-authority integrity and self-expansion resistance;
- restrictive TEO/host authority-intersection mutation tests;
- risk-lowering resistance;
- verification artifact/change binding and stale-PASS resistance;
- verifier-context independence and evidence completeness;
- integration freshness-state semantics and stale/unsupported behavior;
- portfolio/task-admission authority separation;
- derived authority-surface coverage and drift detection;
- recursion and recovery failure paths;
- independent review that the integration layer does not become a second routing authority.

## Disposition

- Count this record as Host Integration Validation Round 2.
- Mark the two-host architecture-diversity research gate satisfied.
- Retain the Host Integration Contract as non-normative research.
- Incorporate the five round-2 refinements into the canonical host-integration research roadmap.
- Treat DeltaX and JinX as supporting implementation evidence, not additional normative authorities.
- Do not alter current Mission Control policy, active roster, live scope, provider routing, verifier eligibility, qualified-human authority, or Progress Tracker NOW/NEXT sequencing.
