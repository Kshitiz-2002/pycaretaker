"""
Environment diffing — compare current installation against a saved requirements file.
Reports added, removed, and version-changed packages.
"""

import os
from typing import Dict, List, Tuple

from pycaretaker.core.packages import get_installed_packages, REQ_FILE

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except ImportError:
    class _Stub:
        def __getattr__(self, _: str) -> str:
            return ""
    Fore = _Stub()  # type: ignore[assignment]
    Style = _Stub()  # type: ignore[assignment]


def parse_requirements(filepath: str) -> Dict[str, str]:
    """Parse a requirements.txt into {name: version} dict."""
    pkgs: Dict[str, str] = {}
    if not os.path.exists(filepath):
        return pkgs
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            if "==" in line:
                name, ver = line.split("==", 1)
                pkgs[name.strip().lower()] = ver.strip()
            else:
                pkgs[line.strip().lower()] = ""
    return pkgs


def diff_environment(
    req_file: str = REQ_FILE,
    verbose: bool = True,
) -> Dict[str, List[str | Tuple[str, str, str]]]:
    """
    Compare current env vs a saved requirements file.

    Returns:
        {
            "added":   [pkg_name, …],
            "removed": [pkg_name, …],
            "changed": [(name, old_ver, new_ver), …],
        }
    """
    saved = parse_requirements(req_file)
    current = get_installed_packages()

    added = sorted(set(current) - set(saved))
    removed = sorted(set(saved) - set(current))
    changed: List[Tuple[str, str, str]] = []
    for name in sorted(set(saved) & set(current)):
        if saved[name] and current[name] and saved[name] != current[name]:
            changed.append((name, saved[name], current[name]))

    result: Dict[str, list] = {
        "added": added,
        "removed": removed,
        "changed": changed,
    }

    if verbose:
        print(f"\n{'='*60}")
        print(f"  Environment diff vs '{req_file}'")
        print(f"{'='*60}\n")

        if not added and not removed and not changed:
            print(f"  {Fore.GREEN}✔ Environment matches the requirements file.{Style.RESET_ALL}\n")
            return result

        if added:
            print(f"  {Fore.GREEN}+ Added ({len(added)}):{Style.RESET_ALL}")
            for pkg in added:
                print(f"    {Fore.GREEN}+ {pkg}=={current[pkg]}{Style.RESET_ALL}")
            print()

        if removed:
            print(f"  {Fore.RED}− Removed ({len(removed)}):{Style.RESET_ALL}")
            for pkg in removed:
                print(f"    {Fore.RED}− {pkg}=={saved[pkg]}{Style.RESET_ALL}")
            print()

        if changed:
            print(f"  {Fore.YELLOW}~ Version changed ({len(changed)}):{Style.RESET_ALL}")
            for name, old, new in changed:
                print(f"    {Fore.YELLOW}~ {name}: {old} → {new}{Style.RESET_ALL}")
            print()

    return result
