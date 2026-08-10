# Repository Layout Stewardship

## Purpose

TEO's filesystem is part of its control surface.

Repository placement must make it possible to distinguish current authority, historical state, research, evidence, implementation, and community material without requiring a reader to reconstruct project history first.

The machine-readable contract is `policy/governance/repository-layout.yaml`. This document explains how stewards should apply it.

## Governing rule

Organize by:

1. authority
2. lifecycle
3. subject

Do not organize primarily by recency, convenience, contributor, provider, or whichever team happened to own a task when the file was created.

## Root rule

The repository root is reserved for durable entrypoints and build metadata.

The permanent root allowlist is:

- `README.md`
- `AI_INSTRUCTIONS.md`
- `CONSTITUTION.md`
- `CHANGELOG.md`
- `CODE_OF_CONDUCT.md`
- `LICENSE`
- `pyproject.toml`
- `.gitignore`

Files still at root but declared as temporary exceptions in the layout policy are migration debt, not precedent for new root files.

A new root-level file requires an intentional governance change. It must not be added merely because its eventual location is undecided.

## Authority zones

### `policy/`

Normative machine-readable control.

This area should represent active control state. Historical staging or activation records may remain temporarily only where the layout policy explicitly lists them as migration exceptions.

### `registry/`

Current or effective-dated ecosystem evidence such as provider, model, capability, and benchmark records.

Registry evidence may change rapidly. It does not redefine stable responsibility merely because implementation evidence changes.

### `reference/`

Executable reference behavior, schemas, examples, and conformance datasets.

Reference artifacts demonstrate how TEO can be implemented. They remain separate from normative policy even when CI depends on them.

### `docs/`

Human-readable explanation, specification, methodology, stewardship, releases, examples, and history.

A document is not normative merely because it is under `docs/`. Normative status must be explicit and must remain consistent with machine-readable policy where applicable.

### `research/`

Non-normative investigation and evidence gathering.

Research may motivate policy changes but must not become active policy through age, repetition, or citation alone.

### `community/`

Teams, workers, specialists, proposals, discussions, and immutable capsules.

Community artifacts can define durable responsibilities, but the area also contains historical capsules. Their lifecycle is therefore explicit rather than inferred from the directory name alone.

### `tests/`

Executable conformance, invariant, regression, and mutation controls.

Tests protect the control plane but do not replace the policy or specification they enforce.

## Lifecycle separation

### Active policy versus historical activation state

A staging file can be historically correct while being operationally obsolete.

Once an activation record no longer represents current policy, it should migrate to `docs/history/` after all runtime, test, CI, and documentation consumers are updated.

The repository must not present a historical `status: staged` record beside current active policy without an explicit migration exception.

### Methodology versus records of execution

`docs/methodology/` is for reusable methods.

A dated record that says a migration, staging exercise, refresh, audit, or validation was performed belongs under history unless it remains an intentionally active methodology artifact.

### Research versus assertions

Research records may contain hypotheses, provisional recommendations, benchmark findings, or external evidence. They remain non-normative until an accepted change updates the applicable policy, registry, specification, or reference artifact.

## Specialist identity rule

Specialist role cards remain in a flat identity namespace under `community/specialists/`.

Do not sort specialist cards into team directories.

The reason is architectural: a specialist's current team allocation may change while the specialist's identity and practitioner-grade capability definition remain stable. Filesystem placement must not turn a current allocation into identity.

The specialist preservation contract remains controlling for role-card contents.

## Capsule rule

Accepted capsules are immutable historical records.

Do not move, rewrite, reformat, correct, or normalize accepted capsule files as part of repository cleanup. The capsule index may evolve, but accepted snapshots remain where they were accepted.

## Reference dataset rule

`reference/datasets/` remains intentionally unchanged.

It already provides a coherent home for public fixtures and datasets used by examples, evaluation, and conformance. A rename would create broad path churn without improving authority clarity.

## Temporary exceptions

A temporary exception must include:

- the exact current path
- the intended target or disposition when known
- the migration phase
- no implication that similar new files are permitted

Adding a new temporary exception is a governance decision. It is not the default response to a placement failure.

## Validation

`ci/validate_repository_layout.py` validates tracked Git paths against the machine-readable layout contract.

The validator intentionally reads `git ls-files` rather than the working directory. Generated artifacts, caches, editable-install metadata, and local runtime output therefore cannot produce placement failures.

The validator fails when, among other cases:

- an undeclared file appears at repository root
- an unknown top-level zone appears
- an undeclared direct routing-policy YAML appears
- a new direct worker extension bypasses the declared topology
- historical or methodology placement violates the current contract
- specialist cards are nested under team directories
- capsule placement or naming violates the immutable capsule namespace
- direct research files bypass topic-scoped research directories

## Migration discipline

The approved sequence is:

1. R1: layout constitution
2. R2: root and research normalization
3. R3: documentation lifecycle separation
4. R4: policy topology
5. R5: worker and implementation topology

Each phase must be independently reviewable and must update path consumers atomically.

A file move is incomplete until all applicable runtime loaders, tests, CI workflows, links, examples, conformance fixtures, and agent instructions resolve the new path.

## Steward test

Before adding or moving a file, answer:

1. What authority does this artifact have?
2. Is it active, historical, immutable, or exploratory?
3. Which durable subject owns it?
4. Is there already a canonical source for the same concept?
5. Will this placement still make sense if teams, models, or providers change?

If those answers are unclear, do not create a new top-level namespace. Resolve the artifact's role first.
