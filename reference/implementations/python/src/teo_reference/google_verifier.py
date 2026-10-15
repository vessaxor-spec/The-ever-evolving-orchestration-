"""Backward-compatible live verifier path; implementation lives in adapters.verifiers.google."""

from .adapters.verifiers.google import *  # noqa: F401,F403
from .adapters.verifiers.google import _decode_json, _extract_text, _extract_usage
