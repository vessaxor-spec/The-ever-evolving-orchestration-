# Host Integration recursion-resistance research

Date: 2026-08-14  
Status: non-normative research  
Scope: provider-independent process-lifetime orchestration recursion admission

## Question

Can TEO keep an external host from multiplying orchestration through specialist spawn, TEO re-entry, parallel branching, or recovery loops beyond an explicit root-scoped budget, without changing current runtime or live authority?

This experiment is deliberately process-local and process-lifetime only. It does not claim restart-durable, remote, distributed, scheduler-level, or compromised-host enforcement.

## Mission Control lenses

- Host Integration Architecture
- Security and Authority Boundaries
- Verification and QA
- Program and Progress Governance

## Recalibration

Repository truth at the start of this slice:

- current `main` was `1b37f1b9dd84c7797a8e3fdcdf24708d029657b6`, the PR #161 merge;
- stable release remained `v1.0.0` and the development line remained `1.0.1.dev0`;
- guarded live execution remained limited to `high_volume_simple` at low or medium effective risk;
- `documentation` remained staged with `activation_authorized: false` and `controlled_replay: null`;
- provider-backed controlled `documentation` replay remained deliberately deferred pending legitimate provider access;
- the Host Integration Contract remained non-normative;
- the only open repository issue remained optional Issue #75;
- the Host Integration roadmap still listed recursion resistance as an open pre-normative gate.

The current sequencing therefore permitted provider-independent Host Integration adversarial research but did not permit this work to widen routing, execution, or authority.

## Diagnosis

Existing controls cover adjacent but different failure modes:

- specialist-spawn routing makes preserved specialists deterministically reachable while preserving Team -> Worker -> Specialist ordering and provider-diverse verification;
- guarded provider retry remains on the same dispatch and is capped independently by `max_attempts_per_dispatch`;
- recovery integrity tests preserve effective risk and qualified-human requirements during redispatch;
- prior Host Integration research binds exact host actions and brokered process-lifetime action retry state.

None of those surfaces establishes a root-scoped orchestration budget that prevents a host from repeatedly causing new TEO entries, specialist spawns, parallel descendant branches, or recovery generations.

That is a distinct control problem. Provider retry is not orchestration recursion, and orchestration recursion must not be allowed to reset provider/action/recovery authority budgets.

## Research boundary

The executable harness introduces a non-normative `ProcessLocalRecursionAuthority` whose mutable state remains TEO-side.

Each root is bound to:

- exact `dispatch_id`;
- exact `task_id`;
- SHA-256 of the canonical root dispatch snapshot;
- immutable recursion-limit digest.

The root recursion limits are:

- maximum TEO re-entry depth;
- maximum total descendant admissions;
- maximum specialist spawns;
- maximum concurrently active descendant branches;
- maximum recovery generations.

Descendant entry kinds are deliberately explicit:

- `specialist_spawn`;
- `teo_reentry`;
- `recovery_reentry`.

A descendant requires a TEO-issued authorization bound to the exact root, parent lease, request identity, entry kind, depth, recovery generation, state revision, dispatch digest, and limits digest.

The authorization token is HMAC-SHA-256 over those claims using a process-local secret retained by the authority. The authorization itself is stateless: repeated host authorization requests cannot create an unbounded pending-token store. Claimed token and request identities remain bounded by the root descendant budget.

A successful claim advances the root revision. Any other authorization created against the prior revision becomes stale. This serializes authority-state mutation even when host callers race claims.

Releasing a descendant frees only its active-branch slot. It does not refund total descendant admissions or specialist-spawn consumption. A parent cannot be released while an active child remains.

## Executable adversarial matrix

The new test module contributes 21 executable cases covering:

1. a bounded specialist -> re-entry -> recovery lineage;
2. duplicate root-budget creation for one dispatch;
3. depth overflow;
4. non-refundable total descendant budget after release;
5. non-refundable specialist-spawn budget after release;
6. active parallel-branch ceiling with release of concurrency only;
7. recursive recovery-generation overflow;
8. recovery attempting to reset consumed root budget;
9. host-forged authorization token;
10. authorization replay;
11. stale parallel preauthorization after state advancement;
12. cross-root authorization reuse;
13. lease budget/dispatch-binding tampering;
14. authorization lineage-counter tampering;
15. unknown widening fields on host-visible records;
16. request-identifier replay after child release;
17. parent release while a child remains active;
18. descendant creation from a released parent;
19. concurrent same-revision claim racing;
20. host attempt to release the root lease and reset the session;
21. invalid or internally widening recursion-limit definitions.

## Verification history

The initial executable head passed Reference Implementation CI #656 with:

- **863 automated tests passed**;
- **528 tracked-file layout checks**;
- regulated specialist evidence structural validation passed;
- **41 JSON Schemas parsed**;
- linked TEO configuration status `valid` with zero issues;
- the provider-diverse artifact-bound end-to-end reference lifecycle passed.

No red canary occurred in that run.

A subsequent Security and Authority Boundaries review found that the first harness retained every unclaimed authorization in a process-local map. Those authorizations were claim-safe because revision checks prevented multiple successful claims, but repeated authorization without claim could still create unnecessary memory growth.

The design was tightened before documentation acceptance: host-visible authorizations became stateless HMAC-bound claims, removing the unbounded pending-authorization store while preserving single-use, revision, lineage, dispatch, and budget binding.

Corrected exact executable head `417247bbf670c48ac203b94f4a955c56649f1c55` then passed Reference Implementation CI #658 with:

- **863 automated tests passed**;
- **528 tracked-file layout checks**;
- regulated specialist evidence structural validation passed;
- **41 JSON Schemas parsed**;
- linked TEO configuration status `valid` with zero issues;
- the provider-diverse artifact-bound end-to-end reference lifecycle passed.

The provider-backed documentation replay did not run as part of this research proof and remains a separate deferred empirical gate.

## What this supports

For the tested process-local research authority, the evidence supports the following bounded claim:

> A TEO-side root-scoped recursion budget can prevent the tested external-host paths from multiplying specialist spawn, TEO re-entry, active descendant branching, or recovery generation beyond immutable process-lifetime ceilings; host-visible authorization tampering, replay, stale-state claims, cross-root reuse, release-based budget reset, and raced same-revision claims fail closed.

The evidence also supports separating same-dispatch provider retry from orchestration recursion. Existing retry policy remains authoritative for provider attempts and this research does not rewrite it.

## What this does not support

This slice does **not** prove:

- restart-durable recursion counters;
- multi-process or distributed recursion-state coordination;
- remote transport or host identity authenticity;
- protection against a compromised host that bypasses the TEO-side authority entirely;
- production scheduler, queue, process, namespace, memory, CPU, or filesystem containment;
- global portfolio or backlog admission authority;
- provider retry correctness beyond existing runtime evidence;
- that every host-native subprocess or tool call is a TEO orchestration re-entry;
- normative specialist-spawn or recovery schemas;
- origin authenticity or non-repudiation for the root dispatch outside this process;
- production-grade secret persistence, rotation, recovery, or distributed HMAC verification;
- any widening of current TEO live execution.

The HMAC is used only to make the tested process-local authorization self-authenticating without retaining unbounded pending state. It is not evidence of remote host trust, release signing, or distributed identity.

## Decision

**Process-lifetime Host Integration recursion resistance is supported at the non-normative research layer.**

The broader recursion gate remains open for restart-durable, multi-process/distributed, production-scheduler, and compromised-host boundaries, and any normative promotion would require a separate current-state design challenge and independent verification.

No new specialist is required. Existing Host Integration architecture, security/authority, verification, and program-governance lenses cover the responsibility.

This research does not supersede the provider-backed controlled `documentation` replay milestone, does not authorize `documentation`, does not change provider/model routing, and does not make the Host Integration Contract normative.