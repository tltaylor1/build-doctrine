#!/usr/bin/env python3
"""Vet an outside repository before adopting it.

    python3 scripts/vet.py OWNER/NAME [--path CHECKOUT] [--json]

Produces the adoption record the standards require for outside code:
what the public raters say (Scorecard, Best Practices), what the
platform says (license, last push, latest release, archived, open
advisories), and what a checkout contains that runs at install time
or was committed as a binary. Every network read is public and
unauthenticated. The record ends with the acceptance block the
adopter fills in: owner, expiry, and what is accepted as it stands.
The record is pasted into the adopting repository's decisions record.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

SCORECARD = "https://api.scorecard.dev/projects/github.com/{repo}"
GITHUB = "https://api.github.com/repos/{repo}"
BEST_PRACTICES = "https://www.bestpractices.dev/projects.json?url=https://github.com/{repo}"
SCORECARD_FLOOR = 7  # checks at or above this need no comment in the record

INSTALL_SCRIPT_KEYS = ("preinstall", "install", "postinstall", "prepare", "preprepare", "postprepare")
BINARY_MAGIC = (
    b"\x7fELF",            # Linux executables and shared objects
    b"MZ",                 # Windows executables and DLLs
    b"\xcf\xfa\xed\xfe",   # Mach-O 64-bit
    b"\xce\xfa\xed\xfe",   # Mach-O 32-bit
    b"\xca\xfe\xba\xbe",   # Mach-O universal, also Java class files
)
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".tox"}
SETUP_SIGNALS = ("cmdclass", "subprocess", "os.system", "urllib", "requests.", "ctypes")


def _get(url: str) -> dict | list | None:
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310  (https, fixed hosts)
            return json.load(response)
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError):
        return None


def signals(repo: str) -> dict:
    """What the raters and the platform say, each field None when unavailable."""
    out: dict = {"repo": repo, "read": datetime.now(UTC).strftime("%Y-%m-%d")}
    sc = _get(SCORECARD.format(repo=repo))
    if isinstance(sc, dict) and "score" in sc:
        out["scorecard"] = {
            "score": sc["score"],
            "date": sc["date"][:10],
            "commit": sc["repo"]["commit"][:12],
            "below_floor": [
                {"name": c["name"], "score": c["score"], "reason": c["reason"]}
                for c in sorted(sc["checks"], key=lambda c: c["name"])
                if c["score"] != -1 and c["score"] < SCORECARD_FLOOR
            ],
            "inconclusive": [c["name"] for c in sc["checks"] if c["score"] == -1],
        }
    else:
        out["scorecard"] = None
    gh = _get(GITHUB.format(repo=repo))
    if isinstance(gh, dict) and "full_name" in gh:
        out["platform"] = {
            "license": (gh.get("license") or {}).get("spdx_id") or "none detected",
            "archived": bool(gh.get("archived")),
            "pushed_at": (gh.get("pushed_at") or "")[:10],
            "stars": gh.get("stargazers_count"),
            "open_issues": gh.get("open_issues_count"),
            "default_branch": gh.get("default_branch"),
        }
        release = _get(GITHUB.format(repo=repo) + "/releases/latest")
        out["platform"]["latest_release"] = (
            f"{release['tag_name']} on {release['published_at'][:10]}"
            if isinstance(release, dict) and "tag_name" in release else "none"
        )
        advisories = _get(GITHUB.format(repo=repo) + "/security-advisories?state=published")
        out["platform"]["published_advisories"] = (
            len(advisories) if isinstance(advisories, list) else "unavailable"
        )
    else:
        out["platform"] = None
    bp = _get(BEST_PRACTICES.format(repo=repo))
    out["best_practices"] = (
        {"id": bp[0]["id"], "level": bp[0].get("badge_level") or "in progress"}
        if isinstance(bp, list) and bp else None
    )
    return out


def scan(path: Path) -> list[dict]:
    """What in a checkout runs at install time or was committed as a binary."""
    findings: list[dict] = []
    for file in sorted(path.rglob("*")):
        if any(part in SKIP_DIRS for part in file.relative_to(path).parts):
            continue
        if not file.is_file() or file.is_symlink():
            continue
        rel = str(file.relative_to(path))
        name = file.name
        if name == "package.json":
            try:
                scripts = json.loads(file.read_text()).get("scripts") or {}
            except (ValueError, UnicodeDecodeError):
                scripts = {}
            for key in INSTALL_SCRIPT_KEYS:
                if key in scripts:
                    findings.append({"kind": "install script", "path": rel,
                                     "detail": f"{key}: {scripts[key]}"})
        elif name == "setup.py":
            text = file.read_text(errors="replace")
            hits = [s for s in SETUP_SIGNALS if s in text]
            if hits:
                findings.append({"kind": "build hook", "path": rel,
                                 "detail": "setup.py uses " + ", ".join(hits)})
        elif name == "pyproject.toml":
            text = file.read_text(errors="replace")
            if re.search(r"\[tool\.[a-z0-9_-]+\.build\.hooks", text) or "build-backend" in text and "custom" in text:
                findings.append({"kind": "build hook", "path": rel,
                                 "detail": "pyproject.toml declares build hooks"})
        elif file.suffix in (".yml", ".yaml") and ".github" in file.parts and "workflows" in file.parts:
            text = file.read_text(errors="replace")
            if "pull_request_target" in text:
                findings.append({"kind": "workflow", "path": rel,
                                 "detail": "runs on pull_request_target, which carries the repository token to fork code"})
        with file.open("rb") as handle:
            head = handle.read(4)
        if head and any(head.startswith(magic) for magic in BINARY_MAGIC):
            findings.append({"kind": "committed binary", "path": rel,
                             "detail": "executable or library by its leading bytes"})
    return findings


def render(s: dict, findings: list[dict] | None, path: Path | None) -> str:
    out: list[str] = []
    w = out.append
    w(f"### Adoption record: {s['repo']}")
    w("")
    w(f"Read {s['read']} by scripts/vet.py from public interfaces.")
    w("")
    sc = s.get("scorecard")
    if sc:
        w(f"**Scorecard {sc['score']} / 10**, scan of {sc['date']} at commit `{sc['commit']}`.")
        if sc["below_floor"]:
            w(f"Checks below {SCORECARD_FLOOR}:")
            w("")
            for c in sc["below_floor"]:
                w(f"- {c['name']}, {c['score']}: {c['reason']}")
        else:
            w(f"No check below {SCORECARD_FLOOR}.")
        if sc["inconclusive"]:
            w("")
            w("Inconclusive, left out of the score: " + ", ".join(sc["inconclusive"]) + ".")
    else:
        w("**Scorecard**: no result for this repository; the scanner has not rated it.")
    w("")
    p = s.get("platform")
    if p:
        w("**Platform**")
        w("")
        w(f"- License: {p['license']}")
        w(f"- Archived: {'yes' if p['archived'] else 'no'}")
        w(f"- Last push: {p['pushed_at']}")
        w(f"- Latest release: {p['latest_release']}")
        w(f"- Published security advisories: {p['published_advisories']}")
        w(f"- Stars {p['stars']}, open issues and pull requests {p['open_issues']}")
    else:
        w("**Platform**: the repository could not be read; check the name.")
    w("")
    bp = s.get("best_practices")
    if bp:
        w(f"**Best Practices**: {bp['level']}, project {bp['id']}.")
    else:
        w("**Best Practices**: no entry.")
    w("")
    if path is not None:
        w(f"**Checkout scan** of `{path}`")
        w("")
        if findings:
            for f in findings:
                w(f"- {f['kind']}: `{f['path']}`, {f['detail']}")
        else:
            w("- No install scripts, build hooks, pull_request_target workflows, or committed binaries.")
    else:
        w("**Checkout scan**: not run; pass --path to scan a checkout.")
    w("")
    w("**Acceptance** (filled in by the adopter)")
    w("")
    w("- Pinned to: commit or digest")
    w("- Fetched through: the controlled source, or the pin with its checksum where none exists")
    w("- Static analysis and secret scan of the checkout: run on, findings")
    w("- License compatible with this repository's license: yes or no, and why")
    w("- Runs with: the privilege, secrets, and egress it needs, nothing more")
    w("- Not reviewed: what was skipped")
    w("- Accepted by: owner")
    w("- Expires: date, after which this acceptance no longer stands")
    w("- Full review scheduled: date")
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo", help="owner/name on github.com")
    parser.add_argument("--path", help="a local checkout to scan for install-time code and binaries")
    parser.add_argument("--json", action="store_true", help="emit the raw data instead of the record")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo):
        print("repo must be owner/name", file=sys.stderr)
        return 2
    path = Path(args.path).resolve() if args.path else None
    if path is not None and not path.is_dir():
        print(f"{path} is not a directory", file=sys.stderr)
        return 2
    data = signals(args.repo)
    findings = scan(path) if path is not None else None
    if args.json:
        print(json.dumps({"signals": data, "findings": findings}, indent=2))
    else:
        print(render(data, findings, path), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
