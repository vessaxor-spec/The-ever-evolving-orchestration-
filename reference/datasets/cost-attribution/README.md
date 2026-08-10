# Source-Backed Cost Attribution Fixtures

This directory contains first-party pricing evidence used by the TEO reference cost-attribution contract.

`pricing-evidence-v1.jsonl` is evidence, not a universal price table. Each record is bound to:

- one provider family;
- one concrete model;
- one explicit billable surface;
- standard processing only;
- one effective window;
- one first-party source and verification timestamp;
- only the rate dimensions the cited source supports.

The current records were verified on 2026-08-10 against first-party OpenAI, Anthropic, and Google pricing or model-release pages. Google records use `verified_from` because the current pricing page proves the rates at verification time but does not establish that those exact rates applied to earlier historical requests. Anthropic Sonnet 5 preserves the provider's explicit introductory and post-intro pricing windows. OpenAI GPT-5.6 records preserve the July 30 Terra/Luna repricing boundary and refuse the base rate above the documented long-context threshold.

Connection mechanism is intentionally absent. API keys, OAuth, subscriptions, CLI access, hosted integrations, enterprise agreements, credits, discounts, negotiated terms, regional multipliers, batch/priority processing, and separately billed tools are not interchangeable billable surfaces. A route is attributed only when the caller explicitly supplies the applicable billable surface and declares that no additional unmodeled billable events occurred.

Pricing changes never rewrite canonical Route-Outcome Evidence. New effective-dated pricing records are appended and historical attribution can be reproduced from the original outcome, pricing evidence, billing-surface context, and usage evidence.
