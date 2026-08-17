from __future__ import annotations

from pathlib import Path
import subprocess
import sys

MODULE = Path("reference/implementations/python/src/teo_reference/host_integration_protocol.py")
ORIGINAL = MODULE.read_text(encoding="utf-8")


def replace_once(text: str, old: str, new: str, name: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{name}: expected one mutation site, found {count}")
    return text.replace(old, new, 1)


mutants = [
    (
        "retry_budget_integer",
        '''        if (\n            isinstance(max_attempts_per_route, bool)\n            or not isinstance(max_attempts_per_route, int)\n            or max_attempts_per_route < 1\n        ):\n            raise HostIntegrationProtocolError(\n                "max_attempts_per_route must be a positive integer"\n            )\n''',
        '''        if isinstance(max_attempts_per_route, bool) or max_attempts_per_route < 1:\n            raise HostIntegrationProtocolError("max_attempts_per_route must be positive")\n''',
        "tests/test_host_integration_protocol.py::test_retry_budget_requires_positive_integer",
    ),
    (
        "receipt_attempt_integer",
        '''        if isinstance(receipt.attempt, bool) or not isinstance(receipt.attempt, int):\n            raise HostIntegrationProtocolError("execution receipt attempt must be an integer")\n''',
        "",
        "tests/test_host_integration_protocol.py::test_execution_receipt_boolean_attempt_is_rejected",
    ),
    (
        "single_outstanding_instruction",
        '''        if self._has_unresolved_execution():\n            raise HostIntegrationProtocolError(\n                "previous execution instruction remains unresolved"\n            )\n''',
        "",
        "tests/test_host_integration_protocol.py::test_outstanding_primary_retry_blocks_fallback_issue",
    ),
    (
        "monotonic_fallback",
        '''        if route_role == "primary" and self._fallback_was_issued():\n            raise HostIntegrationProtocolError(\n                "primary route is closed after fallback issuance"\n            )\n''',
        "",
        "tests/test_host_integration_protocol.py::test_fallback_transition_closes_primary_route_after_fallback_failure",
    ),
    (
        "terminal_phase_closure",
        '''        if self._issued_verification or self._verification_receipt is not None:\n            raise HostIntegrationProtocolError(\n                "execution phase is closed after verification has started"\n            )\n        if self._has_successful_execution():\n            raise HostIntegrationProtocolError(\n                "execution phase is closed after a successful execution receipt"\n            )\n        if route_role == "primary" and self._fallback_was_issued():\n            raise HostIntegrationProtocolError(\n                "primary route is closed after fallback issuance"\n            )\n''',
        "",
        "tests/test_host_integration_protocol.py::test_success_terminates_execution_phase_across_routes",
    ),
]

killed = []
try:
    for name, old, new, target in mutants:
        mutated = replace_once(ORIGINAL, old, new, name)
        MODULE.write_text(mutated, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", target],
            text=True,
            capture_output=True,
        )
        print(f"=== {name} ===")
        print(result.stdout)
        print(result.stderr)
        if result.returncode == 0:
            raise SystemExit(f"SURVIVED: {name} ({target})")
        killed.append(name)
        MODULE.write_text(ORIGINAL, encoding="utf-8")
finally:
    MODULE.write_text(ORIGINAL, encoding="utf-8")

if len(killed) != len(mutants):
    raise SystemExit(f"mutation campaign incomplete: {len(killed)}/{len(mutants)} killed")
print(f"MUTATION_CAMPAIGN_PASS: {len(killed)}/{len(mutants)} killed")
print("killed=" + ",".join(killed))
