# Route-Outcome Evidence Contract

## Status

This specification defines the canonical post-run route-outcome evidence contract for the TEO reference implementation.

Contract version: `1`

The contract is evaluation evidence. It is not routing authority, verification authority, retry authority, fallback authority, provider-health authority, or permission to modify live policy.

## Purpose

TEO already records content-free evidence for every provider attempt. That telemetry is necessary but insufficient for route evaluation because it does not by itself identify the complete governed route, whether a fallback rescued the task, which independent verifier accepted the active execution, or which runtime and policy versions produced the result.

Route-outcome evidence joins those existing records into one integrity-protected, version-scoped post-run record that can be consumed by `orchestration-evaluation-analyst` and future Benchmark and Outcome Lab tooling.

The contract preserves this separation:

```text
Dispatch authority
  -> provider-attempt telemetry
  -> independent verification
  -> route-outcome join
  -> post-run evaluation
  -> shadow recommendation
  -> governed review
```

The route-outcome layer observes completed or abandoned execution history. It cannot select or rewrite a route.

## Canonical artifacts

- Python contract: `reference/implementations/python/src/teo_reference/route_outcome.py`
- JSON Schema: `reference/schemas/route-outcome-record.schema.json`
- Reproducible fixtures: `reference/datasets/route-outcomes/route-outcomes-v1.jsonl`
- Conformance tests: `tests/test_route_outcome_evidence.py`

## Evidence model

One route-outcome record contains:

- task classification and effective risk;
- primary dispatch identity;
- Team, Worker, optional Specialist, and required capabilities;
- selected provider, model, and reasoning effort;
- assigned independent verifier;
- every normalized provider attempt belonging to the route;
- retry usage without collapsing attempts;
- optional fallback redispatch and its separate attempts;
- the active route, when execution succeeded;
- verification disposition and verification provenance;
- whether the accepted result was fallback-assisted;
- whether the final result depended on retry;
- runtime, repository, policy, registry, and declared tool-version context;
- explicit unknown cost state;
- dispatch and telemetry provenance;
- abandonment reason when execution did not reach a terminal runtime result;
- a SHA-256 integrity digest over the canonical record content.

## Primary and fallback separation

Fallback is a new canonical dispatch in TEO. Route-outcome evidence therefore never rewrites fallback as another attempt of the original route.

A fallback-assisted success records both:

```text
primary_route.execution_status = failed
fallback_route.execution_status = succeeded
active_route_role = fallback
fallback_assisted = true
```

This prevents later analysis from treating a route that succeeds only after rescue as equivalent to a route that succeeds on its primary execution.

## Retry separation

Retries remain attempts inside one dispatch.

The record preserves each attempt and exposes:

- `attempt_count` per route;
- `retry_used` per route;
- `retry_assisted` for the complete outcome.

Attempt-level latency, normalized usage, failure scope, failure code, and retry timing remain visible.

## Verification states

The contract preserves uncertainty rather than inventing acceptance.

Supported terminal dispositions are:

- `completed`: successful active execution with passed independent verification and no outstanding qualified-human gate;
- `verification_failed`: successful execution that failed its assigned independent verifier;
- `awaiting_human`: model verification cannot close the required qualified-human authority boundary;
- `verification_missing`: execution succeeded but independent verification evidence is not yet present;
- `execution_failed`: no primary or fallback execution produced an active successful route;
- `abandoned`: execution history ended without a normal terminal runtime outcome and the abandonment reason is recorded.

A missing verifier is not treated as a pass. An abandoned run is not silently dropped.

## Content-minimization boundary

Route-outcome evidence inherits the content-minimization posture of runtime telemetry.

The record does not contain:

- task text;
- task ID or user identifier;
- prompts or conversation messages;
- provider request bodies;
- model output;
- output artifact references;
- provider-native request or response identifiers;
- credentials, authorization headers, or connection secrets.

The join uses dispatch IDs and content-free route metadata rather than user identity.

## Version context

Historical route evidence is not assumed to remain portable after implementation or policy drift.

Version context includes:

- `runtime_version`;
- `repository_revision`;
- optional `routing_policy_revision`;
- optional `registry_revision`;
- declared tool or adapter versions when decision-relevant.

Unknown version fields remain null rather than being guessed.

Concrete executor and verifier model identifiers remain part of the route itself.

## Cost boundary

Route-outcome version 1 does not calculate monetary cost.

The record explicitly contains:

```text
cost.status = unknown
cost.amount = null
cost.currency = null
cost.source = null
```

This prevents missing pricing evidence from being interpreted as zero cost.

Source-backed cost attribution is a separate `NEXT` workstream because pricing evidence changes independently from runtime usage telemetry.

## Provenance

The record declares:

- ordered source dispatch IDs;
- verification dispatch ID when verification exists;
- number of joined provider-attempt telemetry events.

The Python contract fails closed when telemetry belongs to another dispatch, changes the selected provider or model, changes the assigned verifier, uses the wrong primary/fallback role, or has non-contiguous attempt numbering.

## Integrity

`integrity_sha256` is calculated over canonical JSON containing all record fields except the integrity field itself.

Parsing a persisted record validates:

1. JSON Schema shape;
2. route and lineage semantics;
3. terminal-disposition consistency;
4. integrity digest.

A structurally valid but modified record therefore fails closed unless its integrity field is recomputed. Independent evidence stores may add stronger signing or append-only guarantees later without changing the version 1 semantic contract.

## Persistence

`JsonlRouteOutcomeSink` provides a single-process append-only reference persistence mechanism.

It validates schema, semantics, and integrity before writing and validates them again when reading.

This is not distributed storage. Concurrency, access control, retention, signing, export, and distributed integrity remain part of the tracker-defined `LATER` distributed-runtime hardening workstream.

## Evaluation boundary

The route-outcome record is designed for specialist #82, `orchestration-evaluation-analyst`, and controlled evaluation tooling.

It may support analysis of:

- primary-route acceptance;
- fallback dependence;
- retry dependence;
- verifier disagreement;
- failure distributions;
- latency;
- normalized usage;
- version drift;
- later source-backed cost joins.

It does not authorize:

- automatic model promotion or demotion;
- direct policy edits;
- self-modifying routing;
- lowering risk or verification requirements;
- bypassing qualified-human approval.

Any future adaptive path remains evidence -> evaluation -> shadow recommendation -> independent challenge -> maintainer decision -> reviewed policy change -> CI.

## Conformance

The conformance suite proves that:

- primary success is represented independently from fallback-assisted success;
- retries remain separate attempts;
- provider/model/verifier lineage cannot drift during the join;
- successful but unverified execution remains `verification_missing`;
- failed execution remains `execution_failed`;
- abandoned execution is retained with a reason;
- user/task content and output references are absent;
- missing cost remains explicitly unknown;
- unknown schema fields fail closed;
- integrity mutation fails closed;
- JSONL persistence revalidates records;
- reproducible fixtures cover primary success, fallback-assisted success, and abandonment.

## Relationship to the Progress Tracker

This contract implements the current `NOW` Route-Outcome Evidence milestone defined in `docs/stewardship/progress-tracker.md`.

Benchmark comparison, source-backed pricing, and shadow route evaluation remain separate `NEXT` workstreams. Distributed storage and generalized durable execution remain `LATER` work.
