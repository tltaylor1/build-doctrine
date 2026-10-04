"""The doctrine copy check: a copy behind the source is refused, with
the first differing line named, and a current copy passes."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_doctrine_copy.py"


def run(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT), str(repo)], capture_output=True, text=True, timeout=60
    )


def test_a_current_copy_passes(tmp_path: Path) -> None:
    source = (ROOT / "STANDARDS.md").read_text()
    (tmp_path / "AGENTS.md").write_text("Copied from build-doctrine.\n\n" + source)
    assert run(tmp_path).returncode == 0


def test_a_copy_behind_the_source_is_refused(tmp_path: Path) -> None:
    source = (ROOT / "STANDARDS.md").read_text().splitlines()
    (tmp_path / "AGENTS.md").write_text("\n".join(source[:-40]) + "\n")
    completed = run(tmp_path)
    assert completed.returncode == 1
    assert "bring the copy up to date" in completed.stdout or "differs" in completed.stdout


def test_a_missing_copy_is_refused(tmp_path: Path) -> None:
    assert run(tmp_path).returncode == 1
