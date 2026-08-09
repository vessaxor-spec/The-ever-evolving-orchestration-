# Mission Control routing recalibration — 2026-08-09

This record documents the routing decision that follows the Mission Control review of current implementation directions.

The decision changes executable routing rather than only README wording.

## Decisions

- Keep GPT-5.6 Terra as the primary bounded engineering execution route.
- Keep GPT-5.6 Sol as the difficult engineering and cross-system reasoning route.
- Replace the daily-coding preview Gemini Pro fallback with stable Gemini 3.6 Flash.
- Promote Gemini 3.5 Flash-Lite to the primary economical bounded-throughput route.
- Keep Claude Haiku 4.5 as the first cross-provider bounded-throughput fallback.
- Keep GPT-5.6 Luna as an independent economical throughput alternative.
- Keep Gemini 3.6 Flash for stronger bounded agentic, coding, and multimodal work rather than treating it as the cheapest throughput lane.
- Keep Claude Opus 5 as the established high-consequence specialist reasoning route.
- Route Claude Fable 5 only as a frontier escalation after established Opus/Sol paths remain inconclusive and the expected capability gain justifies materially higher cost and latency.
- Preserve provider-diverse verification and capability validity through fallback.
- Keep provider access mechanisms outside model routing.

## Evidence basis

The change is based on current first-party provider documentation reviewed on 2026-08-09 and the existing TEO role boundaries. Provider claims establish current capability and availability evidence, not permanent superiority.

The change must remain reversible through routing policy if TEO-specific evidence later shows a different implementation is better for a role.
