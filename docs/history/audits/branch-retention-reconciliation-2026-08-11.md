# Branch Retention Reconciliation - 2026-08-11

## Authority

This record documents a TEO Repository Stewardship reconciliation of working-branch state after the 2026-08-10 legacy `agent/*` cleanup.

It is repository-hygiene evidence only. It does not create routing, runtime, model-selection, verification, evidence, specialist, release, or live-execution authority.

## Active review lenses

- Repository Stewardship
- Program and Progress Control
- Runtime and Control Integrity
- Independent Verification

## Trigger

A fresh repository reconciliation on 2026-08-11 found that Issue #100 remained correctly completed for its reviewed legacy scope, but newer delivery work had introduced branch-retention drift outside that original scope.

The original prevention workflow automatically handled only same-repository merged `agent/*` pull-request heads. Later accepted work used additional temporary delivery prefixes, so fully accounted merged branches remained visible after their work was preserved on `main`.

The same reconciliation also found one newer orphan `agent/*` reconciliation branch that was not itself the pull-request head, plus one accidental capability-probe branch created during repository tooling inspection.

## Pre-remediation inventory

Before creating the remediation branch, the repository exposed nine branch refs total: protected `main` plus eight non-main refs.

### Accounted cleanup targets

| Branch | Disposition evidence | Decision |
|---|---|---|
| `agent/pr108-progress-reconcile` | points to the accepted PR #108 merge state and has no unique work beyond accepted history | delete |
| `audit/authority-temporal-causality` | PR #132 merged; durable audit and runtime changes are on `main` | delete |
| `audit/mission-control-finalization-authority-recovery-mutations` | PR #133 merged; mutation evidence and tests are on `main` | delete |
| `capsule/0009-evidence-becomes-authority` | PR #134 merged; accepted Capsule 0009 is on `main` and immutable there | delete |
| `cleanup/remove-specialist-origin-references` | PR #1 merged; accepted repository state is on `main` | delete |
| `governance/reframe-human-calibration` | PR #102 merged; optional-calibration governance is on `main` | delete |
| `noop-check` | accidental capability-probe branch; contains no project work or authority | delete by exact-name guard |

### Explicitly retained ref

`evidence/documentation-replay-trigger-v1` is intentionally retained.

The controlled provider-backed `documentation` replay workflow uses that exact same-repository branch identity as part of its trigger boundary. The provider-backed replay is currently a deferred open evidence gate, so deleting or renaming the branch would break an accepted execution path without replacing it.

Retention of that branch does not authorize `documentation` live execution. The candidate remains staged and `activation_authorized: false`.

## Root cause

The durable retention principle said working branches are temporary, but automated enforcement was narrower than actual delivery practice:

- policy automation covered only `agent/*`;
- newer accepted work also used `audit/*`, `capsule/*`, `cleanup/*`, and `governance/*`;
- an intermediate `agent/*` branch that was not a merged PR head could not be removed by the normal event-driven rule;
- there was no exact cleanup path for the accidental `noop-check` probe.

This was a repository-stewardship coverage gap, not a control-plane defect.

## Remediation

The branch-retention workflow is expanded so future same-repository merged pull-request heads are automatically deleted for these temporary prefixes:

- `agent/*`
- `audit/*`
- `capsule/*`
- `cleanup/*`
- `governance/*`

Every automatic deletion still requires:

1. the pull request was actually merged;
2. the head repository is this repository;
3. the branch belongs to a governed temporary prefix;
4. no open pull request currently uses the branch;
5. the ref still exists at cleanup time.

The existing 104-ref legacy snapshot remains unchanged as historical evidence for Issue #100.

A new fixed reviewed post-v1 snapshot accounts for the six ordinary temporary refs listed above. The remediation merge also deletes `noop-check` through an exact-name one-time guard and deletes its own `agent/branch-retention-v2` head through the normal merged-agent rule.

The reserved `evidence/documentation-replay-trigger-v1` branch is not part of any temporary-prefix cleanup set.

## Verification requirements

Before merge:

- repository CI must pass;
- branch-retention tests must prove the widened prefix guard, open-PR preservation, fixed snapshots, and exact probe cleanup;
- the reserved replay branch must remain outside cleanup snapshots;
- no runtime, routing, model, evidence, activation, or release files may change.

After merge:

- the Branch Retention workflow must complete successfully;
- a fresh branch inventory must show only `main` and the intentionally retained replay trigger branch from the pre-remediation set;
- accepted Capsules, merged PR history, release tags, and protected `main` must remain unchanged.

## Disposition

This remediation closes a newly discovered branch-retention coverage gap without reopening Issue #100. Issue #100 remains a completed historical cleanup of the original 104 legacy `agent/*` refs.
