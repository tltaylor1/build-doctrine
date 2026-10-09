#!/usr/bin/env python3
"""Refuse a change that adds a new exact copy of code already in the repository.

    python3 scripts/check_repetition.py /path/to/repo [--base REF] [--archive PATH]

Logic is written once (D-042). An agent asked for a feature writes a
near-copy of something that exists far more often than it reuses it,
and a fix that lands in one copy misses the others; in one application
the same input bound sat in six parsers and the same revocation rule
in three records before anyone counted (October 2026).

The check runs jscpd, vetted in VETTING.md, in its exact-copy mode,
with the clones the base branch already holds as the baseline, so only
a copy the change adds fails. The noisier passes, renamed and
near-miss copies, report leads for a person to read and gate nothing.
Markdown and YAML are left out: a rendered standards copy and repeated
pipeline steps are copies on purpose.

The binary is fetched from its release and checked against the
checksum pinned here before it runs; --archive uses a release archive
already on disk, checked the same way. The base is --base, or the
pull request's base branch from GITHUB_BASE_REF. With neither, there
is nothing to compare against, and the check says it skipped rather
than passing quietly.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

VERSION = "5.4.0"
ASSET = "jscpd-linux-x64-gnu.tar.gz"
SHA256 = "4c2819a5663e5418fe5dcf0faceca7f05c1f080d3c87fd57cc4ccf99ce857194"
URL = f"https://github.com/kucherenko/jscpd/releases/download/v{VERSION}/{ASSET}"
MEMBERS = {"jscpd", "LICENSE"}
FORMATS = "python,javascript,typescript,jsx,tsx,bash,powershell,go,rust,java,csharp,hcl"


class Refused(Exception):
    """The binary cannot be trusted or the inputs are missing."""


def verify(archive: Path, expected: str = SHA256) -> None:
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != expected:
        raise Refused(f"{archive.name}: checksum {digest} is not the pinned {expected}")


def extract(archive: Path, into: Path) -> Path:
    """Extract the binary alone, refusing an archive holding anything
    the release is not known to hold."""
    with tarfile.open(archive) as tar:
        names = {member.name for member in tar.getmembers()}
        if not names <= MEMBERS:
            raise Refused(f"{archive.name}: unexpected members {sorted(names - MEMBERS)}")
        member = tar.getmember("jscpd")
        if not member.isfile():
            raise Refused(f"{archive.name}: jscpd is not a regular file")
        tar.extract(member, into, filter="data")
    binary = into / "jscpd"
    binary.chmod(0o755)
    return binary


def fetch(into: Path) -> Path:
    archive = into / ASSET
    with urllib.request.urlopen(URL, timeout=120) as response:  # noqa: S310
        archive.write_bytes(response.read())
    return archive


def own_checkout(repo: Path, here: Path = Path(__file__)) -> str | None:
    """The glob for this doctrine's own checkout when it sits inside the
    repository being scanned, as a pipeline's doctrine/ folder does. Its
    scripts are not the repository's code, and an adopter that copied
    one of them would otherwise see the copy reported as new."""
    root = here.resolve().parents[1]
    try:
        inside = root.relative_to(repo.resolve())
    except ValueError:
        return None
    return None if inside == Path(".") else f"{inside.as_posix()}/**"


def command(binary: Path, repo: Path, base: str, skip: str | None = None) -> list[str]:
    # Git's own directory is not the repository's code: installed hooks
    # are near-identical by design and exist only in a checkout.
    ignored = ["**/.git/**"] + ([skip] if skip else [])
    return [
        str(binary), str(repo),
        "--format", FORMATS,
        "--ignore", ",".join(ignored),
        "--baseline-from-ref", base,
        "--fail-on-new-clones",
        "--reporters", "console",
    ]


def base_ref(given: str | None) -> str | None:
    if given:
        return given
    branch = os.environ.get("GITHUB_BASE_REF")
    return f"origin/{branch}" if branch else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo", type=Path)
    parser.add_argument("--base", help="the ref whose clones are the baseline, such as origin/main")
    parser.add_argument("--archive", type=Path, help="a release archive already on disk")
    args = parser.parse_args(argv)

    base = base_ref(args.base)
    if base is None:
        print("repetition: skipped, no base to compare against (give --base, or run on a pull request)")
        return 0
    if platform.system() != "Linux" or platform.machine() not in {"x86_64", "AMD64"}:
        print(f"repetition: refused, the pinned binary is for Linux x86-64, not {platform.system()} {platform.machine()}")
        return 2
    work = Path(os.environ.get("RUNNER_TEMP") or tempfile.mkdtemp())
    try:
        archive = args.archive or fetch(work)
        verify(archive)
        binary = extract(archive, work)
    except Refused as exc:
        print(f"repetition: refused, {exc}")
        return 2
    return subprocess.run(command(binary, args.repo, base, own_checkout(args.repo)), check=False).returncode  # noqa: S603


if __name__ == "__main__":
    sys.exit(main())
