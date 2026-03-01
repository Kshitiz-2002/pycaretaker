"""
Export helpers — save profiling data to CSV or JSON.
"""

import csv
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List


@dataclass
class Sample:
    """A single profiling sample."""
    timestamp: str
    memory_mb: float
    cpu_percent: float


def export_csv(samples: List[Sample], filepath: str) -> None:
    """Write profiling samples to a CSV file."""
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "memory_mb", "cpu_percent"])
        writer.writeheader()
        for s in samples:
            writer.writerow(asdict(s))
    print(f"[SUCCESS] Exported {len(samples)} samples to {filepath}")


def export_json(samples: List[Sample], filepath: str) -> None:
    """Write profiling samples to a JSON file."""
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    data = [asdict(s) for s in samples]
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[SUCCESS] Exported {len(samples)} samples to {filepath}")


def export_samples(samples: List[Sample], filepath: str, fmt: str | None = None) -> None:
    """
    Export samples to a file.
    Format is auto-detected from extension or forced with `fmt` ('csv' | 'json').
    """
    if fmt is None:
        ext = os.path.splitext(filepath)[1].lower()
        fmt = "json" if ext == ".json" else "csv"

    if fmt == "json":
        export_json(samples, filepath)
    else:
        export_csv(samples, filepath)
