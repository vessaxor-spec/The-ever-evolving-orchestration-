"""Backward-compatible provider import path; implementation lives in adapters.providers.openai."""

from .adapters.providers.openai import *  # noqa: F401,F403
from .adapters.providers.openai import (
    _safe_artifact_name,
    _decode_json,
    _extract_text,
    _error_details,
    _failure_scope,
    _non_negative_int,
    _extract_usage,
)
