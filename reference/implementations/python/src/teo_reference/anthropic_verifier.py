"""Backward-compatible live verifier path; implementation lives in adapters.verifiers.anthropic."""

from .adapters.verifiers.anthropic import *  # noqa: F401,F403
from .adapters.verifiers.anthropic import _decode_json, _extract_text, _extract_usage
