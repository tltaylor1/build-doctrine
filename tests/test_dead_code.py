"""The dead-code check: it counts only what jscpd is sure of, reads the
dead lines from the report, and fails only when the change adds some
(D-046). The fetching and comparing it shares with the repetition
check are tested there."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_dead_code  # noqa: E402
from check_repetition import verdict  # noqa: E402


class DeadCode(unittest.TestCase):
    def test_only_sure_findings_in_code_categories_count(self) -> None:
        argv = check_dead_code.arguments(Path("repo"), Path("out"), None, False)
        self.assertIn("--dead-code", argv)
        self.assertEqual(argv[argv.index("--min-confidence") + 1], "85")
        categories = argv[argv.index("--dead-code-categories") + 1].split(",")
        self.assertNotIn("unused-member", categories)
        self.assertIn("unused-symbol", categories)

    def test_its_own_checkout_is_skipped_like_the_repetition_check(self) -> None:
        argv = check_dead_code.arguments(Path("repo"), Path("out"), "doctrine/**", False)
        self.assertEqual(argv[argv.index("--ignore") + 1], "**/.git/**,doctrine/**")

    def test_the_dead_lines_are_read_from_the_report(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            report = Path(d) / "basta-report.json"
            report.write_text('{"findings": [], "statistics": {"deadLines": 2}}')
            self.assertEqual(check_dead_code.dead_lines(report), 2)

    def test_more_dead_lines_than_the_base_fails(self) -> None:
        code, message = verdict(2, 9, "origin/main", check_dead_code.DEAD_CODE)
        self.assertEqual(code, 1)
        self.assertIn("dead code: the change adds to it, 2 dead lines on origin/main and 9", message)

    def test_the_same_or_fewer_dead_lines_passes(self) -> None:
        self.assertEqual(verdict(2, 2, "origin/main", check_dead_code.DEAD_CODE)[0], 0)
