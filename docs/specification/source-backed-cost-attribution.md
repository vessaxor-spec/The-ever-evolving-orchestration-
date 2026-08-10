# Source-Backed Cost Attribution

## Status

This specification defines TEO's version 1 source-backed cost-attribution contract.

Cost Attribution version: `1`

This layer converts canonical provider usage evidence plus explicit billable-surface context and effective-dated first-party pricing evidence into reproducible route-cost evidence. It does not change routing, model selection, provider access, verification, human approval, or canonical Route-Outcome Evidence.

## Design principle

A model identity is not a bill.

The same model can be reached through metered API access, a subscription, OAuth-backed CLI access, enterprise agreements, hosted integrations, negotiated pricing, credits, or other commercial surfaces. TEO therefore never infers an API list price merely from provider and model identity.

Cost attribution requires all three evidence classes:

```text
canonical route usage
  + explicit billable surface
  + effective-dated pricing evidence
  -> route cost attribution
```

If a required dimension is missing, incompatible, or unsupported, the monetary result remains `unknown` rather than becoming zero or an estimate.

## Canonical artifacts

- implementation: `reference/implementations/python/src/teo_reference/cost_attribution.py`
- pricing schema: `reference/schemas/pricing-evidence.schema.json`
- route-cost schema: `reference/schemas/route-cost-attribution.schema.json`
- first-party pricing evidence: `reference/datasets/cost-attribution/pricing-evidence-v1.jsonl`
- evidence notes: `reference/datasets/cost-attribution/README.md`
- conformance tests: `tests/test_cost_attribution.py`

## Pricing evidence

A pricing-evidence record binds one price schedule to:

- provider family;
- concrete model;
- explicit billable surface;
- standard processing mode;
- USD per one million tokens;
- effective-from and optional effective-until timestamps;
- first-party source identity and URL;
- source verification time;
- explicit rate dimensions;
- conditions and known excluded charges;
- an integrity hash.

Three effective-date bases are supported:

- `provider_explicit`: the provider states the applicable date or window;
- `source_publication`: the publication date is the best supported lower bound;
- `verified_from`: the source proves the rate at verification time but does not justify backdating it.

Pricing records are append-only evidence. A later price change creates a new effective window. Historical Route-Outcome Evidence is not rewritten.

## Current first-party evidence set

Version 1 includes first-party evidence for the billable surfaces currently relevant to TEO's reference execution and verification paths:

- OpenAI standard API: GPT-5.6 Luna, Terra, and Sol;
- Anthropic standard API: Claude Sonnet 5 introductory and post-introductory windows, plus Claude Haiku 4.5;
- Gemini Developer API paid standard: Gemini 3.5 Flash-Lite and Gemini 3.6 Flash.

The catalog is intentionally conservative. If a first-party source does not establish a cache-write rate, storage charge, tool charge, regional multiplier, or another billable dimension, that dimension is not guessed.

## Billable-surface context

Attribution callers must supply the commercial surface that actually applies to each execution dispatch and, separately, to verification.

Examples of distinct surfaces include:

- `openai_api_standard`;
- `anthropic_api_standard`;
- `gemini_api_paid_standard`;
- a subscription or OAuth-backed CLI surface for which no metered API price has been established.

A subscription, OAuth token, API key, connector, or CLI is not itself a routing signal. Cost attribution uses a billable-surface identity only because commercial terms can differ. If TEO has no pricing evidence for that surface, the cost remains unknown.

## Usage evidence

Execution usage comes from the canonical Route-Outcome attempt records and preserves normalized fields for:

- input tokens;
- output tokens;
- cached input tokens;
- cache-creation input tokens;
- reasoning output tokens;
- tool tokens;
- total tokens.

The live-verification adapters now preserve the same normalized provider usage on an additive `LiveVerificationExecution` evidence path. Existing verification APIs remain compatible and continue to return the canonical `VerificationResult` unless the richer evidence helper is explicitly used.

Provider-native usage fields are normalized only when a stable semantic equivalent exists. Missing usage remains missing.

## Calculation rules

Version 1 uses decimal arithmetic and stores monetary values as decimal strings.

For an attempt with compatible evidence:

```text
uncached input
  = normalized input
  - cached input
  - cache-write input

attempt amount
  = uncached input * uncached-input rate
  + cached input * cached-input rate
  + cache-write input * cache-write rate
  + output tokens * output rate
```

All token rates are per one million tokens.

Reasoning tokens are not double counted when the provider's first-party pricing states that they are included in output-token billing. Tool-token observations remain unknown for monetary attribution when the applicable tool billing rule is not modeled.

## Effective-window and condition matching

A pricing record applies only when all declared dimensions match:

- provider family;
- concrete model;
- billable surface;
- processing mode;
- attempt timestamp within the effective window;
- pricing conditions such as documented input-token thresholds.

Overlapping pricing windows for the same provider, model, surface, and processing mode fail closed.

For OpenAI GPT-5.6, version 1 refuses the documented base price above the base long-context threshold rather than silently applying the lower rate to an ineligible request.

## Additional billable events

Token usage alone may not represent a complete invoice. Some provider surfaces can include separately billed tools, grounding, search, cache storage, regional processing, priority modes, or other charges.

Every execution dispatch and verifier therefore carries an `additional_billable_events_status`:

- `none`: the caller has evidence that no additional unmodeled billable event occurred;
- `unknown`: TEO cannot prove that token-only attribution is complete.

`unknown` prevents a monetary total. This is intentional.

## Route decomposition

Cost is preserved at the same lifecycle boundaries as execution evidence:

- every primary attempt;
- every retry attempt;
- every fallback attempt;
- the route subtotal;
- the verifier separately.

A fallback-rescued route therefore exposes the failed primary cost and successful fallback cost separately. Verification overhead is never hidden inside executor cost.

## Attribution status

The record has three top-level states:

- `known`: every performed execution and verification component is fully attributable under compatible evidence;
- `partial`: at least one component is known and at least one performed component is unknown;
- `unknown`: no complete performed component can be monetarily attributed.

A top-level `total_amount` is published only for `known` attribution. Partial known subtotals remain visible at the component level, but TEO does not present their sum as the route total.

An unperformed verifier is the only case where zero is semantically asserted without provider usage. A performed verifier with missing usage remains unknown.

## Reproducibility and integrity

A route-cost record binds:

- canonical outcome ID;
- canonical outcome integrity hash;
- pricing-evidence IDs;
- explicit billing-surface context;
- normalized usage;
- component calculations;
- attribution timestamp;
- issues explaining any unknown state;
- an integrity hash.

JSONL persistence revalidates schema, semantics, and integrity on read and write.

Because pricing evidence is separate from Route-Outcome Evidence, the same historical route can be independently re-attributed against the price schedule that actually covered the attempt timestamp without mutating the original route record.

## Authority boundary

Source-backed cost attribution may produce economic evidence. It may not:

- select or force a model;
- change Team, Worker, or Specialist routing;
- lower effective risk;
- weaken capability requirements;
- change retry or fallback behavior;
- weaken independent verification;
- satisfy qualified-human approval;
- treat a subscription or OAuth connection as equivalent to metered API billing without evidence;
- optimize live routing directly;
- write routing policy;
- convert missing evidence to zero;
- use current prices as unsupported historical prices.

Cost is one evaluation dimension and remains subordinate to capability, quality, risk, verification, provider diversity, and human authority.

## Relationship to downstream evaluation

Completed cost attribution is intended to feed the later Shadow Route Evaluation workstream together with Route-Outcome Evidence and Benchmark and Outcome Lab evidence.

A lower-cost route is not automatically preferable. Specialist #82 may use source-backed cost as one bounded evidence dimension, but any future recommendation remains recommendation-only and cannot write live routing policy.
