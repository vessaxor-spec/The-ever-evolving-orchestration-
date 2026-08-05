# TEO Python Reference Router

This is the minimal runnable Phase 5 control plane. It reads TEO's existing YAML policy and registries, creates a structured dispatch, assigns an independent verifier, and records a final evidence-bearing outcome.

It does **not** call model-provider APIs. Provider adapters, credentials, retries, streaming, and cost telemetry are later implementation layers. Keeping them outside this first boundary makes the routing behavior inspectable and testable without vendor access.

## Install

```bash
python -m pip install -e .
```

## Validate linked configuration

```bash
teo --repo-root . validate
```

Warnings expose current registry gaps without rewriting or weakening canonical team, worker, or specialist definitions.

## Create a dispatch

```bash
teo --repo-root . plan reference/examples/phase5-task.yaml \
  --output /tmp/teo-dispatch.json \
  --audit-log /tmp/teo-audit.jsonl
```

## Finalize an externally executed result

```bash
teo --repo-root . finalize \
  /tmp/teo-dispatch.json \
  execution-result.json \
  verification-result.json \
  --audit-log /tmp/teo-audit.jsonl
```

The execution and verification records must reference the dispatch ID. The verifier must match the assigned verification implementation and must be independent from the selected worker implementation.

## End-to-end demonstration

```bash
python reference/examples/run_example.py
```

## Tests

```bash
pytest
```
