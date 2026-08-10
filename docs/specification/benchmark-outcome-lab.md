# Benchmark and Outcome Lab

## Status

This specification defines the first executable foundation for TEO's Benchmark and Outcome Lab.

Benchmark Lab version: `1`

This layer evaluates completed route-outcome evidence. It does not acquire routing, model-selection, verification, approval, retry, fallback, or policy-write authority.

## Purpose

The Benchmark and Outcome Lab turns fixed controlled fixtures and canonical route-outcome records into reproducible comparative evidence.

The first implementation focuses on four problems:

1. keep the task and evaluation setup fixed enough that route comparisons are interpretable;
2. preserve nondeterminism through repeated trials rather than treating one run as ground truth;
3. reject incomparable cohorts instead of forcing a score;
4. keep fallback, retry, verification failure, missingness, uncertainty, and version context visible.

## Evidence basis

The design is consistent with current primary-source evaluation guidance:

- Anthropic's agent-evaluation guidance distinguishes tasks, trials, graders, traces, capability evals, and regression evals, and recommends repeated trials for nondeterministic systems: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- OpenAI's evaluation guidance emphasizes that the harness, tools, scoring, budget, and environment are part of the tested system and should remain explicit in controlled comparisons: https://openai.com/index/trustworthy-third-party-evaluations-foundations/
- Google Vertex AI agent evaluation treats the evaluation dataset, agent configuration, metrics, and evaluation run as separate declared artifacts: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/evaluate

TEO does not depend on those frameworks. The sources inform evaluation controls only.

## Canonical artifacts

- evaluator: `reference/implementations/python/src/teo_reference/benchmark_lab.py`
- fixture schema: `reference/schemas/benchmark-fixture.schema.json`
- experiment schema: `reference/schemas/benchmark-experiment.schema.json`
- report schema: `reference/schemas/benchmark-report.schema.json`
- controlled fixtures: `reference/datasets/benchmark-lab/benchmark-fixtures-v1.jsonl`
- trial outcomes: `reference/datasets/benchmark-lab/route-outcomes-v1.jsonl`
- experiment manifest: `reference/datasets/benchmark-lab/benchmark-experiment-v1.json`
- conformance tests: `tests/test_benchmark_lab.py`

## Evaluation sequence

```text
controlled fixture bank
  -> declared experiment manifest
  -> candidate and harness identity
  -> fixed repeated trial bindings
  -> canonical route-outcome records
  -> comparability gate
  -> descriptive metrics and uncertainty
  -> integrity-protected benchmark report
  -> independent evaluation / specialist #82
  -> shadow recommendation later
```

The report is evidence. It cannot edit routing policy.

## Fixture contract

A benchmark fixture declares:

- fixture and suite identity;
- suite version;
- capability or regression intent;
- task type;
- effective risk;
- required capabilities;
- controlled synthetic or otherwise authorized benchmark input;
- explicit success criteria;
- tags;
- integrity hash.

Benchmark fixtures are distinct from production telemetry. Controlled fixture content may be retained when it is synthetic, public, or otherwise authorized for evaluation. Production route-outcome evidence remains content-minimized.

## Experiment manifest

Every experiment declares before evaluation:

- experiment identity;
- study type: `benchmark`, `replay`, or `regression`;
- claim scope: `system_to_system` or `executor_only`;
- benchmark suite and version;
- trials per fixture;
- primary metric;
- fixed stopping rule;
- harness identity and version;
- tool-access profile;
- attempt and wall-time budget where applicable;
- candidate system configurations;
- exact fixture/candidate/trial to route-outcome bindings;
- regression baseline when the study type is regression.

Version and harness identity are evidence, not incidental metadata.

## Repeated trials

Version 1 requires at least two trials per fixture for a declared experiment.

This does not create a universal statistical sufficiency threshold. It prevents the foundation from treating one stochastic run as a stable system property.

The report exposes both:

- `pass_any_trial_fixture_rate`: at least one verified completion among repeated trials;
- `pass_all_trials_fixture_rate`: every repeated trial verified complete.

These correspond to different reliability questions and must not be collapsed into one headline score.

## Comparability gate

The evaluator fails the comparison before computing candidate metrics when the experiment contains material identity drift.

It checks:

- every candidate sees the same fixture and trial matrix;
- no trial is silently missing or extra;
- one route-outcome record cannot be reused across multiple trials;
- route-outcome task type matches the fixture;
- effective risk matches the fixture;
- required capabilities match the fixture;
- primary provider, model, and reasoning effort match the declared candidate;
- assigned verifier matches the declared candidate;
- runtime version matches;
- routing-policy revision matches;
- registry revision matches;
- declared tool versions match.

For `executor_only` claims, all non-executor comparison fields must remain fixed across candidates, including verifier, runtime, routing policy, registry, and declared tool versions.

A failed comparability gate returns `evidence_sufficiency: insufficient` and no candidate scorecard.

## Primary, retry, and fallback separation

The Lab consumes the canonical route-outcome contract and preserves its semantics.

For each candidate it reports separately:

- verified completed trials;
- primary-route verified completions;
- fallback-assisted verified completions;
- retry-assisted verified completions;
- verification failures;
- awaiting-human outcomes;
- verification-missing outcomes;
- execution failures;
- abandoned outcomes.

A route rescued by fallback is therefore not represented as equivalent to a primary-route success.

## Uncertainty

Version 1 reports 95 percent Wilson intervals for verified completion rate and primary verified completion rate.

The interval is descriptive evidence. It is not a policy threshold and does not establish causal superiority.

No universal significance level, minimum sample size, or promotion threshold is encoded.

## Latency and usage

The evaluator reports total observed route duration across primary and fallback attempts.

Normalized token usage is reported only when present in canonical route outcomes. Usage completeness is classified as:

- `complete`;
- `partial`;
- `unknown`.

Missing token usage is not converted to zero.

Monetary cost is intentionally not calculated in this workstream. Source-backed cost attribution remains separately governed by the Progress Tracker.

## Regression signals

Regression experiments declare a baseline candidate.

Version 1 emits `descriptive_drop` when a candidate's controlled verified-completion rate or primary verified-completion rate is lower than the declared baseline.

A descriptive drop is an investigation signal, not automatic rollback or routing authority.

## Integrity and reproducibility

Benchmark fixtures and reports use SHA-256 over canonical JSON content.

Reports preserve:

- experiment manifest digest;
- fixture integrity digests;
- ordered source route-outcome IDs;
- experiment and suite identity;
- harness and candidate identity through the source manifest.

Persisted reports are schema and integrity validated when written and read.

## Authority boundary

The Benchmark Lab may produce controlled comparative evidence.

It may not:

- select a winner as routing policy;
- promote or demote a model;
- weaken capability eligibility;
- lower effective risk;
- alter fallback rules;
- weaken independent verification;
- remove provider-diversity requirements;
- satisfy qualified-human approval;
- calculate unsupported cost claims;
- hide failures or missing trials;
- use one candidate's favorable harness while representing the result as an executor-only comparison.

## Deliberately incomplete in version 1 foundation

This first implementation does not complete the entire Benchmark and Outcome Lab milestone.

Two material capabilities remain open:

1. **Live controlled replay runner.** The current evaluator consumes already-produced canonical route-outcome records. It does not yet execute benchmark fixtures through candidate routes under a controlled runtime harness.
2. **Multi-verifier disagreement measurement.** The current report preserves the canonical runtime verifier disposition but does not yet execute or join multiple independent benchmark verifier observations.

The report states both limitations explicitly.

## Relationship to specialist #82

`orchestration-evaluation-analyst` remains the post-run specialist that interprets controlled evidence, tests evidence sufficiency, and produces bounded recommendation states.

Benchmark Lab itself does not produce `SHADOW_CHANGE_CANDIDATE` or any other policy recommendation. That remains a later governed handoff.

## Relationship to the Progress Tracker

This foundation advances, but does not close, the current `NOW` Benchmark and Outcome Lab workstream.

The next gate after this foundation is validated is to add a controlled replay runner and multi-verifier observation contract while preserving the same fixture, comparability, provenance, and authority boundaries.
