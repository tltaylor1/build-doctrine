"""The dependency record check: a package with no row fails, a row with
no package fails, a complete record passes, and doctrine.yml chooses
the trees."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_dependency_records.py"
HEADER = "| Package | Canonical source | Role | Brought in by |\n|---|---|---|---|\n"


def run(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), str(repo)], capture_output=True, text=True, timeout=60)  # noqa: S603


class DependencyRecords(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def test_a_complete_record_passes(self) -> None:
        (self.repo / "requirements.txt").write_text("fastapi==1.0 \\\n    --hash=sha256:a\nstarlette==2.0 \\\n    --hash=sha256:b\n")
        (self.repo / "DEPENDENCIES.md").write_text(HEADER + "| fastapi | x | web | chosen |\n| Starlette | x | toolkit | fastapi |\n")
        self.assertEqual(run(self.repo).returncode, 0)

    def test_a_package_with_no_record_fails(self) -> None:
        (self.repo / "requirements.txt").write_text("fastapi==1.0\nopentelemetry-api==1.45.0\n")
        (self.repo / "DEPENDENCIES.md").write_text(HEADER + "| fastapi | x | web | chosen |\n")
        completed = run(self.repo)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("opentelemetry-api", completed.stdout)

    def test_a_record_with_no_package_fails(self) -> None:
        (self.repo / "requirements.txt").write_text("fastapi==1.0\n")
        (self.repo / "DEPENDENCIES.md").write_text(HEADER + "| fastapi | x | web | chosen |\n| greenlet | x | gone | sqlalchemy |\n")
        completed = run(self.repo)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("greenlet", completed.stdout)

    def test_doctrine_yml_chooses_the_trees(self) -> None:
        (self.repo / "requirements.txt").write_text("fastapi==1.0\n")
        (self.repo / "requirements-docs.txt").write_text("mkdocs==1.0\n")
        (self.repo / "doctrine.yml").write_text("kind: application\ndependency_trees:\n  - requirements-docs.txt\n")
        (self.repo / "DEPENDENCIES.md").write_text(HEADER + "| mkdocs | x | docs | chosen |\n")
        self.assertEqual(run(self.repo).returncode, 0)

    def test_no_tree_passes(self) -> None:
        self.assertEqual(run(self.repo).returncode, 0)
