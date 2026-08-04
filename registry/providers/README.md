# Provider Registry

Public provider metadata, access modes, tool support, and provider-level constraints.

Provider claims must cite current primary sources. Provider access does not establish that a model is suitable for a task.

## Registry

- [`providers.yaml`](providers.yaml) is the machine-readable provider index.
- [`openai.md`](openai.md) documents OpenAI access and current routing-relevant families.
- [`anthropic.md`](anthropic.md) documents Anthropic access and current routing-relevant families.
- [`google.md`](google.md) documents Gemini access and model version classes.
- [`local-ollama.md`](local-ollama.md) documents local execution through Ollama.

## Required provider fields

A provider entry should identify:

- provider ID and display name
- access modes
- official model catalog or metadata endpoint
- documented tool and modality support
- regional, platform, or account constraints when material
- date reviewed
- primary sources
- limitations and unresolved evidence

Provider entries should be reviewed whenever a routing default changes or official availability information becomes stale.
