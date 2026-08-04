# OpenAI

**Provider ID:** `openai`  
**Reviewed:** 2026-08-05  
**Evidence level:** provider documentation

## Access

OpenAI models are available through the OpenAI API and official client SDKs. The current model catalog identifies GPT-5.6 Sol, Terra, and Luna as the primary frontier family for reasoning, balanced execution, and cost-sensitive throughput.

## Documented tool classes

The current GPT-5.6 catalog documents support for:

- function calling
- web search
- file search
- computer use

Tool availability can depend on the selected endpoint, account permissions, region, and product surface.

## TEO use

TEO currently maps:

- `codex-sol` to `gpt-5.6-sol`
- `codex-terra` to `gpt-5.6-terra`
- `codex-luna` to `gpt-5.6-luna`

These mappings are routing defaults, not permanent endorsements. Actual eligibility still depends on access, tool requirements, risk, cost, latency, and verification independence.

## Source

- https://developers.openai.com/api/docs/models

## Limitations

- Provider documentation establishes identifiers and provider-described features, not TEO-observed task performance.
- Prices, limits, regional availability, and supported tools may change.
- The model list available to an account should be checked before execution.
