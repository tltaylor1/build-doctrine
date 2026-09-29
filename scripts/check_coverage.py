#!/usr/bin/env python3
"""The coverage gate.

COVERAGE.md maps what the published frameworks teach onto the rules in
STANDARDS.md. Two ways that decays, and this checks both.

The first is drift inside the repository: a rule is renamed, a row is
dropped, and the table quietly claims coverage nobody can trace.

The second is the one that actually happened. The first version of
COVERAGE.md was written from memory. It mapped the 2021 Top 10 while
2025 was current, and version 4 of ASVS while 5.0.0 was, and the gate
of the day hardcoded those counts, so it checked the document against
its author's recollection and would have passed forever (D-032). The
item lists now live in frameworks.json with their sources, and this
compares the document against that data rather than against numbers
somebody typed.

Four properties, each decidable without judgment:

1. Every item in frameworks.json has a row in COVERAGE.md.
2. No section carries a row for an item the data does not have, which
   catches an edition's worth of stale rows.
3. Every governed rule in STANDARDS.md appears somewhere in the table.
   A rule added and mapped nowhere is a rule the pass missed; a rule
   renamed leaves its old text nowhere to be found.
4. Every row answers. No empty cell, and a row claiming no rule names
   what would trigger writing one.

What this deliberately does not check: whether a rule cited in a row
actually answers its item, and whether the data still matches what the
framework publishes today. The first is judgment and belongs to the
human tier in ENFORCEMENT.md. The second needs the network, so it is
scripts/refresh_frameworks.py, run deliberately rather than on every
commit.

Run from the repository root; exits nonzero naming what broke.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RULE = re.compile(r"^- \*\*([^*]+)\*\*", re.MULTILINE)
HEADING = re.compile(r"^## (.+)$", re.MULTILINE)
COLUMN_HEADINGS = {"Item", "Category", "Practice", "Chapter", "Level"}


def rule_names(text: str, start: str, end: str) -> list[str]:
    """The bold opening words of every rule between two headings."""
    body = text[text.index(start):text.index(end)]
    return [name.rstrip(".:,") for name in RULE.findall(body)]


def first_clause(name: str) -> str:
    """A rule is cited by its opening words, so a citation may stop
    anywhere the sentence allows. Compare on the first few, which is
    what a reader uses to find it."""
    return " ".join(name.lower().replace(",", " ").split()[:3])


def flatten(text: str) -> str:
    return " ".join(text.lower().replace(",", " ").split())


def table_rows(text: str) -> list[list[str]]:
    out = []
    for line in text.splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 2 and cells[0] not in COLUMN_HEADINGS:
            out.append(cells)
    return out


def section_for(coverage: str, title_fragment: str) -> str | None:
    marks = [(m.group(1), m.start()) for m in HEADING.finditer(coverage)]
    for index, (title, start) in enumerate(marks):
        if title_fragment.lower() in title.lower():
            stop = marks[index + 1][1] if index + 1 < len(marks) else len(coverage)
            return coverage[start:stop]
    return None


def main() -> int:
    standards = (ROOT / "STANDARDS.md").read_text()
    coverage = (ROOT / "COVERAGE.md").read_text()
    data = json.loads((ROOT / "frameworks.json").read_text())["frameworks"]
    failures: list[str] = []
    checked = 0

    for framework in data.values():
        # The data names the section it belongs to, so a renamed
        # heading fails loudly instead of being matched by guesswork.
        section = section_for(coverage, framework["heading"])
        if section is None:
            failures.append(
                f"COVERAGE.md has no section headed {framework['heading']!r}"
            )
            continue
        labels = [row[0] for row in table_rows(section)]

        # One: every published item has a row.
        for item in framework["items"]:
            expected = flatten(f"{item['id']} {item['name']}")
            if any(flatten(label) == expected for label in labels):
                checked += 1
            else:
                failures.append(
                    f"{framework['title']} {framework['version']}: "
                    f"no row for {item['id']} {item['name']!r}"
                )

        # Two: no row for an item the data does not carry.
        known = {flatten(f"{i['id']} {i['name']}") for i in framework["items"]}
        for label in labels:
            if flatten(label) not in known:
                failures.append(
                    f"{framework['title']}: row {label!r} is not in "
                    "frameworks.json"
                )

    governed = rule_names(standards, "## The code", "## Not yet covered")
    governed += rule_names(
        standards, "## Working with an AI agent", "## Definition of done"
    )

    # Three: every governed rule appears in the table.
    lowered = flatten(coverage)
    for name in governed:
        if first_clause(name) not in lowered and flatten(name) not in lowered:
            failures.append(f"STANDARDS.md rule is in no coverage row: {name!r}")

    # Four: every row answers, and a gap names its trigger.
    for cells in table_rows(coverage):
        answer = cells[-1]
        if not answer:
            failures.append(f"a coverage row answers nothing: {cells[0]!r}")
        elif "no rule" in answer.lower() and "trigger" not in answer.lower():
            failures.append(
                f"a coverage row has no rule and no trigger: {cells[0]!r}"
            )

    for failure in failures:
        print(f"coverage: {failure}", file=sys.stderr)
    if failures:
        return 1
    print(
        f"coverage: {checked} published items mapped across {len(data)} "
        f"frameworks, {len(governed)} rules accounted for"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
