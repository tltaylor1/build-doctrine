"""The scorer answers to the scale it implements.

Each test builds a small repository in a temporary directory and holds
the scorer to a stated level: absence scores zero, presence scores
three when only the scorer checks it and four when CI runs the
scorer, a proof lifts a four to five and nothing else does, and an
exclusion is named rather than scored. Standard library only, so the
doctrine repository needs no dependency to test itself.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import score  # noqa: E402


def git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), *args], check=True,
        capture_output=True, text=True,
    )


def repo_with_history(root: Path, subjects: list[str], author: str = "Terry") -> None:
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "t@example.invalid")
    git(root, "config", "user.name", author)
    git(root, "config", "commit.gpgsign", "false")
    for i, subject in enumerate(subjects):
        (root / f"f{i}.txt").write_text(subject)
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", subject)


def levels(results: list[score.Result]) -> dict[str, int | None]:
    return {r.rule: r.level for r in results}


class EmptyRepository(unittest.TestCase):
    def test_absence_scores_zero_and_names_the_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            kind, results = score.score(Path(tmp), None, "application")
            got = levels(results)
            self.assertEqual(got["readme"], 0)
            self.assertEqual(got["license"], 0)
            self.assertEqual(got["troubleshooting"], 0)
            self.assertEqual(got["commit-subjects"], 0)
            self.assertIsNone(got["generated-artifact-parity"])


class PresenceLevels(unittest.TestCase):
    def test_presence_is_three_on_demand_and_four_when_ci_runs_the_scorer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# x\n\n## Run it\n\n```\nmake\n```\n")
            (root / "LICENSE").write_text("MIT")
            self.assertEqual(levels(score.score(root, None, "reference")[1])["license"], 3)
            wf = root / ".github" / "workflows"
            wf.mkdir(parents=True)
            (wf / "ci.yml").write_text(
                "jobs:\n  score:\n    steps:\n"
                "      - uses: actions/checkout@" + "a" * 40 + "\n"
                "      - run: python3 scripts/score.py .\n"
            )
            got = levels(score.score(root, None, "reference")[1])
            self.assertEqual(got["license"], 4)
            self.assertEqual(got["run-instructions"], 1)


class ProofAndExclusion(unittest.TestCase):
    def test_a_proof_lifts_only_a_four_and_an_exclusion_is_named(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# x\n")
            (root / "LICENSE").write_text("MIT")
            wf = root / ".github" / "workflows"
            wf.mkdir(parents=True)
            (wf / "ci.yml").write_text("      - run: python3 scripts/score.py .\n")
            (root / "doctrine.yml").write_text(
                "kind: reference\n"
                "proven:\n"
                "  license: https://example.invalid/run/1\n"
                "  readme: https://example.invalid/run/2\n"
                "exclusions:\n"
                "  security-policy: a table of public facts serves no code\n"
            )
            kind, results = score.score(root, None)
            self.assertEqual(kind, "reference")
            got = levels(results)
            self.assertEqual(got["license"], 5)
            self.assertEqual(got["readme"], 5)
            self.assertIsNone(got["security-policy"])
            reason = next(r.reason for r in results if r.rule == "security-policy")
            self.assertTrue(reason.startswith("excluded: "))
            # A rule at zero stays at zero however much proof is claimed.
            (root / "doctrine.yml").write_text(
                "kind: reference\nproven:\n  contributing: https://example.invalid\n"
            )
            self.assertEqual(levels(score.score(root, None)[1])["contributing"], 0)


class CommitSubjects(unittest.TestCase):
    def test_identifier_led_subjects_pass_and_bot_traffic_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_with_history(root, ["D-001: the first rule", "README: the shape"])
            self.assertEqual(levels(score.score(root, None, "reference")[1])["commit-subjects"], 3)
            (root / "bump.txt").write_text("x")
            git(root, "add", "-A")
            git(root, "-c", "user.name=dependabot[bot]", "commit", "-q", "-m",
                "Bump something from 1 to 2")
            self.assertEqual(levels(score.score(root, None, "reference")[1])["commit-subjects"], 3)
            (root / "plain.txt").write_text("x")
            git(root, "add", "-A")
            git(root, "commit", "-q", "-m", "fix a thing")
            self.assertEqual(levels(score.score(root, None, "reference")[1])["commit-subjects"], 0)


class PinnedActions(unittest.TestCase):
    def test_one_unpinned_use_fails_the_rule(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wf = root / ".github" / "workflows"
            wf.mkdir(parents=True)
            (wf / "ci.yml").write_text(
                "      - uses: actions/checkout@" + "b" * 40 + "\n"
                "      - uses: actions/setup-python@v5\n"
            )
            self.assertEqual(levels(score.score(root, None, "reference")[1])["pinned-actions"], 0)
            (wf / "ci.yml").write_text("      - uses: actions/checkout@" + "b" * 40 + "\n")
            self.assertEqual(levels(score.score(root, None, "reference")[1])["pinned-actions"], 3)


if __name__ == "__main__":
    unittest.main()
