"""The enforcement gate fails on each thing it exists to catch.

Every test plants one violation in a copy of the repository, because the
failures this gate is built for are all edits somebody makes on purpose
for a good local reason: a row reworded, a step replaced with a shorter
one, a table row added in a hurry. None of them looks like a mistake at
the time, which is why a machine has to hold the pairing.

The last test is the one the audit earned. A mechanism swapped for
something that does not do the job, while the row above it stays exactly
as it was, is the shape that ran for months undetected.
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_against(
    enforcement: str | None = None, mechanisms: str | None = None
) -> subprocess.CompletedProcess[str]:
    """Run the gate over a copy of the repository, so a planted violation
    never touches the working tree.

    The whole tree is copied rather than a list of the files the gate
    reads. A list would have to be maintained as the gate grows, and an
    out-of-date list makes the harness fail while the repository is fine,
    which is the same maintenance trap this gate exists to close.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "repo"
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(
            ".git", "__pycache__", "*.pyc"
        ))
        if enforcement is not None:
            (root / "ENFORCEMENT.md").write_text(enforcement)
        if mechanisms is not None:
            (root / "mechanisms.json").write_text(mechanisms)
        return subprocess.run(
            [sys.executable, str(root / "scripts" / "check_mechanisms.py")],
            capture_output=True, text=True, check=False,
        )


class Mechanisms(unittest.TestCase):
    def setUp(self) -> None:
        self.enforcement = (ROOT / "ENFORCEMENT.md").read_text()
        self.mechanisms = (ROOT / "mechanisms.json").read_text()

    def test_the_repository_as_it_stands_passes(self) -> None:
        result = run_against()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_a_blocking_row_with_no_mechanism_fails(self) -> None:
        planted = self.enforcement.replace(
            "| Behavior matches its tests | pytest |",
            "| Inputs are validated somewhere | good intentions | nothing |\n"
            "| Behavior matches its tests | pytest |",
            1,
        )
        result = run_against(enforcement=planted)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Inputs are validated somewhere", result.stderr)

    def test_a_reworded_row_fails(self) -> None:
        """Renaming a row orphans its mechanism, and the point of failing
        is to make whoever renames it look at the mechanism again."""
        planted = self.enforcement.replace(
            "| The spreadsheet exit stays escaped |",
            "| The spreadsheet export stays escaped |",
            1,
        )
        result = run_against(enforcement=planted)
        self.assertEqual(result.returncode, 1)
        self.assertIn("The spreadsheet export stays escaped", result.stderr)
        self.assertIn("The spreadsheet exit stays escaped", result.stderr)

    def test_a_mechanism_recorded_for_no_row_fails(self) -> None:
        data = json.loads(self.mechanisms)
        data["mechanisms"].append({
            "rule": "A rule nobody wrote down",
            "table": "Blocked in the pipeline",
            "artifacts": [
                {"holder": "this", "path": "STANDARDS.md", "pattern": "the"}
            ],
        })
        result = run_against(mechanisms=json.dumps(data))
        self.assertEqual(result.returncode, 1)
        self.assertIn("is in no blocking table", result.stderr)

    def test_a_named_file_that_does_not_exist_fails(self) -> None:
        data = json.loads(self.mechanisms)
        data["mechanisms"][0]["artifacts"][0]["path"] = "scripts/wishful.sh"
        result = run_against(mechanisms=json.dumps(data))
        self.assertEqual(result.returncode, 1)
        self.assertIn("names a file that does not exist", result.stderr)

    def test_a_mechanism_outside_this_repository_must_name_it(self) -> None:
        """Declared and verified must not look alike, and a declaration
        that names no repository is neither."""
        data = json.loads(self.mechanisms)
        for entry in data["mechanisms"]:
            for artifact in entry["artifacts"]:
                if artifact["holder"] == "application":
                    del artifact["repository"]
                    break
            else:
                continue
            break
        result = run_against(mechanisms=json.dumps(data))
        self.assertEqual(result.returncode, 1)
        self.assertIn("without naming the repository", result.stderr)

    def test_a_path_in_the_prose_that_exists_nowhere_fails(self) -> None:
        planted = self.enforcement.replace(
            "## The scale",
            "Run `scripts/check_everything.py` at each release.\n\n## The scale",
            1,
        )
        result = run_against(enforcement=planted)
        self.assertEqual(result.returncode, 1)
        self.assertIn("scripts/check_everything.py", result.stderr)

    def test_a_mechanism_swapped_for_something_weaker_fails(self) -> None:
        """The audit's own finding, planted. The template's secret scan is
        replaced with the action it used to use, which scans the event's
        commit range, while the row above it still says full history. The
        row reads correctly and the repository no longer does it."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(
                ".git", "__pycache__", "*.pyc"
            ))
            workflow = root / "template" / ".github" / "workflows" / "ci.yml"
            text = workflow.read_text()
            start = text.index("      # The binary, not the action.")
            stop = text.index("  # The workflows are code")
            workflow.write_text(
                text[:start]
                + "      - name: Secret scan over full history (gitleaks)\n"
                  "        uses: gitleaks/gitleaks-action@e0c47f4f8be36e29"
                  "cdc102c57e68cb5cbf0e8d1e  # v3.0.0\n\n"
                + text[stop:]
            )
            result = subprocess.run(
                [sys.executable, str(root / "scripts" / "check_mechanisms.py")],
                capture_output=True, text=True, check=False,
            )
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("No secret in any commit", result.stderr)
        self.assertIn("no longer matches", result.stderr)


if __name__ == "__main__":
    unittest.main()
