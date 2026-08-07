# Provisional machine-panel verifier calibration

## Status

This specification defines a **provisional evidence tier** for verifier calibration when independent human reviewers are not available.

It does not replace the independent-human evidence tier in `verifier-calibration-empirical.yaml` and must not be represented as human-rated calibration.

The governing machine-readable policy is:

- `policy/verification/verifier-calibration-machine-panel.yaml`

The reference implementation is:

- `teo_reference.verifier_calibration_machine_panel`

## Why this tier exists

TEO should not stop collecting evidence solely because qualified independent human reviewers are temporarily unavailable. It also must not solve that operational constraint by calling AI agents "human reviewers" or by silently weakening the meaning of independent ground truth.

The machine-panel tier therefore permits a bounded alternate evidence path with a narrower claim surface.

It can measure:

- cross-provider machine agreement
- disagreement and unresolved cases
- repeatability across the evaluated verifier routes
- accuracy against the existing fixed reference-control corpus
- criterion-level error patterns
- provider-route differences
- latency and provider-reported token usage

It cannot establish:

- independent human ground truth
- human-aligned verifier quality
- authority to change routing
- authority to expand guarded live execution
- authority to remove the human-review tier

## Separation from the human evidence path

The provisional tier uses separate policy, label, observation, and report semantics.

Human-backed artifacts remain governed by:

- `verifier-calibration-empirical.yaml`
- `verifier-calibration-human-label.schema.json`
- `verifier-calibration-empirical-observation.schema.json`

Machine-panel artifacts use:

- `verifier-calibration-machine-panel.yaml`
- `verifier-calibration-machine-panel-label.schema.json`
- `verifier-calibration-provisional-observation.schema.json`

This separation is deliberate. A machine-panel observation must not become indistinguishable from an observation collected after independent human labels were finalized.

## Blinding model

Machine judges receive the same observable review material a human reviewer would need:

- task
- candidate output
- rubric checks
- status precedence

They do not receive:

- canonical case IDs
- case categories
- reference-control decisions
- deterministic expected results
- observations from the verifier routes being evaluated

The review packet uses random opaque `review_item_id` values. The alias-to-case mapping remains in a separate private local map and is used only after panel collection for analysis.

The software can enforce the packet boundary and persisted artifact shape. It cannot prove that a provider model has no latent knowledge of public repository content. This limitation is one reason the tier remains provisional.

## Panel routes

The initial panel uses three provider families and exact models that differ from the verifier routes being measured:

| Provider | Machine judge | Evaluated verifier |
|---|---|---|
| OpenAI | `gpt-5.6-terra` | `gpt-5.6-sol` |
| Anthropic | `claude-opus-5` | `claude-sonnet-5` |
| Google | `gemini-3.1-pro-preview` | `gemini-3.6-flash` |

The Google panel route is an explicitly acknowledged preview dependency. Preview status is visible in policy and does not transfer any routing authority.

Exact-model separation prevents the most direct form of self-judging. Provider-family overlap remains because the purpose of this tier is cross-provider machine consensus, not independent human ground truth.

## Consensus semantics

Each blinded item receives one judgment from each of the three panel routes.

If at least two routes produce the same complete structured decision, the item has a **provisional machine majority**.

If no decision has two votes, the item remains **unresolved**.

Unresolved cases are not force-adjudicated by pretending that another model is a human adjudicator. They remain visible in the report.

Panel coverage can still be complete when one or more cases have no majority. This permits the bounded live study to continue because the reference-control corpus, not machine majority, remains the objective comparison anchor for the provisional experiment.

## Reference-control anchor

The fixed public control corpus remains the test anchor for provisional metrics.

The final report therefore says:

- `metrics_against_reference_control`
- `metrics_by_verifier_route_against_reference_control`

It does not say `metrics_against_independent_machine_ground_truth`.

Machine-panel majority is reported separately, including:

- majority coverage
- exact agreement with the reference control where a majority exists
- disagreement cases
- no-majority cases

This naming is an evidence boundary, not cosmetic wording.

## Collection sequence

The provisional study has two live stages.

### Stage 1: blinded machine panel

For eight fixed cases and three panel routes:

`8 cases x 3 machine judges = 24 live calls`

Each persisted machine-panel label includes:

- opaque review item ID
- judge provider family
- exact judge model
- reasoning level
- timestamp
- rubric version
- duration
- provider-reported input and output tokens
- structured decision
- explicit provisional evidence tier
- explicit blinding attestations

It does not persist task or candidate content, canonical case ID, provider-native payload, credentials, request identifiers, or connection mechanism.

### Stage 2: provisional verifier observations

After full three-route panel coverage exists:

`8 cases x 3 evaluated verifier routes x 3 runs = 72 live calls`

These observations are stored under a separate provisional schema and path from the human-backed empirical observations.

The combined planned live workload is therefore:

`24 + 72 = 96 calls`

A live command requires explicit `--execute-live` acknowledgement.

## Authority boundary

Even a complete provisional study with perfect reference-control scores has the following authority state:

- human ground-truth claim: false
- empirical verifier-quality claim: false
- live-scope expansion: false
- routing authority: false
- automatic route update: false
- human-review tier replaced: false

A future route change still requires an explicit human acceptance decision and an independent residual-risk review. The provisional tier provides evidence for that future decision; it does not make the decision itself.

## Example commands

Show the plan without provider calls:

```bash
python -m teo_reference.verifier_calibration_machine_panel \
  --repo-root . \
  plan
```

Collect the 24 blinded machine-panel judgments:

```bash
python -m teo_reference.verifier_calibration_machine_panel \
  --repo-root . \
  collect-panel \
  --execute-live
```

Collect the 72 provisional verifier observations after panel coverage:

```bash
python -m teo_reference.verifier_calibration_machine_panel \
  --repo-root . \
  collect-observations \
  --packet .teo/runtime/verifier-calibration/machine-panel-packet.json \
  --panel-labels .teo/runtime/verifier-calibration/machine-panel-labels.jsonl \
  --execute-live
```

Evaluate the provisional evidence:

```bash
python -m teo_reference.verifier_calibration_machine_panel \
  --repo-root . \
  evaluate \
  --packet .teo/runtime/verifier-calibration/machine-panel-packet.json \
  --mapping .teo/runtime/verifier-calibration/machine-panel-map.json \
  --panel-labels .teo/runtime/verifier-calibration/machine-panel-labels.jsonl \
  --observations .teo/runtime/verifier-calibration/provisional-observations.jsonl
```

Environment-backed provider connections use the same connection-neutral boundary as the existing empirical collector. Access mechanism remains outside model and route identity.