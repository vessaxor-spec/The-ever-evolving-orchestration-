# Optional Independent Human Calibration Study

Independent human calibration is an optional evidence-enhancement mechanism for TEO. It is not an approval authority, release gate, routing gate, live-scope gate, or prerequisite for architectural evolution.

## Purpose

The optional study exists to provide additional external evidence about verifier behavior when maintainers or contributors decide that an independently human-labeled comparison would be useful.

TEO engineering authority remains governed by reproducible evidence, policy constraints, automated and adversarial testing, CI, public technical review, and maintainer governance.

Qualified human approval remains mandatory wherever the underlying task or risk domain already requires it. This requirement is separate from the optional calibration study and is not weakened by declining or deferring the study.

## What TEO may claim without this study

TEO may claim that its architecture, reference control plane, guarded live provider paths, fallback, verification, telemetry, calibration machinery, provisional machine-panel study, and CI controls are implemented and operational when supported by the repository evidence.

TEO must not describe verifier results as independently human-validated unless an appropriate human calibration study has actually been completed.

That claim boundary does not prevent releases, routing changes, model updates, live-scope decisions, or other architectural evolution when those changes satisfy the repository's normal engineering and governance requirements.

## Optional study design

If maintainers choose to run the stronger calibration study, the current reference design is:

1. Generate one blinded packet from the fixed calibration corpus.
2. Obtain at least two independent human reviewer decisions for every case.
3. Use a distinct blinded adjudicator for any reviewer disagreement.
4. Keep reviewers blinded from reference-control labels and model observations.
5. Use opaque reviewer identifiers rather than names or email addresses in calibration records.
6. Normalize labels while preserving packet provenance and blinding attestations.
7. Collect live empirical verifier observations only after the human label set is complete.
8. Evaluate accuracy, false-pass and false-fail behavior, escalation behavior, criterion accuracy, repeatability, cross-verifier disagreement, latency, and provider-reported usage.
9. Record study limitations and residual risks.

This design is a research protocol, not a governance requirement.

## Public collaboration model

Issue #75 is the canonical tracker for this optional research program.

Community participation should occur through normal public GitHub issues, pull requests, technical feedback, and voluntary study contributions. Participation in the study does not confer approval authority over TEO releases, routing, architecture, or maintainer decisions.

If blinded reviewer decisions are collected, the public review packet must remain separate from the private alias map. Reviewer decisions should be submitted as JSONL artifacts or through a controlled maintainer handoff rather than exposing the alias map publicly.

The private alias map must never be given to reviewers before their decisions are final. Gold labels, case categories, deterministic expected results, and verifier observations must also remain hidden during review.

## Authority boundary

Machine-panel evidence is not a substitute for independent human validation when a claim is specifically presented as independently human-validated. Machine-panel evidence remains provisional and must not be misrepresented as human review or human ground truth.

Independent human calibration, when performed, adds evidence. It does not self-authorize route changes, broaden live execution, veto engineering decisions, or become a prerequisite for future TEO development.

Engineering changes remain subject to the repository's normal evidence, testing, CI, policy, public review, and maintainer-governance controls.

## Completion condition

Because this is optional research, TEO has no architectural dependency on completing the study.

A particular human-calibration study is complete when its repository record contains:

- complete blinded human labels,
- any required adjudications,
- the corresponding empirical verifier study,
- evaluated calibration metrics,
- documented limitations and residual risks, and
- a published study conclusion.
