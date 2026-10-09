"""The doctrine copy check: a current rendering passes, a copy behind
the source is refused with the first differing line named, a missing
copy is refused, --write produces a copy that passes, and the
rendering points relative links at this repository."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_doctrine_copy.py"
sys.path.insert(0, str(ROOT / "scripts"))
import check_doctrine_copy  # noqa: E402


def run(repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT), str(repo), *extra], capture_output=True, text=True, timeout=60
    )


class DoctrineCopy(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def test_write_then_check_passes(self) -> None:
        self.assertEqual(run(self.repo, "--write").returncode, 0)
        self.assertTrue((self.repo / "AGENTS.md").read_text().startswith("These standards originate"))
        self.assertEqual(run(self.repo).returncode, 0)

    def test_a_copy_behind_the_source_is_refused(self) -> None:
        run(self.repo, "--write")
        lines = (self.repo / "AGENTS.md").read_text().splitlines()
        (self.repo / "AGENTS.md").write_text("\n".join(lines[:-40]) + "\n")
        completed = run(self.repo)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("bring it current", completed.stdout)

    def test_a_missing_copy_is_refused(self) -> None:
        self.assertEqual(run(self.repo).returncode, 1)

    def test_an_existing_preamble_is_kept(self) -> None:
        (self.repo / "AGENTS.md").write_text("Adopted at project start.\n\n# Standards\nold\n")
        run(self.repo, "--write")
        text = (self.repo / "AGENTS.md").read_text()
        self.assertTrue(text.startswith("Adopted at project start.\n\n# Standards"))
        self.assertEqual(run(self.repo).returncode, 0)

    def test_relative_links_point_at_this_repository(self) -> None:
        out = check_doctrine_copy.render(
            "see [ENFORCEMENT.md](ENFORCEMENT.md) and [the scale](ENFORCEMENT.md#the-scale) and [x](https://a.b/c.md)"
        )
        self.assertEqual(
            out,
            "see [ENFORCEMENT.md](https://github.com/tltaylor1/build-doctrine/blob/main/ENFORCEMENT.md) "
            "and [the scale](https://github.com/tltaylor1/build-doctrine/blob/main/ENFORCEMENT.md#the-scale) "
            "and [x](https://a.b/c.md)",
        )
