"""
Plugin loader for PyCareTaker.
Discovers and runs user plugins from a configurable directory.
"""

import importlib.util
import os
import sys
import traceback
from typing import Any, Dict, List


def discover_plugins(plugin_dir: str = "plugins") -> List[str]:
    """Return a list of .py files in the plugin directory."""
    if not os.path.isdir(plugin_dir):
        print(f"[INFO] Plugin directory '{plugin_dir}' not found.")
        return []
    return [
        os.path.join(plugin_dir, f)
        for f in sorted(os.listdir(plugin_dir))
        if f.endswith(".py") and not f.startswith("_")
    ]


def load_and_run_plugins(
    plugin_dir: str = "plugins",
    context: Dict[str, Any] | None = None,
) -> None:
    """Discover, load, and execute all plugins in the given directory."""
    files = discover_plugins(plugin_dir)
    if not files:
        print("[INFO] No plugins found.")
        return

    if context is None:
        context = {}

    print(f"\n{'='*50}")
    print(f"  Running {len(files)} plugin(s) from '{plugin_dir}/'")
    print(f"{'='*50}\n")

    for filepath in files:
        module_name = os.path.splitext(os.path.basename(filepath))[0]
        print(f"  ▸ Loading plugin: {module_name}")
        try:
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec is None or spec.loader is None:
                print(f"    [WARN] Could not load '{filepath}', skipping.")
                continue
            mod = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)  # type: ignore[union-attr]

            if hasattr(mod, "run") and callable(mod.run):
                mod.run(context)
                print(f"    [OK] Plugin '{module_name}' executed successfully.")
            else:
                print(f"    [WARN] Plugin '{module_name}' has no run(context) function.")
        except Exception:
            print(f"    [ERROR] Plugin '{module_name}' failed:")
            traceback.print_exc()

    print(f"\n{'='*50}")
    print("  Plugin execution complete.")
    print(f"{'='*50}\n")
