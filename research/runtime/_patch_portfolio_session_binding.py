from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


module_path = Path("research/runtime/host_integration_portfolio_authority_separation.py")
module = module_path.read_text(encoding="utf-8")
module = replace_once(
    module,
    """class _AdmissionState:\n    task_id: str\n    task_digest: str\n    admission_revision: int\n    active: bool = True\n    claimed: bool = False\n""",
    """class _AdmissionState:\n    task_id: str\n    task_digest: str\n    admission_revision: int\n    active: bool = True\n    claimed: bool = False\n    session_id: str | None = None\n""",
    "admission state session binding",
)
module = replace_once(
    module,
    """            admission.claimed = True\n            return AdmittedTaskSession(\n                session_id=f\"teo-session-{secrets.token_hex(12)}\",\n                portfolio_id=self.portfolio_id,\n""",
    """            session_id = f\"teo-session-{secrets.token_hex(12)}\"\n            admission.claimed = True\n            admission.session_id = session_id\n            return AdmittedTaskSession(\n                session_id=session_id,\n                portfolio_id=self.portfolio_id,\n""",
    "issued session identity",
)
module = replace_once(
    module,
    """            if not admission.claimed:\n                raise PortfolioAuthorityError(\"session admission was never claimed\")\n            if admission.task_id != parsed_session.task_id:\n""",
    """            if not admission.claimed:\n                raise PortfolioAuthorityError(\"session admission was never claimed\")\n            if admission.session_id != parsed_session.session_id:\n                raise PortfolioAuthorityError(\"session identity does not match issued host session\")\n            if admission.task_id != parsed_session.task_id:\n""",
    "session revalidation identity check",
)
module_path.write_text(module, encoding="utf-8")


test_path = Path("tests/test_host_integration_portfolio_authority_separation.py")
tests = test_path.read_text(encoding="utf-8")
insert_before = """def test_session_binding_tamper_is_rejected_on_revalidation() -> None:\n"""
new_test = """def test_fabricated_session_identity_is_rejected_on_revalidation() -> None:\n    authority = HostPortfolioAuthority()\n    payload = task()\n    grant, gateway = admit(authority, payload)\n    session = gateway.claim(request(grant), grant, payload).to_dict()\n    session[\"session_id\"] = \"teo-session-fabricated\"\n\n    with pytest.raises(PortfolioAuthorityError, match=\"session identity\"):\n        gateway.revalidate(session, payload)\n\n\n"""
tests = replace_once(
    tests,
    insert_before,
    new_test + insert_before,
    "fabricated session identity test",
)
test_path.write_text(tests, encoding="utf-8")


note_path = Path("research/runtime/host-integration-portfolio-authority-separation-2026-08-15.md")
note = note_path.read_text(encoding="utf-8")
note = replace_once(
    note,
    "- session binding tamper; and\n",
    "- fabricated or substituted session identity during revalidation;\n- session binding tamper; and\n",
    "session identity adversarial case",
)
note = replace_once(
    note,
    "TEO can claim that exact admission once and revalidate the resulting task session. The TEO-facing gateway exposes no operation for queue creation, task selection, admission, prioritization, cancellation, revocation, or portfolio inspection.\n",
    "TEO can claim that exact admission once and revalidate the resulting task session. Revalidation is bound to the exact host-issued session identity so a fabricated session record cannot impersonate an already-claimed admission through the conformant gateway. The TEO-facing gateway exposes no operation for queue creation, task selection, admission, prioritization, cancellation, revocation, or portfolio inspection.\n",
    "research claim session identity",
)
note_path.write_text(note, encoding="utf-8")
