"""The coverage gate holds the three properties it claims.

Each test plants one violation in a copy of the real documents and
requires the gate to name it, which is the same standard the doctrine
sets for every other control: a check that has never been seen to fail
is a check nobody has reason to trust.

The fourth test is the one that matters most in practice. It runs the
gate against the repository as it stands and requires a clean exit, so
a rule added without a coverage row fails here rather than in a review
six months later.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "check_coverage.py"


def run_against(standards: str, coverage: str) -> subprocess.CompletedProcess[str]:
    """Run the gate over a copy of the documents, so a planted
    violation never touches the working tree."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "scripts").mkdir()
        (root / "scripts" / "check_coverage.py").write_text(GATE.read_text())
        (root / "STANDARDS.md").write_text(standards)
        (root / "COVERAGE.md").write_text(coverage)
        return subprocess.run(
            [sys.executable, str(root / "scripts" / "check_coverage.py")],
            capture_output=True, text=True, check=False,
        )


class Coverage(unittest.TestCase):
    def setUp(self) -> None:
        self.standards = (ROOT / "STANDARDS.md").read_text()
        self.coverage = (ROOT / "COVERAGE.md").read_text()

    def test_the_repository_as_it_stands_passes(self) -> None:
        result = run_against(self.standards, self.coverage)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_a_rule_nobody_mapped_fails(self) -> None:
        """A rule added to the standards and mapped nowhere. This also
        covers a rename, since renaming leaves the new text unmapped."""
        planted = self.standards.replace(
            "- **Deny by default.**",
            "- **Sessions are pinned to an address.** Invented for this test.\n"
            "- **Deny by default.**",
            1,
        )
        result = run_against(planted, self.coverage)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Sessions are pinned to an address", result.stderr)

    def test_a_framework_losing_a_row_fails(self) -> None:
        planted = self.coverage.replace(
            "| A10 Server-Side Request Forgery", "| A10 removed for this test |\n"
            "| A10 Server-Side Request Forgery", 1,
        )
        # Adding a row is as wrong as dropping one: the count is the
        # framework's own and neither direction is an accident.
        result = run_against(self.standards, planted)
        self.assertEqual(result.returncode, 1)
        self.assertIn("OWASP Top 10 (2021)", result.stderr)

    def test_a_gap_without_a_trigger_fails(self) -> None:
        """A row that says it has no rule must say what would produce
        one, or it is a gap nobody will close."""
        planted = self.coverage.replace(
            "Triggered by the first project that grounds a model on data it stores",
            "nothing here does this",
            1,
        )
        result = run_against(self.standards, planted)
        self.assertEqual(result.returncode, 1)
        self.assertIn("no rule and no trigger", result.stderr)


if __name__ == "__main__":
    unittest.main()
