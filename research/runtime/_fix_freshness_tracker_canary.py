from pathlib import Path

path = Path("tests/test_documentation_control_plane_truth.py")
text = path.read_text(encoding="utf-8")
old = '''        "Reference Implementation CI #658 passed **863 tests**, **528 tracked-file layout checks**",
        "red-canary CI #676",
        "Corrected Reference Implementation CI #678 passed **891 tests**, **532 tracked-file layout checks**",
'''
new = '''        "Reference Implementation CI #658 passed **863 tests**, **528 tracked-file layout checks**",
        "Red-canary CI #676",
        "Corrected Reference Implementation CI #678 passed **891 tests**, **532 tracked-file layout checks**",
'''
if text.count(old) != 1:
    raise SystemExit(f"expected exactly one tracker canary sequence, found {text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
