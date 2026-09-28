#!/usr/bin/env python3
"""The coverage gate.

COVERAGE.md maps what the published frameworks teach onto the rules in
STANDARDS.md. A mapping document decays the moment a rule is renamed
or a row is dropped, and a decayed mapping is worse than none: it
claims coverage a reader cannot trace, which is the compliance
wallpaper the doctrine refuses elsewhere.

Three properties, each chosen because a machine can decide it without
judgment:

1. Every governed rule appears in the table. A rule added to the
   standards and mapped nowhere is a rule the pass missed, and a rule
   renamed leaves its old text nowhere to be found, so this catches
   both.
2. Every framework keeps its full item count. A row cannot vanish
   quietly, which is how a table becomes a selection of the
   convenient items.
3. Every row answers. No empty cell, and a row that says it has no
   rule must name what would trigger one, because "no rule" without a
   trigger is a gap nobody will ever close.

What this deliberately does not check: whether a rule cited in a row
actually answers the item. That is judgment, it belongs to the human
tier in ENFORCEMENT.md, and a script pretending to decide it would be
the second-order version of the wallpaper this file exists against.

Run from the repository root; exits nonzero naming what broke.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Each framework and the number of rows it must carry. The counts are
# the frameworks' own, and a change here is a deliberate act: either
# the framework published a new edition, or somebody is trimming the
# table.
EXPECTED_ROWS = {
    "OWASP Top 10 (2021)": 10,
    "OWASP API Security Top 10 (2023)": 10,
    "OWASP Top 10 for LLM Applications (2025)": 10,
    "STRIDE": 6,
    "NIST SSDF (SP 800-218)": 19,
    "OWASP ASVS, by chapter": 14,
    "SLSA build levels": 3,
}

RULE = re.compile(r"^- \*\*([^*]+)\*\*", re.MULTILINE)
HEADING = re.compile(r"^## (.+)$", re.MULTILINE)


def rule_names(text: str, start: str, end: str) -> list[str]:
    """The bold opening words of every rule between two headings."""
    body = text[text.index(start):text.index(end)]
    return [name.rstrip(".:,") for name in RULE.findall(body)]


def first_clause(name: str) -> str:
    """A rule is cited by its opening words, so the citation may stop
    anywhere the sentence allows. Compare on the first few words, which
    is what a reader uses to find it."""
    return " ".join(name.lower().replace(",", " ").split()[:3])


def sections(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    marks = [(m.group(1), m.start()) for m in HEADING.finditer(text)]
    for index, (title, start) in enumerate(marks):
        stop = marks[index + 1][1] if index + 1 < len(marks) else len(text)
        out[title] = text[start:stop]
    return out


def main() -> int:
    standards = (ROOT / "STANDARDS.md").read_text()
    coverage = (ROOT / "COVERAGE.md").read_text()
    failures: list[str] = []

    governed = rule_names(standards, "## The code", "## Not yet covered")
    governed += rule_names(standards, "## Working with an AI agent", "## Definition of done")

    # One: every governed rule is accounted for in the table. Both
    # sides are normalized the same way, because a rule wrapped across
    # lines in one file and written flat in the other is the same rule.
    lowered = " ".join(coverage.lower().replace(",", " ").split())
    for name in governed:
        clause = first_clause(name)
        flat = " ".join(name.lower().replace(",", " ").split())
        if clause not in lowered and flat not in lowered:
            failures.append(f"STANDARDS.md rule is in no coverage row: {name!r}")

    # Two: every row answers, and a gap names its trigger.
    for line in coverage.splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0] in {
            "Item", "Category", "Practice", "Chapter", "Level"
        }:
            continue
        answer = cells[-1]
        if not answer:
            failures.append(f"a coverage row answers nothing: {cells[0]!r}")
        elif "no rule" in answer.lower() and "trigger" not in answer.lower():
            failures.append(
                f"a coverage row has no rule and no trigger: {cells[0]!r}"
            )

    # Three: every framework keeps its rows.
    for title, expected in EXPECTED_ROWS.items():
        block = sections(coverage).get(title)
        if block is None:
            failures.append(f"COVERAGE.md lost the section: {title}")
            continue
        rows = [
            line for line in block.splitlines()
            if line.startswith("|") and not line.startswith("|---")
            and not re.match(r"^\|\s*(Item|Category|Practice|Chapter|Level)\s*\|", line)
        ]
        if len(rows) != expected:
            failures.append(
                f"{title}: {len(rows)} rows, expected {expected}"
            )

    for failure in failures:
        print(f"coverage: {failure}", file=sys.stderr)
    if failures:
        return 1
    print(
        f"coverage: {len(governed)} rules mapped across "
        f"{len(EXPECTED_ROWS)} frameworks, every row present"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
