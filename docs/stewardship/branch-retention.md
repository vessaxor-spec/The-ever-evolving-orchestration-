# Branch Retention

TEO treats working branches as temporary delivery references, not as durable architectural authority or historical records.

## Durable history

The following preserve accepted project history and must not depend on retaining completed feature branches:

- protected `main`
- immutable release tags and GitHub Releases
- merged pull-request records and discussions
- accepted Capsules
- records under `docs/history/`
- canonical current policy, registries, reference code, and stewardship documents on `main`

Deleting an accounted working-branch ref does not delete the commits reachable from accepted repository history, the pull-request record, a release tag, or an accepted Capsule.

## Default retention rule

Same-repository branches under `agent/*` are temporary.

After a pull request from an `agent/*` branch is merged into `main`, the branch should be deleted automatically after the merge record and required validation have been preserved.

Closed but unmerged `agent/*` branches should be deleted after the work is explicitly abandoned, superseded, or otherwise accounted for. They must be retained when they still back an open pull request, an active recovery process, or an explicit forensic hold.

A branch must never be retained merely because it contains an older implementation of a decision that is already represented by `main`, a merged pull request, a release, a Capsule, or a historical record.

## Automated enforcement

`.github/workflows/branch-retention.yml` enforces the normal merged-branch rule.

The workflow:

1. runs only after a pull request is closed,
2. requires that the pull request was actually merged,
3. requires that the head branch belongs to this repository,
4. acts only on `agent/*` branches,
5. checks that no open pull request currently uses the branch before deletion, and
6. deletes only the accounted branch ref.

The workflow uses the repository-scoped GitHub token and does not call external actions.

## Legacy cleanup

Issue #100 records the one-time cleanup of the historical `agent/*` backlog discovered by the 2026-08-10 hard audit.

The cleanup workflow contains a fixed snapshot of the 104 legacy refs reviewed for that issue. It does not dynamically sweep arbitrary future branches. The legacy sweep runs only when the reviewed `agent/branch-retention-hygiene` pull request is merged.

Any legacy ref that unexpectedly backs an open pull request at execution time is preserved automatically.

The audit and disposition record is `docs/history/audits/branch-cleanup-2026-08-10.md`.

## Authority boundary

Branch retention is repository hygiene only.

It must not change:

- routing or model-selection policy
- team, worker, or specialist responsibility
- runtime or verification behavior
- evidence or registry content
- accepted Capsules
- release tags or GitHub Releases
- protected `main`

If preserving a branch is necessary to investigate an incident or recover work, preservation takes priority over cleanup until the reason is resolved and documented.
