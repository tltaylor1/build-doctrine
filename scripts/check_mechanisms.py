#!/usr/bin/env python3
"""The enforcement gate: every blocking row names a mechanism that exists.

ENFORCEMENT.md opens by saying that every rule appears there with the
thing that actually checks it, and that a rule with no mechanism is a
hope. Nothing checked that sentence. A mechanism audit found it false in
six places, and five of them were one shape: a control implemented in
the repository where it was learned, and a table that generalized it to
an artifact it had never reached. The worst had been running for months
as a step named "Secret scan over full history" that scanned the event's
commit range (D-033).

So this reads mechanisms.json, where each blocking row names the files
that hold its mechanism, and checks four things.

1. Every row in the two blocking tables has an entry, and every entry
   names a row that exists. A renamed row fails, which forces whoever
   renames it to look at the mechanism again.
2. Every artifact in this repository, including the template it ships,
   exists.
3. Every pattern is actually found in its artifact. This is what catches
   a mechanism deleted or replaced while the row stayed put.
4. Every artifact that lives in an application repository names that
   repository, and is reported as declared rather than verified.

That last one is the honest limit. This repository cannot read another
one, so it must not imply it did: the count of declared entries is
printed next to the count of verified ones. Those rows are checked by
the project's own pipeline, which is where the test lives.

What this deliberately does not check: whether a test that exists asserts
the right property. A pattern proves a mechanism is present, not that it
works. Mutation runs answer that, and the human tier in ENFORCEMENT.md
owns what neither can decide.

Run from the repository root; exits nonzero naming what broke.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "mechanisms.json"
ENFORCEMENT = ROOT / "ENFORCEMENT.md"

TABLES = ("Blocked at commit", "Blocked in the pipeline")
# Where a holder's files are rooted. "application" has no root here on
# purpose: that repository is not this one, and pretending otherwise is
# the failure this gate exists to refuse.
ROOTS = {"this": ROOT, "template": ROOT / "template"}


def rows_of(text: str, title: str) -> list[str]:
    """The first cell of every row in one section's table."""
    start = text.index(f"## {title}")
    stop = text.find("\n## ", start + 5)
    body = text[start : stop if stop != -1 else len(text)]
    out = []
    for line in body.splitlines():
        if line.startswith("|") and not line.startswith("|---"):
            first = line.strip("|").split("|")[0].strip()
            if first not in ("Rule", ""):
                out.append(first)
    return out


def main() -> int:
    document = ENFORCEMENT.read_text()
    entries = json.loads(DATA.read_text())["mechanisms"]
    failures: list[str] = []
    verified = 0
    declared = 0

    documented: dict[str, str] = {}
    for title in TABLES:
        for rule in rows_of(document, title):
            documented[rule] = title

    claimed = {entry["rule"] for entry in entries}
    if len(claimed) != len(entries):
        failures.append("mechanisms.json names the same rule twice")

    # One: the tables and the data describe the same set of rules.
    for rule, title in documented.items():
        if rule not in claimed:
            failures.append(
                f"{title!r} has a row with no mechanism recorded: {rule!r}"
            )
    for entry in entries:
        rule = entry["rule"]
        if rule not in documented:
            failures.append(
                f"mechanisms.json records a rule that is in no blocking "
                f"table: {rule!r}"
            )
        elif documented[rule] != entry["table"]:
            failures.append(
                f"{rule!r} is recorded under {entry['table']!r} and appears "
                f"under {documented[rule]!r}"
            )

    for entry in entries:
        for artifact in entry["artifacts"]:
            holder = artifact["holder"]
            where = artifact["path"]

            # Four: an artifact this repository cannot read is declared,
            # never counted as verified.
            if holder not in ROOTS:
                if holder != "application":
                    failures.append(
                        f"{entry['rule']!r} names an unknown holder: {holder!r}"
                    )
                elif not artifact.get("repository"):
                    failures.append(
                        f"{entry['rule']!r} declares a mechanism outside this "
                        f"repository without naming the repository: {where}"
                    )
                else:
                    declared += 1
                continue

            path = ROOTS[holder] / where
            # Two: it exists.
            if not path.is_file():
                failures.append(
                    f"{entry['rule']!r} names a file that does not exist: "
                    f"{path.relative_to(ROOT)}"
                )
                continue
            # Three: it still holds the mechanism.
            if not re.search(artifact["pattern"], path.read_text()):
                failures.append(
                    f"{entry['rule']!r}: {path.relative_to(ROOT)} no longer "
                    f"matches {artifact['pattern']!r}"
                )
                continue
            verified += 1

    # Every path the document names in prose exists here, or is declared
    # in the data as living in an application repository. Cheap, and it
    # covers the tiers this data file does not: a command in the
    # verification tier whose script was renamed fails here.
    elsewhere = {
        artifact["path"]
        for entry in entries
        for artifact in entry["artifacts"]
        if artifact["holder"] == "application"
    }
    for match in re.finditer(r"`([^`\s]+)`", document):
        token = match.group(1)
        if not re.fullmatch(r"[\w./-]+", token):
            continue
        if "/" not in token and not token.endswith(
            (".py", ".sh", ".yml", ".yaml", ".json", ".toml", ".ini", ".md")
        ):
            continue
        if (ROOT / token).exists() or token in elsewhere:
            continue
        # A leaf filename reads better in prose than the full path, and a
        # directory reads better with its trailing slash. Both are accepted
        # when the data declares them, and only then.
        leaves = {path.split("/")[-1] for path in elsewhere}
        heads = {path.split("/")[0] for path in elsewhere}
        if token in leaves or token.rstrip("/") in heads:
            continue
        failures.append(
            f"ENFORCEMENT.md names a path that is neither here nor declared "
            f"in mechanisms.json: {token}"
        )

    for failure in sorted(set(failures)):
        print(f"mechanisms: {failure}", file=sys.stderr)
    if failures:
        return 1
    print(
        f"mechanisms: {len(entries)} blocking rows, {verified} artifact(s) "
        f"verified here, {declared} declared in an application repository "
        "and checked by its own pipeline"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
