"""
Package recommendations — AI suggests related packages after install.
"""

from pycaretaker.ai.backend import get_backend

_SYSTEM_PROMPT = """\
You are PyCareTaker, a Python package recommendation engine.
Given a package the user just installed, suggest 2-3 complementary packages.
Respond with ONLY a compact JSON array, no markdown, like:
[
  {"name": "flask-login", "reason": "Authentication support for Flask apps."},
  {"name": "flask-cors",  "reason": "Handle Cross-Origin requests easily."}
]
"""


def suggest_related(package_name: str) -> None:
    """Print AI-powered package recommendations after an install."""
    ai = get_backend()
    if not ai.available:
        return  # silently skip when no AI backend

    import json

    prompt = f"The user just installed '{package_name}'. Suggest complementary packages."
    raw = ai.ask(prompt, system=_SYSTEM_PROMPT)

    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        suggestions = json.loads(cleaned.strip())
    except (json.JSONDecodeError, ValueError):
        return

    if not suggestions:
        return

    print(f"\n  💡 AI Recommendations (related to {package_name}):")
    for s in suggestions:
        name = s.get("name", "?")
        reason = s.get("reason", "")
        print(f"     ▸ {name:<25} — {reason}")
    print()
