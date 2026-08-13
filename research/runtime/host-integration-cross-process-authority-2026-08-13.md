# Host Integration cross-process authority research

Date: 2026-08-13  
Status: non-normative research  
Scope: provider-independent, brokered process-lifetime Host Integration authority

## Question

Can an external host process consume one exact TEO-authorized action without gaining the ability to mint TEO authority, mutate the routed dispatch or action snapshot, replay an execution claim, or multiply the current TEO retry budget?

This is deliberately narrower than the production Host Integration promotion requirement for cross-process or distributed dispatch/exact-action authenticity and replay. The experiment tests a conformant brokered process boundary. It does not claim that an untrusted or compromised host is unable to bypass the broker and mutate resources through some other local mechanism.

## Mission Control lenses

- Orchestration Architecture
- Host Integration
- Runtime Security and Least Authority
- Independent Verification

## Recalibration

Repository truth at the start of this slice:

- stable release remained `v1.0.0`;
- development line remained `1.0.1.dev0`;
- current `main` was `ea97df46f4d96b720a61c0aea42b4295fe2e6992`;
- guarded live execution remained limited to `high_volume_simple` at low or medium effective risk;
- `documentation` remained staged with `activation_authorized: false`;
- provider-backed controlled `documentation` replay remained deferred pending legitimate provider access;
- the Host Integration Contract remained explicitly non-normative;
- the Host Integration roadmap still required production/distributed authenticity, resource/credential/tenant binding, distributed retry coordination, freshness, and independent review before normative promotion;
- draft PR #154 independently owned the artifact-bound finalization remediation and was not modified by this slice.

The current sequencing therefore rejected a normative Host Integration protocol implementation. Provider-independent adversarial research remained admissible while the live replay gate was deferred.

## Diagnosis

The existing exact execution-envelope research proved only a process-local authority object. That authority already binds:

- the complete `DispatchRecord` snapshot;
- effective risk;
- capability and operation;
- exact resource target;
- canonical parameters;
- side-effect class;
- prerequisites;
- TEO and host execution scopes;
- exact attempt number;
- the effective retry budget;
- single-use execution tokens.

The remaining question was whether the same authority state could stay on the TEO side while a separate host process requested and consumed an exact execution authorization.

A self-contained host-verifiable signed capability was intentionally not introduced. The repository has no approved production signing/key-management boundary for Host Integration, and introducing one through a research slice would have created new key custody, rotation, revocation, persistence, and trust-anchor questions before the current roadmap permits normative promotion.

## Candidate boundary

The research harness introduces a brokered loopback authority endpoint.

### TEO-side authority

The TEO-side process:

1. creates the existing `ExecutionEnvelopeAuthority` from current live and retry policy;
2. issues one exact TEO action before exposing the host endpoint;
3. retains all mutable authority state and retry/replay state;
4. creates one random process-lifetime authority session identifier;
5. exposes only `authorize` and `claim` operations.

The endpoint exposes **no action-issuance operation**.

### Host-side request

A host process receives the exact authority descriptor and may request only:

- the declared research protocol version;
- the exact authority session;
- the already-issued action token;
- the exact dispatch snapshot;
- the exact action snapshot;
- satisfied prerequisites;
- an exact positive integer attempt number;
- for `claim`, the previously issued execution token.

Unknown fields are rejected rather than best-effort parsed. The host cannot provide a fallback override, replacement provider/model choice, or other undeclared widening field through this protocol surface.

### Brokered authorization

The TEO-side gateway revalidates:

- protocol version;
- authority-session identity;
- the authority-issued action token;
- canonical dispatch equality;
- canonical action equality;
- prerequisites;
- attempt sequencing and budget through the existing exact execution-envelope authority.

A gateway lock serializes state-changing authorization and claim operations so concurrent duplicate claims cannot both consume the same execution token.

### Claim semantics

`claim` means that the conformant host integration path has consumed one TEO-side execution authorization. It is **not** evidence that the external side effect subsequently occurred or that the host could not bypass the integration path.

A future production protocol would need separate result/effect evidence, appropriate host identity and transport authenticity, and an OS/resource authority boundary before this could support stronger execution claims.

## Executable adversarial matrix

The tests exercise separate Python host processes over the loopback broker and cover:

1. positive exact-action authorization and claim across separate host processes;
2. rejection of host-requested TEO action issuance;
3. rejection of a host-minted action token;
4. rejection of dispatch mutation;
5. rejection of action/parameter mutation;
6. rejection of cross-session token reuse;
7. rejection of old action-token reuse even when the host substitutes the new session, dispatch, and action snapshots;
8. rejection of unknown protocol fields such as a host fallback override;
9. rejection of a claim without prior authorization;
10. single-use execution-claim enforcement across host processes;
11. concurrent duplicate-claim serialization with exactly one successful claimant;
12. one-pending-attempt enforcement;
13. rejection of reauthorizing a consumed attempt while allowing the next sequential attempt;
14. rejection of a third host attempt when the effective TEO/action budget is two, even though the host limit is broader;
15. rejection of boolean and string attempt values masquerading as integers.

The child process does not receive the mutable `ExecutionEnvelopeAuthority` object. It loads only the transport helper and submits the bounded request to the authority broker.

## Red-canary evidence

Reference Implementation CI #624 was intentionally preserved as red evidence after the first implementation attempt.

Results:

- repository layout validation passed;
- Python compilation passed;
- 811 tests passed;
- 6 tests failed.

The six failures were all negative-path transport failures. The underlying exact-action authority raised the expected `ExecutionEnvelopeError` for replay, missing authorization, duplicate pending attempt, stale attempt sequence, and retry-budget exhaustion, but the test had loaded the base research harness twice with `runpy`. That produced two distinct Python exception-class identities. The TCP handler therefore failed to recognize the externally injected authority instance's otherwise-correct rejection and closed the child connection.

No failed case was incorrectly authorized.

The correction made the test use the same base-harness instance already loaded by the cross-process module. It did not broaden the production catch clause, alter action authorization, weaken replay enforcement, or change current TEO authority.

## Green verification

Exact-head Reference Implementation CI #625 passed on commit `79db1c22a194b669b1717491349ca8a4a0ad9330` with:

- **817 automated tests passed**;
- **519 tracked-file layout checks**;
- regulated specialist evidence structural validation passed;
- **41 JSON Schemas parsed**;
- linked TEO configuration status `valid` with zero issues;
- the provider-diverse end-to-end example passed.

The end-to-end repository example continued to preserve provider-diverse independent verification. This research did not alter routing policy, provider adapters, schemas, live scope, or finalization behavior.

A final exact-head CI run after this research record is added remains required before merge.

## What this supports

For the tested brokered process-lifetime boundary, the evidence supports the following narrower claim:

> A conformant external host process can request and consume one exact TEO-side authorization while TEO retains the mutable authority/replay state; the tested host path cannot mint a TEO action, mutate the bound dispatch/action, reuse an execution claim, race two successful claims, or multiply the effective TEO retry budget through the exposed protocol.

This is useful evidence for a future host-native execution protocol because it preserves the architectural split in which TEO owns orchestration/authority decisions while an embedding host may own native provider or tool transport.

## What this does not support

This slice does **not** prove:

- that a compromised host cannot bypass the broker and mutate its own environment directly;
- disconnected or self-verifying signed execution envelopes;
- network-adversary security or remote transport authenticity;
- OS sandbox, privilege, namespace, filesystem, symlink, mount, or resource containment;
- host process identity, user identity, credential, account, or tenant binding;
- confidentiality of bearer tokens against another process with equivalent local access;
- authority persistence, replay state, or retry coordination after TEO process restart;
- distributed consensus or multi-node authority synchronization;
- production resource canonicalization;
- provider/model economics, latency, or task adherence;
- result/effect receipt authenticity after authorization is consumed;
- production Host Integration schema or transport semantics;
- normative Host Integration promotion;
- any widening of current TEO live-execution authority.

Because these limits remain material, the existing roadmap requirement for cross-process or distributed dispatch/exact-action authenticity and replay remains **open at the production/normative boundary**. This experiment narrows that gap but does not close it.

## Decision

**Brokered process-lifetime cross-process authority and replay resistance is supported for the tested conformant boundary.**

Do not promote the Host Integration Contract from this evidence alone. Preserve the current provider-backed `documentation` replay sequencing and all current routing, verification, qualified-human, and live-execution authority boundaries.

A future production Host Integration design should reuse this separation of authority from host-native execution, but must independently solve the remaining production authenticity, host identity, resource/credential/tenant binding, restart/distributed replay, effect-evidence, and independent-review gates before normative promotion.
