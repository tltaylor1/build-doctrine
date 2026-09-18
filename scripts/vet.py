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
VETTING.md explains every reading, what it means, and what the tool
cannot see.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
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
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".tox",
             ".hypothesis", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SETUP_SIGNALS = ("cmdclass", "subprocess", "os.system", "urllib", "requests.", "ctypes")


def _get(url: str) -> dict | list | None:
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310  (https, fixed hosts)
            return json.load(response)
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError):
        return None


def _scorecard_local(repo: str) -> dict | None:
    """Run the Scorecard command on the repository when the public API
    has never rated it. Needs the scorecard binary on the path and a
    GITHUB_AUTH_TOKEN in the environment, both the operator's own."""
    binary = shutil.which("scorecard")
    if binary is None:
        return None
    try:
        out = subprocess.run(  # noqa: S603  (fixed argument list, operator-named repo)
            [binary, f"--repo=github.com/{repo}", "--format=json"],
            capture_output=True, text=True, timeout=900, check=False,
        )
        return json.loads(out.stdout) if out.returncode == 0 and out.stdout else None
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def signals(repo: str) -> dict:
    """What the raters and the platform say, each field None when unavailable."""
    out: dict = {"repo": repo, "read": datetime.now(UTC).strftime("%Y-%m-%d")}
    sc = _get(SCORECARD.format(repo=repo))
    source = "the public Scorecard API"
    if not (isinstance(sc, dict) and "score" in sc):
        sc = _scorecard_local(repo)
        source = "the Scorecard command run here"
    if isinstance(sc, dict) and "score" in sc:
        out["scorecard"] = {
            "source": source,
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
        try:
            with file.open("rb") as handle:
                head = handle.read(4)
        except OSError as error:
            findings.append({"kind": "unreadable file", "path": rel,
                             "detail": f"could not be read ({error.strerror}); nothing here was scanned"})
            continue
        if head and any(head.startswith(magic) for magic in BINARY_MAGIC):
            findings.append({"kind": "committed binary", "path": rel,
                             "detail": "executable or library by its leading bytes"})
    return findings


def dependency_scan(path: Path) -> dict | None:
    """Known vulnerabilities in the checkout's dependency tree, read from
    its lockfiles and manifests by trivy when it is installed. This is
    the transitive dependency nobody looked at, which is the more common
    of the two ways outside code fails."""
    binary = shutil.which("trivy")
    if binary is None:
        return None
    try:
        out = subprocess.run(  # noqa: S603  (fixed argument list, operator-named path)
            [binary, "fs", "--quiet", "--scanners", "vuln", "--format", "json", str(path)],
            capture_output=True, text=True, timeout=900, check=False,
        )
        data = json.loads(out.stdout) if out.returncode == 0 and out.stdout else None
    except (OSError, subprocess.SubprocessError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    findings: list[dict] = []
    targets: list[str] = []
    for result in data.get("Results") or []:
        targets.append(result.get("Target", ""))
        for v in result.get("Vulnerabilities") or []:
            findings.append({
                "package": v.get("PkgName"), "installed": v.get("InstalledVersion"),
                "fixed": v.get("FixedVersion") or "no fix", "id": v.get("VulnerabilityID"),
                "severity": v.get("Severity", "UNKNOWN"),
            })
    return {"targets": targets, "findings": findings}


STOP_CHECKS = ("Dangerous-Workflow", "Token-Permissions", "Vulnerabilities", "Binary-Artifacts")
STALE_DAYS = 365


def concerns(s: dict, findings: list[dict] | None) -> list[str]:
    """The readings VETTING.md marks as reasons to stop, in one list."""
    out: list[str] = []
    sc = s.get("scorecard")
    if sc:
        for c in sc["below_floor"]:
            if c["name"] in STOP_CHECKS:
                out.append(f"Scorecard {c['name']} at {c['score']}: {c['reason']}")
    p = s.get("platform")
    if p:
        if p["archived"]:
            out.append("the repository is archived; nothing will be fixed")
        if p["license"] == "none detected":
            out.append("no license detected; there is no right to use it")
        if p["pushed_at"]:
            try:
                pushed = datetime.strptime(p["pushed_at"], "%Y-%m-%d").replace(tzinfo=UTC)
                read = datetime.strptime(s["read"], "%Y-%m-%d").replace(tzinfo=UTC)
                if (read - pushed).days > STALE_DAYS:
                    out.append(f"last push {p['pushed_at']}, more than a year before this reading")
            except ValueError:
                pass
    for f in findings or []:
        out.append(f"{f['kind']} at {f['path']}: {f['detail']}")
    deps = s.get("dependencies")
    if deps:
        serious = [v for v in deps["findings"]
                   if v["severity"] in ("CRITICAL", "HIGH") and v["fixed"] != "no fix"]
        if serious:
            out.append(f"{len(serious)} critical or high vulnerabilities with a published fix "
                       "in the dependency tree")
    return out


def render(s: dict, findings: list[dict] | None, path: Path | None) -> str:
    out: list[str] = []
    w = out.append
    w(f"### Adoption record: {s['repo']}")
    w("")
    w(f"Read {s['read']} by scripts/vet.py from public interfaces.")
    w("")
    sc = s.get("scorecard")
    if sc:
        w(f"**Scorecard {sc['score']} / 10**, scan of {sc['date']} at commit `{sc['commit']}`,")
        w(f"read from {sc.get('source', 'the public Scorecard API')}.")
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
        w("**Scorecard**: no result. The public scanner has not rated this repository,")
        w("and the scorecard command was not available here to run the same checks;")
        w("VETTING.md says how to install it.")
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
    deps = s.get("dependencies")
    if path is not None and deps:
        w(f"**Dependency tree**, {len(deps['targets'])} manifest or lock file(s) read by trivy")
        w("")
        if deps["findings"]:
            counts: dict[str, int] = {}
            for v in deps["findings"]:
                counts[v["severity"]] = counts.get(v["severity"], 0) + 1
            w("- " + ", ".join(f"{n} {sev.lower()}" for sev, n in sorted(counts.items())))
            for v in deps["findings"]:
                if v["severity"] in ("CRITICAL", "HIGH"):
                    w(f"- {v['severity'].lower()}: {v['package']} {v['installed']}, "
                      f"{v['id']}, fixed in {v['fixed']}")
        else:
            w("- No known vulnerabilities in the declared dependencies.")
    elif path is not None:
        w("**Dependency tree**: not scanned; trivy is not installed here. VETTING.md says how.")
    w("")
    flagged = concerns(s, findings)
    w("**Concerns**, each a reason to stop and read (see VETTING.md)")
    w("")
    if flagged:
        for line in flagged:
            w(f"- {line}")
    else:
        w("- None found. The remaining questions are the ones only a reader can answer.")
    w("")
    w("**Acceptance** (filled in by the adopter)")
    w("")
    w("- Pinned to: commit or digest")
    w("- Fetched through: the controlled source, or the pin with its checksum where none exists")
    w("- Static analysis and secret scan of the checkout: run on, findings")
    w("- License compatible with this repository's license: yes or no, and why")
    w("- Runs with: the privilege, secrets, and egress it needs, nothing more")
    w("- Sign-in: behind the program's identity provider, or none exposed")
    w("- Logs: the events its audit and access logs produce, and where they are collected")
    w("- Major dependencies: their advisory histories read, and what they showed")
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
    data["dependencies"] = dependency_scan(path) if path is not None else None
    if args.json:
        print(json.dumps({"signals": data, "findings": findings}, indent=2))
    else:
        print(render(data, findings, path), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
