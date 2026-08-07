# Runtime research: provisional machine-panel verifier calibration

**Date:** 2026-08-07  
**Status:** implementation rationale  
**Authority:** none

## Constraint

The independent-human calibration protocol is structurally ready, but independent human reviewers may not always be available at the point when engineering is ready to continue evidence collection.

The project needs a way to continue learning without falsifying the evidence tier.

## Rejected shortcut

A TEO specialist lens, alternate AI agent, or provider-diverse set of models must not be relabeled as an independent human reviewer.

That shortcut would make the record easier to complete but would destroy the meaning of the human-review control.

## Chosen approach

Add a separate provisional machine-panel tier.

The tier uses three provider-diverse machine judges on a blinded review packet, followed by the same bounded repeated verifier study. The machine judges use exact models different from the verifier models being scored.

Initial panel:

- OpenAI `gpt-5.6-terra`
- Anthropic `claude-opus-5`
- Google `gemini-3.1-pro-preview`, explicitly acknowledged as preview

Evaluated verifier routes remain:

- OpenAI `gpt-5.6-sol`
- Anthropic `claude-sonnet-5`
- Google `gemini-3.6-flash`

This avoids exact-model self-judging while retaining three provider families.

## Important epistemic limit

Provider diversity is not human independence.

The panel can provide evidence about cross-model agreement and disagreement. It cannot establish human-aligned ground truth. The fixed reference-control corpus therefore remains the objective anchor for provisional metrics, and machine-panel majority is reported as a separate signal.

## No-majority behavior

A three-way disagreement is not force-adjudicated. It remains unresolved.

This is intentional. Adding another AI model and calling it an adjudicator would produce another machine opinion, not independent human ground truth. The unresolved state preserves information rather than manufacturing certainty.

## Study size

Machine panel:

- 8 cases
- 3 panel routes
- 1 judgment per route/case
- 24 live calls

Provisional verifier study:

- 8 cases
- 3 evaluated verifier routes
- 3 runs per route/case
- 72 live calls

Total planned live calls:

- 96

## Authority boundary

The provisional tier cannot by itself authorize:

- a human-ground-truth claim
- an empirical verifier-quality claim
- a routing change
- automatic route updates
- broader guarded live execution
- deletion or replacement of the independent-human tier

Any later route change remains subject to explicit human acceptance and residual-risk review.

## Why this still has value

Even without human ground truth, the provisional tier can surface:

- systematic false passes and false fails against the fixed control corpus
- provider-specific weaknesses
- route-specific repeatability failures
- cross-provider disagreement
- unstable criteria
- unexpected human-escalation behavior
- latency and usage differences
- cases that remain unresolved even across strong independent models

Those findings can justify further engineering and can prioritize the cases that deserve eventual human review.