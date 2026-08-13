# Final Execution Provenance Projection

**Status:** Candidate compatible extension under verification  
**Date:** 2026-08-13  
**Owner:** TEO orchestration evidence boundary

## Purpose

TEO already has authoritative routing intent in `DispatchRecord` and canonical observed execution evidence in Route-Outcome Evidence. Host and consumer integrations sometimes need a compact answer to a narrower question:

> Which provider/model route actually completed the execution represented by this final result?

A dispatch-selected provider is not sufficient evidence for that claim because primary execution can fail, fallback can become active, retries can occur, and runtime telemetry can contradict an intended route.

The optional `FinalOutcome.execution_provenance` projection exposes the successful active route only after the canonical Route-Outcome Evidence record has been revalidated.

## Authority Boundary

The projection is read-only evidence.

It does not:

- select a provider, model, reasoning effort, worker, specialist, fallback, or verifier;
- widen task, capability, host, tool, or live-execution authority;
- authorize a host action;
- convert provider access into routing fitness;
- replace `DispatchRecord` as routing authority;
- replace the complete Route-Outcome Evidence record as canonical route evidence.

A host may consume the projection to understand what TEO observed. A host must not use the projection to override a future TEO routing decision.

## Source of Truth

The only accepted source is a canonical `RouteOutcomeRecord` that passes:

1. strict JSON Schema validation;
2. route semantic validation;
3. dispatch/attempt/provider/model consistency checks already enforced by Route-Outcome Evidence;
4. active-route success checks;
5. verification provenance checks;
6. integrity SHA-256 recomputation.

The source digest is a content-integrity identifier, not a cryptographic signature or identity-authentication mechanism.

## Projection Contract

When present, `execution_provenance` contains:

- `source = route_outcome`;
- source route-outcome ID;
- source route-outcome integrity SHA-256;
- successful active dispatch ID;
- active route role (`primary` or `fallback`);
- observed active provider family;
- observed active model;
- assigned reasoning effort, when present;
- verification dispatch ID;
- route final disposition;
- whether fallback assisted the accepted route;
- whether retry assisted the route.

The projection deliberately omits task content, provider output, evidence payloads, prompts, model reasoning, credentials, and other content that is unnecessary to identify the active execution lane.

## Host-Facing Finalization Path

Existing finalization remains unchanged:

```text
teo finalize <dispatch> <execution> <verification>
```

When a host also possesses the canonical Route-Outcome Evidence record for the final active dispatch, it may request the compatible projection through:

```text
teo finalize <dispatch> <execution> <verification> --route-outcome <route-outcome-record>
```

The `--route-outcome` input is optional. TEO revalidates it before attachment and then validates the emitted `FinalOutcome` against the strict final-outcome schema.

The option does not allow a host to nominate or override provider identity. If the supplied route record does not agree with the final dispatch/execution/verification result, finalization fails closed.

## Binding Rules

Before projection, TEO must prove all of the following:

1. the Route-Outcome record is valid and integrity-consistent;
2. the Route-Outcome record has a successful active route;
3. active route dispatch ID equals the `FinalOutcome.dispatch_id`;
4. the `FinalOutcome.execution_status` is `succeeded`;
5. active route model equals `FinalOutcome.selected_model`;
6. active route verifier model equals `FinalOutcome.verifier_model`;
7. verification provenance belongs to the active dispatch;
8. Route-Outcome verification status equals `FinalOutcome.verification_status`;
9. Route-Outcome final disposition maps consistently to `FinalOutcome.status`.

Supported disposition mappings are:

| Route-Outcome disposition | FinalOutcome status |
|---|---|
| `completed` | `completed` |
| `verification_failed` | `failed` |
| `awaiting_human` | `awaiting_human` |

`execution_failed`, `abandoned`, and `verification_missing` do not produce verified final execution provenance because the current `FinalOutcome` contract cannot represent them as a successful, verification-bound active route.

## Fallback Semantics

When primary execution fails and a fallback route succeeds, the projection must identify the **fallback provider/model**.

The failed primary provider must not be reported as the active execution lane merely because it was the original dispatch selection.

This is the primary reason the projection is derived from Route-Outcome Evidence rather than directly from `DispatchRecord`.

## Verifier Semantics

The verifier is not an execution lane.

A verifier provider/model may be independently visible through other TEO evidence, but it must not satisfy a claim that two distinct execution providers were usable. The projection's `provider_family` and `model` identify only the successful active execution route.

## Compatibility

`execution_provenance` is optional.

When it is absent, `FinalOutcome.to_dict()` preserves the pre-extension serialized shape. Existing clients therefore do not receive a new `null` field merely because the implementation understands the extension.

Consumers must treat absence as **unproven**, never infer provider identity from model names, result text, provider self-report, or stale dispatch intent.

## Mutation and Falsification Expectations

Load-bearing tests must fail if any of these protections are weakened:

- tampered Route-Outcome content is accepted without matching integrity;
- a failed primary is reported as active after fallback success;
- active dispatch ID mismatch is accepted;
- active model mismatch is accepted;
- verifier-model mismatch is accepted;
- verification status/disposition mismatch is accepted;
- an unverified or failed route is projected as verified execution provenance;
- different route evidence can silently replace already attached provenance;
- legacy FinalOutcome serialization is widened when no provenance is attached;
- the host-facing finalize path accepts mismatched Route-Outcome Evidence.

## Invariant

> **Routing intent says what TEO chose; Route-Outcome Evidence says what TEO observed; final execution provenance may report only the validated successful active route.**
