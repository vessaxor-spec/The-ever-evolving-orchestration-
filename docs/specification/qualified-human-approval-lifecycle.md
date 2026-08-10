# Qualified-Human Approval Lifecycle

## Status

This specification defines the version 1 reference lifecycle for qualified-human authority evidence in TEO.

The lifecycle implements authority that routing policy already requires. It does not create new human-approval requirements, widen live execution, select models, change provider access, or create policy-write authority.

## Core rule

A model-verification result cannot satisfy a qualified-human approval requirement.

When a dispatch is already marked `human_approval_required`, successful execution and independent model verification stop at `awaiting_human`. The qualified-human lifecycle begins only after that gate has been reached.

The lifecycle is:

```text
Human-required dispatch
  -> successful execution
  -> independent verification
  -> Route-Outcome Evidence: awaiting_human
  -> qualified-human approval request
  -> scoped human authority evidence
  -> approval lifecycle disposition
  -> terminal human finalization
```

The original Route-Outcome Evidence remains immutable. Human finalization is a separate integrity-protected record that binds the exact route outcome and exact approval evidence.

## Records

### Qualified-human authority grant

`qualified_human_authority_grant` records why an opaque human subject reference is authorized to act for a declared authority requirement.

A grant contains:

- an opaque `subject_ref`;
- an `authority_class`;
- covered authority-requirement identifiers;
- covered effective-risk levels;
- covered task types;
- validity timestamps;
- external issuer and qualification evidence;
- an integrity hash.

A person's identifier is not a routing signal. Authority comes from the grant's declared scope and external qualification evidence.

The following are explicitly not qualification signals:

- model selection;
- provider access or authentication method;
- billing identity;
- the human identifier itself.

### Qualified-human approval request

`qualified_human_approval_request` binds the authority question to the exact runtime evidence.

The request requires:

- the active dispatch ID;
- a canonical SHA-256 digest of the exact dispatch content;
- task ID and task type;
- effective risk;
- authority requirement ID;
- required authority class;
- authority reason and policy source;
- the exact `awaiting_human` Route-Outcome Evidence ID and integrity hash;
- verification dispatch and status from that route outcome;
- applicable benchmark or shadow review evidence when present.

A request cannot be created for a dispatch that is not already marked `human_approval_required`.

A benchmark conclusion, shadow recommendation, Mission Control review, maintainer review, model verifier, or specialist output can provide supporting evidence. None of them satisfy qualified-human approval.

### Qualified-human approval disposition

`qualified_human_approval_disposition` is append-only lifecycle evidence.

Supported states are:

- `approved`;
- `rejected`;
- `unable_to_determine`;
- `expired`;
- `revoked`.

The initial `requested` state belongs to the approval-request record.

Human decisions and revocations require `actor_type: human` and an exact authority-grant reference. The referenced grant must cover the request's required authority class, authority requirement, effective risk, task type, and decision timestamp.

`expired` is system-generated from an already declared request or approval expiry. It cannot carry a human authority grant.

An approval must declare `approval_expires_at`. It cannot outlive the request or the authority grant that supported it.

Lifecycle transitions are linear:

```text
requested
  -> approved
  -> revoked | expired

requested
  -> rejected | unable_to_determine | expired
```

Rejected, unable-to-determine, revoked, and expired states are blocking states.

### Qualified-human finalization

`qualified_human_finalization` evaluates the current approval chain against the exact dispatch and Route-Outcome Evidence.

The result is either:

- `completed`, when the current state is a still-valid scoped approval; or
- `blocked`, with an explicit reason of `missing_approval`, `rejected`, `unable_to_determine`, `expired`, or `revoked`.

A completed human finalization records the approving opaque subject reference and authority class for auditability. These values are evidence of who exercised already-required authority. They do not become model-routing inputs.

A finalization never mutates the original Route-Outcome Evidence and never changes the dispatch-selected model, verifier, provider access, billing surface, effective risk, capabilities, or live-execution scope.

## Impersonation boundary

Approval, rejection, and revocation records accept only `actor_type: human`.

The schema does not accept actor types such as:

- model;
- specialist;
- verifier;
- Mission Control;
- maintainer.

A maintainer who is independently qualified may act only through a human authority grant that proves the required authority scope. Maintainer status by itself is not approval authority.

This distinction prevents control-plane records from self-satisfying a human gate while preserving legitimate human authority evidence.

## Evidence and integrity

Every lifecycle record is protected by canonical SHA-256 integrity.

The reference JSONL ledger is append-only and revalidates records when writing and reading. A mutated record fails validation rather than silently changing authority history.

The finalization path rechecks:

- exact dispatch digest;
- task identity;
- effective risk;
- exact Route-Outcome Evidence ID and hash;
- verification evidence binding;
- exact approval-request hash;
- contiguous disposition lineage;
- authority-grant hash and scope;
- request validity;
- approval validity;
- revocation and expiry state.

## Authority boundaries

The lifecycle has no authority to:

- write routing policy;
- change live routing;
- widen live execution scope;
- lower effective risk;
- bypass required capabilities;
- bypass independent verification;
- accept preview models;
- change provider-access semantics;
- convert review evidence into human approval;
- grant a human authority class without external qualification evidence.

The lifecycle only proves whether an already-required qualified-human gate has been satisfied for the exact evidence-bound outcome.

## Reference implementation

The executable reference is:

- `reference/implementations/python/src/teo_reference/qualified_human_approval.py`

Schemas are:

- `reference/schemas/qualified-human-authority-grant.schema.json`
- `reference/schemas/qualified-human-approval-request.schema.json`
- `reference/schemas/qualified-human-approval-disposition.schema.json`
- `reference/schemas/qualified-human-finalization.schema.json`

Conformance coverage is in:

- `tests/test_qualified_human_approval.py`

The milestone is complete only when CI proves the request, scope, lifecycle, impersonation, expiry, revocation, mutation, ledger, and finalization boundaries without weakening existing routing or verification controls.