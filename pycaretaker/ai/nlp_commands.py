"""
Natural language commands — translate human input into pip actions via LLM.
"""

import json
from typing import Any, Dict, List

from pycaretaker.ai.backend import get_backend
from pycaretaker.core.packages import install_package, remove_package, get_installed_packages


_SYSTEM_PROMPT = """\
You are PyCareTaker, a Python package management assistant.
The user will describe what they want in natural language.
You MUST respond with a JSON object (no markdown, no explanation) in this exact format:

{
  "actions": [
    {"type": "install", "package": "package-name"},
    {"type": "remove",  "package": "package-name"}
  ],
  "explanation": "Short one-line explanation of what you chose and why."
}

Rules:
- "type" must be "install" or "remove".
- "package" must be a valid PyPI package name.
- If the request is ambiguous, pick the most popular / standard package.
- If you cannot determine any action, return {"actions": [], "explanation": "..."}.
- ONLY output valid JSON. No markdown code fences.
"""


def process_natural_command(user_text: str, dry_run: bool = False) -> Dict[str, Any]:
    """
    Send natural language to the LLM, parse the structured response,
    and execute the resulting pip actions.

    Returns:
        {"actions": [...], "explanation": str, "executed": bool}
    """
    ai = get_backend()
    if not ai.available:
        print("[INFO] AI backend not available. Provide --api-key or start Ollama.")
        return {"actions": [], "explanation": "", "executed": False}

    installed = get_installed_packages()
    context = (
        f"Currently installed packages: {', '.join(sorted(installed.keys())[:40])}\n"
        f"User request: {user_text}"
    )

    raw = ai.ask(context, system=_SYSTEM_PROMPT)

    # Try to parse JSON from the response
    try:
        # Strip markdown fences if the model wrapped it
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

        result = json.loads(cleaned)
    except json.JSONDecodeError:
        print(f"[WARN] Could not parse AI response as JSON:\n{raw}")
        return {"actions": [], "explanation": raw, "executed": False}

    actions = result.get("actions", [])
    explanation = result.get("explanation", "")

    print(f"\n  AI Interpretation: {explanation}")
    if not actions:
        print("  No actionable commands identified.")
        return {"actions": actions, "explanation": explanation, "executed": False}

    print(f"  Planned actions:")
    for a in actions:
        icon = "📦" if a["type"] == "install" else "🗑️"
        print(f"    {icon}  {a['type']} → {a['package']}")
    print()

    if dry_run:
        print("  [DRY-RUN] No changes made.")
        return {"actions": actions, "explanation": explanation, "executed": False}

    # Execute
    for a in actions:
        if a["type"] == "install":
            install_package(a["package"])
        elif a["type"] == "remove":
            remove_package(a["package"])

    return {"actions": actions, "explanation": explanation, "executed": True}
