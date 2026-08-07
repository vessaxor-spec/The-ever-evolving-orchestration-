from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from teo_reference.config import ConfigBundle


REPO_ROOT = Path(__file__).resolve().parents[1]


def issues_after(mutator) -> list[str]:
    bundle = ConfigBundle.load(REPO_ROOT)
    mutator(bundle)
    return bundle.validate()


def test_route_model_reference_must_exist_in_canonical_registry() -> None:
    issues = issues_after(
        lambda bundle: bundle.routing["routing"]["daily_coding"]["primary"].update(
            {"model": "model-that-does-not-exist"}
        )
    )
    assert any(
        issue.startswith("ERROR:")
        and "daily_coding.primary" in issue
        and "unregistered model" in issue
        for issue in issues
    )


def test_models_yaml_provider_must_match_canonical_model_evidence() -> None:
    issues = issues_after(
        lambda bundle: bundle.models["models"]["gemini-flash"].update(
            {"provider_family": "anthropic"}
        )
    )
    assert any(
        issue.startswith("ERROR:")
        and "gemini-3.6-flash provider mismatch" in issue
        for issue in issues
    )


def test_declared_reasoning_effort_must_be_supported_when_registry_lists_levels() -> None:
    issues = issues_after(
        lambda bundle: bundle.routing["routing"]["multimodal_analysis"]["primary"].update(
            {"reasoning": "xhigh"}
        )
    )
    assert any(
        issue.startswith("ERROR:")
        and "multimodal_analysis.primary" in issue
        and "unsupported reasoning effort xhigh" in issue
        for issue in issues
    )


def test_route_must_retain_an_explicit_provider_diverse_verifier_candidate() -> None:
    def mutate(bundle: ConfigBundle) -> None:
        route = bundle.routing["routing"]["daily_coding"]
        route["semantic_reviewer"] = {
            "agent": "codex",
            "model": "gpt-5.6-sol",
            "profile": "sol",
            "reasoning": "high",
        }
        route["executable_verifier"] = {
            "agent": "codex",
            "model": "gpt-5.6-terra",
            "profile": "terra",
            "reasoning": "medium",
        }

    issues = issues_after(mutate)
    assert any(
        issue == "ERROR: route daily_coding has no explicit model- and provider-diverse verifier candidate"
        for issue in issues
    )


def test_clean_repository_configuration_has_no_errors() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    assert not [issue for issue in bundle.validate() if issue.startswith("ERROR:")]
