"""Score a repository against the doctrine, one level per rule.

    python3 scripts/score.py /path/to/repo [--repo owner/name] [--json]

Every rule scores on the six-level scale ENFORCEMENT.md defines:

    0  absent, or stated and found false
    1  stated in a committed document, nothing verifies it
    2  attested: a dated manual procedure inside its validity window
    3  checked on demand: a committed command verifies it and passes
    4  gated: the check runs in CI and is in the required set
    5  gated and proven: evidence the gate has caught a real violation

The scorer establishes levels 0 through 4 from the repository itself
and the platform API when reachable. Level 5 is never inferred: it is
granted only when the scored repository's doctrine.yml records a
proof, a link to the run or test where the gate fired, and the rule
already stands at 4. Rules a repository kind does not need are named
as not applicable, and a repository may exclude a rule with a stated
reason, because an undocumented gap and a considered exclusion look
identical in a score.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

KINDS = ("application", "doctrine", "reference", "study", "profile", "diagrams")
SHA_PIN = re.compile(r"uses:\s*\S+@[0-9a-f]{40}")
ANY_USES = re.compile(r"uses:\s*\S+@")
SUBJECT = re.compile(r"^(D-\d+|[A-Z][A-Z0-9-]{1,30}):\s")
DECISION_HEAD = re.compile(r"^## D-\d+", re.MULTILINE)


@dataclass
class Result:
    rule: str
    level: int | None  # None means not applicable or excluded
    reason: str


def read(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except OSError:
        return ""


def find_file(root: Path, stem: str) -> Path | None:
    for candidate in sorted(root.iterdir()) if root.exists() else []:
        if candidate.is_file() and candidate.name.upper().startswith(stem):
            return candidate
    return None


def load_manifest(root: Path) -> dict:
    """doctrine.yml, read without a YAML library: flat keys, a kind, an
    invites_contributions flag, and two maps of rule to text."""
    manifest: dict = {"kind": None, "invites_contributions": None,
                      "proven": {}, "exclusions": {}}
    text = read(root / "doctrine.yml")
    section = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            key, _, value = line.partition(":")
            key, value = key.strip(), value.strip()
            section = key if key in ("proven", "exclusions") and not value else None
            if key == "kind":
                manifest["kind"] = value
            elif key == "invites_contributions":
                manifest["invites_contributions"] = value.lower() == "true"
        elif section:
            key, _, value = line.strip().partition(":")
            manifest[section][key.strip()] = value.strip().strip('"')
    return manifest


def guess_kind(root: Path) -> str:
    if (root / "STANDARDS.md").exists() and (root / "ENFORCEMENT.md").exists():
        return "doctrine"
    if (root / "pyproject.toml").exists() or (root / "Dockerfile").exists():
        return "application"
    if any(root.glob("*.csv")) or any(root.glob("*/*.csv")):
        return "reference"
    return "reference"


def workflows(root: Path) -> list[Path]:
    return sorted((root / ".github" / "workflows").glob("*.yml"))


def workflow_text(root: Path) -> str:
    return "\n".join(read(w) for w in workflows(root))


def required_checks(repo: str | None) -> list[str] | None:
    """The platform's required status checks, or None when unreachable."""
    if not repo:
        return None
    try:
        out = subprocess.run(
            ["gh", "api", f"repos/{repo}/rulesets", "--jq", ".[].id"],
            capture_output=True, text=True, timeout=30, check=False,
        )
        if out.returncode != 0:
            return None
        checks: list[str] = []
        for rid in out.stdout.split():
            detail = subprocess.run(
                ["gh", "api", f"repos/{repo}/rulesets/{rid}"],
                capture_output=True, text=True, timeout=30, check=False,
            )
            if detail.returncode != 0:
                continue
            data = json.loads(detail.stdout)
            for rule in data.get("rules", []):
                if rule.get("type") == "required_status_checks":
                    params = rule.get("parameters", {})
                    checks += [c["context"] for c in params.get("required_status_checks", [])]
        return checks
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def git_subjects(root: Path, count: int = 30) -> list[str]:
    """Recent human and agent subjects: merge commits are platform text
    and bot bumps answer to their own conventions, so neither counts."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "log", f"-{count}", "--format=%an%x09%s"],
            capture_output=True, text=True, timeout=30, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if out.returncode != 0:
        return []
    subjects = []
    for line in out.stdout.splitlines():
        author, _, subject = line.partition("\t")
        if "[bot]" in author or subject.startswith("Merge "):
            continue
        if subject.strip():
            subjects.append(subject)
    return subjects


def presence(root: Path, stem: str, what: str, in_ci: bool) -> tuple[int, str]:
    found = find_file(root, stem)
    if not found:
        return 0, f"no {what} file"
    level = 4 if in_ci else 3
    return level, f"{found.name} present; " + (
        "this scorer runs in CI" if in_ci else "checked on demand by this scorer"
    )


def score(root: Path, repo: str | None, kind_override: str | None = None) -> tuple[str, list[Result]]:
    manifest = load_manifest(root)
    kind = kind_override or manifest["kind"] or guess_kind(root)
    if kind not in KINDS:
        kind = guess_kind(root)
    invites = manifest["invites_contributions"]
    if invites is None:
        invites = kind in ("application", "doctrine", "reference", "study")
    wf = workflow_text(root)
    scorer_in_ci = "score.py" in wf
    readme = read(find_file(root, "README") or root / "README.md")
    results: list[Result] = []

    def add(rule: str, applies: bool, level: int | None, reason: str) -> None:
        if rule in manifest["exclusions"]:
            results.append(Result(rule, None, "excluded: " + manifest["exclusions"][rule]))
            return
        if not applies:
            article = "an" if kind[0] in "aeiou" else "a"
            results.append(Result(rule, None, f"not applicable to {article} {kind} repository"))
            return
        if level == 4 and rule in manifest["proven"]:
            level, reason = 5, reason + "; proven: " + manifest["proven"][rule]
        results.append(Result(rule, level, reason))

    lvl, why = presence(root, "README", "README", scorer_in_ci)
    add("readme", True, lvl, why)
    lvl, why = presence(root, "LICENSE", "LICENSE", scorer_in_ci)
    add("license", kind != "profile", lvl, why)
    lvl, why = presence(root, "SECURITY", "SECURITY.md", scorer_in_ci)
    add("security-policy", kind in ("application", "doctrine", "reference", "study"), lvl, why)
    lvl, why = presence(root, "CONTRIBUTING", "CONTRIBUTING", scorer_in_ci)
    add("contributing", bool(invites), lvl, why)

    decisions = read(root / "DECISIONS.md")
    entries = len(DECISION_HEAD.findall(decisions))
    if not decisions:
        add("decisions-record", kind in ("application", "doctrine"), 0, "no DECISIONS.md")
    else:
        counted = any("DECISIONS" in read(t) for t in root.glob("tests/*.py"))
        level = 4 if counted else 1
        add("decisions-record", kind in ("application", "doctrine"), level,
            f"{entries} numbered entries; " + (
                "a test recounts them" if counted else "nothing recounts the entries"))

    subjects = git_subjects(root)
    if subjects:
        bad = [s for s in subjects if not SUBJECT.match(s)]
        walked = "check_commit_message" in wf
        hook = (root / ".pre-commit-config.yaml").exists() and "commit" in read(root / ".pre-commit-config.yaml")
        if bad:
            add("commit-subjects", True, 0,
                f"{len(bad)} of {len(subjects)} recent subjects lack a leading identifier")
        else:
            level = 4 if walked else (3 if hook else 3)
            add("commit-subjects", True, level,
                f"all {len(subjects)} recent subjects lead with an identifier; " + (
                    "CI walks the messages" if walked else "verified by this scorer"))
    else:
        add("commit-subjects", True, 0, "no git history readable")

    if wf:
        uses = ANY_USES.findall(wf)
        pinned = SHA_PIN.findall(wf)
        if len(uses) != len(pinned):
            add("pinned-actions", True, 0,
                f"{len(uses) - len(pinned)} of {len(uses)} action uses are not pinned to a commit")
        else:
            audited = any(t in wf for t in ("zizmor", "pinact", "check_actions_inventory"))
            add("pinned-actions", True, 4 if audited else 3,
                f"all {len(uses)} uses pinned by commit; " + (
                    "a workflow audit gates it" if audited else "verified by this scorer"))
    else:
        add("pinned-actions", False, None, "")

    if wf:
        checks = required_checks(repo)
        if checks is None:
            add("ci-gate", kind != "profile", 1,
                "workflows exist; required checks unverified (no platform access)")
        elif checks:
            add("ci-gate", kind != "profile", 4,
                f"{len(checks)} required checks on the mainline: " + ", ".join(sorted(checks)))
        else:
            add("ci-gate", kind != "profile", 1, "workflows exist but nothing is required to merge")
    else:
        add("ci-gate", kind not in ("profile", "diagrams"), 0, "no workflows")

    dep = (root / ".github" / "dependabot.yml").exists() or (root / "renovate.json").exists()
    add("dependency-updates", kind in ("application", "doctrine"), 3 if dep else 0,
        "update automation configured" if dep else "no dependency update configuration")

    run_head = re.search(r"^#+\s*(run|running|quick start|getting started|how to run|getting the deck|using)", readme, re.I | re.M)
    add("run-instructions", kind in ("application", "reference", "study"),
        1 if run_head and "```" in readme else 0,
        "README has a run section with a command block" if run_head else "README has no run section")

    trouble = re.search(r"^#+\s*.*troubleshoot", readme, re.I | re.M)
    add("troubleshooting", kind == "application", 1 if trouble else 0,
        "README names the likely failures" if trouble else "README has no troubleshooting section")

    figures = re.findall(r"\*\*\d[\d,]*\s+\w+", readme)
    if figures:
        recounted = any("README" in read(t) for t in root.glob("tests/*.py"))
        add("counted-figures", kind == "application", 4 if recounted else 1,
            f"{len(figures)} bold figures; " + (
                "a test recounts them from the source" if recounted else "nothing recounts them"))
    else:
        add("counted-figures", kind == "application", 0, "README states no figures")

    scripts = list(root.glob("scripts/*.py"))
    checker = [s for s in scripts if "--check" in read(s)]
    if kind in ("reference", "study"):
        if checker:
            in_ci = any(s.name in wf for s in checker)
            add("generated-artifact-parity", True, 4 if in_ci else 3,
                f"{checker[0].name} verifies the generated artifact; " + (
                    "CI runs it" if in_ci else "checked on demand"))
        else:
            add("generated-artifact-parity", True, 0, "no parity check for generated artifacts")
    else:
        add("generated-artifact-parity", False, None, "")

    return kind, results


def render(root: Path, kind: str, results: list[Result]) -> str:
    scored = [r for r in results if r.level is not None]
    mean = sum(r.level for r in scored) / len(scored) if scored else 0.0
    lines = [f"## {root.name}: {mean:.1f} of 5 across {len(scored)} rules ({kind})", "",
             "| Rule | Level | Evidence |", "|---|---|---|"]
    for r in results:
        level = "n/a" if r.level is None else str(r.level)
        lines.append(f"| {r.rule} | {level} | {r.reason} |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path")
    parser.add_argument("--repo", help="owner/name, for required-check lookup")
    parser.add_argument("--kind", choices=KINDS, help="override the repository kind")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    kind, results = score(root, args.repo, args.kind)
    if args.json:
        print(json.dumps({"repository": root.name, "kind": kind,
                          "rules": [r.__dict__ for r in results]}, indent=2))
    else:
        print(render(root, kind, results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
