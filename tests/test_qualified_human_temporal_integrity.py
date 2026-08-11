from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from teo_reference.provider_adapter import ProviderAdapterContractError
from teo_reference.qualified_human_approval import (
    evaluate_qualified_human_finalization,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
HELPERS_PATH = REPO_ROOT / "tests" / "test_qualified_human_approval.py"


def _load_helpers():
    spec = importlib.util.spec_from_file_location(
        "teo_qualified_human_test_helpers",
        HELPERS_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load qualified-human approval test helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


helpers = _load_helpers()


def test_initial_approval_disposition_cannot_predate_request() -> None:
    request = helpers.approval_request()
    grant = helpers.authority_grant()

    with pytest.raises(
        ProviderAdapterContractError,
        match="disposition cannot predate its approval request",
    ):
        helpers.approved_disposition(
            request=request,
            grant=grant,
            effective_at="2026-08-10T20:04:00+00:00",
        )


def test_human_finalization_cannot_predate_latest_disposition() -> None:
    dispatch = helpers.critical_dispatch()
    outcome = helpers.awaiting_human_outcome(dispatch)
    request = helpers.approval_request(dispatch=dispatch, outcome=outcome)
    grant = helpers.authority_grant()
    approved = helpers.approved_disposition(request=request, grant=grant)

    with pytest.raises(
        ProviderAdapterContractError,
        match="finalization cannot predate its current approval disposition",
    ):
        evaluate_qualified_human_finalization(
            dispatch,
            outcome,
            request,
            [approved],
            authority_grants=[grant],
            repo_root=REPO_ROOT,
            finalized_at="2026-08-10T20:06:00+00:00",
        )
