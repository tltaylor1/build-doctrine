#!/usr/bin/env python3
"""Refuse a change that adds code nothing uses.

    python3 scripts/check_dead_code.py /path/to/repo [--base REF] [--archive PATH]

Code nothing calls is surface with no purpose: it is read, reviewed,
patched, and audited like the rest, and an agent that rewrites instead
of reusing leaves the old version behind. In one application a scan
found four constants nothing read, one of them a second statement of a
rule the running code stated again elsewhere (October 2026, D-046).

The check runs jscpd's dead-code analysis, the tool the repetition check
already pins, on the base branch and on the change, and fails when the
change has more dead lines. It counts only the findings jscpd is sure
of, at confidence 85 or above, in unused files, exports, symbols, and
imports; members and properties are left out, because an object mapper
and a validation library read them where no call shows. JavaScript,
TypeScript, and Python are read. Everything about fetching, checking,
and comparing is shared with the repetition check.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_repetition import Measure, gate  # noqa: E402

CATEGORIES = "unused-file,unused-export,unused-symbol,unused-import"
MIN_CONFIDENCE = "85"


def arguments(tree: Path, out: Path, skip: str | None, console: bool) -> list[str]:
    ignored = ["**/.git/**"] + ([skip] if skip else [])
    return [
        str(tree), "--dead-code",
        "--dead-code-categories", CATEGORIES,
        "--min-confidence", MIN_CONFIDENCE,
        "--ignore", ",".join(ignored),
        "--reporters", "json,console" if console else "json",
        "--output", str(out),
    ]


def dead_lines(report: Path) -> int:
    return int(json.loads(report.read_text())["statistics"]["deadLines"])


DEAD_CODE = Measure(label="dead code", unit="dead lines", report="basta-report.json",
                    arguments=arguments, read=dead_lines)


def main(argv: list[str] | None = None) -> int:
    return gate(argv, DEAD_CODE, __doc__.splitlines()[0])


if __name__ == "__main__":
    sys.exit(main())
