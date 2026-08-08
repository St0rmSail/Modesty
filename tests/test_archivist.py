from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from Brain.Team.archivist import Archivist
from Runtime.Knowledge.catalog import KnowledgeCatalog
from Runtime.Knowledge.stores import StorePaths


class ArchivistTest(unittest.TestCase):
    def test_catalogues_both_stores_without_changing_documents(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            filing = root / "Filing"
            bookshelf = root / "Bookshelf"
            filing.mkdir()
            (bookshelf / "Reference").mkdir(parents=True)
            private = filing / "note.md"
            shared = bookshelf / "Reference" / "fact.md"
            private.write_text("# Private Note\n\nSecret.", encoding="utf-8")
            shared.write_text("---\ntype: Reference\ntitle: A Fact\n---\n\n# A Fact", encoding="utf-8")
            original = private.read_bytes(), shared.read_bytes()
            catalog = KnowledgeCatalog(root / "catalog.db")

            report = Archivist(StorePaths(filing, bookshelf), catalog).inventory()
            entries = catalog.entries()

            self.assertEqual((report.documents, report.warnings), (2, 0))
            self.assertEqual({entry.store for entry in entries}, {"filing_cabinet", "bookshelf"})
            self.assertEqual((private.read_bytes(), shared.read_bytes()), original)

    def test_warns_for_bookshelf_metadata_and_removes_stale_entries(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            filing = root / "Filing"
            bookshelf = root / "Bookshelf"
            filing.mkdir()
            bookshelf.mkdir()
            candidate = bookshelf / "candidate.md"
            candidate.write_text("# Candidate", encoding="utf-8")
            catalog = KnowledgeCatalog(root / "catalog.db")
            archivist = Archivist(StorePaths(filing, bookshelf), catalog)

            first = archivist.inventory()
            candidate.unlink()
            second = archivist.inventory()

            self.assertEqual(first.warnings, 1)
            self.assertEqual(second.removed, 1)
            self.assertEqual(catalog.entries(), [])

    def test_ignores_templates_and_tracks_content_hash_changes(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            filing = root / "Filing"
            bookshelf = root / "Bookshelf"
            filing.mkdir()
            (bookshelf / "_Templates").mkdir(parents=True)
            (bookshelf / "_Templates" / "concept.md").write_text("template", encoding="utf-8")
            document = bookshelf / "index.md"
            document.write_text("# Bookshelf", encoding="utf-8")
            catalog = KnowledgeCatalog(root / "catalog.db")
            archivist = Archivist(StorePaths(filing, bookshelf), catalog)

            archivist.inventory()
            old_hash = catalog.entries()[0].sha256
            document.write_text("# Bookshelf\n\nChanged", encoding="utf-8")
            archivist.inventory()

            self.assertEqual(len(catalog.entries()), 1)
            self.assertNotEqual(catalog.entries()[0].sha256, old_hash)


if __name__ == "__main__":
    unittest.main()
