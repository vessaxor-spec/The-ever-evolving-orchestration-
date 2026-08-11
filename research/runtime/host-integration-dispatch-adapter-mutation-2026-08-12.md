# Host Integration Dispatch Authorization and Adapter Self-Expansion Mutation Audit

**Date:** 2026-08-12  
**Authority:** non-normative research  
**Base revision:** `dbd838c2bf9c2bb5f106c8b4f846b95205e23e47`

## Question

Can an external host bypass TEO routing authority by fabricating or altering a dispatch record, or expand execution by injecting provider-native capabilities through the provider adapter payload?

## Mission Control lenses

- orchestration security
- authority boundaries
- adversarial verification
- repository integrity

## Diagnosis

The current provider adapter contract strongly binds a provider attempt to the fields present in the supplied `DispatchRecord`: selected provider, selected model, risk, capabilities, and dispatch identity are carried into the provider-neutral request, and provider/model substitutions in the normalized response are rejected.

That is necessary but not sufficient for an external host boundary. `execute_provider_once()` accepts a `DispatchRecord` object supplied by its caller. The generic execution function has no independent provenance mechanism proving that the dispatcher actually issued that exact record. A host able to construct a syntactically valid record can therefore satisfy the generic adapter contract without demonstrating dispatcher provenance.

This is a host-integration evidence gap, not a claim that the current guarded live wrappers authorize arbitrary task classes. Existing live wrappers remain separate authorization boundaries.

## Dispatch-authorization adversarial slice

The research harness `host_integration_dispatch_authorization.py` introduces a deliberately narrow process-local authority registry:

1. the authority records the complete canonical snapshot of an actually issued `DispatchRecord`;
2. it returns an opaque capability token referencing authority-owned state;
3. the execution boundary verifies the token and byte-exact canonical dispatch snapshot before invoking any adapter;
4. an unissued token or any changed dispatch field fails before provider execution.

The control is intentionally **not** promoted into the reference runtime. It is a research mechanism for testing the missing provenance property.

### Tamper mutations

The executable tests challenge the issued record by independently changing:

1. dispatch identity;
2. task identity;
3. task type;
4. effective risk, including risk lowering;
5. selected team;
6. selected worker;
7. selected specialist;
8. required capabilities;
9. selected provider;
10. selected model;
11. fallback assignment;
12. verifier assignment;
13. human-approval requirement;
14. dispatch status.

They also test an entirely unissued token and token reuse against a different dispatch snapshot.

The candidate boundary is successful only if every mutation is rejected before the adapter is called.

## Adapter self-expansion slice

The bundled OpenAI, Anthropic, and Google adapters were examined as executable adapters rather than assuming the generic `ProviderAdapter` protocol provides registration integrity.

For each bundled adapter, a caller-supplied payload attempts to inject:

- `tools`;
- `tool_choice`;
- `web_search`;
- `mcp_servers`;
- a host-selected fallback model;
- a host-selected fallback provider.

The adapters are required to construct their outbound provider request from their own bounded allowlisted fields and the dispatch-selected model. The adversarial fields must not appear in the provider-native request body.

This establishes a narrower claim than "all adapters are safe":

- **bundled adapter payload-driven self-expansion:** executable resistance is supported by this audit;
- **arbitrary third-party adapter provenance, registration, and manifest integrity:** remains open and requires a separate authority mechanism before external adapters can be treated as trusted execution components.

## Verification record

Reference Implementation CI **#554** was intentionally red during the first audit run: the Anthropic adversarial fixture omitted Claude Sonnet 5's required explicit reasoning effort, so the adapter correctly refused the request before the injection test reached the provider payload. That was a test-fixture defect, not a surviving authority mutation or production-control defect.

The fixture was corrected without weakening the tested boundary. Reference Implementation CI **#555** then passed:

- **703 tests**;
- **497 tracked-file repository-layout checks**;
- regulated specialist evidence structural validation;
- **41 parsed JSON Schemas**;
- linked TEO configuration with zero issues;
- the provider-diverse end-to-end example.

The successful run proves, for this research slice, that all 14 dispatch mutations, forged-token use, and cross-dispatch token reuse are rejected before adapter invocation. It also proves that the bundled OpenAI, Anthropic, and Google adapters omit the injected tool, MCP, web-search, and fallback-expansion fields from their outbound provider-native request bodies while retaining the dispatch-selected model.

## Security boundary of the candidate control

The process-local registry is not a distributed attestation design. The opaque token is meaningful only because the registry retains the authoritative snapshot in memory. It does not prove integrity across a hostile process boundary, restart, distributed runtime, or compromised authority process.

A later production design would need one of the following, with independent security review:

- an authoritative dispatch store with authenticated lookup and revision binding; or
- a cryptographically issued dispatch attestation with explicit key lifecycle, rotation, revocation, replay, and freshness semantics.

A plain unkeyed hash carried beside the dispatch is insufficient because a hostile host could recompute it after tampering.

## Decision

**Dispatch-provenance enforcement property: supported in a process-local research boundary.** The existing generic executor itself does not prove provenance, but an authority-owned exact dispatch snapshot can reject the tested fabrication and tampering classes before any adapter call.

**Bundled-adapter payload self-expansion resistance: supported for the current OpenAI, Anthropic, and Google adapters.** Caller-injected execution-surface fields are not forwarded into provider-native requests.

**Third-party adapter trust: still open.** The generic adapter protocol does not itself establish adapter provenance, approved registration, code identity, or manifest integrity.

This research does **not** make the Host Integration Contract normative, authorize external-host execution, register third-party adapters, change live scope, or solve cross-process dispatch authenticity, replay, or freshness. Those remain later gates.
