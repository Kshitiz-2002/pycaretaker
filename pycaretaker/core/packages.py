"""
Package management primitives — install, remove, freeze, snapshot.
Refactored from the original package_manager.py.
"""

import os
import subprocess
import sys
import time
from typing import Dict, List, Set

REQ_FILE: str = "requirements.txt"

# Use the current Python interpreter's pip to ensure venv correctness
_PIP_CMD: List[str] = [sys.executable, "-m", "pip"]

# Timestamp of last change made through PyCareTaker (avoids false "external" alerts)
last_internal_change: float = 0.0


def mark_internal_change() -> None:
    global last_internal_change
    last_internal_change = time.time()


def ensure_requirements_file(filename: str = REQ_FILE) -> None:
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("")
        print(f"[INFO] Created {filename}")


def get_installed_packages() -> Dict[str, str]:
    """Return {package_name: version} dict of everything installed."""
    result = subprocess.run(
        [*_PIP_CMD, "freeze"], capture_output=True, text=True, check=True
    )
    pkgs: Dict[str, str] = {}
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if "==" in line:
            name, ver = line.split("==", 1)
            pkgs[name.lower()] = ver
        elif line:
            pkgs[line.lower()] = ""
    return pkgs


def get_freeze_lines() -> Set[str]:
    """Return the raw pip freeze lines as a set."""
    result = subprocess.run(
        [*_PIP_CMD, "freeze"], capture_output=True, text=True, check=True
    )
    return set(result.stdout.strip().splitlines())


def write_all_packages(filename: str = REQ_FILE) -> None:
    ensure_requirements_file(filename)
    result = subprocess.run(
        [*_PIP_CMD, "freeze"], capture_output=True, text=True, check=True
    )
    packages: List[str] = sorted(result.stdout.strip().splitlines())
    with open(filename, "w") as f:
        f.write("\n".join(packages) + "\n")
    print(f"[INFO] Requirements snapshot updated ({len(packages)} packages).")


def install_package(package_spec: str, filename: str = REQ_FILE) -> bool:
    """Install a package and update the requirements file. Returns True on success."""
    try:
        subprocess.run([*_PIP_CMD, "install", package_spec], check=True)
        write_all_packages(filename)
        print(f"[SUCCESS] Installed {package_spec}")
        mark_internal_change()
        return True
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] Failed to install {package_spec}: {exc}")
        return False


def remove_package(package_name: str, filename: str = REQ_FILE) -> bool:
    """Uninstall a package and update the requirements file. Returns True on success."""
    try:
        subprocess.run([*_PIP_CMD, "uninstall", "-y", package_name], check=True)
        write_all_packages(filename)
        print(f"[SUCCESS] Removed {package_name}")
        mark_internal_change()
        return True
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] Failed to remove {package_name}: {exc}")
        return False
