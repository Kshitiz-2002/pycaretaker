"""
Background change monitor — detects external pip installs/removals.
Refactored from the original package_manager.py.
"""

import threading
import time
from typing import Set

from pycaretaker.core.packages import (
    ensure_requirements_file,
    get_freeze_lines,
    last_internal_change,
    write_all_packages,
    REQ_FILE,
)


def _monitor_loop(filename: str, interval: int) -> None:
    ensure_requirements_file(filename)
    last_snapshot: Set[str] = get_freeze_lines()

    while True:
        time.sleep(interval)
        current_snapshot: Set[str] = get_freeze_lines()
        if current_snapshot != last_snapshot:
            # Skip if the change was made by PyCareTaker itself
            from pycaretaker.core.packages import last_internal_change as lic
            if time.time() - lic < interval + 1:
                last_snapshot = current_snapshot
                continue
            added = current_snapshot - last_snapshot
            removed = last_snapshot - current_snapshot
            if added:
                print(f"[NOTICE] External install detected: {', '.join(sorted(added))}")
            if removed:
                print(f"[NOTICE] External removal detected: {', '.join(sorted(removed))}")
            write_all_packages(filename)
            last_snapshot = current_snapshot


def start_monitor(filename: str = REQ_FILE, interval: int = 10) -> threading.Thread:
    """Start the background change-monitor thread and return it."""
    t = threading.Thread(target=_monitor_loop, args=(filename, interval), daemon=True)
    t.start()
    return t
