"""The retired-name check (D-035): an old project name in active
text fails, a file or a line allowed as history passes, and a binary
file whose bytes spell a word is not read."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import check_names  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NAMES = {"old-project": "new-project", "old/thing": "new/thing"}


def repository(files: dict[str, bytes], manifest: str = "") -> Path:
    root = Path(tempfile.mkdtemp())
    subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
    for name, data in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    if manifest:
        (root / "doctrine.yml").write_text(manifest)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    return root


class RetiredNames(unittest.TestCase):
    def test_an_old_name_in_active_text_is_a_finding_with_its_replacement(self) -> None:
        root = repository({"README.md": b"Built beside old-project, see old/thing.\n"})
        found = check_names.findings(root, NAMES)
        self.assertEqual(len(found), 2)
        self.assertIn("README.md:1: retired name 'old-project'; expected 'new-project'", found)

    def test_the_match_ignores_case(self) -> None:
        root = repository({"a.md": b"Old-Project once\n"})
        self.assertEqual(len(check_names.findings(root, NAMES)), 1)

    def test_a_file_allowed_as_history_passes_whole(self) -> None:
        root = repository({"DECISIONS.md": b"old-project was renamed\n"},
                          "kind: doctrine\nname_allowlist:\n  - DECISIONS.md\n")
        self.assertEqual(check_names.findings(root, NAMES), [])

    def test_a_phrase_allows_only_the_lines_that_carry_it(self) -> None:
        root = repository(
            {"README.md": b"Coming from an old-project checkout, rename it.\nold-project again\n"},
            "kind: doctrine\nname_allowlist:\n  - README.md: Coming from an old-project checkout\n",
        )
        found = check_names.findings(root, NAMES)
        self.assertEqual([f.split(":")[1] for f in found], ["2"])

    def test_a_binary_file_is_not_read(self) -> None:
        root = repository({"banner.png": b"\x89PNG\x00old-project\x00"})
        self.assertEqual(check_names.findings(root, NAMES), [])

    def test_an_untracked_file_is_not_read(self) -> None:
        root = repository({"a.md": b"clean\n"})
        (root / "scratch.md").write_text("old-project\n")
        self.assertEqual(check_names.findings(root, NAMES), [])

    def test_the_program_list_names_replacements(self) -> None:
        names = check_names.retired_names()
        self.assertIn("build-doctrine", names.values())
        for old, new in names.items():
            self.assertNotEqual(old, new)
            self.assertTrue(new)

    def test_this_repository_carries_no_retired_name_in_active_text(self) -> None:
        self.assertEqual(check_names.findings(ROOT, check_names.retired_names()), [])
