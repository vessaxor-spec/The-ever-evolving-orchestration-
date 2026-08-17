# Host Integration Protocol 0.1 Candidate

**Status:** reference candidate, non-normative, non-production
**Protocol identifier:** `teo-host-integration/0.1`

## Purpose

This candidate defines the smallest executable message boundary needed for a conformant embedding host to execute TEO-selected provider/model work through host-native transport while TEO retains routing, retry, fallback, verifier selection, and acceptance authority.

It does not make the host a second router and does not make TEO the owner of the host's provider authentication or transport.

The architectural split is:

```text
host task admission
        |
        v
TEO DispatchRecord
        |
        v
TEO execution instruction
        |
        v
host-native provider transport
        |
        v
host execution receipt
        |
        +---- failed -> TEO decides retry or declared fallback
        |
        v
TEO verification instruction
        |
        v
host-native independent verifier transport
        |
        v
host verification receipt
        |
        v
TEO evidence/finalization layers
```

## Message types

The candidate has four messages, all bound to `teo-host-integration/0.1`:

1. `HostExecutionInstruction`
2. `HostExecutionReceipt`
3. `HostVerificationInstruction`
4. `HostVerificationReceipt`

The wire shape is defined by `reference/schemas/host-integration-protocol.schema.json`.

## Dispatch snapshot binding

A protocol session takes a defensive copy of the authoritative `DispatchRecord` at session creation and records a canonical digest of that snapshot. Every subsequent execution, receipt, verification, and evidence transition revalidates the snapshot before proceeding.

If provider/model selection, fallback, verification assignment, routed task, capabilities, risk, or any other dispatch field changes after session creation, the reference coordinator rejects the transition rather than silently inheriting the changed routing authority.

This is process-local drift detection. It is not a cryptographic production authority mechanism against an actor that can arbitrarily rewrite the coordinator's own memory.

## Execution instruction

An execution instruction is created from the bound authoritative `DispatchRecord` snapshot. It binds:

- dispatch and task identity;
- route role: `primary` or `fallback`;
- provider family;
- model;
- selected reasoning effort when declared;
- exact attempt number and session attempt ceiling;
- original routed task;
- required capabilities;
- SHA-256 of the canonical instruction payload.

The host may select its native transport for that provider, including a CLI or other authenticated local adapter, but it may not replace the provider, model, route role, attempt, or task and still claim conformance with that instruction.

No credential, token, account secret, or provider authentication material belongs in this protocol message.

## Execution receipt

A successful execution receipt must echo the bound execution identity and provide:

- exact instruction identity and digest;
- dispatch, route role, provider, model, and attempt;
- execution status;
- exact output reference;
- lowercase SHA-256 output identity;
- optional evidence references.

A failed receipt carries no successful output identity. A failed receipt that supplies an output reference or output digest as though execution succeeded is rejected as contradictory evidence.

The reference coordinator rejects unknown instructions, provider/model drift, route drift, attempt drift, duplicate receipts, contradictory failed receipts, and malformed successful output identity.

## Retry and fallback

The host does not decide retry or fallback.

For this candidate:

- the session retry ceiling must be a positive integer;
- only one execution instruction may remain unresolved at a time;
- attempt `n + 1` may be issued only after accepted attempt `n` for the same route failed;
- attempts cannot exceed the TEO-side session ceiling;
- fallback can be issued only after the latest accepted primary attempt failed;
- once any fallback instruction is issued, the primary route cannot reopen within that session;
- once any execution receipt succeeds, the execution phase is terminal;
- once verification begins, no further execution instruction may be issued;
- fallback identity comes only from `DispatchRecord.fallback_implementation`;
- a host cannot introduce an undeclared fallback provider/model through a receipt.

This candidate uses a process-local session ceiling. It does not replace canonical TEO retry policy. A production integration must derive and bind that ceiling to the applicable policy snapshot rather than accept an arbitrary caller value.

## Verification instruction

Verification begins only after a successful execution receipt exists.

The verification instruction binds:

- dispatch and task identity;
- active successful route role;
- observed executor provider/model from the accepted receipt;
- TEO-selected verifier provider/model;
- exact output reference and SHA-256;
- required verification methods;
- canonical instruction digest.

When the `DispatchRecord` requires independent verification, the reference coordinator rejects verifier reuse of the active executor model or provider family.

Executor chain-of-thought, hidden reasoning, conversation history, and self-assessment are not protocol inputs.

## Verification receipt

A verification receipt must echo the exact verification instruction identity, verifier provider/model, and artifact identity. The reference coordinator rejects stale or substituted artifact identity, verifier drift, unknown instructions, and duplicate verification receipts.

Accepted statuses are:

- `passed`
- `failed`
- `needs_human`

A receipt is evidence presented to TEO. It is not itself final acceptance authority.

## Evidence projection

After successful execution evidence and a verification receipt have both been accepted, the process-local reference session may expose a compact evidence projection containing:

- active primary/fallback role;
- observed executor provider/model;
- successful execution attempt;
- execution-instruction digest;
- output reference and digest;
- observed verifier provider/model;
- verification status;
- verification-instruction digest.

This projection is intended to feed TEO's canonical Route-Outcome Evidence and Final Execution Provenance layers. It does not replace either layer.

## Preserved ownership boundaries

This candidate preserves these boundaries:

- TEO owns task routing, specialist/capability selection, provider/model choice, fallback eligibility, retry authorization, verifier selection, orchestration verification, and final route evidence.
- The embedding host owns native provider authentication, CLI/API process invocation, environment-local execution mechanics, and local secret custody.
- Host authority may narrow execution further but cannot widen TEO authority.
- Protocol messages never carry credentials or raw secrets.

## Explicit limitations

This candidate is deliberately not a production Host Integration promotion.

It does not yet prove:

- transport authenticity against a network or hostile local actor;
- authenticated host/process/user/account/tenant identity;
- restart-persistent or distributed replay state;
- production retry-policy snapshot binding;
- OS/resource containment or prevention of host bypass outside the protocol;
- credential-scope binding;
- remote key custody, rotation, or revocation;
- effect authenticity merely because a receipt was submitted;
- production filesystem/network target canonicalization;
- distributed coordination;
- that every external host should use this transport shape.

Those gates remain governed by the Host Integration research roadmap. Promotion beyond reference-candidate status requires separate evidence and review.

## Acceptance criteria for this slice

The candidate is acceptable only if tests demonstrate at minimum:

- primary provider/model binding;
- provider and model drift rejection;
- instruction-tamper rejection;
- bound dispatch mutation rejection;
- successful output identity requirement;
- contradictory failed-receipt rejection;
- replay rejection;
- no host-invented fallback;
- TEO-controlled fallback after primary failure;
- sequential bounded retry with a positive-integer budget;
- one unresolved execution instruction at a time;
- monotonic primary-to-fallback progression without route reopening;
- terminal execution after success or verification start;
- independent verifier binding;
- stale verifier-artifact rejection;
- verification replay rejection;
- evidence projection reports the actual successful execution lane;
- protocol messages validate against the versioned JSON Schema.

No routing policy, live-execution scope, provider-access policy, specialist registry, or production authority is widened by this candidate.
