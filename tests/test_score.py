"""The scorer answers to the scale it implements.

Each test builds a small repository in a temporary directory and holds
the scorer to a stated level: absence scores zero, presence scores
three when only the scorer checks it and four when CI runs the
scorer, a proof lifts a four to five and nothing else does, and an
exclusion is named rather than scored. Standard library only, so the
doctrine repository needs no dependency to test itself.
"""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
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


    def test_an_agent_app_authors_history_the_rule_still_reads(self) -> None:
        """A repository whose changes are all proposed by its agent app
        has a history, and the rule judges it. Excluding every author
        carrying the bot suffix made that repository read as having no
        history at all, and scored it zero while every subject
        conformed (D-029)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_with_history(root, ["D-001: the first rule"])
            (root / "one.txt").write_text("x")
            git(root, "add", "-A")
            git(root, "-c", "user.name=an-agent[bot]", "commit", "-q", "-m",
                "D-002: the agent's own change")
            self.assertEqual(
                levels(score.score(root, None, "reference")[1])["commit-subjects"], 3)
            # And it is judged, not merely counted: a subject the agent
            # writes without an identifier fails the same way a
            # person's would.
            (root / "two.txt").write_text("x")
            git(root, "add", "-A")
            git(root, "-c", "user.name=an-agent[bot]", "commit", "-q", "-m",
                "fix a thing")
            self.assertEqual(
                levels(score.score(root, None, "reference")[1])["commit-subjects"], 0)


    def test_a_subphase_number_leads_a_subject(self) -> None:
        """A repository built to a phase plan commits work as the
        subphase it belongs to, and that identifies the change as well
        as a decision number does (D-030)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_with_history(root, ["1.5: the delta, which is the product",
                                     "1.1a: the neutral tables"])
            self.assertEqual(
                levels(score.score(root, None, "reference")[1])["commit-subjects"], 3)
            # Still a rule: a bare number or a sentence is not one.
            (root / "x.txt").write_text("x")
            git(root, "add", "-A")
            git(root, "commit", "-q", "-m", "15: no dot, no identifier")
            self.assertEqual(
                levels(score.score(root, None, "reference")[1])["commit-subjects"], 0)


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


class BadgeOutput(unittest.TestCase):
    def test_the_badge_carries_the_mean_and_a_color_band(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kind, results = score.score(root, None, "profile")
            doc = score.badge(root, results)
            self.assertEqual(doc["schemaVersion"], 1)
            self.assertEqual(doc["label"], "build-doctrine score")
            self.assertEqual(doc["message"], "0.0 / 5")
            self.assertEqual(doc["color"], "red")
            results[0].level = 5
            self.assertEqual(score.badge(root, [results[0]])["color"], "brightgreen")


class ParityChecker(unittest.TestCase):
    """The generated-artifact rule counts a real checker and nothing else.

    Every case here is one this rule got wrong while a scores table was being
    turned into a generated file. It credited a repository for a checker
    that was the scorer itself, it named one script while crediting CI for
    another, and when the detector was narrowed to argparse it scored a
    working checker driven by sys.argv as absent.
    """

    def build(self, kind: str, files: dict[str, str]) -> dict[str, tuple]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / "doctrine.yml").write_text(f"kind: {kind}\n")
            for name, text in files.items():
                (root / name).write_text(text)
            _, results = score.score(root, None, kind)
            return {r.rule: (r.level, r.reason) for r in results}

    def test_a_script_that_only_mentions_the_flag_is_not_a_checker(self) -> None:
        results = self.build("reference", {
            "scripts/notes.py": "# the --check flag would be nice one day\n",
        })
        level, reason = results["generated-artifact-parity"]
        self.assertEqual(level, 0, reason)

    def test_argparse_and_argv_both_count(self) -> None:
        for source in (
            'import argparse\np.add_argument("--check")\n',
            'import sys\nif "--check" in sys.argv:\n    pass\n',
        ):
            results = self.build("reference", {"scripts/render.py": source})
            level, reason = results["generated-artifact-parity"]
            self.assertEqual(level, 3, reason)
            self.assertIn("render.py", reason)

    def test_ci_credit_names_the_script_ci_actually_runs(self) -> None:
        """Two checkers, one of them in a workflow. The evidence must be
        about that one, not about whichever was found first."""
        results = self.build("reference", {
            "scripts/aaa_local.py": 'import argparse\np.add_argument("--check")\n',
            "scripts/zzz_gated.py": 'import argparse\np.add_argument("--check")\n',
            ".github/workflows/ci.yml": "run: python3 scripts/zzz_gated.py --check\n",
        })
        level, reason = results["generated-artifact-parity"]
        self.assertEqual(level, 4, reason)
        self.assertIn("zzz_gated.py", reason)
        self.assertNotIn("aaa_local.py", reason)

    def test_the_scorer_is_not_its_own_checker(self) -> None:
        """The detector must not match the source that implements it."""
        source = (ROOT / "scripts" / "score.py").read_text()
        self.assertNotIn("--" + "check", source)


class RuleByRuleDocumentation(unittest.TestCase):
    """ENFORCEMENT.md carries one entry per scorer rule, so the rules and
    their documentation cannot disagree about what exists."""

    def test_every_scorer_rule_is_documented(self) -> None:
        root = Path(__file__).resolve().parent.parent
        source = (root / "scripts" / "score.py").read_text()
        rules = set(re.findall(r'add\("([a-z-]+)"', source))
        text = (root / "ENFORCEMENT.md").read_text()
        head = text.index("## What the scorer reads, rule by rule")
        end = text.index("\n## ", head + 10)
        documented = set(re.findall(r"^### ([a-z-]+)$", text[head:end], re.MULTILINE))
        self.assertTrue(rules, "the scorer names no rules")
        self.assertEqual(documented, rules, sorted(documented ^ rules))
