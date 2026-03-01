"""
Lightweight profiler — tracks memory + CPU usage with live dual graph.
Extends the original memwatch with CPU tracking and export support.
"""

import os
import time
from datetime import datetime
from typing import List

import psutil

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
except ImportError:
    plt = None  # type: ignore[assignment]

from pycaretaker.core.export import Sample, export_samples

# -- Global sample store --
_samples: List[Sample] = []
MAX_SAMPLES: int = 600


def get_samples() -> List[Sample]:
    """Return a copy of the collected samples."""
    return list(_samples)


def track_usage(
    interval: int = 5,
    log: bool = True,
    export_path: str | None = None,
    export_format: str | None = None,
) -> None:
    """
    Track memory and CPU usage in real-time with a live dual graph.
    Press Ctrl+C to stop.  If export_path is set, data is saved on exit.
    """
    process = psutil.Process(os.getpid())

    if plt is None:
        print("[WARN] matplotlib not installed — running headless (no graph).")
        _headless_loop(process, interval, log, export_path, export_format)
        return

    plt.ion()
    fig, (ax_mem, ax_cpu) = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor("#0d1117")
    fig.suptitle("PyCareTaker — System Profiler", color="#58a6ff", fontsize=14, fontweight="bold")

    for ax in (ax_mem, ax_cpu):
        ax.set_facecolor("#161b22")
        ax.tick_params(colors="#8b949e")
        ax.spines["bottom"].set_color("#30363d")
        ax.spines["left"].set_color("#30363d")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(True, color="#21262d", linewidth=0.5)

    try:
        while True:
            mem_mb = process.memory_info().rss / (1024 * 1024)
            cpu_pct = psutil.cpu_percent(interval=0.1)
            now = datetime.now()

            _samples.append(Sample(
                timestamp=now.strftime("%Y-%m-%d %H:%M:%S"),
                memory_mb=round(mem_mb, 2),
                cpu_percent=round(cpu_pct, 1),
            ))
            if len(_samples) > MAX_SAMPLES:
                _samples.pop(0)

            if log:
                print(
                    f"[PROF] {now.strftime('%H:%M:%S')} │ "
                    f"Memory: {mem_mb:7.2f} MB │ CPU: {cpu_pct:5.1f}%"
                )

            # Update plots
            times = [s.timestamp.split(" ")[-1] for s in _samples]
            mem_vals = [s.memory_mb for s in _samples]
            cpu_vals = [s.cpu_percent for s in _samples]

            ax_mem.clear()
            ax_mem.fill_between(range(len(mem_vals)), mem_vals, alpha=0.3, color="#388bfd")
            ax_mem.plot(mem_vals, color="#58a6ff", linewidth=1.5)
            ax_mem.set_title("Memory (MB)", color="#c9d1d9", fontsize=11)
            ax_mem.set_ylabel("MB", color="#8b949e")
            ax_mem.set_facecolor("#161b22")
            ax_mem.grid(True, color="#21262d", linewidth=0.5)

            ax_cpu.clear()
            ax_cpu.fill_between(range(len(cpu_vals)), cpu_vals, alpha=0.3, color="#f78166")
            ax_cpu.plot(cpu_vals, color="#f97583", linewidth=1.5)
            ax_cpu.set_title("CPU (%)", color="#c9d1d9", fontsize=11)
            ax_cpu.set_ylabel("%", color="#8b949e")
            ax_cpu.set_ylim(0, 100)
            ax_cpu.set_facecolor("#161b22")
            ax_cpu.grid(True, color="#21262d", linewidth=0.5)

            plt.pause(0.01)
            time.sleep(max(0, interval - 0.1))

    except KeyboardInterrupt:
        print("\n[INFO] Profiler stopped.")
        plt.ioff()
        if export_path:
            export_samples(_samples, export_path, export_format)
        plt.show()


def _headless_loop(
    process: psutil.Process,
    interval: int,
    log: bool,
    export_path: str | None,
    export_format: str | None,
) -> None:
    """Fallback loop without matplotlib."""
    try:
        while True:
            mem_mb = process.memory_info().rss / (1024 * 1024)
            cpu_pct = psutil.cpu_percent(interval=0.1)
            now = datetime.now()
            _samples.append(Sample(
                timestamp=now.strftime("%Y-%m-%d %H:%M:%S"),
                memory_mb=round(mem_mb, 2),
                cpu_percent=round(cpu_pct, 1),
            ))
            if len(_samples) > MAX_SAMPLES:
                _samples.pop(0)
            if log:
                print(
                    f"[PROF] {now.strftime('%H:%M:%S')} │ "
                    f"Memory: {mem_mb:7.2f} MB │ CPU: {cpu_pct:5.1f}%"
                )
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[INFO] Profiler stopped.")
        if export_path:
            export_samples(_samples, export_path, export_format)
