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
            "- dedicated Research Team workers for broad research, market research, analytics, and documentation",
            "- dedicated Research Team workers for broad research, user research, market research, analytics, and documentation",
        ),
        (
            "| `research` | source discovery, triangulation, contradiction analysis, confidence calibration, and research synthesis |\n| `market_research` | competitive landscapes, bounded market sizing, lifecycle analysis, weak signals, willingness-to-pay, and strategic market evidence |",
            "| `research` | source discovery, triangulation, contradiction analysis, confidence calibration, and research synthesis |\n| `user_research` | interviews, surveys, usability findings, feedback themes, JTBD framing, persona evidence, mixed-method triangulation, and user-insight synthesis |\n| `market_research` | competitive landscapes, bounded market sizing, lifecycle analysis, weak signals, willingness-to-pay, and strategic market evidence |",
        ),
        (
            "- research synthesis is not quantitative analytics\n- market intelligence is not broad-domain research",
            "- research synthesis is not quantitative analytics\n- user research is not market intelligence, quantitative analytics, documentation, or UX-design judgment\n- market intelligence is not broad-domain research",
        ),
        (
            "| `deep_research` | broad evidence gathering and synthesis |\n| `market_research` | current market and competitive intelligence |",
            "| `deep_research` | broad evidence gathering and synthesis |\n| `user_research` | qualitative user evidence and feedback synthesis |\n| `market_research` | current market and competitive intelligence |",
        ),
        (
            "| Broad and market research | Gemini Pro | Claude Sonnet and Codex Sol |\n| Quantitative analytics | Codex Sol | Gemini Pro with Claude Sonnet verification |",
            "| Broad and market research | Gemini Pro | Claude Sonnet and Codex Sol |\n| Qualitative user research | Claude Sonnet | Gemini Pro with Codex Sol verification |\n| Quantitative analytics | Codex Sol | Gemini Pro with Claude Sonnet verification |",
        ),
        (
            "- broad research worker boundaries\n- market-research worker boundaries",
            "- broad research worker boundaries\n- user-research worker boundaries\n- market-research worker boundaries",
        ),
        (
            "- Research Team: broad research, market research, analytics\n- Review Team: code review\n\nThe next planned worker is `user_research`, derived from the existing feedback-synthesizer specialist and kept separate from analytics and market intelligence.",
            "- Research Team: broad research, user research, market research, analytics\n- Review Team: code review\n\nThe next dedicated worker will be selected from the remaining exact warning baseline using responsibility uniqueness, routing value, risk, and verification needs rather than arbitrary roster order.",
        ),
        (
            "The first Capsule belongs in [`community/capsules/`](community/capsules/).",
            "Accepted Capsules are indexed in [`community/capsules/`](community/capsules/).",
        ),
    ]

    for old, new in replacements:
        text = replace_once(text, old, new)

    README.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
