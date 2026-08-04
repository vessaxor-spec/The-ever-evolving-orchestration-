# Capability Registry

Stable, provider-neutral capability definitions used to match task requirements to eligible implementations.

The canonical machine-readable registry is [`capabilities.yaml`](capabilities.yaml).

## Capability rules

- Capabilities describe what must be done, not which provider should do it.
- Model reasoning and tool access are separate eligibility questions.
- A capability must not be inferred solely from a provider name or model tier.
- Eligibility evidence must be proportionate to task risk.
- Human approval, independent verification, rollback readiness, and audit trace are controls rather than model capabilities.

## Capability groups

The initial registry covers:

- interpretation and orchestration
- planning and high reasoning
- coding, repository inspection, tool execution, debugging, and testing
- research, source grounding, long context, and multimodal understanding
- extraction, classification, transformation, and structured output
- semantic review, adversarial review, executable verification, and evidence verification

Each entry defines expected evidence so routing can distinguish a claimed capability from a demonstrated one.
