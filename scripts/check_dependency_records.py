#!/usr/bin/env python3
"""Refuse a runtime tree that holds a package with no record, and a record with no package.

    python3 scripts/check_dependency_records.py /path/to/repo

A package is verified against the public registry before it is adopted,
and recorded in DEPENDENCIES.md with its canonical source, its role, and
what brought it in. The record carries no version: the lockfile holds
the version, and a version written in prose went stale in two
applications (October 2026). A framework update then brought a new
runtime package into both with nobody looking, because the rule was in
prose and nothing ran it (D-039).

The trees checked are listed in doctrine.yml under dependency_trees;
without that key, requirements.txt is checked when it exists. A package
in a tree with no row fails, and so does a row naming a package no tree
holds, so the record cannot drift in either direction.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PIN = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==", re.M)


def normal(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def trees(root: Path) -> list[Path]:
    manifest = root / "doctrine.yml"
    listed: list[str] = []
    if manifest.exists():
        inside = False
        for raw in manifest.read_text().splitlines():
            if raw and not raw.startswith(" "):
                inside = raw.startswith("dependency_trees:")
                continue
            if inside and raw.strip().startswith("- "):
                listed.append(raw.strip()[2:].strip())
    if not listed and (root / "requirements.txt").exists():
        listed = ["requirements.txt"]
    return [root / name for name in listed]


def recorded(root: Path) -> set[str]:
    path = root / "DEPENDENCIES.md"
    if not path.exists():
        return set()
    names = set()
    for line in path.read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and cells and cells[0] and not set(cells[0]) <= set("-: ") and cells[0].lower() != "package":
            names.add(normal(cells[0].strip("`")))
    return names


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    paths = trees(root)
    if not paths:
        print("no runtime tree to check")
        return 0
    held: dict[str, str] = {}
    for path in paths:
        for name in PIN.findall(path.read_text()):
            held.setdefault(normal(name), path.name)
    rows = recorded(root)
    missing = sorted(set(held) - rows)
    stale = sorted(rows - set(held))
    for name in missing:
        print(f"FAIL {held[name]} holds {name}, which DEPENDENCIES.md does not record; vet it before it is used")
    for name in stale:
        print(f"FAIL DEPENDENCIES.md records {name}, which no runtime tree holds; remove the row")
    if missing or stale:
        return 1
    print(f"every package in {', '.join(p.name for p in paths)} is recorded, and every record is held ({len(held)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
