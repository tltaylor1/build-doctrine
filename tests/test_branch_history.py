"""The branch history check: a branch of plain commits passes, a branch
carrying a merge commit fails and names it, a missing base skips out
loud, and on a pull request the head is the branch itself (D-047)."""

import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_branch_history  # noqa: E402


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, timeout=60)  # noqa: S603, S607


class BranchHistory(unittest.TestCase):
    def setUp(self) -> None:
        # The pipeline sets these on pull request runs; the tests build
        # their own repositories and must not read them.
        self.enterContext(mock.patch.dict(os.environ, {"GITHUB_BASE_REF": "", "GITHUB_HEAD_REF": ""}))
        self.repo = Path(self.enterContext(tempfile.TemporaryDirectory()))
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "t@t")
        git(self.repo, "config", "user.name", "t")
        (self.repo / "a.txt").write_text("a\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "base")

    def commit(self, name: str) -> None:
        (self.repo / name).write_text(name + "\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", name)

    def test_a_branch_of_plain_commits_passes(self) -> None:
        git(self.repo, "switch", "-qc", "feature")
        self.commit("b.txt")
        self.assertEqual(check_branch_history.main([str(self.repo), "--base", "main"]), 0)

    def test_a_branch_carrying_a_merge_commit_fails_and_names_it(self) -> None:
        git(self.repo, "switch", "-qc", "other")
        self.commit("c.txt")
        git(self.repo, "switch", "-qc", "feature", "main")
        self.commit("b.txt")
        git(self.repo, "merge", "-q", "--no-edit", "other")
        with mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            code = check_branch_history.main([str(self.repo), "--base", "main"])
        self.assertEqual(code, 1)
        self.assertIn("Merge branch 'other'", out.getvalue())

    def test_no_base_skips_out_loud(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            self.assertEqual(check_branch_history.main([str(self.repo)]), 0)
        self.assertIn("skipped", out.getvalue())

    def test_on_a_pull_request_the_head_is_the_branch_not_the_checkout(self) -> None:
        with mock.patch.dict(os.environ, {"GITHUB_BASE_REF": "main", "GITHUB_HEAD_REF": "feature"}):
            self.assertEqual(check_branch_history.refs(None, None), ("origin/main", "origin/feature"))

    def test_a_base_given_by_hand_compares_with_the_checkout(self) -> None:
        with mock.patch.dict(os.environ, {"GITHUB_BASE_REF": "main", "GITHUB_HEAD_REF": "feature"}):
            self.assertEqual(check_branch_history.refs("main", None), ("main", "HEAD"))

