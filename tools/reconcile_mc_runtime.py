from pathlib import Path

def r(path, old, new):
    p=Path(path); t=p.read_text()
    if t.count(old)!=1: raise SystemExit(f'{path}: expected 1 match, got {t.count(old)}')
    p.write_text(t.replace(old,new))

r('community/workers/workers.yaml', '''  documentation:\n    mission: create accurate, usable, and maintainable technical documentation\n    owning_team: research\n    responsibilities:\n      - technical_writing\n      - examples\n      - reference_updates\n      - consistency_review\n    required_capabilities:\n      - synthesis\n      - technical_accuracy\n      - clear_writing\n    preferred_implementations:\n      - claude-sonnet-5\n      - gpt-5.6-sol\n      - gemini-3.6-flash\n    fallbacks:\n      - gemini-3.1-pro-preview\n      - gpt-5.6-sol\n''', '''  documentation:\n    mission: create accurate, usable, and maintainable technical documentation\n    owning_team: research\n    responsibilities:\n      - technical_writing\n      - examples\n      - reference_updates\n      - consistency_review\n    required_capabilities:\n      - synthesis\n      - technical_accuracy\n      - clear_writing\n    preferred_implementations:\n      - claude-sonnet-5\n      - gpt-5.6-sol\n      - gemini-3.6-flash\n      - gemini-3.5-flash-lite\n      - claude-haiku-4-5\n    fallbacks:\n      - gemini-3.1-pro-preview\n      - gpt-5.6-sol\n''')

r('policy/routing/routing.yaml', '''  throughput:\n    - agent: agy\n      model: gemini-3.5-flash-lite\n    - agent: claude\n      model: claude-haiku-4-5\n    - agent: codex\n      model: gpt-5.6-luna\n    - agent: agy\n      model: gemini-3.6-flash\n''', '''  throughput:\n    - agent: agy\n      model: gemini-3.5-flash-lite\n    - agent: claude\n      model: claude-haiku-4-5\n    - agent: codex\n      model: gpt-5.6-luna\n''')

r('reference/implementations/python/src/teo_reference/google_adapter.py', 'CANARY_MODELS = {"gemini-3.6-flash"}', 'CANARY_MODELS = {"gemini-3.5-flash-lite", "gemini-3.6-flash"}')
r('reference/implementations/python/src/teo_reference/google_adapter.py', '"Gemini live canary is restricted to Gemini 3.6 Flash"', '"Gemini live canary is restricted to the routed stable Gemini canary models"')
r('reference/implementations/python/src/teo_reference/google_adapter.py', 'f"Gemini 3.6 Flash does not support TEO reasoning effort {request.reasoning_effort}"', 'f"Selected Gemini canary model does not support TEO reasoning effort {request.reasoning_effort}"')
print('runtime reconciliation applied')
