# Google Gemini

**Provider ID:** `google`  
**Reviewed:** 2026-08-05  
**Evidence level:** provider documentation

## Access

Google publishes Gemini models through the Gemini API and Google AI Studio. The API also provides model-list and model-get methods for retrieving available identifiers and metadata.

## Version classes

Google distinguishes:

- `stable` models intended for production use
- `preview` models that may have tighter limits and shorter deprecation notice
- `latest` aliases that can change the underlying release
- `experimental` models that are not stable production targets

TEO should prefer a pinned stable identifier when the task requires predictable production behavior. Preview use must be visible in the dispatch record.

## Current family relevant to TEO

- Gemini 3.1 Pro Preview for advanced problem solving, agentic work, and coding
- Gemini 3.6 Flash as the current stable Flash implementation for agentic and multimodal tasks
- Gemini 3.5 Flash as a stable higher-intelligence Flash option
- Gemini 3.1 Flash-Lite as a stable cost-sensitive option

## Sources

- https://ai.google.dev/gemini-api/docs/models
- https://ai.google.dev/api/models

## Limitations

- Preview identifiers can be replaced or deprecated faster than stable identifiers.
- Provider descriptions are not TEO-observed quality measurements.
- Input modalities, tools, context limits, and output types vary by model and must be checked on the model-specific page.
