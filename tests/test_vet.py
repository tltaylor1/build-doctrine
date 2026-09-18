"""The vetting script notices what runs at install time and renders a
record that names every field the standards require, without the
network.

The scan is the part that can silently miss: a planted install
script, build hook, fork-privileged workflow, and committed binary
must each be reported, and a clean tree must report nothing. The
render is checked against a fixed set of signals so the record's
shape cannot drift under the standards that cite it.
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import vet  # noqa: E402

SIGNALS = {
    "repo": "example/thing",
    "read": "2026-09-16",
    "scorecard": {
        "score": 6.4, "date": "2026-09-14", "commit": "abcdef123456",
        "below_floor": [{"name": "Maintained", "score": 3, "reason": "2 commit(s) in the last 90 days"}],
        "inconclusive": ["Code-Review"],
    },
    "platform": {
        "license": "MIT", "archived": False, "pushed_at": "2026-09-10",
        "stars": 12, "open_issues": 3, "default_branch": "main",
        "latest_release": "v1.2.0 on 2026-08-01", "published_advisories": 0,
    },
    "best_practices": None,
}


class Scan(unittest.TestCase):
    def test_planted_install_time_code_and_binaries_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text('{"scripts": {"postinstall": "node setup.js", "test": "jest"}}')
            (root / "setup.py").write_text("from setuptools import setup\nimport subprocess\nsetup(cmdclass={})\n")
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "ci.yml").write_text("on:\n  pull_request_target:\n")
            (root / "tool.bin").write_bytes(b"\x7fELF" + b"\0" * 32)
            (root / "readme.md").write_text("plain text\n")
            kinds = sorted(f["kind"] for f in vet.scan(root))
        self.assertEqual(kinds, ["build hook", "committed binary", "install script", "workflow"])

    def test_a_clean_tree_reports_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text('{"scripts": {"test": "jest"}}')
            (root / "app.py").write_text("print('hello')\n")
            (root / ".git").mkdir()
            (root / ".git" / "index").write_bytes(b"\x7fELF ignored inside .git")
            self.assertEqual(vet.scan(root), [])


class Concerns(unittest.TestCase):
    def test_reasons_to_stop_are_listed_and_nothing_else(self) -> None:
        signals = {
            "repo": "x/y", "read": "2026-09-16",
            "scorecard": {"score": 4.0, "date": "2026-09-14", "commit": "abc", "inconclusive": [],
                          "below_floor": [{"name": "Dangerous-Workflow", "score": 0, "reason": "script injection"},
                                          {"name": "Maintained", "score": 3, "reason": "quiet"}]},
            "platform": {"license": "none detected", "archived": True, "pushed_at": "2024-01-01",
                         "stars": 0, "open_issues": 0, "default_branch": "main",
                         "latest_release": "none", "published_advisories": 0},
            "best_practices": None,
        }
        findings = [{"kind": "install script", "path": "package.json", "detail": "postinstall: node x.js"}]
        got = vet.concerns(signals, findings)
        self.assertEqual(len(got), 5, got)
        self.assertTrue(any("Dangerous-Workflow" in g for g in got))
        self.assertFalse(any("Maintained" in g for g in got))
        self.assertTrue(any("archived" in g for g in got))
        self.assertTrue(any("no license" in g for g in got))
        self.assertTrue(any("more than a year" in g for g in got))
        self.assertTrue(any("install script" in g for g in got))

    def test_a_clean_reading_has_no_concerns(self) -> None:
        self.assertEqual(vet.concerns(SIGNALS, []), [])
        self.assertIn("None found", vet.render(SIGNALS, [], Path("/tmp/checkout")))


class Dependencies(unittest.TestCase):
    def test_fixed_serious_findings_are_a_concern_and_others_are_not(self) -> None:
        deps = {"targets": ["requirements.txt"], "findings": [
            {"package": "a", "installed": "1", "fixed": "2", "id": "CVE-1", "severity": "HIGH"},
            {"package": "b", "installed": "1", "fixed": "no fix", "id": "CVE-2", "severity": "CRITICAL"},
            {"package": "c", "installed": "1", "fixed": "2", "id": "CVE-3", "severity": "LOW"},
        ]}
        got = vet.concerns({**SIGNALS, "dependencies": deps}, [])
        self.assertEqual(got, ["1 critical or high vulnerabilities with a published fix in the dependency tree"])
        text = vet.render({**SIGNALS, "dependencies": deps}, [], Path("/tmp/checkout"))
        self.assertIn("Dependency tree", text)
        self.assertIn("high: a 1, CVE-1, fixed in 2", text)
        self.assertIn("critical: b 1, CVE-2, fixed in no fix", text)
        self.assertNotIn("CVE-3", text)

    def test_missing_scanner_is_stated(self) -> None:
        text = vet.render({**SIGNALS, "dependencies": None}, [], Path("/tmp/checkout"))
        self.assertIn("not scanned; trivy is not installed", text)


class Record(unittest.TestCase):
    def test_record_names_every_required_field(self) -> None:
        text = vet.render(SIGNALS, [], Path("/tmp/checkout"))
        for needle in (
            "Scorecard 6.4 / 10", "Maintained, 3", "Inconclusive", "Code-Review",
            "License: MIT", "Latest release: v1.2.0", "advisories: 0",
            "Best Practices**: no entry", "No install scripts", "Concerns",
            "Pinned to", "Fetched through", "Static analysis", "License compatible",
            "Runs with", "Sign-in", "Logs", "Major dependencies",
            "Not reviewed", "Accepted by", "Expires", "Full review scheduled",
        ):
            self.assertIn(needle, text, needle)

    def test_record_states_when_nothing_could_be_read(self) -> None:
        text = vet.render({"repo": "x/y", "read": "2026-09-16", "scorecard": None,
                           "platform": None, "best_practices": None}, None, None)
        self.assertIn("no result", text)
        self.assertIn("could not be read", text)
        self.assertIn("not run; pass --path", text)


if __name__ == "__main__":
    unittest.main()
