# Route-Outcome Fixtures

This directory contains content-minimized, integrity-protected route-outcome fixtures for deterministic evaluation and conformance.

`route-outcomes-v1.jsonl` contains three version 1 records:

1. primary-route success with passed independent verification;
2. fallback-assisted success preserving the failed primary route;
3. abandoned execution retaining partial attempt evidence and an abandonment reason.

Each line must validate against `reference/schemas/route-outcome-record.schema.json` and its `integrity_sha256` value.

The fixtures contain no task text, user identifier, prompt, model output, output artifact reference, provider-native request ID, credential, or connection secret.
