# Documentation Controlled Replay

## Status

Validated staged replay harness. Empirical provider-backed replay evidence remains pending.

This record documents the controlled replay gate for the staged `documentation` live-scope candidate. It does not activate `documentation`, change the active guarded runtime, widen live verification, or authorize high or critical live execution.

## Mission Control lenses

- Mission Control orchestration
- Research / `orchestration-evaluation-analyst`
- Engineering
- Assurance
- Review
- Verification

No new specialist was required. The existing `orchestration-evaluation-analyst` remains the correct evidence-analysis owner and has no live-routing or policy-write authority.

## Starting repository truth

The gate began from merged `main` at:

`47785d43fa119633f3ec436a48b61f53d76859fd`

At that point:

- `documentation` was staged and `activation_authorized: false`;
- active guarded execution remained `high_volume_simple` at low or medium effective risk;
- high and critical live execution remained unauthorized;
- canonical documentation routing selected Claude Sonnet 5 with GPT-5.6 Sol routine fallback;
- GPT-5.6 Terra was the assigned primary verifier;
- Gemini 3.6 Flash was the fresh verifier after Sonnet or Anthropic failure redispatch;
- the required Sonnet 5, Sol, and Terra adapter capabilities were implemented;
- controlled documentation replay evidence did not yet exist.

## Design decision

The existing Benchmark and Outcome Lab live replay runner was not reused directly because that runner deliberately invokes the active guarded canary and live-verification wrappers. Those wrappers correctly refuse `documentation` while the candidate remains staged.

The controlled documentation replay therefore uses a separate evaluation-only lane with these properties:

1. the candidate must remain `staged` and `activation_authorized: false`;
2. active scope must remain exactly `high_volume_simple` at low or medium effective risk;
3. all pre-replay routing, fallback, verifier, adapter, and high-risk refusal gates must pass before any provider call;
4. the complete replay plan is routed without network access before execution starts;
5. each trial uses isolated in-memory circuit state;
6. the active retry policy is reused exactly;
7. execution uses the normal canonical documentation primary route rather than a forced-model bypass;
8. verification must use the exact dispatch-assigned provider-diverse verifier;
9. provider-attempt telemetry is held only in memory for Route-Outcome Evidence construction and is not active runtime telemetry;
10. every trial emits canonical Route-Outcome Evidence;
11. the replay emits a strict integrity-protected record that explicitly states that live scope was not widened.

## Deliberate fallback boundary

Automatic fallback is disabled in this replay milestone.

A primary model or provider failure is recorded as `execution_failed`. The harness does not silently turn staged replay into a second live runtime by performing unrestricted redispatch.

Deliberate fallback, rollback, and recovery execution remains a separate later gate because the Progress Tracker already treats recovery evidence as distinct from controlled replay evidence.

Transient failures that the active retry policy classifies as retryable may retry under the same dispatch. Provider-scoped failures are not reclassified as transient merely to make the replay succeed.

## Replay contracts

The implementation adds:

- `reference/schemas/live-scope-replay-plan.schema.json`
- `reference/schemas/live-scope-replay-record.schema.json`
- `reference/implementations/python/src/teo_reference/live_scope_replay.py`
- `reference/implementations/python/src/teo_reference/live_scope_replay_cli.py`

The public library surface provides:

- `LiveScopeReplayPlan`
- `LiveScopeReplayRecord`
- `LiveScopeReplayExecution`
- `run_staged_documentation_replay`

The operator CLI provides:

```text
python -m teo_reference.live_scope_replay_cli --repo-root . validate --plan <plan.json>
```

and, only with explicit acknowledgement:

```text
python -m teo_reference.live_scope_replay_cli --repo-root . run \
  --plan <plan.json> \
  --output-dir .teo/runtime/live-scope-replay/documentation \
  --execute-live
```

The convenience environment bridge recognizes `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` because the staged primary route and assigned verifier use those providers. This bridge is only an operator convenience. The replay library accepts provider-neutral `ProviderConnection` objects, and connection method is not part of routing identity.

## Evidence separation

CI uses deterministic fake provider transports to prove contracts and control behavior. Those calls are not empirical provider-backed replay observations.

This follows TEO's existing empirical verifier-calibration precedent: operator-run live collection is separate from CI, and green CI does not itself become empirical provider evidence.

Therefore this gate distinguishes:

- **implemented and CI-validated replay harness:** complete;
- **provider-backed empirical documentation replay evidence:** pending;
- **active-scope authorization:** false.

No `controlled_replay` evidence pointer should be populated in `policy/runtime/live-execution-expansion.yaml` until a real operator execution produces the exact integrity-protected replay record and Route-Outcome Evidence set.

## Corrective CI findings

The implementation benefited from three legitimate CI findings before the harness became green.

### CI #479: task capability floor

The first replay fixtures incorrectly declared documentation worker-added capabilities as caller-required task capabilities. In particular, `clear_writing` was not a valid externally requestable Research capability.

Correction:

- replay fixtures now declare only an externally valid task-level capability floor, `transformation`;
- canonical worker-added capabilities remain part of normal dispatch context and Route-Outcome Evidence;
- an invalid-plan test requests Engineering-only `coding` and proves the entire plan fails before provider calls.

This preserves the distinction between task requirements and worker-resolved dispatch context.

### CI #480: effective-risk truth

The original low-risk fixture text triggered TEO's content-derived medium-risk floor. The replay preflight correctly rejected the mismatch.

Correction:

- the low fixture was simplified to neutral bounded transformation content;
- the exact declared/effective risk equality check was retained.

Risk checks were not weakened to make the fixture pass.

### CI #481: provider-scoped failure is not transient retry

The retry test originally used Anthropic `overloaded_error`. TEO correctly classifies that failure as provider-scoped, so it must not retry under the same dispatch.

Correction:

- the retry test now uses a true transient `api_error`;
- provider-scoped failure remains reserved for later fallback/recovery evaluation.

Failure semantics were not changed to make the test pass.

## Validated implementation evidence

Reference Implementation CI #482 validated the replay harness after the three corrections:

- 648 tests passed;
- 469 tracked files passed repository-layout validation;
- regulated specialist evidence passed structural validation;
- 40 JSON Schemas parsed;
- linked TEO configuration reported zero issues;
- the provider-diverse end-to-end reference lifecycle passed.

A later final-head CI must validate the operator CLI and stewardship reconciliation before merge.

## Remaining evidence gate

The next replay step is a real provider-backed operator execution using the exact staged plan and current repository revision.

That execution must produce:

- an integrity-protected replay plan;
- an integrity-protected staged replay record;
- canonical Route-Outcome Evidence for every trial;
- exact Sonnet 5 primary execution and Terra verification identity;
- low and medium fixture coverage;
- active-scope non-expansion evidence;
- no high or critical execution;
- no hidden automatic fallback;
- explicit limitations and provenance.

Only after that provider-backed evidence exists may `controlled_replay` be marked present for the staged candidate.

Rollback/recovery evidence, governed Shadow Route Evaluation, and independent review of any eventual active-scope change remain later gates.
