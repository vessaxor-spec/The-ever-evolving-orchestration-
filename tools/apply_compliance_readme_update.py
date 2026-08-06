from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one README match, found {count}: {old!r}")
    return text.replace(old, new, 1)


def main() -> None:
    text = README.read_text(encoding="utf-8")

    replacements = [
        (
            "- dedicated Research Team workers for broad research, user research, market research, analytics, and documentation\n- deterministic task classification for the active reference routes",
            "- dedicated Research Team workers for broad research, user research, market research, analytics, and documentation\n- dedicated Review Team workers for code review and compliance review\n- deterministic task classification for the active reference routes",
        ),
        (
            "The Review Team challenges assumptions, reviews architecture and code, checks requirements alignment, identifies hidden risks, and escalates consequential decisions.\n\nReview includes semantic challenge, adversarial reasoning, security analysis, performance review, accessibility review, and contract integrity checks.",
            "The Review Team challenges assumptions, reviews architecture and code, checks requirements alignment, identifies hidden risks, and escalates consequential decisions.\n\nIts dedicated workers currently include:\n\n| Worker | Responsibility |\n|---|---|\n| `code_review` | correctness, minimal-change discipline, contracts, regression risk, and AI-authored code review |\n| `compliance` | regulatory applicability, control mapping, audit evidence, privacy and AI governance, third-party risk, and human-gated remediation decisions |\n\nReview also includes semantic challenge, adversarial reasoning, security analysis, performance review, accessibility review, and contract integrity checks. Compliance does not issue legal opinions, audit certifications, or technical implementations.",
        ),
        (
            "| `code_review` | correctness, scope, contracts, and regression review |\n| `security_review` | critical security analysis and verification |",
            "| `code_review` | correctness, scope, contracts, and regression review |\n| `compliance_review` | critical compliance applicability, controls, evidence, privacy, and AI-governance review |\n| `security_review` | critical security analysis and verification |",
        ),
        (
            "| Quantitative analytics | Codex Sol | Gemini Pro with Claude Sonnet verification |\n| Multimodal and rapid collection | Gemini Flash | Claude Sonnet and technical follow-up when needed |",
            "| Quantitative analytics | Codex Sol | Gemini Pro with Claude Sonnet verification |\n| Compliance and AI governance | Claude Sonnet | Codex Sol fallback with Gemini Pro verification and qualified human approval |\n| Multimodal and rapid collection | Gemini Flash | Claude Sonnet and technical follow-up when needed |",
        ),
        (
            "- [`policy/routing/research-routing.yaml`](policy/routing/research-routing.yaml)\n- [`policy/routing/team-routing.yaml`](policy/routing/team-routing.yaml)",
            "- [`policy/routing/research-routing.yaml`](policy/routing/research-routing.yaml)\n- [`policy/routing/review-routing.yaml`](policy/routing/review-routing.yaml)\n- [`policy/routing/team-routing.yaml`](policy/routing/team-routing.yaml)",
        ),
        (
            "- analytics worker boundaries\n- exact configuration-warning baselines",
            "- analytics worker boundaries\n- compliance worker boundaries and critical-risk human approval\n- exact configuration-warning baselines",
        ),
        (
            "- Review Team: code review",
            "- Review Team: code review, compliance review",
        ),
    ]

    for old, new in replacements:
        text = replace_once(text, old, new)

    README.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
