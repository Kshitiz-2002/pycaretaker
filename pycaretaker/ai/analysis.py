"""
AI memory/CPU analysis — interprets profiling data and provides insights.
"""

from typing import List

from pycaretaker.ai.backend import get_backend
from pycaretaker.core.export import Sample


def analyze_profiling_data(samples: List[Sample]) -> str:
    """Send profiling summary to the AI and return its analysis."""
    ai = get_backend()
    if not ai.available:
        print("[INFO] AI backend not available, skipping analysis.")
        return ""

    if not samples:
        return "No profiling data to analyze."

    # Build summary stats
    mem_vals = [s.memory_mb for s in samples]
    cpu_vals = [s.cpu_percent for s in samples]
    duration_str = f"{samples[0].timestamp} → {samples[-1].timestamp}"

    summary = (
        f"Profiling data ({len(samples)} samples, {duration_str}):\n"
        f"  Memory: min={min(mem_vals):.1f} MB, max={max(mem_vals):.1f} MB, "
        f"avg={sum(mem_vals)/len(mem_vals):.1f} MB\n"
        f"  CPU:    min={min(cpu_vals):.1f}%, max={max(cpu_vals):.1f}%, "
        f"avg={sum(cpu_vals)/len(cpu_vals):.1f}%\n"
        f"  Trend:  first_mem={mem_vals[0]:.1f} MB → last_mem={mem_vals[-1]:.1f} MB "
        f"(delta={mem_vals[-1]-mem_vals[0]:+.1f} MB)"
    )

    prompt = (
        f"{summary}\n\n"
        "Analyze this profiling data. Look for:\n"
        "1. Memory leaks (steadily increasing memory)\n"
        "2. CPU spikes or sustained high usage\n"
        "3. Overall health assessment\n"
        "Be concise (3-5 sentences max)."
    )

    analysis = ai.ask(prompt)

    if analysis:
        print(f"\n  🤖 AI Profiling Analysis:")
        for line in analysis.split("\n"):
            print(f"     {line}")
        print()

    return analysis
