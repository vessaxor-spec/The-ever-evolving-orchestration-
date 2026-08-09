from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"expected exactly one match in {path}, found {text.count(old)}")
    p.write_text(text.replace(old, new), encoding="utf-8")


# 1) Promote stable Gemini 3.6 Flash as the routine coding fallback instead of preview Pro.
replace_once(
    "policy/routing/routing.yaml",
    """  daily_coding:\n    primary:\n      agent: codex\n      model: gpt-5.6-terra\n      profile: terra\n      reasoning: medium\n    planning_support:\n      agent: codex\n      model: gpt-5.6-sol\n      profile: sol\n      reasoning: medium\n      use_when:\n        - implementation_spans_multiple_components\n        - requirements_are_ambiguous\n        - architectural_constraints_are_present\n    fallback:\n      agent: agy\n      model: gemini-3.1-pro-preview\n      profile: sol\n      reasoning: medium\n""",
    """  daily_coding:\n    primary:\n      agent: codex\n      model: gpt-5.6-terra\n      profile: terra\n      reasoning: medium\n    planning_support:\n      agent: codex\n      model: gpt-5.6-sol\n      profile: sol\n      reasoning: medium\n      use_when:\n        - implementation_spans_multiple_components\n        - requirements_are_ambiguous\n        - architectural_constraints_are_present\n    fallback:\n      agent: agy\n      model: gemini-3.6-flash\n      profile: terra\n      reasoning: medium\n      purpose: preserve stable cross-provider coding execution without requiring preview acceptance\n""",
)

# 2) Move bounded throughput to the current stable Flash-Lite generation.
replace_once(
    "policy/routing/routing.yaml",
    """  high_volume_simple:\n    primary:\n      agent: claude\n      model: claude-haiku-4-5\n      profile: luna\n      reasoning: low\n    fallback:\n      agent: agy\n      model: gemini-3.6-flash\n      profile: luna\n      reasoning: low\n      purpose: continue high-volume work when the Anthropic route is unavailable\n    alternatives:\n      - agent: agy\n        model: gemini-3.6-flash\n        profile: luna\n      - agent: codex\n        model: gpt-5.6-luna\n        profile: luna\n    verifier:\n      agent: agy\n      model: gemini-3.6-flash\n      profile: luna\n      reasoning: medium\n      purpose: provider-diverse pointwise validation of bounded high-volume output\n    semantic_reviewer:\n      agent: claude\n      model: claude-sonnet-5\n      profile: sol\n      reasoning: medium\n      purpose: fresh semantic verification when Gemini becomes the model-fallback executor\n    technical_verifier:\n      agent: codex\n      model: gpt-5.6-sol\n      profile: sol\n      reasoning: medium\n      purpose: fresh provider-diverse verification when Anthropic is unavailable\n""",
    """  high_volume_simple:\n    primary:\n      agent: agy\n      model: gemini-3.5-flash-lite\n      profile: luna\n      reasoning: low\n      purpose: current stable low-cost high-throughput execution\n    fallback:\n      agent: claude\n      model: claude-haiku-4-5\n      profile: luna\n      reasoning: low\n      purpose: preserve provider-diverse bounded language throughput when the Google route is unavailable\n    alternatives:\n      - agent: codex\n        model: gpt-5.6-luna\n        profile: luna\n      - agent: agy\n        model: gemini-3.6-flash\n        profile: luna\n    verifier:\n      agent: claude\n      model: claude-haiku-4-5\n      profile: luna\n      reasoning: default\n      purpose: provider-diverse pointwise validation of the primary Flash-Lite route\n    semantic_reviewer:\n      agent: agy\n      model: gemini-3.6-flash\n      profile: luna\n      reasoning: medium\n      purpose: fresh provider-diverse verification when Haiku becomes the model-fallback executor and Google remains eligible\n    technical_verifier:\n      agent: codex\n      model: gpt-5.6-sol\n      profile: sol\n      reasoning: medium\n      purpose: fresh provider-diverse verification when Google is unavailable or a stronger independent check is required\n""",
)

# 3) Update generic throughput fallback order to prefer the new stable Flash-Lite lane.
replace_once(
    "policy/routing/routing.yaml",
    """  throughput:\n    - agent: agy\n      model: gemini-3.6-flash\n    - agent: codex\n      model: gpt-5.6-luna\n    - agent: claude\n      model: claude-haiku-4-5\n""",
    """  throughput:\n    - agent: agy\n      model: gemini-3.5-flash-lite\n    - agent: claude\n      model: claude-haiku-4-5\n    - agent: codex\n      model: gpt-5.6-luna\n    - agent: agy\n      model: gemini-3.6-flash\n""",
)

# 4) Specialist throughput template follows the same primary/fallback/verifier discipline.
replace_once(
    "policy/routing/specialist-model-routing.yaml",
    """  luna_throughput:\n    primary:\n      agent: codex\n      model: gpt-5.6-luna\n      reasoning_by_risk:\n        low: low\n        medium: medium\n        high: high\n        critical: high\n    fallback:\n      agent: claude\n      model: claude-haiku-4-5\n      reasoning: default\n    verifier:\n      agent: agy\n      model: gemini-3.6-flash\n      reasoning_by_risk:\n        low: low\n        medium: medium\n        high: high\n        critical: high\n""",
    """  luna_throughput:\n    primary:\n      agent: agy\n      model: gemini-3.5-flash-lite\n      reasoning_by_risk:\n        low: low\n        medium: medium\n        high: high\n        critical: high\n    fallback:\n      agent: claude\n      model: claude-haiku-4-5\n      reasoning: default\n    verifier:\n      agent: codex\n      model: gpt-5.6-luna\n      reasoning_by_risk:\n        low: low\n        medium: medium\n        high: high\n        critical: high\n""",
)

# 5) Fable becomes a narrow frontier escalation after established Opus/Sol routes prove insufficient.
replace_once(
    "policy/routing/specialist-model-routing.yaml",
    """    conditional_effort_escalation:\n      model: claude-opus-5\n      reasoning: max\n      use_when:\n      - unresolved_material_disagreement\n      - critical_cross_system_ambiguity\n      - quality_gain_is_decision_relevant\n""",
    """    conditional_effort_escalation:\n      model: claude-fable-5\n      reasoning: max\n      use_when:\n      - unresolved_material_disagreement_after_opus_review\n      - critical_cross_system_ambiguity_after_standard_escalation\n      - long_horizon_agentic_reasoning_where_quality_gain_is_decision_relevant\n""",
)

# 6) Mission Control orchestration gets the same narrow frontier lane; routine MC routes remain unchanged.
replace_once(
    "policy/routing/mission-control-routing.yaml",
    """    escalation:\n      agent: claude\n      model: claude-opus-5\n      profile: sol\n      reasoning: high\n      use_when:\n        - production_side_effect\n        - irreversible_action\n        - security_sensitive_operation\n        - authority_violation\n        - unresolved_pipeline_loop\n""",
    """    escalation:\n      agent: claude\n      model: claude-opus-5\n      profile: sol\n      reasoning: high\n      use_when:\n        - production_side_effect\n        - irreversible_action\n        - security_sensitive_operation\n        - authority_violation\n    frontier_escalation:\n      agent: claude\n      model: claude-fable-5\n      profile: sol\n      reasoning: max\n      use_when:\n        - unresolved_pipeline_loop_after_opus_review\n        - long_horizon_agentic_orchestration_remains_inconclusive\n        - cross_system_authority_conflict_remains_unresolved\n""",
)

# 7) Canonical aliases/registry: Flash-Lite is now routed; Fable is narrowly routed as escalation.
replace_once(
    "models.yaml",
    """  gemini-flash:\n    provider_family: google\n    concrete_model: gemini-3.6-flash\n    availability: stable\n    role: fast mapping and multimodal processing\n    profile: luna\n""",
    """  gemini-flash:\n    provider_family: google\n    concrete_model: gemini-3.6-flash\n    availability: stable\n    role: fast mapping, agentic execution, coding fallback, and multimodal processing\n    profile: luna\n""",
)

insert_after = """    limitations:\n      - escalate consequential synthesis to a stronger reasoning model\n\n"""
addition = """  gemini-flash-lite:\n    provider_family: google\n    concrete_model: gemini-3.5-flash-lite\n    availability: stable\n    role: primary economical high-volume execution\n    profile: luna\n    preferred_for:\n      - extraction\n      - classification\n      - structured transformation\n      - document parsing\n      - simple high-volume work\n    limitations:\n      - escalate ambiguity and consequential synthesis to a stronger reasoning route\n      - preserve provider-diverse verification\n\n"""
p = Path("models.yaml")
text = p.read_text(encoding="utf-8")
if addition not in text:
    marker_index = text.index(insert_after, text.index("  gemini-flash:")) + len(insert_after)
    text = text[:marker_index] + addition + text[marker_index:]
p.write_text(text, encoding="utf-8")

replace_once(
    "models.yaml",
    """    role: candidate maximum-capability escalation\n    routing_status: registered_unrouted\n""",
    """    role: narrow maximum-capability frontier escalation\n    routing_status: routed_frontier_escalation\n""",
)

replace_once(
    "registry/models/models.yaml",
    """    teo_routing_role: candidate critical escalation implementation\n    routing_status: registered_unrouted\n    routing_status_reason: retained for evidence-based escalation evaluation; not promoted by release recency alone\n""",
    """    teo_routing_role: narrow frontier escalation after established high-consequence routes remain inconclusive\n    routing_status: routed_frontier_escalation\n    routing_status_reason: used only for unresolved long-horizon or cross-system escalation where added capability justifies higher cost and latency\n""",
)

replace_once(
    "registry/models/models.yaml",
    """  gemini-3.5-flash-lite:\n    provider: google\n    availability: stable\n    provider_description: fastest and lowest-cost Gemini 3.5 model for high-throughput execution\n    teo_routing_role: candidate economical throughput implementation\n    routing_status: registered_unrouted\n    routing_status_reason: evaluate against current Luna and Flash throughput routes before adoption\n    evidence_type: provider_claim\n    source: https://ai.google.dev/gemini-api/docs/latest-model\n""",
    """  gemini-3.5-flash-lite:\n    provider: google\n    availability: stable\n    provider_description: fastest and lowest-cost Gemini 3.5 model for high-throughput execution\n    teo_routing_role: primary economical throughput implementation\n    routing_status: routed\n    input_modalities: [text, image, video, audio, pdf]\n    output_modalities: [text]\n    reasoning_control: thinking_level\n    reasoning_levels: [minimal, low, medium, high]\n    reasoning_default: minimal\n    context_window_tokens: 1048576\n    max_output_tokens: 65536\n    evidence_type: provider_claim\n    source: https://ai.google.dev/gemini-api/docs/latest-model\n""",
)

# 8) README reflects executable policy instead of the prior candidate language.
replace_once(
    "README.md",
    """| Economical bounded throughput | Claude Haiku 4.5 | Gemini 3.6 Flash fallback; GPT-5.6 Luna remains an alternative |\n""",
    """| Economical bounded throughput | Gemini 3.5 Flash-Lite | Claude Haiku 4.5 fallback; GPT-5.6 Luna alternative; Gemini 3.6 Flash for stronger bounded agentic or multimodal work |\n""",
)
replace_once(
    "README.md",
    """Two newer implementations are deliberately **not** promoted merely because they are newer:\n\n- `claude-fable-5` is registered as a frontier escalation candidate. Anthropic currently positions it above Opus 5 in raw capability, but its higher cost, slower latency, and different safety behavior mean TEO requires task-relevant evidence before routing promotion.\n- `gemini-3.5-flash-lite` is registered as a throughput candidate. Google positions it specifically for high-volume, low-cost execution, but TEO does not silently replace Luna, Haiku, or existing Flash routes without controlled comparison.\n""",
    """Two newer implementations now have deliberately bounded roles rather than blanket promotion:\n\n- `claude-fable-5` is routed only as a frontier escalation after established Opus/Sol high-consequence paths remain inconclusive and the expected quality gain justifies materially higher cost and latency.\n- `gemini-3.5-flash-lite` is the primary economical bounded-throughput route because current Google evidence explicitly positions it for high-volume, low-cost execution; provider-diverse Haiku and Luna paths remain available.\n""",
)

print("Mission Control routing migration applied")
