"""The refresh command fails on the things it exists to catch.

It is the one check here that needs the network, so these tests do not
use it: each replaces the fetch with a page written for the test, which
also lets a new edition be simulated without waiting years for one.

The first test is the load-bearing one. A framework recorded in
frameworks.json with no verifier in the script would be reported
without ever being read, which is the same shape of failure as the
original gate that checked a document against its author's memory.
"""

import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import refresh_frameworks as refresh  # noqa: E402

ENTRY = {
    "title": "Example Framework",
    "heading": "Example (2.0)",
    "version": "2.0",
    "source": "https://example.test/2.0",
    "retrieved": "2026-09-28",
    "items": [
        {"id": "X1", "name": "First Thing"},
        {"id": "X2", "name": "Second Thing"},
    ],
}

VERIFIER = {
    "ids": r"\bX\d\b",
    "edition": {"url": "https://example.test/", "pattern": r"/(\d\.\d)/"},
}

PAGE = "X1 First Thing. X2 Second Thing."
INDEX = 'a href="/1.0/" and a href="/2.0/"'


def run(page: str = PAGE, index: str = INDEX, entry: dict = ENTRY,
        verifier: dict = VERIFIER) -> tuple[bool, str]:
    def fake(url: str, strip_tags: bool = True) -> str:
        return index if url == verifier["edition"]["url"] else page

    with patch.object(refresh, "fetch", fake):
        ok, lines = refresh.check("example", entry, verifier)
    return ok, "\n".join(lines)


class Verifiers(unittest.TestCase):
    def test_every_framework_in_the_data_has_a_verifier(self) -> None:
        data = json.loads(refresh.DATA.read_text())["frameworks"]
        self.assertEqual(set(data), set(refresh.VERIFIERS))

    def test_every_verifier_declares_an_edition_probe_or_states_it_has_none(
        self,
    ) -> None:
        """None is a deliberate answer and a missing key is an oversight,
        so the difference is required to be written down."""
        for key, verifier in refresh.VERIFIERS.items():
            self.assertIn("edition", verifier, key)
            self.assertIn("ids", verifier, key)


class Comparison(unittest.TestCase):
    def test_versions_order_by_number_and_not_by_text(self) -> None:
        self.assertGreater(refresh.as_version("1.2"), refresh.as_version("1.1"))
        self.assertGreater(refresh.as_version("2025"), refresh.as_version("2021"))
        self.assertGreater(refresh.as_version("5.0.0"), refresh.as_version("4.0"))
        # The comparison a text sort gets wrong, and the one that will
        # matter first: a tenth release against a ninth.
        self.assertGreater(refresh.as_version("1.10"), refresh.as_version("1.9"))

    def test_names_compare_on_words_alone(self) -> None:
        self.assertEqual(
            refresh.flatten("Server-Side Request Forgery"),
            refresh.flatten("server side request forgery"),
        )


class Checks(unittest.TestCase):
    def test_a_source_that_still_matches_passes(self) -> None:
        ok, report = run()
        self.assertTrue(ok, report)
        self.assertIn("all 2 recorded items still appear", report)
        self.assertIn("2.0 is the newest published", report)

    def test_a_newer_edition_fails_and_names_itself(self) -> None:
        ok, report = run(index='href="/2.0/" href="/3.1/"')
        self.assertFalse(ok)
        self.assertIn("a newer edition is published: 3.1", report)

    def test_a_renamed_item_fails(self) -> None:
        ok, report = run(page="X1 First Thing. X2 Renamed Entirely.")
        self.assertFalse(ok)
        self.assertIn("X2 Second Thing", report)

    def test_an_item_added_upstream_fails(self) -> None:
        ok, report = run(page=PAGE + " X3 Brand New Thing.")
        self.assertFalse(ok)
        self.assertIn("identifiers the data does not: x3", report)

    def test_an_identifier_upstream_may_be_ignored_only_with_a_reason(self) -> None:
        """The SSDF case: the publication names a practice where it
        records deleting it. The exception is reported, not silent."""
        verifier = dict(VERIFIER, ids_ignore={"X3": "withdrawn in 2.0"})
        ok, report = run(page=PAGE + " X3 Withdrawn Thing.", verifier=verifier)
        self.assertTrue(ok, report)
        self.assertIn("ignoring X3 upstream: withdrawn in 2.0", report)

    def test_an_unreachable_source_is_unchecked_and_fails(self) -> None:
        """Unverified and verified must not look alike."""
        def broken(url: str, strip_tags: bool = True) -> str:
            raise urllib.error.URLError("no route to host")

        with patch.object(refresh, "fetch", broken):
            ok, lines = refresh.check("example", ENTRY, VERIFIER)
        self.assertFalse(ok)
        self.assertIn("unchecked", "\n".join(lines))

    def test_an_edition_index_that_no_longer_matches_is_unchecked(self) -> None:
        """A rewritten index page must not read as no new edition."""
        ok, report = run(index="this page was redesigned")
        self.assertFalse(ok)
        self.assertIn("unchecked: no version found", report)


if __name__ == "__main__":
    unittest.main()
