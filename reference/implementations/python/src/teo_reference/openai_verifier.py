"""Backward-compatible live verifier path; implementation lives in adapters.verifiers.openai."""

from .adapters.verifiers.openai import *  # noqa: F401,F403
from .adapters.verifiers.openai import _decode_json, _extract_output_text
