"""
PyCareTaker CLI — unified command-line interface for all features.

Usage:
    python package_manager.py <command> [options]

Commands:
    install <package>       Install a package
    remove <package>        Uninstall a package
    deps                    Visualize dependency graph
    outdated                Check for outdated packages
    diff                    Compare env vs requirements.txt
    memwatch                Live memory + CPU profiler
    security                Run security scan
    ai "<text>"             Natural language command (AI)
    plugins                 Run user plugins
    interactive             Interactive shell mode
"""

import argparse
import sys
import os

# Ensure the project root is on sys.path
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pycaretaker",
        description=(
            "🛡️  PyCareTaker v0.1 — A smart Python package manager companion.\n"
            "Manage, monitor, visualize, and analyze your Python environment "
            "— with optional AI insights."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # --- install ---
    p_install = sub.add_parser("install", help="Install a package")
    p_install.add_argument("package", help="Package spec, e.g. flask or flask==2.3")

    # --- remove ---
    p_remove = sub.add_parser("remove", help="Uninstall a package")
    p_remove.add_argument("package", help="Package name to uninstall")

    # --- deps ---
    p_deps = sub.add_parser("deps", help="Visualize dependency graph")
    p_deps.add_argument("--save", metavar="FILE", help="Save graph to PNG instead of displaying")
    p_deps.add_argument("--text", action="store_true", help="Print text-based tree instead")

    # --- outdated ---
    sub.add_parser("outdated", help="Check for outdated packages against PyPI")

    # --- diff ---
    p_diff = sub.add_parser("diff", help="Compare current env vs requirements.txt")
    p_diff.add_argument("--file", default="requirements.txt", help="Requirements file to compare")

    # --- memwatch ---
    p_mem = sub.add_parser("memwatch", help="Live memory + CPU profiler")
    p_mem.add_argument("--silent", action="store_true", help="Suppress terminal logging")
    p_mem.add_argument("--export", metavar="FILE", help="Export data on exit (CSV or JSON)")
    p_mem.add_argument("--format", choices=["csv", "json"], help="Force export format")
    p_mem.add_argument("--interval", type=int, default=5, help="Sampling interval in seconds")

    # --- security ---
    sub.add_parser("security", help="Run security vulnerability scan")

    # --- ai ---
    p_ai = sub.add_parser("ai", help="Natural language command (AI-powered)")
    p_ai.add_argument("text", nargs="+", help="Natural language instruction")
    p_ai.add_argument("--dry-run", action="store_true", help="Show plan without executing")

    # --- plugins ---
    p_plug = sub.add_parser("plugins", help="Run user plugins")
    p_plug.add_argument("--dir", default="plugins", help="Plugin directory")

    # --- interactive ---
    sub.add_parser("interactive", help="Interactive shell mode")

    # --- Global AI flags ---
    parser.add_argument("--api-key", help="OpenAI-compatible API key")
    parser.add_argument("--model", help="Model name (default: gpt-3.5-turbo or first Ollama model)")

    return parser


def _print_banner() -> None:
    banner = r"""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   🛡️  PyCareTaker v0.1                                     ║
    ║   Smart Python Package Manager Companion                 ║
    ║                                                          ║
    ║   Manage · Monitor · Visualize · Analyze                 ║
    ║   with optional AI insights                              ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Init AI backend if key was provided
    if getattr(args, "api_key", None) or getattr(args, "model", None):
        from pycaretaker.ai.backend import get_backend
        get_backend(api_key=args.api_key, model=args.model)

    if args.command is None:
        _print_banner()
        parser.print_help()
        return

    # ── install ──
    if args.command == "install":
        from pycaretaker.core.packages import install_package
        success = install_package(args.package)
        if success:
            # AI recommendations (non-blocking, best-effort)
            try:
                from pycaretaker.ai.recommendations import suggest_related
                suggest_related(args.package.split("==")[0].split("[")[0])
            except Exception:
                pass

    # ── remove ──
    elif args.command == "remove":
        from pycaretaker.core.packages import remove_package
        remove_package(args.package)

    # ── deps ──
    elif args.command == "deps":
        from pycaretaker.core.deps import show_dependency_graph, print_dependency_tree
        if args.text:
            print_dependency_tree()
        else:
            show_dependency_graph(save_path=args.save)

    # ── outdated ──
    elif args.command == "outdated":
        from pycaretaker.core.outdated import check_outdated
        check_outdated(verbose=True)

    # ── diff ──
    elif args.command == "diff":
        from pycaretaker.core.diff import diff_environment
        diff_environment(req_file=args.file, verbose=True)

    # ── memwatch ──
    elif args.command == "memwatch":
        from pycaretaker.core.profiler import track_usage, get_samples
        print("\n  🔍 PyCareTaker System Profiler")
        print(f"  Sampling every {args.interval}s. Press Ctrl+C to stop.\n")
        track_usage(
            interval=args.interval,
            log=not args.silent,
            export_path=args.export,
            export_format=args.format,
        )
        # Optionally analyze with AI on exit
        samples = get_samples()
        if samples:
            try:
                from pycaretaker.ai.analysis import analyze_profiling_data
                analyze_profiling_data(samples)
            except Exception:
                pass

    # ── security ──
    elif args.command == "security":
        from pycaretaker.ai.security import security_scan
        security_scan(verbose=True)

    # ── ai ──
    elif args.command == "ai":
        from pycaretaker.ai.nlp_commands import process_natural_command
        text = " ".join(args.text)
        process_natural_command(text, dry_run=args.dry_run)

    # ── plugins ──
    elif args.command == "plugins":
        from pycaretaker.plugins import load_and_run_plugins
        from pycaretaker.core.packages import get_installed_packages
        context = {"installed_packages": get_installed_packages()}
        load_and_run_plugins(plugin_dir=args.dir, context=context)

    # ── interactive ──
    elif args.command == "interactive":
        _interactive_mode()


def _interactive_mode() -> None:
    """Enhanced interactive shell with all commands accessible."""
    from pycaretaker.core.packages import install_package, remove_package
    from pycaretaker.core.monitor import start_monitor

    start_monitor()
    _print_banner()

    print("  Commands:")
    print("    install <package>      │ Install a package")
    print("    remove <package>       │ Uninstall a package")
    print("    deps [--text]          │ Dependency graph")
    print("    outdated               │ Check PyPI versions")
    print("    diff                   │ Env vs requirements.txt")
    print("    memwatch               │ CPU + Memory profiler")
    print("    security               │ Vulnerability scan")
    print("    ai <text>              │ Natural language command")
    print("    plugins                │ Run user plugins")
    print("    exit                   │ Quit")
    print()

    while True:
        try:
            cmd = input("  pycaretaker › ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  [INFO] Bye!")
            break

        if not cmd:
            continue
        if cmd.lower() == "exit":
            print("  [INFO] Bye!")
            break

        # Dispatch via the same CLI parser
        try:
            parts = cmd.split()
            main(parts)
        except SystemExit:
            pass  # argparse calls sys.exit on --help or errors
        except Exception as exc:
            print(f"  [ERROR] {exc}")


if __name__ == "__main__":
    main()
