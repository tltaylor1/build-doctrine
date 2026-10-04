"""The doctrine copy check: a current rendering passes, a copy behind
the source is refused with the first differing line named, a missing
copy is refused, --write produces a copy that passes, and the
rendering points relative links at this repository."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_doctrine_copy.py"
sys.path.insert(0, str(ROOT / "scripts"))
import check_doctrine_copy  # noqa: E402


def run(repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT), str(repo), *extra], capture_output=True, text=True, timeout=60
    )


def test_write_then_check_passes(tmp_path: Path) -> None:
    assert run(tmp_path, "--write").returncode == 0
    assert (tmp_path / "AGENTS.md").read_text().startswith("These standards originate")
    assert run(tmp_path).returncode == 0


def test_a_copy_behind_the_source_is_refused(tmp_path: Path) -> None:
    run(tmp_path, "--write")
    lines = (tmp_path / "AGENTS.md").read_text().splitlines()
    (tmp_path / "AGENTS.md").write_text("\n".join(lines[:-40]) + "\n")
    completed = run(tmp_path)
    assert completed.returncode == 1 and "bring it current" in completed.stdout


def test_a_missing_copy_is_refused(tmp_path: Path) -> None:
    assert run(tmp_path).returncode == 1


def test_an_existing_preamble_is_kept(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("Adopted at project start.\n\n# Standards\nold\n")
    run(tmp_path, "--write")
    text = (tmp_path / "AGENTS.md").read_text()
    assert text.startswith("Adopted at project start.\n\n# Standards")
    assert run(tmp_path).returncode == 0


def test_relative_links_point_at_this_repository() -> None:
    out = check_doctrine_copy.render("see [ENFORCEMENT.md](ENFORCEMENT.md) and [the scale](ENFORCEMENT.md#the-scale) and [x](https://a.b/c.md)")
    assert out == ("see [ENFORCEMENT.md](https://github.com/tltaylor1/build-doctrine/blob/main/ENFORCEMENT.md) "
                   "and [the scale](https://github.com/tltaylor1/build-doctrine/blob/main/ENFORCEMENT.md#the-scale) and [x](https://a.b/c.md)")
