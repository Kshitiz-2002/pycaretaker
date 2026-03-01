"""
Version tracking — compare installed packages against PyPI latest versions.
Uses the PyPI JSON API to fetch the latest release info.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, List, Tuple

from pycaretaker.core.packages import get_installed_packages

try:
    from packaging.version import Version, InvalidVersion
except ImportError:
    Version = None  # type: ignore[assignment, misc]
    InvalidVersion = Exception  # type: ignore[assignment, misc]

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except ImportError:
    # Fallback: no colours
    class _Stub:
        def __getattr__(self, _: str) -> str:
            return ""
    Fore = _Stub()  # type: ignore[assignment]
    Style = _Stub()  # type: ignore[assignment]


def fetch_pypi_version(package_name: str) -> str | None:
    """Fetch the latest version string from PyPI JSON API."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
            return data.get("info", {}).get("version")
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
        return None


def _version_status(installed: str, latest: str) -> str:
    """Return 'up-to-date', 'outdated', or 'unknown'."""
    if Version is None:
        return "outdated" if installed != latest else "up-to-date"
    try:
        return "up-to-date" if Version(installed) >= Version(latest) else "outdated"
    except InvalidVersion:
        return "unknown"


def check_outdated(verbose: bool = True) -> List[Dict[str, str]]:
    """
    Compare every installed package against PyPI.
    Returns a list of dicts: {name, installed, latest, status}.
    """
    installed = get_installed_packages()
    results: List[Dict[str, str]] = []

    if verbose:
        print(f"\n{'='*60}")
        print("  Checking {0} installed packages against PyPI …".format(len(installed)))
        print(f"{'='*60}\n")
        print(f"  {'Package':<30} {'Installed':<14} {'Latest':<14} Status")
        print(f"  {'─'*30} {'─'*14} {'─'*14} {'─'*10}")

    for name, ver in sorted(installed.items()):
        latest = fetch_pypi_version(name)
        if latest is None:
            status = "unknown"
        else:
            status = _version_status(ver, latest)

        results.append({
            "name": name,
            "installed": ver,
            "latest": latest or "?",
            "status": status,
        })

        if verbose:
            if status == "outdated":
                colour = Fore.YELLOW
                icon = "⚠"
            elif status == "up-to-date":
                colour = Fore.GREEN
                icon = "✔"
            else:
                colour = Fore.RED
                icon = "?"
            print(
                f"  {colour}{name:<30} {ver:<14} {(latest or '?'):<14} {icon} {status}{Style.RESET_ALL}"
            )

    if verbose:
        outdated_count = sum(1 for r in results if r["status"] == "outdated")
        print(f"\n  Summary: {outdated_count} outdated, "
              f"{len(results) - outdated_count} up-to-date/unknown.\n")

    return results
