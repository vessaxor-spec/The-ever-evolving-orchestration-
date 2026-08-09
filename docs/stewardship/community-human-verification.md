# Community Human Verification Stewardship

TEO keeps independent human verification as a stronger evidence tier without making it a blocker for the functional v1 reference release.

## Purpose

The community stewardship path exists to complete blinded human calibration after v1 and to provide an accountable human evidence layer before any claim of human-ground-truth verifier quality, policy-governed live-scope expansion, or route change that requires explicit human acceptance.

## What v1 may claim before this work is complete

TEO may claim that its architecture, reference control plane, guarded live provider paths, fallback, verification, telemetry, calibration machinery, provisional machine-panel study, and CI controls are implemented and operational.

TEO must not claim that verifier quality has been independently validated by humans until this stewardship process is complete.

## Required human evidence

The current strong calibration path requires:

1. One blinded packet generated from the fixed calibration corpus.
2. At least two independent human reviewers for every case.
3. A distinct blinded adjudicator for each disagreement.
4. Reviewers blinded from reference-control labels and model observations.
5. Opaque reviewer identifiers rather than names or email addresses in calibration records.
6. Normalized labels that preserve packet provenance and both blinding attestations.
7. Live empirical verifier observations collected only after the human label set is complete.
8. Independent residual-risk review and explicit human acceptance before any authority expansion governed by the calibration policy.

## GitHub community workflow

Issue #75 is the canonical stewardship tracker.

Community maintainers may volunteer reviewers through the issue while keeping the actual blinded review packet separate from the private alias map. Reviewer decisions should be submitted as JSONL artifacts or through a controlled maintainer handoff rather than exposing the alias map publicly.

The private alias map must never be given to reviewers before their decisions are final. Gold labels, case categories, deterministic expected results, and verifier observations must also remain hidden during review.

## Authority boundary

Machine-panel evidence is not a substitute for this tier. It can support provisional operational evidence and help exercise the full calibration machinery, but it cannot be described as human review, cannot establish human ground truth, and cannot independently authorize route changes or broader live execution.

Critical effective-risk decisions continue to require qualified human approval wherever TEO policy already requires it. Deferring this calibration study does not weaken that runtime authority boundary.

## Completion condition

The stewardship tier is complete only when the repository records:

- complete blinded human labels,
- any required adjudications,
- the corresponding live empirical study,
- evaluated calibration metrics,
- an independent residual-risk review, and
- an explicit human acceptance or rejection record.
