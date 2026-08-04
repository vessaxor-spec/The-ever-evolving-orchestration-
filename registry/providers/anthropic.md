# Anthropic

**Provider ID:** `anthropic`  
**Reviewed:** 2026-08-05  
**Evidence level:** provider documentation

## Access

Anthropic documents current Claude models as available through the Claude API and, depending on the model, through Amazon Bedrock, Claude Platform on AWS, Google Cloud, and Microsoft Foundry.

Current Claude models support text and image input, text output, multilingual use, and vision.

## Current family relevant to TEO

- Claude Fable 5 for the highest generally available capability and long-running agents
- Claude Opus 5 for complex agentic coding and enterprise work
- Claude Sonnet 5 for a speed and intelligence balance
- Claude Haiku 4.5 for the fastest current Claude tier

TEO currently routes to Opus, Sonnet, and Haiku roles. Fable is registered as a candidate escalation implementation rather than an automatic default.

## Source

- https://platform.claude.com/docs/en/about-claude/models/overview

## Limitations

- Provider descriptions and comparative latency labels are not TEO benchmark results.
- Model access can vary by platform and account.
- Limited-availability models must not be treated as generally available fallbacks.
- Exact identifiers must be rechecked before deployment because provider versioning conventions can change.
