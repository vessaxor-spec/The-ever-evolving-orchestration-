# TEO Python Reference Router

This is the runnable reference control plane for The Ever-Evolving Orchestration. It reads TEO's YAML policy and registries, creates a structured dispatch, assigns an independent verifier, and records a final evidence-bearing outcome.

The router itself remains provider-neutral. Live provider execution is optional and occurs only through the provider-adapter boundary after routing has already selected the authorized provider family, model, and reasoning effort.

The guarded live canary supports three provider families for `high_volume_simple` tasks at low or medium risk:

- Anthropic Claude Haiku 4.5
- OpenAI GPT-5.6 Luna
- Google Gemini 3.6 Flash

Each adapter performs one attempt only. Adapters do not own fallback, retry, verification, escalation, or human approval.

The runtime coordinator can perform one guarded automatic fallback after a `model` or `provider` failure. It returns the failure to TEO, applies the failed model or provider block, creates a new dispatch ID, assigns a fresh independent verifier, and then executes the newly selected provider once. Request, transient, and capability failures do not trigger this fallback, and a failed fallback never chains automatically to a third provider.

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

1. TEO routing authorizes a provider family, model, and reasoning effort through `ProviderExecutionRequest`.
2. Runtime supplies a provider-specific `ProviderConnection` without exposing credential material to the dispatch or audit record.

The general contracts are documented in:

- `docs/specification/provider-adapter-contract.md`
- `docs/specification/provider-connection-boundary.md`
- `docs/specification/guarded-canary-fallback.md`

Current guarded implementations are:

- `teo_reference.anthropic_adapter.AnthropicMessagesAdapter`
- `teo_reference.openai_adapter.OpenAIResponsesAdapter`
- `teo_reference.google_adapter.GeminiInteractionsAdapter`

Single-attempt convenience helpers are:

- `execute_anthropic_canary_once`
- `execute_openai_canary_once`
- `execute_gemini_canary_once`

The guarded orchestration helper is:

- `execute_guarded_canary`

OpenAI maps TEO effort to Responses API `reasoning.effort`. Gemini maps it to Interactions API `generation_config.thinking_level`. Claude Haiku 4.5 does not support Anthropic's newer `output_config.effort` parameter, so the adapter does not invent one.

All canaries refuse high or critical risk before provider execution.

A successful provider execution is not a completed TEO outcome. Independent verification, and qualified human approval when required, remain separate gates.

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
