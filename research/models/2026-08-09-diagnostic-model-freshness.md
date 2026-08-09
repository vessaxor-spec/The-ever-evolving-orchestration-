# Diagnostic model freshness review — 2026-08-09

## Decision

The diagnostic freshness observations are valid review triggers, not automatic routing changes.

- `claude-fable-5` remains registered but intentionally unrouted. Current Anthropic documentation identifies Fable 5 as its highest-capability widely released model, but TEO requires role-fit evidence before changing an established escalation route.
- `gemini-3.5-flash-lite` is added to the canonical evidence registry as a stable, registered-unrouted economical-throughput candidate. Current Google documentation positions it as the fastest and lowest-cost Gemini 3.5 model for high-throughput execution.
- `gemini-3.1-flash-lite` is retained as a previous-generation candidate while migration evidence is evaluated.
- No primary, fallback, verifier, calibration, or canary route is changed by this review.

## Primary sources

- Anthropic Claude models overview: https://platform.claude.com/docs/en/about-claude/models/overview
- Google Gemini latest models: https://ai.google.dev/gemini-api/docs/latest-model

## Acceptance rule

A newer model may enter the registry because it exists and is relevant. It may enter an active route only after capability fit, reasoning controls, availability, fallback/verifier independence, operational evidence, and regression risk are evaluated.
