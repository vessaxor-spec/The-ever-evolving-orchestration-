from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"Expected exactly one match in {path}, found {count}: {old[:80]!r}"
        )
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


# TEO-M1: make policy-driven preview-primary skips visible in the dispatch audit trail.
replace_once(
    "reference/implementations/python/src/teo_reference/engine.py",
    "        primary = self._resolve_primary(task_type, worker, task)\n",
    "        primary = self._resolve_primary(task_type, worker, task)\n"
    "        primary_policy_warning = self._primary_policy_warning(task_type, worker, task, primary)\n",
)
replace_once(
    "reference/implementations/python/src/teo_reference/engine.py",
    "        warnings = []\n",
    "        warnings = [primary_policy_warning] if primary_policy_warning else []\n",
)
helper = '''    def _primary_policy_warning(
        self,
        task_type: str,
        worker: str,
        task: TaskRequest,
        selected: ImplementationChoice,
    ) -> str | None:
        route = self.config.implementation_routes.get(task_type, {})
        for key in ROUTE_IMPLEMENTATION_KEYS.get(task_type, ("primary",)):
            candidate = route.get(key)
            if not isinstance(candidate, dict) or not candidate.get("model"):
                continue
            choice = self._choice(candidate, f"routing.{task_type}.{key}")
            if choice.model == selected.model:
                return None
            preview_was_only_policy_block = (
                choice.availability == "preview"
                and choice.model not in task.constraints.accepted_preview_models
                and choice.model not in task.constraints.blocked_implementations
                and (
                    not choice.provider_family
                    or choice.provider_family not in task.constraints.blocked_providers
                )
                and self._worker_allows_model(worker, choice)
            )
            if preview_was_only_policy_block:
                return (
                    f"Declared primary {choice.model} was skipped because preview implementations "
                    "require explicit acceptance via constraints.accepted_preview_models."
                )
            return None
        return None

'''
replace_once(
    "reference/implementations/python/src/teo_reference/engine.py",
    "    def _resolve_primary(self, task_type: str, worker: str, task: TaskRequest) -> ImplementationChoice:\n",
    helper
    + "    def _resolve_primary(self, task_type: str, worker: str, task: TaskRequest) -> ImplementationChoice:\n",
)

# TEO-L4: make repeatability agreement a true pairwise agreement metric.
replace_once(
    "reference/implementations/python/src/teo_reference/verifier_calibration.py",
    "        counts = Counter(statuses)\n"
    "        repeatability_scores.append(max(counts.values()) / len(statuses))\n",
    "        counts = Counter(statuses)\n"
    "        total_pairs = len(statuses) * (len(statuses) - 1) // 2\n"
    "        agreeing_pairs = sum(count * (count - 1) // 2 for count in counts.values())\n"
    "        repeatability_scores.append(agreeing_pairs / total_pairs)\n",
)
replace_once(
    "tests/test_verifier_calibration.py",
    "    assert report.repeatability_agreement_rate == pytest.approx(2 / 3)\n",
    "    assert report.repeatability_agreement_rate == pytest.approx(1 / 3)\n",
)

# TEO-L1: keep classifier/interpreter metadata outside the selectable task-type map.
routing_path = Path("policy/routing/routing.yaml")
routing_text = routing_path.read_text(encoding="utf-8")
start = routing_text.index("  task_routing:\n")
end = routing_text.index("\nfallback_order:\n", start)
block = routing_text[start:end]
dedented = "\n".join(
    line[2:] if line.startswith("  ") else line for line in block.splitlines()
) + "\n\n"
routing_text = routing_text[:start] + routing_text[end + 1 :]
insertion = routing_text.index("routing:\n")
routing_text = routing_text[:insertion] + dedented + routing_text[insertion:]
routing_text = routing_text.replace("version: 0.5\n", "version: 0.6\n", 1)
routing_text = routing_text.replace(
    "reviewed_at: 2026-08-07\n", "reviewed_at: 2026-08-09\n", 1
)
routing_path.write_text(routing_text, encoding="utf-8")

# TEO-L2/L3: make intentional unrouted status explicit and register the current Flash-Lite candidate.
registry_path = Path("registry/models/models.yaml")
registry = registry_path.read_text(encoding="utf-8")
registry = registry.replace(
    "version: 0.2\nstatus: public\nreviewed_at: 2026-08-07\n",
    "version: 0.3\nstatus: public\nreviewed_at: 2026-08-09\n",
    1,
)
registry = registry.replace(
    "    teo_routing_role: candidate critical escalation implementation\n"
    "    input_modalities: [text, image]\n",
    "    teo_routing_role: candidate critical escalation implementation\n"
    "    routing_status: registered_unrouted\n"
    "    routing_status_reason: retained for evidence-based escalation evaluation; not promoted by release recency alone\n"
    "    input_modalities: [text, image]\n",
    1,
)
anchor = '''  gemini-3.5-flash:
    provider: google
    availability: stable
    provider_description: sustained frontier performance on agentic and coding tasks
    teo_routing_role: candidate higher-intelligence Flash implementation
    evidence_type: provider_claim
    source: https://ai.google.dev/gemini-api/docs/models

'''
addition = anchor + '''  gemini-3.5-flash-lite:
    provider: google
    availability: stable
    provider_description: fastest and lowest-cost Gemini 3.5 model for high-throughput execution
    teo_routing_role: candidate economical throughput implementation
    routing_status: registered_unrouted
    routing_status_reason: evaluate against current Luna and Flash throughput routes before adoption
    evidence_type: provider_claim
    source: https://ai.google.dev/gemini-api/docs/latest-model

'''
if registry.count(anchor) != 1:
    raise SystemExit("Gemini 3.5 Flash registry anchor drifted")
registry = registry.replace(anchor, addition, 1)
replace_target = (
    "    teo_routing_role: candidate economical throughput implementation\n"
    "    evidence_type: provider_claim\n"
    "    source: https://ai.google.dev/gemini-api/docs/models\n\n"
    "  local-model:\n"
)
replace_value = (
    "    teo_routing_role: candidate economical throughput implementation\n"
    "    routing_status: previous_generation_candidate\n"
    "    lifecycle_note: retained for compatibility evidence while Gemini 3.5 Flash-Lite is evaluated\n"
    "    evidence_type: provider_claim\n"
    "    source: https://ai.google.dev/gemini-api/docs/models\n\n"
    "  local-model:\n"
)
if registry.count(replace_target) != 1:
    raise SystemExit("Gemini 3.1 Flash-Lite registry anchor drifted")
registry = registry.replace(replace_target, replace_value, 1)
registry_path.write_text(registry, encoding="utf-8")

models_path = Path("models.yaml")
models_text = models_path.read_text(encoding="utf-8")
models_text = models_text.replace(
    "version: 0.3\nstatus: public-draft\nreviewed_at: 2026-08-05\n",
    "version: 0.4\nstatus: public-draft\nreviewed_at: 2026-08-09\n",
    1,
)
models_text = models_text.replace(
    "    role: candidate maximum-capability escalation\n    profile: sol\n",
    "    role: candidate maximum-capability escalation\n"
    "    routing_status: registered_unrouted\n"
    "    profile: sol\n",
    1,
)
models_path.write_text(models_text, encoding="utf-8")

Path("tests/test_preview_and_routing_shape.py").write_text(
    '''from pathlib import Path

from teo_reference.config import ConfigBundle
from teo_reference.engine import OrchestrationEngine
from teo_reference.schemas import TaskRequest


REPO_ROOT = Path(__file__).resolve().parents[1]


def engine() -> OrchestrationEngine:
    return OrchestrationEngine(ConfigBundle.load(REPO_ROOT))


def test_preview_primary_skip_is_visible_in_dispatch_warnings() -> None:
    dispatch = engine().dispatch(
        TaskRequest.from_dict(
            {
                "task": "Research and compare the current evidence.",
                "task_type": "deep_research",
                "risk_level": "low",
            }
        )
    )
    assert dispatch.selected_implementation.model == "claude-sonnet-5"
    assert any(
        "gemini-3.1-pro-preview" in warning
        and "accepted_preview_models" in warning
        for warning in dispatch.warnings
    )


def test_explicit_preview_acceptance_selects_declared_primary_without_skip_warning() -> None:
    dispatch = engine().dispatch(
        TaskRequest.from_dict(
            {
                "task": "Research and compare the current evidence.",
                "task_type": "deep_research",
                "risk_level": "low",
                "constraints": {
                    "accepted_preview_models": ["gemini-3.1-pro-preview"],
                },
            }
        )
    )
    assert dispatch.selected_implementation.model == "gemini-3.1-pro-preview"
    assert not any("was skipped" in warning for warning in dispatch.warnings)


def test_task_routing_metadata_is_not_a_selectable_implementation_route() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    assert "task_routing" not in bundle.implementation_routes
    assert isinstance(bundle.routing.get("task_routing"), dict)
    expected = set(bundle.team_routes) - {"release"}
    assert set(bundle.implementation_routes) == expected
''',
    encoding="utf-8",
)

research = Path("research/models/2026-08-09-diagnostic-model-freshness.md")
research.parent.mkdir(parents=True, exist_ok=True)
research.write_text(
    '''# Diagnostic model freshness review — 2026-08-09

## Decision

The diagnostic freshness observations are valid review triggers, not automatic routing changes.

- `claude-fable-5` remains registered but intentionally unrouted. Current Anthropic documentation identifies Fable 5 as its highest-capability widely released model, but TEO requires role-fit evidence before changing an established escalation route.
- `gemini-3.5-flash-lite` is added to the canonical evidence registry as a stable, registered-unrouted economical-throughput candidate. Current Google documentation positions it as the fastest and lowest-cost Gemini 3.5 model for high-throughput execution.
- `gemini-3.1-flash-lite` is retained as a previous-generation candidate while migration evidence is evaluated.
- No primary, fallback, verifier, calibration, or canary route is changed by this review.

## Primary sources

- Anthropic Claude models overview: https://platform.claude.com/docs/en/about-claude/models/overview
- Google Gemini latest models: https://ai.google.dev/gemini-api/docs/latest-model

## Acceptance rule

A newer model may enter the registry because it exists and is relevant. It may enter an active route only after capability fit, reasoning controls, availability, fallback/verifier independence, operational evidence, and regression risk are evaluated.
''',
    encoding="utf-8",
)

# Remove this one-shot script from the resulting remediation commit.
Path(__file__).unlink()
