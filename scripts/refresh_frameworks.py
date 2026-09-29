#!/usr/bin/env python3
"""Refetch every framework source and fail when one has moved.

frameworks.json records what each framework published, with its source
and the date it was read. That record is only worth something if
something notices when it goes out of date, and the offline gate
cannot: scripts/check_coverage.py checks the document against the data
file, so when the data file itself is a version behind, both agree and
both are wrong. That is exactly what happened before this existed
(D-032).

So this asks the sources two questions.

1. Do the recorded items still appear where they were read? A renamed
   item or a reworded chapter title shows up here.
2. Has a newer edition been published? This is the question that
   matters, and the one presence alone cannot answer: the 2021 Top 10
   page still exists and still says 2021, so a document mapping it
   stays internally consistent forever. Each framework therefore has a
   second probe against the index that lists its editions, and a
   version higher than the recorded one is a failure naming itself.

It needs the network, so it is not a commit hook. It runs on a schedule
in the pipeline and by hand before a coverage change, and a failure is
work to do rather than a broken build: read the new edition, update
frameworks.json, and redo the mapping for whatever changed.

The script refuses to guess. Where a source cannot be reached or read,
the framework is reported unchecked and the exit code is nonzero,
because an unverified claim and a verified one must not look alike.

Usage: scripts/refresh_frameworks.py [--framework KEY]
"""

import argparse
import json
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "frameworks.json"
TIMEOUT = 40
AGENT = "build-doctrine-refresh (+https://github.com/tltaylor1/build-doctrine)"

# How to verify each framework. Keyed by the key in frameworks.json, and
# the keys must match exactly: a framework added to the data without a
# verifier here fails rather than being silently unchecked.
#
# items:   where the item list is read. Defaults to the entry's source.
# ids:     a pattern matching item identifiers upstream. Where one can be
#          written without false positives, an identifier found upstream
#          and missing from the data is a failure, which catches an added
#          item as well as a renamed one.
# edition: the index that lists published editions, with a pattern whose
#          first group is a version. Anything higher than the recorded
#          version fails. Where a framework has no editions, this is None
#          and the report says so rather than implying a check ran.
VERIFIERS: dict[str, dict] = {
    "owasp-top-10": {
        "ids": r"\bA\d{2}:2025\b",
        "edition": {
            "url": "https://owasp.org/www-project-top-ten/",
            "pattern": r"Top 10[:\s]+(20\d\d)",
        },
    },
    "owasp-api-top-10": {
        "ids": r"\bAPI\d{1,2}:2023\b",
        "edition": {
            "url": "https://api-security.owasp.org/",
            "pattern": r"editions/(20\d\d)",
        },
    },
    "owasp-llm-top-10": {
        # The identifiers carry their own edition year, and this page is
        # the list's home rather than one year's copy of it, so a new
        # edition arrives here as identifiers the data does not have.
        "ids": r"\bLLM\d{2}:20\d\d\b",
        "edition": None,
    },
    "stride": {
        # Six categories from a definition that has not changed since
        # Microsoft published it. No editions to compare.
        "ids": None,
        "edition": None,
    },
    "nist-ssdf": {
        "ids": r"\b(?:PO|PS|PW|RV)\.\d\b",
        "ids_ignore": {
            "PW.3": "deleted in version 1.1 and merged into PW.4, and the "
                    "publication still names it where it records the deletion",
        },
        "edition": {
            "url": "https://csrc.nist.gov/pubs/sp/800/218/final",
            "pattern": r"Version (\d\.\d)",
        },
    },
    "owasp-asvs": {
        # The chapter titles are the directory's filenames, read through
        # the API because the tree page is rendered in the browser.
        "items": "https://api.github.com/repos/OWASP/ASVS/contents/5.0/en",
        "ids": None,
        "edition": {
            "url": "https://api.github.com/repos/OWASP/ASVS/contents/",
            "pattern": r'"name":\s*"(\d+\.\d+)"',
        },
    },
    "slsa": {
        "ids": r"\b(?:Build|Source) L\d\b",
        "edition": {
            "url": "https://slsa.dev/spec/",
            "pattern": r"/spec/v(\d+\.\d+)/",
        },
    },
}


def fetch(url: str, strip_tags: bool = True) -> str:
    """The text of a URL. A PDF is converted, because SP 800-218 is only
    published as one and reading it is the whole point.

    An edition index is read with its markup intact, because the version
    it lists is usually in a link target rather than in the words on the
    page, and stripping the tags throws exactly that away."""
    request = urllib.request.Request(url, headers={"User-Agent": AGENT})
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=TIMEOUT, context=context) as body:
        raw = body.read()
    if raw[:5] == b"%PDF-":
        if not shutil.which("pdftotext"):
            raise RuntimeError("pdftotext is not installed and the source is a PDF")
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "source.pdf"
            pdf.write_bytes(raw)
            done = subprocess.run(
                ["pdftotext", "-q", str(pdf), "-"],
                capture_output=True, text=True, check=False,
            )
            if done.returncode != 0:
                raise RuntimeError(f"pdftotext failed: {done.stderr.strip()}")
            return done.stdout
    text = raw.decode("utf-8", errors="replace")
    if not strip_tags:
        return text
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.S | re.I)
    return unescape(re.sub(r"<[^>]+>", " ", text))


def flatten(text: str) -> str:
    """Compare on words only. Upstream moves between hyphens, slashes,
    and smart punctuation without changing what an item is called."""
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text.lower()).split())


def as_version(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", text))


def sources_of(entry: dict, verifier: dict) -> list[str]:
    where = verifier.get("items") or entry["source"]
    return [where] if isinstance(where, str) else list(where)


def check(key: str, entry: dict, verifier: dict) -> tuple[bool, list[str]]:
    """Returns whether the framework verified, and the lines to report."""
    lines: list[str] = []
    ok = True

    try:
        text = " ".join(fetch(url) for url in sources_of(entry, verifier))
    except (urllib.error.URLError, OSError, RuntimeError) as problem:
        return False, [f"  unchecked: could not read the source: {problem}"]

    flat = flatten(text)

    missing = [
        f"{item['id']} {item['name']}"
        for item in entry["items"]
        if flatten(item["id"]) not in flat or flatten(item["name"]) not in flat
    ]
    if missing:
        ok = False
        lines.append(
            f"  {len(missing)} recorded item(s) no longer appear at the source:"
        )
        lines += [f"    {name}" for name in missing]
    else:
        lines.append(f"  all {len(entry['items'])} recorded items still appear")

    if verifier["ids"]:
        recorded = {flatten(item["id"]) for item in entry["items"]}
        # An identifier the source names while explaining that it is gone.
        # Listed with its reason, and reported, so the exception is visible
        # rather than being a quiet hole in the check.
        ignored = verifier.get("ids_ignore", {})
        for identifier, reason in ignored.items():
            lines.append(f"  ignoring {identifier} upstream: {reason}")
        found = {flatten(found) for found in re.findall(verifier["ids"], text)}
        extra = sorted(found - recorded - {flatten(one) for one in ignored})
        if extra:
            ok = False
            lines.append(
                "  the source carries identifiers the data does not: "
                + ", ".join(extra)
            )
    else:
        lines.append("  no identifier pattern: presence of each item is the check")

    probe = verifier["edition"]
    if probe is None:
        lines.append("  no editions to compare")
    else:
        try:
            index = fetch(probe["url"], strip_tags=False)
        except (urllib.error.URLError, OSError, RuntimeError) as problem:
            return False, lines + [
                f"  unchecked: could not read the edition index: {problem}"
            ]
        published = sorted(
            {found for found in re.findall(probe["pattern"], index)},
            key=as_version,
        )
        if not published:
            ok = False
            lines.append(
                f"  unchecked: no version found at {probe['url']}, so the "
                "pattern no longer matches the page"
            )
        else:
            recorded = as_version(entry["version"])
            newer = [one for one in published if as_version(one) > recorded]
            if newer:
                ok = False
                lines.append(
                    f"  a newer edition is published: {', '.join(newer)} "
                    f"(recorded: {entry['version']})"
                )
            else:
                lines.append(
                    f"  {entry['version']} is the newest published "
                    f"(seen: {', '.join(published)})"
                )
    return ok, lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--framework", help="check one key from frameworks.json instead of all"
    )
    arguments = parser.parse_args()

    data = json.loads(DATA.read_text())["frameworks"]

    # A framework with no verifier is worse than one that fails, because
    # it looks checked in the report and is not.
    unverified = sorted(set(data) - set(VERIFIERS))
    unknown = sorted(set(VERIFIERS) - set(data))
    if unverified or unknown:
        for key in unverified:
            print(f"{key}: in frameworks.json with no verifier here", file=sys.stderr)
        for key in unknown:
            print(f"{key}: verified here and not in frameworks.json", file=sys.stderr)
        return 2

    keys = [arguments.framework] if arguments.framework else list(data)
    if arguments.framework and arguments.framework not in data:
        print(f"no such framework: {arguments.framework}", file=sys.stderr)
        return 2

    failed = []
    for key in keys:
        entry = data[key]
        print(f"{key} ({entry['title']} {entry['version']})")
        ok, lines = check(key, entry, VERIFIERS[key])
        for line in lines:
            print(line)
        if not ok:
            failed.append(key)

    print()
    if failed:
        print(
            f"refresh: {len(failed)} of {len(keys)} framework(s) need attention: "
            + ", ".join(failed),
            file=sys.stderr,
        )
        print(
            "refresh: update frameworks.json from the source, redo the mapping "
            "for what changed, and set retrieved to today's date.",
            file=sys.stderr,
        )
        return 1
    print(f"refresh: {len(keys)} framework(s) match their sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
