"""Backward-compatible provider import path; implementation lives in adapters.providers.anthropic."""

from .adapters.providers.anthropic import *  # noqa: F401,F403
from .adapters.providers.anthropic import (
    _safe_artifact_name,
    _decode_json,
    _error_details,
    _failure_scope,
    _extract_text,
    _provider_model_matches,
    _non_negative_int,
    _extract_usage,
)
