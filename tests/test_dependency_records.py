"""The dependency record check: a package with no row fails, a row with
no package fails, a complete record passes, and doctrine.yml chooses
the trees."""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_dependency_records.py"
HEADER = "| Package | Canonical source | Role | Brought in by |\n|---|---|---|---|\n"


def run(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), str(repo)], capture_output=True, text=True, timeout=60)  # noqa: S603


def test_a_complete_record_passes(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("fastapi==1.0 \\\n    --hash=sha256:a\nstarlette==2.0 \\\n    --hash=sha256:b\n")
    (tmp_path / "DEPENDENCIES.md").write_text(HEADER + "| fastapi | x | web | chosen |\n| Starlette | x | toolkit | fastapi |\n")
    assert run(tmp_path).returncode == 0


def test_a_package_with_no_record_fails(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("fastapi==1.0\nopentelemetry-api==1.45.0\n")
    (tmp_path / "DEPENDENCIES.md").write_text(HEADER + "| fastapi | x | web | chosen |\n")
    completed = run(tmp_path)
    assert completed.returncode == 1 and "opentelemetry-api" in completed.stdout


def test_a_record_with_no_package_fails(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("fastapi==1.0\n")
    (tmp_path / "DEPENDENCIES.md").write_text(HEADER + "| fastapi | x | web | chosen |\n| greenlet | x | gone | sqlalchemy |\n")
    completed = run(tmp_path)
    assert completed.returncode == 1 and "greenlet" in completed.stdout


def test_doctrine_yml_chooses_the_trees(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("fastapi==1.0\n")
    (tmp_path / "requirements-docs.txt").write_text("mkdocs==1.0\n")
    (tmp_path / "doctrine.yml").write_text("kind: application\ndependency_trees:\n  - requirements-docs.txt\n")
    (tmp_path / "DEPENDENCIES.md").write_text(HEADER + "| mkdocs | x | docs | chosen |\n")
    assert run(tmp_path).returncode == 0


def test_no_tree_passes(tmp_path: Path) -> None:
    assert run(tmp_path).returncode == 0
