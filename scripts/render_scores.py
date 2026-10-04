#!/usr/bin/env python3
"""Write SCORES.md from the scorer, and check it has not drifted.

SCORES.md is the scale applied to every repository built under this doctrine. It was
assembled by hand: run the scorer seven times, paste seven tables, type
the date. A table maintained that way goes stale silently, and it is the
one document in this repository whose whole content is a claim about other
repositories (D-034).

So the tables come from the scorer here. `--check` regenerates and
compares, which is the shape the doctrine asks of any generated artifact:
a command that decides whether the committed copy still matches its
source.

It reads local clones and the platform, so it belongs to a checkpoint
rather than to every commit, and it says so in the document it writes.
Clones are expected beside this repository, which is where the repositories
keeps them; pass --clones to look elsewhere. A repository that cannot be
read is reported and the run fails rather than the document losing a
section quietly.

Usage:
  scripts/render_scores.py            write SCORES.md
  scripts/render_scores.py --check    exit nonzero if it would change
"""

import argparse
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score as scorer  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "SCORES.md"

# The repositories built under this doctrine, in the order the document presents them:
# the flagship first, then this doctrine, then the rest by what they are.
# (clone directory, owner/name for platform lookups, kind override)
REPOSITORIES = [
    ("manifest-identity", "manifest-identity/manifest-identity", None),
    ("build-doctrine", "tltaylor1/build-doctrine", None),
    ("aws-azure-security-mapping", "tltaylor1/aws-azure-security-mapping", None),
    ("SampleDiagrams", "tltaylor1/sample-diagrams", None),
    ("anki-decks", "tltaylor1/anki-decks", None),
    ("secure-expense-mvp", "tltaylor1/secure-expense-mvp", None),
    ("tltaylor1", "tltaylor1/tltaylor1", None),
]

HEADER = """# Scores

The repositories built under this doctrine, against [the scale](ENFORCEMENT.md#the-scale),
scored on {date} by `scripts/score.py`, one run per repository from a
local clone with platform access.

This file is written by `scripts/render_scores.py`, and
`scripts/render_scores.py --check` fails when the committed copy no longer
matches what the scorer produces. It is a checkpoint command rather than a
pipeline gate, because it reads clones and the platform that a runner does
not have, which is why this document sits at level 3 of its own scale and
not at 4.
"""


def sections(clones: Path) -> tuple[list[str], list[str]]:
    rendered: list[str] = []
    problems: list[str] = []
    for directory, repo, kind in REPOSITORIES:
        root = clones / directory
        if not (root / ".git").exists():
            problems.append(f"no clone at {root}")
            continue
        kind_found, results = scorer.score(root, repo, kind)
        rendered.append(scorer.render(root, kind_found, results))
    return rendered, problems


def build(clones: Path, date: str) -> tuple[str, list[str]]:
    rendered, problems = sections(clones)
    body = "\n\n".join(rendered)
    return HEADER.format(date=date) + "\n" + body + "\n", problems


def committed_date() -> str:
    """Keep the date the committed file states, so a check run on another
    day compares content and not the calendar. Writing a new file dates it
    today; --check never rewrites the date."""
    for line in TARGET.read_text().splitlines():
        if line.startswith("scored on "):
            return line.split("scored on ", 1)[1].split(" by ")[0].strip()
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                       help="compare instead of writing; nonzero if it differs")
    parser.add_argument("--clones", default=str(ROOT.parent),
                       help="directory holding the clones (default: beside this one)")
    arguments = parser.parse_args()
    clones = Path(arguments.clones).resolve()

    date = (committed_date() if arguments.check and TARGET.exists()
            else datetime.date.today().isoformat())
    text, problems = build(clones, date)

    for problem in problems:
        print(f"scores: {problem}", file=sys.stderr)
    if problems:
        print("scores: every repository must be readable, or the document "
              "loses a section without saying so", file=sys.stderr)
        return 1

    if arguments.check:
        if TARGET.read_text() == text:
            print(f"scores: SCORES.md matches the scorer for "
                  f"{len(REPOSITORIES)} repositories")
            return 0
        print("scores: SCORES.md no longer matches the scorer; run "
              "scripts/render_scores.py", file=sys.stderr)
        return 1

    TARGET.write_text(text)
    print(f"scores: wrote {TARGET.name} for {len(REPOSITORIES)} repositories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
