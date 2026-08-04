# Local models through Ollama

**Provider ID:** `local_ollama`  
**Reviewed:** 2026-08-05  
**Evidence level:** runtime documentation

## Access

Ollama supports local execution on macOS, Windows, and Linux. Its local API is served by default at:

```text
http://localhost:11434/api
```

Ollama also documents an optional cloud API. TEO treats local and cloud execution as separate deployment contexts because their privacy, latency, availability, and governance properties differ.

## TEO use

Local models may be selected for:

- private or offline execution
- economical throughput
- local coding fallback
- workloads where data egress is restricted
- reproducible testing against a pinned model and quantization

## Sources

- https://docs.ollama.com/quickstart
- https://docs.ollama.com/api/introduction

## Limitations

- `local` is not a capability claim. Quality depends on the selected model, model version, quantization, context configuration, hardware, runtime, and tool integration.
- Model tags can change unless a digest or immutable artifact is recorded.
- Local execution does not remove the need for verification, authorization, logging, or safety controls.
- Hardware resource limits must be included in the dispatch context.
