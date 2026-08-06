# Main Branch Protection

This document records the intended governance settings for the default `main` branch of The Ever-Evolving Orchestration.

Repository-host settings are not stored in Git, so this document is a reviewable statement of intent rather than the enforcement mechanism itself.

## Purpose

`main` is the authoritative public state of TEO. Working branches may be experimental, incomplete, or temporary. Changes should enter `main` only through a visible pull request with validation and an auditable merge record.

Branch protection is intended to prevent:

- accidental direct commits to `main`
- force pushes that rewrite accepted history
- deletion of the default branch
- merging changes that fail the reference control-plane checks
- merging while review conversations remain unresolved
- accepting a pull request that is no longer current with `main`

It is not intended to prevent normal development, repository administration, or emergency recovery through a documented and accountable process.

## Required policy

The `main` branch should require:

- changes through a pull request
- zero mandatory external approvals while the project has only one active maintainer
- resolution of all review conversations before merge
- the required status check `Validate reference router`
- the pull-request branch to be up to date before merge
- blocked force pushes
- blocked branch deletion

The branch should not be locked or made read-only.

Signed commits are not mandatory at this stage. They may be introduced later through a separate reviewed governance change after contributor tooling and recovery procedures are documented.

## Administrator treatment

Initial activation may retain administrator bypass while the rule is tested. After a successful protected pull-request cycle, administrators should be included in the rule so routine maintenance follows the same branch, pull-request, CI, and merge path.

Any emergency bypass should be exceptional, documented, and followed by an immediate review of the resulting commit.

## Required check availability

The workflow `.github/workflows/reference-ci.yml` runs `Validate reference router` for every pull request, including documentation-only and capsule-only changes. This prevents required checks from remaining indefinitely pending because a pull request did not match a workflow path filter.

Push validation on `main` remains scoped to control-plane-relevant paths to avoid unnecessary duplicate runs after documentation-only merges.

## Expected merge path

```text
Working branch
  -> Pull request
  -> Validate reference router
  -> Resolve review conversations
  -> Update branch when required
  -> Squash merge into main
```

Squash merge remains the preferred method because it preserves a readable public history while retaining the complete pull-request discussion and validation record.

## Recovery

Protection does not replace backups, immutable Capsules, or Git history. If an accepted state is damaged:

1. identify the last accepted commit
2. create a recovery branch from that commit
3. restore the intended state through a pull request
4. run the required validation
5. document the incident and recovery decision
6. create a new Capsule only when the architectural state itself warrants preservation

Do not rewrite an accepted Capsule to describe the recovery retroactively.
