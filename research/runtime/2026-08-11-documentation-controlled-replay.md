# Documentation Controlled Replay

## Status

Validated staged replay harness and auditable provider-execution path. Empirical provider-backed replay evidence remains pending on operator provider access.

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

A legitimate API-key, OAuth/subscription-backed, delegated, connector, local runtime, or other provider-supported connection may be used when it implements the same authorized provider-neutral connection contract. Changing the connection method must not change the selected model, reasoning effort, fallback, verifier, risk, capability, or authority decision.

## Evidence separation

CI uses deterministic fake provider transports to prove contracts and control behavior. Those calls are not empirical provider-backed replay observations.

This follows TEO's existing empirical verifier-calibration precedent: operator-run live collection is separate from CI, and green CI does not itself become empirical provider evidence.

Therefore this gate distinguishes:

- **implemented and CI-validated replay harness:** complete;
- **auditable provider-execution workflow:** complete;
- **provider-backed empirical documentation replay evidence:** pending;
- **active-scope authorization:** false.

No `controlled_replay` evidence pointer should be populated in `policy/runtime/live-execution-expansion.yaml` until a real operator execution produces the exact integrity-protected replay record and Route-Outcome Evidence set.

## Corrective CI findings

The replay implementation benefited from three legitimate CI findings before the harness became green.

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

After the operator CLI, CLI boundary tests, research record, and removal of the non-auditable one-time workflow were included, clean-head Reference Implementation CI #488 validated the durable replay-harness branch state:

- 651 tests passed;
- 472 tracked files passed repository-layout validation;
- regulated specialist evidence passed structural validation;
- 40 JSON Schemas parsed;
- linked TEO configuration reported zero issues;
- the provider-diverse end-to-end reference lifecycle passed.

The auditable GitHub-hosted execution path was then added and hardened through PRs #122, #123, #125, and #127. The final Actions-native audit design removed dependency on GitHub issue or pull-request write permission and uses only `contents: read`. It records the exact trusted base revision and run identity in the Actions log and step summary and always uploads a content-minimized audit artifact.

Reference Implementation CI #503 validated that final workflow design:

- 653 tests passed;
- 474 tracked files passed repository-layout validation;
- regulated specialist evidence passed structural validation;
- 40 JSON Schemas parsed;
- linked TEO configuration reported zero issues;
- the provider-diverse end-to-end reference lifecycle passed.

CI proves the replay contracts, preflight, retry semantics, evidence construction, operator acknowledgement boundary, trusted-base execution, audit path, and active-scope refusal behavior. It does not prove a provider-backed documentation replay was executed.

## Provider-backed execution attempts

### Runs #5 and #8: audit sink failures, no provider calls

The first two reserved trigger attempts reached the trusted-base workflow but failed at the external pull-request audit-comment sink.

- run #5 used the GitHub CLI issue-comment path and was refused by the workflow token;
- run #8 used the REST issue-comment endpoint and was also refused by the repository's effective workflow-token permissions;
- both attempts stopped before replay environment installation or live provider execution;
- neither attempt is empirical replay evidence.

The correction was to remove GitHub commenting as an execution dependency, not to broaden workflow permissions. The final workflow uses Actions-native logs, step summaries, and artifacts and requires only repository-content read permission.

### Run #11: provider-access blocker

The first attempt that reached the actual provider-access gate was Controlled Documentation Replay Evidence run:

`31462300962`

It executed from trusted repository revision:

`e93e25110e9b8256a119b6d472128a74b3ef857e`

The Actions-native start record confirmed:

- trigger: same-repository pull request #128;
- task type: `documentation`;
- candidate state: `staged`;
- `activation_authorized: false`;
- evidence status: pending provider-backed execution.

The exact replay plan validated before provider access with:

- `provider_calls: 0`;
- replay ID `documentation-provider-backed-replay-v1-31462300962`;
- plan SHA-256 `6b895c3d3823eb2572e09b9b0b9e2845f77a64293a2d45e2b7a1681b2886f6ef`.

The live step then failed before calling either provider because the GitHub-hosted runner had no usable values for the required convenience connection variables. The first explicit refusal was:

`Missing required repository secret: ANTHROPIC_API_KEY`

The run environment also showed the OpenAI convenience variable unset. The replay CLI therefore did not make a provider request.

The run emitted no canonical provider-backed replay artifact and no Route-Outcome Evidence set. It did upload the audit artifact:

- name: `teo-documentation-replay-audit-31462300962`;
- artifact ID: `9090226379`;
- artifact SHA-256: `30dc43b49836a0092ef75af0b88c5a660e11867dd68c06a9f0a86030d5c2dc08`;
- retention expiry: 2026-09-10.

Independent inspection of that artifact confirmed:

- trusted base revision exactly matched the workflow checkout;
- replay plan and audit start identity matched run #11;
- provider-backed evidence accepted was `false`;
- the result explicitly states that no empirical success is claimed.

### Diagnosis

Run #11 is an **operator provider-access blocker**, not a routing, risk, verifier, replay-contract, or activation failure.

The exact route remains:

- primary: Anthropic Claude Sonnet 5 at medium effort;
- verifier: OpenAI GPT-5.6 Terra at medium effort.

TEO must not change this route merely because the GitHub-hosted convenience bridge lacks credentials. Provider access remains downstream of routing. The next empirical attempt may use the existing API-key convenience variables or another legitimate provider-supported `ProviderConnection`, including an OAuth/subscription-backed or delegated connection, provided that the exact selected route and all evidence and authority invariants remain unchanged.

No connected service available during this run could supply the missing Anthropic execution path, so no substitute provider was used.

## Remaining evidence gate

The next replay step remains a real provider-backed operator execution using the exact staged plan and a current repository revision after legitimate provider access is available.

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

The live-execution-expansion milestone therefore remains at 65%. `documentation` remains `activation_authorized: false`, the active guarded scope remains `high_volume_simple` at low or medium effective risk, and high or critical live execution remains unauthorized.

Rollback/recovery evidence, governed Shadow Route Evaluation, and independent review of any eventual active-scope change remain later gates.
