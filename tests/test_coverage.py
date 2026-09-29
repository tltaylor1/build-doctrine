"""The coverage gate holds the properties it claims.

Each test plants one violation in a copy of the real documents and
requires the gate to name it, which is the same standard the doctrine
sets for every other control: a check that has never been seen to fail
is a check nobody has reason to trust.

Two of these matter more than the others. The first runs the gate
against the repository as it stands and requires a clean exit, so a
rule added without a coverage row fails here rather than in a review
six months later. The last plants a stale edition, which is the
failure that actually happened: the first COVERAGE.md mapped the 2021
Top 10 while 2025 was current, and the gate of the day hardcoded that
recollection, so it passed (D-032). The gate now reads frameworks.json
instead, and the test proves a stale row cannot pass.
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "check_coverage.py"


def run_against(
    standards: str, coverage: str, frameworks: str | None = None
) -> subprocess.CompletedProcess[str]:
    """Run the gate over a copy of the documents, so a planted
    violation never touches the working tree."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "scripts").mkdir()
        shutil.copy(GATE, root / "scripts" / "check_coverage.py")
        (root / "STANDARDS.md").write_text(standards)
        (root / "COVERAGE.md").write_text(coverage)
        (root / "frameworks.json").write_text(
            frameworks
            if frameworks is not None
            else (ROOT / "frameworks.json").read_text()
        )
        return subprocess.run(
            [sys.executable, str(root / "scripts" / "check_coverage.py")],
            capture_output=True, text=True, check=False,
        )


class Coverage(unittest.TestCase):
    def setUp(self) -> None:
        self.standards = (ROOT / "STANDARDS.md").read_text()
        self.coverage = (ROOT / "COVERAGE.md").read_text()
        self.frameworks = (ROOT / "frameworks.json").read_text()

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
        """A published item with no row. The count is the framework's
        own, so dropping one is never an accident."""
        rows = [
            line for line in self.coverage.splitlines()
            if not line.startswith("| A10:2025 ")
        ]
        result = run_against(self.standards, "\n".join(rows))
        self.assertEqual(result.returncode, 1)
        self.assertIn("no row for A10:2025", result.stderr)

    def test_a_row_for_an_item_the_data_does_not_have_fails(self) -> None:
        """The stale-edition failure, in the direction that hides best:
        a row left behind after the framework dropped the item. In 2021
        A10 was server-side request forgery, and a row still saying so
        would have sat there looking answered."""
        planted = self.coverage.replace(
            "| A10:2025 Mishandling",
            "| A10:2021 Server-Side Request Forgery | left behind | Tokens "
            "travel in a request header |\n| A10:2025 Mishandling",
            1,
        )
        result = run_against(self.standards, planted)
        self.assertEqual(result.returncode, 1)
        self.assertIn("is not in frameworks.json", result.stderr)

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

    def test_a_renamed_section_heading_fails(self) -> None:
        """The data names the section it belongs to. A heading edited on
        one side only fails rather than silently checking nothing."""
        heading = json.loads(self.frameworks)["frameworks"]["slsa"]["heading"]
        self.assertIn(f"## {heading}", self.coverage)
        planted = self.coverage.replace(f"## {heading}", "## Supply chain levels", 1)
        result = run_against(self.standards, planted)
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"no section headed {heading!r}", result.stderr)

    def test_a_new_edition_in_the_data_fails_the_document(self) -> None:
        """The refresh command's whole purpose, seen from this end. When
        a new edition lands in frameworks.json, the document that still
        maps the old one fails, which is what the first gate could not
        do because its expected values were typed by hand."""
        data = json.loads(self.frameworks)
        items = data["frameworks"]["owasp-top-10"]["items"]
        items[-1] = {"id": "A11:2030", "name": "Invented For This Test"}
        result = run_against(
            self.standards, self.coverage, json.dumps(data)
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("no row for A11:2030", result.stderr)


if __name__ == "__main__":
    unittest.main()
