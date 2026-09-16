"""The documentation site is generated from the documents, never
written beside them.

Every root document has a page in reading order, so a document added
without the site noticing is impossible, and every link between the
documents resolves to a page that holds the heading it names.
"""

import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import build_docs  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


class Site(unittest.TestCase):
    def test_every_root_document_is_a_page(self) -> None:
        docs = {p.name for p in ROOT.glob("*.md")} - build_docs.NOT_PAGES
        self.assertEqual(docs, {src for src, _ in build_docs.PAGES})

    def test_every_cross_page_anchor_resolves(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "site"
            written = build_docs.build(out)
            headings = {
                name: {build_docs.slug(m.group(2))
                       for m in build_docs.HEADING.finditer((out / name).read_text())}
                for name in written
            }
            for name in written:
                for m in re.finditer(r"\]\(([\w.-]+\.md)?#([\w-]+)\)", (out / name).read_text()):
                    page = m.group(1) or name
                    self.assertIn(page, headings, (name, m.group(0)))
                    self.assertIn(m.group(2), headings[page], (name, m.group(0)))
            self.assertTrue((out / "diagrams").is_dir())
            joined = "".join((out / n).read_text() for n in written)
            self.assertNotIn("](diagrams/../", joined)
            self.assertNotIn("](STANDARDS.md", joined)


if __name__ == "__main__":
    unittest.main()
