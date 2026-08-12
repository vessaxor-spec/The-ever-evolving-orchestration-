# Host Integration verifier-context and artifact-binding adversarial research

**Date:** 2026-08-12  
**Status:** validated non-normative research evidence  
**Base repository revision:** `a601882c6b33416bff7e0b0b464be42bb6541fa7`  
**Runtime authority change:** none

## Mission Control lenses

- Verification: exact evidence-to-artifact binding and verdict semantics.
- Assurance: fail-closed finalization and mutation resistance.
- Formal-methods lens: identity invariants across task, dispatch, change, artifact, revision, digest, and target reference.
- Security/red-team lens: stale PASS replay, artifact substitution, post-verification mutation, and verifier priming through executor-derived context.

## Decision point

The current Host Integration research sequence identifies verifier-context independence plus exact artifact/change-set verification and stale-PASS resistance as the next bounded provider-independent adversarial gate.

The question is narrow:

> Can a host finalize only the exact artifact that an independent verifier actually examined, without allowing executor-private context or a prior verdict to prime that verifier?

## Repository diagnosis

The current reference runtime already checks important dispatch-level verification invariants, but artifact identity is not carried structurally through the canonical verification result and finalization boundary.

Inspection of `reference/implementations/python/src/teo_reference/runtime_verification.py`, `verification_adapter.py`, `schemas.py`, and `engine.py` shows:

1. live verification reads the execution output and sends artifact text to the assigned verifier;
2. the resulting `VerificationResult` records `dispatch_id`, status, verifier model, checks, evidence, and notes;
3. `VerificationResult` does not structurally retain an artifact identifier, change identifier, revision, content digest, or target reference;
4. `OrchestrationEngine.finalize()` verifies dispatch identity and verifier assignment/independence, then treats a `passed` verification as sufficient for completion;
5. finalization does not compare the artifact examined by the verifier with the artifact being finalized.

This leaves a structural stale-PASS/substitution gap at the host integration boundary. A PASS associated with the same dispatch cannot, from the canonical result alone, prove that it belongs to the exact later artifact or revision presented for finalization.

This research slice does not label the reference runtime defective for its currently authorized scope. It demonstrates a boundary that must be closed before a Host Integration Contract can claim exact artifact-bound finalization.

## Research contract

`host_integration_artifact_bound_verification.py` introduces a research-only contract with two independent properties.

### 1. Verifier-context independence

An independent verifier request is built only from declared verification inputs:

- exact artifact identity;
- task;
- artifact text whose SHA-256 digest matches that identity;
- declared verification methods;
- assigned verifier provider family and model;
- explicit evidence references.

Opaque host context is not admitted. Executor reasoning, executor messages, conversation history, prior verdicts, and executor self-assessment are rejected before verifier invocation can be represented.

The purpose is not to claim that all contextual information is unsafe. It is to prevent an external host from silently converting verifier independence into executor-conditioned self-review. Additional context would need an explicit governed field and evidence semantics rather than an opaque context bag.

### 2. Exact artifact-bound finalization

A PASS is bound to the exact tuple:

`task_id + dispatch_id + change_id + artifact_id + revision + sha256 digest + target_ref`

Finalization fails closed unless the execution succeeded, the verdict is `passed`, and every identity field exactly matches the finalization target.

Provider family is deliberately not part of artifact identity. OpenAI, Anthropic, and Google verifier provenance can all satisfy the same binding contract when the exact verified artifact identity matches. Provider choice does not widen or weaken artifact authority.

## Mutation matrix

The targeted test matrix contains 21 cases.

### Positive controls: 4

1. independent verifier request contains only declared artifact context;
2. exact artifact PASS with OpenAI verifier provenance completes;
3. exact artifact PASS with Anthropic verifier provenance completes;
4. exact artifact PASS with Google verifier provenance completes.

### Negative/adversarial cases: 17

Verifier-context isolation:

1. executor reasoning injection is rejected;
2. executor message injection is rejected;
3. conversation-history injection is rejected;
4. host-supplied prior verdict is rejected;
5. executor self-assessment injection is rejected.

Artifact/change binding:

6. wrong task identity is rejected;
7. wrong dispatch identity is rejected;
8. wrong change identity is rejected;
9. sibling/substituted artifact identity is rejected;
10. older artifact revision is rejected;
11. changed content digest after verification is rejected;
12. wrong branch/target reference is rejected.

Verdict/execution authority:

13. exact-target `failed` verdict cannot finalize;
14. exact-target `needs_human` verdict cannot finalize;
15. failed execution cannot reuse an exact-target PASS.

Identity structure:

16. blank artifact identity is rejected;
17. malformed SHA-256 identity is rejected.

## Local verification

The isolated research harness was syntax-checked and executed with:

```text
pytest -q tests/test_host_integration_artifact_bound_verification.py
.....................                                                    [100%]
21 passed in 0.05s
```

## Repository verification

Reference Implementation CI #577 reproduced the research slice on the exact PR #146 head before stewardship reconciliation:

- 788 automated tests passed;
- 509 tracked-file layout checks passed;
- regulated specialist evidence structural validation passed;
- 41 JSON Schemas parsed;
- linked TEO configuration was valid with zero issues;
- the provider-diverse end-to-end reference lifecycle passed.

The workflow ran on GitHub-hosted Ubuntu 24.04 and completed successfully. This is repository-level conformance evidence for the non-normative research slice. It is not empirical provider-backed `documentation` replay evidence and does not widen live authority.

## What this proves

At the tested process-local Host Integration research boundary, this slice demonstrates a concrete fail-closed shape in which:

- an independent verifier cannot inherit tested executor-derived or verdict-priming host context;
- a generic PASS is insufficient;
- same-dispatch evidence cannot authorize a different change, artifact, revision, digest, or target reference;
- post-verification artifact mutation invalidates the PASS binding;
- provider provenance remains neutral to exact artifact identity.

## What this does not prove

This research does not:

- change `VerificationResult`, `FinalOutcome`, the Provider Adapter Contract, or any normative runtime schema;
- widen live execution authority;
- authorize `documentation` live execution;
- provide wall-clock evidence expiry or freshness-window semantics;
- provide signed cross-process artifact identity or distributed replay resistance;
- establish production package provenance, tenant/account binding, or distributed state synchronization;
- replace the deferred provider-backed controlled `documentation` replay gate;
- complete independent architectural review of the Host Integration Contract.

Revision/digest mismatch resistance is covered here. Time-based freshness and expiry semantics remain a separate evidence gate.

## Decision

Keep this implementation in the non-normative research plane. Do not modify canonical runtime verification/finalization schemas from this evidence alone.

Reference Implementation CI #577 reproduces the 21-case matrix inside the full repository validation suite, so verifier-context independence plus exact artifact/change-set stale-PASS resistance is satisfied at the research layer. Reconcile the Progress Tracker with the exact CI evidence before merge, preserve the deferred provider-backed `documentation` replay gate, and proceed to the next bounded Host Integration evidence gate only after repository truth is aligned.
