"""The decisions record answers to its own structure.

The role-call application recounts its decisions against a stated
figure, and that gate fired twice in one day. This repository states
no figure, so the recount here holds the record's shape instead:
entries are numbered without gaps or duplicates, and every entry has
a body, because a heading with nothing under it is a decision that
was never actually recorded.
"""

import re
import unittest
from pathlib import Path

RECORD = Path(__file__).resolve().parent.parent / "DECISIONS.md"
HEADING = re.compile(r"^## D-(\d{3}): (.+)$", re.MULTILINE)


class DecisionsRecord(unittest.TestCase):
    def test_entries_are_sequential_and_each_has_a_body(self) -> None:
        text = RECORD.read_text()
        matches = list(HEADING.finditer(text))
        numbers = [int(m.group(1)) for m in matches]
        self.assertEqual(numbers, list(range(1, len(numbers) + 1)),
                         "decision numbers must run 1 to N with no gaps or repeats")
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[match.end():end].strip()
            self.assertGreater(len(body), 200, f"D-{match.group(1)} has no real body")

    def test_every_recent_entry_names_what_it_rejected(self) -> None:
        # From D-025 onward, the entry that made the record scorable, an
        # entry names the alternatives it turned down in so many words.
        # Earlier entries argue against alternatives without the word,
        # and rewriting history to satisfy a regex would be the wrong fix.
        text = RECORD.read_text()
        matches = list(HEADING.finditer(text))
        for index, match in enumerate(matches):
            if int(match.group(1)) < 25:
                continue
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[match.end():end]
            self.assertRegex(body, r"[Rr]ejected",
                             f"D-{match.group(1)} names no rejected alternative")


if __name__ == "__main__":
    unittest.main()
