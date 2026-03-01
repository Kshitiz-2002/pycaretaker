"""
Security insights — check installed packages for known vulnerabilities.
Uses pip-audit when available, and optionally asks the AI backend for analysis.
"""

import json
import subprocess
import urllib.request
import urllib.error
from typing import Any, Dict, List

from pycaretaker.core.packages import get_installed_packages
from pycaretaker.ai.backend import get_backend

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except ImportError:
    class _Stub:
        def __getattr__(self, _: str) -> str:
            return ""
    Fore = _Stub()  # type: ignore[assignment]
    Style = _Stub()  # type: ignore[assignment]


def _run_pip_audit() -> List[Dict[str, str]]:
    """Run pip-audit and return a list of vulnerability dicts."""
    try:
        result = subprocess.run(
            ["pip-audit", "--format", "json", "--progress-spinner", "off"],
            capture_output=True, text=True, timeout=120,
        )
        if result.stdout.strip():
            data = json.loads(result.stdout)
            if isinstance(data, list):
                return data
            return data.get("dependencies", [])
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError, subprocess.TimeoutExpired):
        pass
    return []


def _check_pypi_vulnerabilities(name: str) -> List[str]:
    """Fetch vulnerability info from PyPI JSON API (limited)."""
    url = f"https://pypi.org/pypi/{name}/json"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
            vulns = data.get("vulnerabilities", [])
            return [
                f"{v.get('id', '?')}: {v.get('summary', 'No summary')}"
                for v in vulns
            ]
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
        return []


def security_scan(verbose: bool = True) -> Dict[str, Any]:
    """
    Run a security scan on the current environment.
    Returns {vulnerabilities: [...], ai_analysis: str}.
    """
    installed = get_installed_packages()
    all_vulns: List[Dict[str, Any]] = []

    if verbose:
        print(f"\n{'='*60}")
        print("  🔒 PyCareTaker Security Scan")
        print(f"{'='*60}\n")

    # Try pip-audit first
    if verbose:
        print("  [1/3] Running pip-audit …", end=" ")
    audit_results = _run_pip_audit()
    if audit_results:
        if verbose:
            print(f"found {len(audit_results)} result(s).")
        for entry in audit_results:
            vuln_name = entry.get("name", "?")
            vuln_ver = entry.get("version", "?")
            vulns = entry.get("vulns", [])
            for v in vulns:
                all_vulns.append({
                    "package": vuln_name,
                    "version": vuln_ver,
                    "id": v.get("id", "?"),
                    "description": v.get("description", "")[:120],
                    "fix_versions": v.get("fix_versions", []),
                })
    else:
        if verbose:
            print("pip-audit not available or no issues found.")

    # Spot-check a few packages via PyPI
    if verbose:
        print("  [2/3] Checking PyPI vulnerability database …")
    check_list = list(installed.keys())[:30]  # limit to avoid rate-limiting
    for name in check_list:
        vulns = _check_pypi_vulnerabilities(name)
        for v in vulns:
            all_vulns.append({"package": name, "version": installed[name], "id": v, "description": v})

    # AI analysis
    ai_analysis = ""
    ai = get_backend()
    if ai.available:
        if verbose:
            print("  [3/3] Asking AI for security insights …")
        pkg_list = ", ".join(f"{n}=={v}" for n, v in sorted(installed.items())[:40])
        prompt = (
            f"Analyze these Python packages for known security concerns:\n{pkg_list}\n"
            "Be concise. If any are known to have had CVEs, mention them. "
            "Otherwise say the environment looks safe."
        )
        ai_analysis = ai.ask(prompt)
    else:
        if verbose:
            print("  [3/3] AI backend not available, skipping AI analysis.")

    # Print results
    if verbose:
        print(f"\n{'─'*60}")
        if all_vulns:
            print(f"  {Fore.RED}⚠ Found {len(all_vulns)} vulnerability(ies):{Style.RESET_ALL}\n")
            for v in all_vulns:
                print(f"    {Fore.RED}• {v['package']}=={v.get('version','?')}{Style.RESET_ALL}")
                print(f"      ID: {v.get('id','?')}")
                desc = v.get("description", "")
                if desc:
                    print(f"      {desc[:100]}")
                fix = v.get("fix_versions")
                if fix:
                    print(f"      Fix: upgrade to {', '.join(fix)}")
                print()
        else:
            print(f"  {Fore.GREEN}✔ No known vulnerabilities found.{Style.RESET_ALL}\n")

        if ai_analysis:
            print(f"  🤖 AI Security Insights:")
            for line in ai_analysis.split("\n"):
                print(f"     {line}")
            print()

    return {"vulnerabilities": all_vulns, "ai_analysis": ai_analysis}
