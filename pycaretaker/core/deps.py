"""
Dependency visualization — build and render a package dependency graph.
Uses importlib.metadata for discovery and networkx + matplotlib for rendering.
"""

import importlib.metadata
from typing import Dict, List, Set

try:
    import networkx as nx
except ImportError:
    nx = None  # type: ignore[assignment]

try:
    import matplotlib
    matplotlib.use("Agg")  # non-interactive backend for save; switched to TkAgg when showing
    import matplotlib.pyplot as plt
except ImportError:
    plt = None  # type: ignore[assignment]


def _parse_requires(requires_list: List[str] | None) -> List[str]:
    """Extract plain package names from Requires-Dist strings, ignoring extras."""
    if not requires_list:
        return []
    names: List[str] = []
    for req in requires_list:
        # Skip optional / extra-only dependencies
        if "extra ==" in req:
            continue
        # Name is everything before the first space, semicolon, or bracket
        name = req.split(";")[0].split("(")[0].split("[")[0].split("<")[0]
        name = name.split(">")[0].split("!")[0].split("~")[0].split("=")[0].strip()
        if name:
            names.append(name.lower())
    return names


def build_dependency_graph() -> "nx.DiGraph | None":
    """Build a directed graph of installed package dependencies."""
    if nx is None:
        print("[ERROR] networkx is not installed. Run: pip install networkx")
        return None

    G = nx.DiGraph()
    installed: Set[str] = set()

    for dist in importlib.metadata.distributions():
        pkg_name = dist.metadata["Name"].lower()
        installed.add(pkg_name)
        G.add_node(pkg_name)

    for dist in importlib.metadata.distributions():
        pkg_name = dist.metadata["Name"].lower()
        for dep in _parse_requires(dist.requires):
            if dep in installed:
                G.add_edge(pkg_name, dep)

    return G


def show_dependency_graph(save_path: str | None = None) -> None:
    """Render the dependency graph using matplotlib."""
    G = build_dependency_graph()
    if G is None:
        return
    if plt is None:
        print("[ERROR] matplotlib is not installed. Run: pip install matplotlib")
        return

    # Use interactive backend for display
    if save_path is None:
        matplotlib.use("TkAgg")
        import matplotlib.pyplot as _plt
    else:
        _plt = plt

    fig, ax = _plt.subplots(figsize=(16, 10))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    # Layout
    try:
        pos = nx.spring_layout(G, k=1.8, iterations=60, seed=42)
    except Exception:
        pos = nx.shell_layout(G)

    # Node sizing by degree
    degrees = dict(G.degree())
    node_sizes = [max(120, degrees.get(n, 1) * 80) for n in G.nodes()]

    # Color by in-degree (warm = many dependents)
    in_deg = dict(G.in_degree())
    max_in = max(in_deg.values()) if in_deg else 1
    node_colors = [in_deg.get(n, 0) / max(max_in, 1) for n in G.nodes()]

    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_size=node_sizes,
        node_color=node_colors,
        cmap=_plt.cm.plasma,
        alpha=0.9,
        edgecolors="#58a6ff",
        linewidths=0.5,
    )
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color="#30363d",
        arrows=True,
        arrowsize=8,
        alpha=0.5,
        width=0.6,
    )
    nx.draw_networkx_labels(
        G, pos, ax=ax,
        font_size=6,
        font_color="#c9d1d9",
        font_weight="bold",
    )

    ax.set_title(
        f"PyCareTaker — Dependency Graph  ({G.number_of_nodes()} packages, {G.number_of_edges()} edges)",
        color="#58a6ff", fontsize=14, fontweight="bold", pad=15,
    )
    ax.axis("off")
    _plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, facecolor=fig.get_facecolor())
        print(f"[SUCCESS] Dependency graph saved to {save_path}")
    else:
        _plt.show()


def print_dependency_tree() -> None:
    """Print a text-based dependency tree to the terminal."""
    G = build_dependency_graph()
    if G is None:
        return

    # Find root packages (nothing depends on them)
    roots = [n for n in G.nodes() if G.in_degree(n) == 0]
    if not roots:
        roots = sorted(G.nodes())

    visited: Set[str] = set()

    def _print_tree(node: str, prefix: str = "", is_last: bool = True) -> None:
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{node}")
        visited.add(node)
        children = sorted(G.successors(node))
        children = [c for c in children if c not in visited]
        for i, child in enumerate(children):
            extension = "    " if is_last else "│   "
            _print_tree(child, prefix + extension, i == len(children) - 1)

    print("\n  Dependency Tree")
    print("  " + "=" * 40)
    for i, root in enumerate(sorted(roots)):
        if root not in visited:
            _print_tree(root, "  ", i == len(roots) - 1)
    print()
