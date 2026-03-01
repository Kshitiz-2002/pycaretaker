"""
Unit tests for PyCareTaker core modules.
Run with:  python -m pytest tests/test_core.py -v
"""

import json
import csv
import io
import os
import sys
import tempfile
import unittest

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pycaretaker.core.export import Sample, export_csv, export_json, export_samples
from pycaretaker.core.diff import parse_requirements
from pycaretaker.plugins import discover_plugins


class TestExportCSV(unittest.TestCase):
    """Test CSV export of profiling samples."""

    def test_export_csv_creates_file(self):
        samples = [
            Sample(timestamp="2026-01-01 12:00:00", memory_mb=50.0, cpu_percent=10.0),
            Sample(timestamp="2026-01-01 12:00:05", memory_mb=52.5, cpu_percent=15.3),
        ]
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            export_csv(samples, path)
            self.assertTrue(os.path.exists(path))
            with open(path) as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            self.assertEqual(len(rows), 2)
            self.assertAlmostEqual(float(rows[0]["memory_mb"]), 50.0)
            self.assertAlmostEqual(float(rows[1]["cpu_percent"]), 15.3)
        finally:
            os.unlink(path)


class TestExportJSON(unittest.TestCase):
    """Test JSON export of profiling samples."""

    def test_export_json_creates_file(self):
        samples = [
            Sample(timestamp="2026-01-01 12:00:00", memory_mb=50.0, cpu_percent=10.0),
        ]
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            export_json(samples, path)
            self.assertTrue(os.path.exists(path))
            with open(path) as f:
                data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["timestamp"], "2026-01-01 12:00:00")
        finally:
            os.unlink(path)


class TestExportAutoDetect(unittest.TestCase):
    """Test format auto-detection in export_samples."""

    def test_csv_extension(self):
        samples = [Sample(timestamp="t", memory_mb=1.0, cpu_percent=2.0)]
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            export_samples(samples, path)
            with open(path) as f:
                content = f.read()
            self.assertIn("timestamp", content)
            self.assertIn("memory_mb", content)
        finally:
            os.unlink(path)

    def test_json_extension(self):
        samples = [Sample(timestamp="t", memory_mb=1.0, cpu_percent=2.0)]
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            export_samples(samples, path)
            with open(path) as f:
                data = json.load(f)
            self.assertIsInstance(data, list)
        finally:
            os.unlink(path)


class TestDiffParsing(unittest.TestCase):
    """Test requirements.txt parsing."""

    def test_parse_simple(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("flask==2.3.0\nrequests==2.31.0\n# comment\nnumpy\n")
            path = f.name
        try:
            pkgs = parse_requirements(path)
            self.assertEqual(pkgs["flask"], "2.3.0")
            self.assertEqual(pkgs["requests"], "2.31.0")
            self.assertEqual(pkgs["numpy"], "")
            self.assertNotIn("# comment", pkgs)
        finally:
            os.unlink(path)

    def test_parse_nonexistent(self):
        pkgs = parse_requirements("/nonexistent/file.txt")
        self.assertEqual(pkgs, {})


class TestPluginDiscovery(unittest.TestCase):
    """Test plugin file discovery."""

    def test_no_directory(self):
        plugins = discover_plugins("/nonexistent/dir")
        self.assertEqual(plugins, [])

    def test_finds_py_files(self):
        with tempfile.TemporaryDirectory() as d:
            # Create some files
            for name in ["checker.py", "scanner.py", "_private.py", "readme.txt"]:
                with open(os.path.join(d, name), "w") as f:
                    f.write("# test")
            plugins = discover_plugins(d)
            basenames = [os.path.basename(p) for p in plugins]
            self.assertIn("checker.py", basenames)
            self.assertIn("scanner.py", basenames)
            self.assertNotIn("_private.py", basenames)
            self.assertNotIn("readme.txt", basenames)


class TestDepsImport(unittest.TestCase):
    """Verify deps module import succeeds."""

    def test_import(self):
        from pycaretaker.core.deps import build_dependency_graph, _parse_requires
        # Test require parsing
        result = _parse_requires(["requests>=2.0", "flask; extra == 'web'", "numpy"])
        self.assertIn("requests", result)
        self.assertNotIn("flask", result)  # extra-only dependency
        self.assertIn("numpy", result)


class TestOutdatedImport(unittest.TestCase):
    """Verify outdated module import and version comparison."""

    def test_version_status(self):
        from pycaretaker.core.outdated import _version_status
        self.assertEqual(_version_status("1.0.0", "1.0.0"), "up-to-date")
        self.assertEqual(_version_status("1.0.0", "2.0.0"), "outdated")
        self.assertEqual(_version_status("2.0.0", "1.0.0"), "up-to-date")


if __name__ == "__main__":
    unittest.main()
