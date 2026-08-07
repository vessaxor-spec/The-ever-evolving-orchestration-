# Blinded Human Calibration Review

## Purpose

Independent human labels are the empirical comparison target for the first TEO verifier calibration study.

Reviewers must not derive those labels from TEO's existing reference-control decisions or from the live verifier observations they are intended to evaluate.

The human-review workflow therefore creates a blinded packet before live collection.

## Reviewer packet

The packet contains only:

- an opaque packet ID
- rubric version
- the four verifier checks and their descriptions
- status precedence
- opaque review-item IDs
- original task text
- candidate output text

It does not contain:

- canonical case IDs
- case categories
- reference-control decisions
- deterministic expected results
- live verifier observations
- provider/model identity

Several canonical case IDs contain semantic hints about their expected result. The packet therefore replaces them with random review-item aliases rather than merely hiding the `gold` field.

## Private alias map

Packet generation also writes a private local mapping from review-item alias to canonical case ID.

The alias map is not distributed to reviewers. It exists only so blinded reviewer responses can be normalized back to the canonical case IDs required by the empirical evaluator.

Both packet and map live under `.teo/` by default and remain repository-ignored.

## Reviewer response

A blinded reviewer response identifies only the opaque review-item alias and records:

- opaque reviewer ID
- reviewer or adjudicator role
- review timestamp
- rubric version
- attestation that model observations were blinded
- attestation that reference-control labels were blinded
- structured verifier decision

The raw blinded-review schema is:

- `reference/schemas/verifier-calibration-human-review-label.schema.json`

The reviewer packet schema is:

- `reference/schemas/verifier-calibration-human-review-packet.schema.json`

The private alias-map schema is:

- `reference/schemas/verifier-calibration-human-review-map.schema.json`

## Normalization

After reviewer responses are complete, the operator combines the private alias map with the blinded labels.

Normalization replaces `review_item_id` with canonical `case_id` and writes the content-free canonical human-label JSONL accepted by the empirical collector.

The normalization output does not include the reviewer packet content, reference labels, or alias map.

## Operator workflow

Create a packet and private alias map:

```text
python -m teo_reference.verifier_calibration_human_review --repo-root . packet
```

Distribute only the generated review packet to reviewers. Do not distribute the private map or the public reference-control corpus as review material.

Normalize completed blinded reviewer files:

```text
python -m teo_reference.verifier_calibration_human_review --repo-root . normalize \
  --mapping .teo/runtime/verifier-calibration/human-review-map.json \
  --raw-labels reviewer-a.jsonl \
  --raw-labels reviewer-b.jsonl \
  --output .teo/runtime/verifier-calibration/human-labels.jsonl
```

If reviewers disagree on a case, collect a blinded adjudicator response using the same packet and include that raw label during normalization.

The empirical label-readiness gate then validates reviewer count, disagreement/adjudication, rubric version, timestamp, and canonical deterministic consistency before any live provider call can begin.

## Independence boundary

Technical blinding cannot prove a human reviewer did not independently inspect the public repository. The protocol therefore combines:

- reviewer materials that do not expose reference outcomes
- explicit blinding attestations
- opaque review aliases
- separation of the private mapping
- label completion before model observations
- independent adjudication on disagreement

This creates an auditable evidence process without pretending software can prove a reviewer's external knowledge state.
