from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PACKAGE = REPO_ROOT / "reference" / "implementations" / "python" / "src" / "teo_reference"


@dataclass(frozen=True, slots=True)
class MutationProbe:
    name: str
    source_file: str
    old: str
    new: str
    pytest_targets: tuple[str, ...]


MUTATIONS = (
    MutationProbe(
        name="disposition_cannot_predate_request",
        source_file="qualified_human_approval.py",
        old="if effective_at < requested_at:",
        new="if False and effective_at < requested_at:",
        pytest_targets=(
            "tests/test_qualified_human_temporal_integrity.py::test_initial_approval_disposition_cannot_predate_request",
        ),
    ),
    MutationProbe(
        name="finalization_cannot_predate_current_disposition",
        source_file="qualified_human_approval.py",
        old="if latest is not None and finalized < _parse_datetime(",
        new="if False and latest is not None and finalized < _parse_datetime(",
        pytest_targets=(
            "tests/test_qualified_human_temporal_integrity.py::test_human_finalization_cannot_predate_latest_disposition",
        ),
    ),
    MutationProbe(
        name="authority_grant_must_cover_effective_risk",
        source_file="qualified_human_approval.py",
        old='if request_data["effective_risk"] not in grant_data["scope"]["risk_levels"]:',
        new='if False and request_data["effective_risk"] not in grant_data["scope"]["risk_levels"]:',
        pytest_targets=(
            "tests/test_qualified_human_approval.py::test_out_of_scope_authority_grant_fails_closed",
        ),
    ),
    MutationProbe(
        name="finalization_revalidates_exact_dispatch_binding",
        source_file="qualified_human_approval.py",
        old='if request_data["dispatch_sha256"] != _canonical_sha256(dispatch.to_dict()):',
        new='if False and request_data["dispatch_sha256"] != _canonical_sha256(dispatch.to_dict()):',
        pytest_targets=(
            "tests/test_qualified_human_approval.py::test_finalization_revalidates_exact_dispatch_and_route_outcome_binding",
        ),
    ),
    MutationProbe(
        name="approval_is_expired_at_exact_expiry_instant",
        source_file="qualified_human_approval.py",
        old="if finalized >= expiry:",
        new="if finalized > expiry:",
        pytest_targets=(
            "tests/test_qualified_human_approval.py::test_approved_disposition_expires_fail_closed_without_rewriting_history",
        ),
    ),
    MutationProbe(
        name="request_is_expired_at_exact_expiry_instant",
        source_file="qualified_human_approval.py",
        old='if at >= _parse_datetime(request_data["expires_at"], "approval request expires_at"):',
        new='if at > _parse_datetime(request_data["expires_at"], "approval request expires_at"):',
        pytest_targets=(
            "tests/test_qualified_human_approval.py::test_request_expiry_is_explicit_and_system_only",
        ),
    ),
    MutationProbe(
        name="authority_grant_is_invalid_at_valid_until",
        source_file="qualified_human_approval.py",
        old="if at < valid_from or (valid_until is not None and at >= valid_until):",
        new="if at < valid_from or (valid_until is not None and at > valid_until):",
        pytest_targets=(
            "tests/test_qualified_human_approval.py::test_out_of_scope_authority_grant_fails_closed",
            "tests/test_qualified_human_approval.py::test_approval_cannot_outlive_request_or_authority_grant",
        ),
    ),
    MutationProbe(
        name="fallback_redispatch_preserves_active_effective_risk",
        source_file="runtime_canary.py",
        old="task_type=dispatch.task_type,\n        risk_level=dispatch.risk_level,\n        domain=task.domain,",
        new="task_type=dispatch.task_type,\n        risk_level=task.risk_level,\n        domain=task.domain,",
        pytest_targets=(
            "tests/test_recovery_authority_integrity.py::test_failure_redispatch_preserves_risk_and_human_authority_requirement",
        ),
    ),
    MutationProbe(
        name="fallback_redispatch_preserves_explicit_human_approval_constraint",
        source_file="runtime_canary.py",
        old="require_human_approval=task.constraints.require_human_approval,",
        new="require_human_approval=False,",
        pytest_targets=(
            "tests/test_recovery_authority_integrity.py::test_failure_redispatch_preserves_risk_and_human_authority_requirement",
        ),
    ),
    MutationProbe(
        name="circuit_preparation_preserves_explicit_human_approval_constraint",
        source_file="runtime_circuit_breaker.py",
        old="require_human_approval=task.constraints.require_human_approval,",
        new="require_human_approval=False,",
        pytest_targets=(
            "tests/test_recovery_authority_integrity.py::test_circuit_recovery_only_adds_provider_blocks_without_lowering_authority",
        ),
    ),
)


def _run_mutant(probe: MutationProbe, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    mutant_root = tmp_path / probe.name
    mutant_package = mutant_root / "teo_reference"
    shutil.copytree(SOURCE_PACKAGE, mutant_package)

    source_path = mutant_package / probe.source_file
    source = source_path.read_text(encoding="utf-8")
    occurrences = source.count(probe.old)
    assert occurrences == 1, (
        f"Mutation {probe.name} expected exactly one source match in {probe.source_file}; "
        f"found {occurrences}"
    )
    source_path.write_text(source.replace(probe.old, probe.new, 1), encoding="utf-8")

    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        part
        for part in (str(mutant_root), environment.get("PYTHONPATH", ""))
        if part
    )
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *probe.pytest_targets],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


@pytest.mark.parametrize("probe", MUTATIONS, ids=lambda probe: probe.name)
def test_targeted_control_integrity_mutants_are_killed(
    probe: MutationProbe,
    tmp_path: Path,
) -> None:
    result = _run_mutant(probe, tmp_path)
    output = "\n".join(part for part in (result.stdout, result.stderr) if part)
    assert result.returncode != 0, (
        f"SURVIVING MUTANT: {probe.name}. The targeted regression suite stayed green after "
        f"weakening {probe.source_file}.\n{output}"
    )
