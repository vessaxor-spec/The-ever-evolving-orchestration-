# Capability Registry

Provider-neutral capability definitions used to constrain TEO routing.

## Registry sources

TEO resolves the active capability registry from two governed sources:

1. `registry/capabilities/capabilities.yaml` for stable shared capability definitions.
2. Active worker `required_capabilities` for domain-specific capability names, paired with the worker's owning team and verification requirements.

The Python reference router exposes this union through `ConfigBundle.capability_registry`.

Worker-derived capability entries do not replace the stable registry. They make the active worker contract executable while avoiding invented provider-specific capability claims.

## Capability rules

- Capabilities describe what must be done, not which provider should do it.
- A caller-requested capability must exist in the active capability registry.
- A caller-requested capability must be compatible with the selected worker's accountable team unless the capability is explicitly cross-team.
- Model reasoning and tool access remain separate eligibility questions.
- A capability must not be inferred solely from provider name or model tier.
- Human approval, independent verification, rollback readiness, and audit trace are controls rather than model capabilities.
- Unknown requested capabilities fail closed.

## Implementation eligibility

The reference router uses layered authorization rather than claiming a universal model-capability benchmark matrix:

1. Resolve Team and Worker.
2. Resolve the worker's required capabilities plus authorized caller-requested capabilities.
3. Select a base implementation only from models authorized by that worker's `preferred_implementations` or `fallbacks`.
4. If a Specialist is explicitly matched, the active specialist-model routing policy may refine primary, fallback, verifier, and reasoning effort without changing Team, Worker, specialist source, or effective risk.
5. Preview implementations remain ineligible unless the task explicitly accepts the concrete preview model.
6. Independent verification must use a different model and provider family from execution.

Worker implementation lists and specialist model templates are policy authorization, not empirical proof that a model is best for the task. Empirical route quality remains a separate evidence layer.

## Stable capability groups

The base registry covers interpretation and orchestration, planning and high reasoning, engineering execution, research and source grounding, multimodal understanding, structured transformation, semantic/adversarial review, executable verification, and evidence verification.

Worker contracts extend that vocabulary for active specialist domains such as reliability, physical systems, assurance, finance, marketing, legal/compliance, and other preserved specialist responsibilities.

## Conformance

Configuration validation and routing tests require:

- every active worker to declare required capabilities
- every active worker implementation reference to resolve to the model registry
- every active specialist to have a deterministic Team -> Worker spawn path
- unknown caller-requested capabilities to fail closed
- provider-diverse independent verification
- explicit preview-model authorization

This keeps the capability layer executable without overstating model quality evidence that has not yet been measured.
