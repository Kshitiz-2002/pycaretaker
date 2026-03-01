"""
Example plugin: License Checker
Inspects installed packages and reports their license metadata.
"""

import importlib.metadata


def run(context: dict) -> None:
    """Plugin entry point — called by the PyCareTaker plugin loader."""
    print("\n    📝 License Report")
    print(f"    {'─'*50}")
    print(f"    {'Package':<30} {'License':<30}")
    print(f"    {'─'*30} {'─'*30}")

    count = 0
    unknown = 0
    for dist in sorted(importlib.metadata.distributions(), key=lambda d: d.metadata["Name"].lower()):
        name = dist.metadata["Name"]
        license_text = dist.metadata.get("License") or ""
        classifier_license = ""

        # Try to extract from classifiers
        classifiers = dist.metadata.get_all("Classifier") or []
        for c in classifiers:
            if c.startswith("License"):
                parts = c.split(" :: ")
                classifier_license = parts[-1] if len(parts) > 1 else c
                break

        final_license = license_text.strip() or classifier_license or "Unknown"
        if len(final_license) > 28:
            final_license = final_license[:25] + "..."

        if final_license == "Unknown":
            unknown += 1

        print(f"    {name:<30} {final_license:<30}")
        count += 1

    print(f"\n    Total: {count} packages, {unknown} with unknown license.\n")
