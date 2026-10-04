#!/usr/bin/env python3
"""Refuse a copy of the standards that is behind the source, and write a current one.

    python3 scripts/check_doctrine_copy.py /path/to/repo          # check
    python3 scripts/check_doctrine_copy.py /path/to/repo --write  # bring the copy current

Each repository carries STANDARDS.md as AGENTS.md, the file coding
agents read. A copy drifts the day the source changes, silently, and
the agent then works from rules the source no longer states. The
application repository's copy was 358 lines against a 995-line source
when this was noticed (October 2026), and the rules broken that week
were absent from the file the agent was reading.

The copy is a rendering, not a paste: the source's relative links to
this repository's own documents point at files the copy's repository
does not have, so they are rewritten to this repository on GitHub. A
copy may open with a preamble saying where it came from; the text
from the first top-level heading on must match the rendering exactly.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SOURCE = HERE / "STANDARDS.md"
HOME = "https://github.com/tltaylor1/build-doctrine/blob/main/"
PREAMBLE = (
    "These standards originate from the build-doctrine repository at\n"
    "github.com/tltaylor1/build-doctrine, which holds the canonical and\n"
    "current version, its enforcement mappings, and the reasoning behind each\n"
    "rule. This file is a rendering of that source; the doctrine job compares\n"
    "it with the source and refuses a copy that has fallen behind.\n\n"
)
RELATIVE = re.compile(r"\]\(((?!https?://|#|mailto:)[A-Za-z0-9_./-]+\.(?:md|json|yml|yaml|sh|py|svg|png|txt))(#[^)]*)?\)")


def render(source: str) -> str:
    """The source with every relative link pointed at this repository."""
    return RELATIVE.sub(lambda m: "](" + HOME + m.group(1) + (m.group(2) or "") + ")", source)


def body(text: str) -> list[str]:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("# "):
            return lines[i:]
    return lines


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0] if args else ".").resolve()
    copy = root / "AGENTS.md"
    rendered = render(SOURCE.read_text())
    if "--write" in sys.argv:
        preamble = PREAMBLE
        if copy.exists():
            head = copy.read_text().split("\n# ", 1)[0]
            if head.strip() and not head.startswith("# "):
                preamble = head.rstrip("\n") + "\n\n"
        copy.write_text(preamble + rendered)
        print(f"wrote {copy}")
        return 0
    if not copy.exists():
        print(f"no AGENTS.md in {root}; run this script with --write there")
        return 1
    want, have = body(rendered), body(copy.read_text())
    for number, (w, h) in enumerate(zip(want, have), 1):
        if w != h:
            print(f"AGENTS.md differs from the rendered STANDARDS.md at body line {number}:\n  source: {w[:90]}\n  copy:   {h[:90]}\n"
                  "run scripts/check_doctrine_copy.py <repo> --write from build-doctrine to bring it current")
            return 1
    if len(want) != len(have):
        print(f"AGENTS.md is {len(have)} body lines; the rendered STANDARDS.md is {len(want)}; run --write to bring it current")
        return 1
    print("AGENTS.md matches STANDARDS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
