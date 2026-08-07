# TEO Python Reference Router

This is the runnable reference control plane for The Ever-Evolving Orchestration. It reads TEO's YAML policy and registries, creates a structured dispatch, assigns an independent verifier, and records a final evidence-bearing outcome.

The router itself remains provider-neutral. Live provider execution is optional and occurs only through the provider-adapter boundary after routing has already selected the authorized provider family and model.

The first guarded live canary supports Anthropic Claude Haiku 4.5 for `high_volume_simple` tasks at low or medium risk. It performs one attempt only. It does not own fallback, retry, verification, escalation, or human approval.

Connection method is deliberately separate from routing. API keys, OAuth, delegated identity, service accounts, connector sessions, local credentials, and future connection mechanisms belong behind `ProviderConnection`; they do not change the selected model route.

## Install

```bash
python -m pip install -e '.[test]'
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

## Provider execution boundary

Provider execution is split into two independent concerns:

1. TEO routing authorizes a provider family and model through `ProviderExecutionRequest`.
2. Runtime supplies a provider-specific `ProviderConnection` without exposing credential material to the dispatch or audit record.

The general contract is documented in:

- `docs/specification/provider-adapter-contract.md`
- `docs/specification/provider-connection-boundary.md`

The current guarded Anthropic implementation is:

- `teo_reference.anthropic_adapter.AnthropicMessagesAdapter`
- `teo_reference.anthropic_adapter.execute_anthropic_canary_once`

The canary accepts only a dispatch already routed to Anthropic Claude Haiku 4.5 for `high_volume_simple`, and refuses high or critical risk before network execution.

## Finalize an executed result

```bash
teo --repo-root . finalize \
  /tmp/teo-dispatch.json \
  execution-result.json \
  verification-result.json \
  --audit-log /tmp/teo-audit.jsonl
```

Execution and verification records must reference the dispatch ID. The verifier must match the assigned verification implementation and must remain independent from the selected worker implementation.

## End-to-end demonstration

```bash
python reference/examples/run_example.py
```

## Tests

```bash
pytest
```
