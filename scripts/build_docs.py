#!/usr/bin/env python3
"""Generate the documentation site's pages from the repository's own
documents, so the site has no source of its own to drift.

    python3 scripts/build_docs.py [--out docs/site]

Each root document becomes one page, in reading order. Links between
the documents are rewritten to the page names, images under diagrams/
are copied beside the pages, and links to anything else in the
repository point at it on GitHub. The output directory is generated
at build time and never committed.
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/tltaylor1/build-doctrine"
# Reading order. Every root document except CLAUDE.md, which is a
# one-line pointer for one tool, has a place here; a test holds that.
PAGES = [
    ("README.md", "index.md"),
    ("FUNDAMENTALS.md", "01-fundamentals.md"),
    ("STANDARDS.md", "02-standards.md"),
    ("ENFORCEMENT.md", "03-enforcement.md"),
    ("REVIEW.md", "04-review.md"),
    ("DECISIONS.md", "05-decisions.md"),
    ("COMPONENTS.md", "06-components.md"),
    ("USING.md", "07-using.md"),
    ("VETTING.md", "08-vetting.md"),
    ("SCORES.md", "09-scores.md"),
    ("PLATFORM-BASELINE.md", "10-platform-baseline.md"),
    ("SECURITY.md", "11-security.md"),
    ("CONTRIBUTING.md", "12-contributing.md"),
    ("ACKNOWLEDGEMENTS.md", "13-acknowledgements.md"),
    ("AGENTS.md", "14-agents.md"),
]
NOT_PAGES = {"CLAUDE.md"}
ASSET_DIRS = {"diagrams": "diagrams"}
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$", re.MULTILINE)
LINK = re.compile(r"\]\(([^)\s]+)\)")


def slug(text: str) -> str:
    """The anchor both GitHub and the site's toc extension derive from
    a heading: lowercase, punctuation dropped, spaces to hyphens."""
    text = re.sub(r"[`*_]", "", text).lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", text.strip())


def rewrite_links(body: str, pages: dict[str, str]) -> str:
    def fix(m: re.Match[str]) -> str:
        target = m.group(1)
        if target.startswith(("#", "http://", "https://", "mailto:")):
            return m.group(0)
        path, _, fragment = target.partition("#")
        path = path.lstrip("./")
        suffix = f"#{fragment}" if fragment else ""
        if path in pages:
            return f"]({pages[path]}{suffix})"
        for src, dst in ASSET_DIRS.items():
            if path.startswith(src + "/"):
                return f"]({dst}/{path[len(src) + 1:]})"
        kind = "tree" if path.endswith("/") or "." not in path.rsplit("/", 1)[-1] else "blob"
        return f"]({REPO_URL}/{kind}/main/{path}{suffix})"
    return LINK.sub(fix, body)


def build(out: Path) -> list[str]:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    pages = dict(PAGES)
    written = []
    for src, dst in PAGES:
        (out / dst).write_text(rewrite_links((ROOT / src).read_text(), pages))
        written.append(dst)
    for src, dst in ASSET_DIRS.items():
        if (ROOT / src).is_dir():
            shutil.copytree(ROOT / src, out / dst)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="docs/site")
    args = parser.parse_args()
    written = build(ROOT / args.out)
    print(f"{len(written)} pages written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
