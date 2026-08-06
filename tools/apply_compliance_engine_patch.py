from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "reference/implementations/python/src/teo_reference/engine.py"


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one engine match, found {count}: {old!r}")
    return text.replace(old, new, 1)


def main() -> None:
    text = ENGINE.read_text(encoding="utf-8")

    text = replace_once(
        text,
        '    (\n        "market_research",\n',
        '''    (
        "compliance_review",
        (
            "compliance audit",
            "compliance review",
            "soc 2",
            "soc2",
            "iso 27001",
            "iso 27701",
            "pci dss",
            "pci-dss",
            "gdpr compliance",
            "ccpa compliance",
            "hipaa compliance",
            "privacy impact assessment",
            "data protection impact assessment",
            "dpia",
            "control mapping",
            "operating effectiveness",
            "audit evidence",
            "ai act compliance",
            "agentic trust",
            "privacy policy based on data flow",
        ),
    ),
    (
        "market_research",
''',
    )

    text = replace_once(
        text,
        '    "user_research": ("primary",),\n    "market_research": ("primary",),',
        '    "user_research": ("primary",),\n    "compliance_review": ("primary",),\n    "market_research": ("primary",),',
    )

    text = replace_once(
        text,
        '            "user_insight_translation",\n        },\n        "research",',
        '''            "user_insight_translation",
            "compliance_reasoning",
            "regulatory_applicability_analysis",
            "control_mapping",
            "evidence_assessment",
            "audit_methodology",
            "privacy_and_data_governance",
            "ai_governance",
            "third_party_risk_analysis",
            "risk_classification",
            "traceable_writing",
        },
        "research",''',
    )

    ENGINE.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
