#!/usr/bin/env python3
"""Refuse a pull request branch that carries a merge commit.

    python3 scripts/check_branch_history.py /path/to/repo [--base REF] [--head REF]

An open pull request is brought up to date by rebuilding it on the
mainline, never by merging another branch into it (D-047). A merge
commit made on a local machine left one pull request blocked after its
owner approved it, while the same files as plain commits merged at
once.

The check lists the merge commits between the base and the branch's
head. On a pull request the pipeline checks out the platform's own
merge of the two, so the head is read from GITHUB_HEAD_REF, the branch
itself, rather than from what is checked out. With no base there is
nothing to compare against, and the check says it skipped.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def refs(given_base: str | None, given_head: str | None) -> tuple[str | None, str]:
    base = given_base or (f"origin/{os.environ['GITHUB_BASE_REF']}" if os.environ.get("GITHUB_BASE_REF") else None)
    head = given_head or (f"origin/{os.environ['GITHUB_HEAD_REF']}" if os.environ.get("GITHUB_HEAD_REF") else "HEAD")
    return base, head


def merges(repo: Path, base: str, head: str) -> list[str]:
    out = subprocess.run(  # noqa: S603, S607
        ["git", "-C", str(repo), "log", "--merges", "--format=%h %s", f"{base}..{head}"],
        capture_output=True, text=True, check=True,
    )
    return [line for line in out.stdout.splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo", type=Path)
    parser.add_argument("--base", help="the ref the branch will merge into, such as origin/main")
    parser.add_argument("--head", help="the branch's own head, when it is not what is checked out")
    args = parser.parse_args(argv)
    base, head = refs(args.base, args.head)
    if base is None:
        print("branch history: skipped, no base to compare against (give --base, or run on a pull request)")
        return 0
    try:
        found = merges(args.repo, base, head)
    except subprocess.CalledProcessError as exc:
        print(f"branch history: refused, git could not compare {base} with {head}: {exc.stderr.strip()}")
        return 2
    if found:
        print("branch history: the branch carries a merge commit; rebuild it on the mainline instead:")
        for line in found:
            print(f"  {line}")
        return 1
    print(f"branch history: no merge commit between {base} and {head}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
