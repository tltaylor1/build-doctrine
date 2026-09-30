#!/usr/bin/env python3
"""Refuse a retired project name in active text.

    python3 scripts/check_names.py [/path/to/repo]

A rename leaves the old name behind in related-project sections,
hooks, badges, and descriptions, and an audit finds them by hand
weeks later (D-035). This check reads the program's list of retired
names in deprecated-names.yml, beside this script's repository, and
walks the tracked text files of the repository given (this one by
default). A file that holds an old name as history is allowed by name
in that repository's doctrine.yml, either whole or for the lines that
carry a stated phrase:

    name_allowlist:
      - DECISIONS.md
      - README.md: Coming from a role-call checkout

Binary files are skipped by content, not by extension, so an image
whose bytes happen to spell a word is not a finding. Exit status is 1
when any active line carries a retired name, with the file, the line,
and the expected replacement named.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
NAMES = HERE / "deprecated-names.yml"


def retired_names(path: Path = NAMES) -> dict[str, str]:
    """The retired names and their replacements, one per line as
    `old: new`; comments and blank lines are skipped."""
    names: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        old, sep, new = line.partition(": ")
        if sep:
            names[old.strip()] = new.strip()
    return names


def allowlist(root: Path) -> list[tuple[str, str | None]]:
    """(path, phrase) pairs from doctrine.yml: a bare path allows the
    whole file, a path with a phrase allows only lines carrying it."""
    manifest = root / "doctrine.yml"
    if not manifest.exists():
        return []
    entries: list[tuple[str, str | None]] = []
    inside = False
    for raw in manifest.read_text().splitlines():
        if not raw.startswith(" ") and raw.strip():
            inside = raw.startswith("name_allowlist:")
            continue
        if inside and raw.strip().startswith("- "):
            item = raw.strip()[2:].strip()
            path, sep, phrase = item.partition(": ")
            entries.append((path.strip(), phrase.strip() if sep else None))
    return entries


def tracked_files(root: Path) -> list[Path]:
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True, check=True, timeout=60,
    ).stdout
    return [root / name for name in out.decode().split("\0") if name]


def is_text(data: bytes) -> bool:
    return b"\0" not in data[:8192]


def findings(root: Path, names: dict[str, str]) -> list[str]:
    allowed = allowlist(root)
    lowered = {old.lower(): (old, new) for old, new in names.items()}
    out: list[str] = []
    for path in tracked_files(root):
        rel = path.relative_to(root).as_posix()
        # The list and the allowlist name the old names on purpose.
        if rel in ("deprecated-names.yml", "doctrine.yml") or not path.is_file():
            continue
        data = path.read_bytes()
        if not is_text(data):
            continue
        whole = any(p == rel and phrase is None for p, phrase in allowed)
        if whole:
            continue
        phrases = [phrase for p, phrase in allowed if p == rel and phrase]
        for number, line in enumerate(data.decode("utf-8", errors="replace").splitlines(), 1):
            low = line.lower()
            if any(phrase in line for phrase in phrases):
                continue
            for key, (old, new) in lowered.items():
                if key in low:
                    out.append(f"{rel}:{number}: retired name {old!r}; expected {new!r}")
    return out


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    problems = findings(root, retired_names())
    for problem in problems:
        print(f"FAIL {problem}")
    if problems:
        print(f"{len(problems)} active line(s) carry a retired name; allow history in "
              "doctrine.yml under name_allowlist, or replace the name")
        return 1
    print("no retired name in active text")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
