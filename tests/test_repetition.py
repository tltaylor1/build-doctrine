"""The repetition check: refusal paths first. A wrong checksum is
refused before anything is extracted, an archive holding more than the
release holds is refused, a missing base skips out loud, and the
command it runs gates only new exact copies in code formats."""

import hashlib
import io
import os
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_repetition  # noqa: E402


def archive(directory: Path, members: dict[str, bytes]) -> Path:
    path = directory / check_repetition.ASSET
    with tarfile.open(path, "w:gz") as tar:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return path


class Repetition(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def test_a_wrong_checksum_is_refused(self) -> None:
        path = archive(self.dir, {"jscpd": b"not the release"})
        with self.assertRaises(check_repetition.Refused):
            check_repetition.verify(path)

    def test_a_wrong_checksum_extracts_nothing(self) -> None:
        path = archive(self.dir, {"jscpd": b"not the release"})
        with mock.patch.dict(os.environ, {"RUNNER_TEMP": str(self.dir)}), \
                mock.patch("platform.system", return_value="Linux"), \
                mock.patch("platform.machine", return_value="x86_64"):
            code = check_repetition.main([str(self.dir), "--base", "origin/main", "--archive", str(path)])
        self.assertEqual(code, 2)
        self.assertFalse((self.dir / "jscpd").exists())

    def test_the_matching_checksum_passes(self) -> None:
        path = archive(self.dir, {"jscpd": b"binary"})
        check_repetition.verify(path, hashlib.sha256(path.read_bytes()).hexdigest())

    def test_an_unexpected_member_is_refused(self) -> None:
        path = archive(self.dir, {"jscpd": b"binary", "../escape": b"x"})
        with self.assertRaises(check_repetition.Refused):
            check_repetition.extract(path, self.dir / "out")

    def test_only_the_binary_is_extracted(self) -> None:
        path = archive(self.dir, {"jscpd": b"binary", "LICENSE": b"MIT"})
        (self.dir / "out").mkdir()
        binary = check_repetition.extract(path, self.dir / "out")
        self.assertEqual(sorted(p.name for p in (self.dir / "out").iterdir()), ["jscpd"])
        self.assertTrue(os.access(binary, os.X_OK))

    def test_no_base_skips_out_loud(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            code = check_repetition.main([str(self.dir)])
        self.assertEqual(code, 0)
        self.assertIn("skipped", out.getvalue())

    def test_the_pull_request_base_is_read_from_the_environment(self) -> None:
        with mock.patch.dict(os.environ, {"GITHUB_BASE_REF": "main"}):
            self.assertEqual(check_repetition.base_ref(None), "origin/main")

    def test_the_command_measures_exact_copies_in_code_only(self) -> None:
        argv = check_repetition.command(Path("/bin/jscpd"), Path("repo"), Path("out"))
        self.assertEqual(argv[argv.index("--reporters") + 1], "json")
        formats = argv[argv.index("--format") + 1].split(",")
        self.assertIn("python", formats)
        self.assertNotIn("markdown", formats)
        self.assertNotIn("yaml", formats)
        self.assertEqual(argv[argv.index("--ignore") + 1], "**/.git/**")
        for noisier in ("--ignore-identifiers", "--ignore-literals", "--max-gap-lines", "--semantic"):
            self.assertNotIn(noisier, argv)

    def test_a_doctrine_checkout_inside_the_repository_is_skipped(self) -> None:
        repo = self.dir / "app"
        script = repo / "doctrine" / "scripts" / "check_repetition.py"
        script.parent.mkdir(parents=True)
        script.touch()
        skip = check_repetition.own_checkout(repo, script)
        self.assertEqual(skip, "doctrine/**")
        argv = check_repetition.command(Path("/bin/jscpd"), repo, Path("out"), skip)
        self.assertEqual(argv[argv.index("--ignore") + 1], "**/.git/**,doctrine/**")

    def test_the_doctrine_scanning_itself_skips_nothing_of_its_own(self) -> None:
        script = self.dir / "scripts" / "check_repetition.py"
        script.parent.mkdir(parents=True)
        script.touch()
        self.assertIsNone(check_repetition.own_checkout(self.dir, script))

    def test_a_checkout_outside_the_repository_is_not_named(self) -> None:
        script = self.dir / "elsewhere" / "scripts" / "check_repetition.py"
        script.parent.mkdir(parents=True)
        script.touch()
        (self.dir / "app").mkdir()
        self.assertIsNone(check_repetition.own_checkout(self.dir / "app", script))

    def test_more_duplicated_lines_than_the_base_fails(self) -> None:
        code, message = check_repetition.verdict(100, 112, "origin/main")
        self.assertEqual(code, 1)
        self.assertIn("100 duplicated lines on origin/main and 112", message)

    def test_the_same_or_fewer_duplicated_lines_passes(self) -> None:
        self.assertEqual(check_repetition.verdict(100, 100, "origin/main")[0], 0)
        self.assertEqual(check_repetition.verdict(100, 92, "origin/main")[0], 0)

    def test_the_count_is_read_from_the_report(self) -> None:
        report = self.dir / "jscpd-report.json"
        report.write_text('{"statistics": {"total": {"duplicatedLines": 1092}}, "duplicates": []}')
        self.assertEqual(check_repetition.duplicated_lines(report), 1092)

