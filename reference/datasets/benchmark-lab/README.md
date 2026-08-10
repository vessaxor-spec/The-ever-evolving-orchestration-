# Benchmark Lab Reference Dataset

This directory contains the controlled reference dataset for the first executable TEO Benchmark and Outcome Lab foundation.

## Contents

- `benchmark-fixtures-v1.jsonl`: fixed synthetic benchmark cases with explicit task, risk, capability, criteria, suite version, and integrity metadata.
- `benchmark-experiment-v1.json`: the declared comparison manifest, harness identity, candidate configurations, fixed repeated-trial plan, and exact route-outcome bindings.
- `route-outcomes-v1.jsonl`: canonical route-outcome records representing the declared controlled trials.

## Data boundary

The fixture inputs are synthetic and content-safe. They are intentionally stored because controlled benchmark cases must be reproducible.

The route-outcome records retain the content-minimized canonical TEO evidence boundary. They do not contain production user task text, user identifiers, prompts, model output, credentials, or provider-native payloads.

This dataset is evaluation evidence only. It does not select a live route, authorize model promotion, or modify policy.

## Foundation scope

The current dataset demonstrates:

- fixed fixture identity;
- two repeated trials per fixture and candidate;
- executor-only comparison under a fixed verifier and runtime context;
- primary-route success;
- fallback-assisted success;
- retry-assisted success;
- independent-verification failure;
- latency and normalized usage evidence;
- reproducible comparison and regression checks.

It does not represent a production benchmark claim or a current provider leaderboard. The synthetic outcomes exist to prove the evaluation contract and conformance behavior.

Live controlled replay execution and multi-verifier disagreement measurement remain later gates in the active Benchmark and Outcome Lab workstream.
