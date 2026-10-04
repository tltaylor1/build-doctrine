#!/usr/bin/env python3
"""Refuse a copy of the standards that is behind the source.

    python3 scripts/check_doctrine_copy.py /path/to/repo

Each repository carries STANDARDS.md as AGENTS.md, the file coding
agents read. A copy drifts the day the source changes, silently, and
the agent then works from rules the source no longer states. The
application repository's copy was 358 lines against a 995-line source
when this was noticed (October 2026), and the rules broken that week
were absent from the file the agent was reading.

The copy may open with a preamble saying where it came from; the text
from the first top-level heading on must match the source exactly.
Exit status is 1 on a difference, with the first differing line named.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SOURCE = HERE / "STANDARDS.md"


def body(text: str) -> list[str]:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("# "):
            return lines[i:]
    return lines


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    copy = root / "AGENTS.md"
    if not copy.exists():
        print(f"no AGENTS.md in {root}; copy STANDARDS.md there with a one-line CLAUDE.md pointing to it")
        return 1
    want, have = body(SOURCE.read_text()), body(copy.read_text())
    for number, (w, h) in enumerate(zip(want, have), 1):
        if w != h:
            print(f"AGENTS.md differs from STANDARDS.md at body line {number}:\n  source: {w[:90]}\n  copy:   {h[:90]}")
            return 1
    if len(want) != len(have):
        print(f"AGENTS.md is {len(have)} body lines; STANDARDS.md is {len(want)}; bring the copy up to date")
        return 1
    print("AGENTS.md matches STANDARDS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
