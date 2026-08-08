from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from Brain.Team.archivist import Archivist
from Brain.Team.delegation import TeamDelegator
from Runtime.Knowledge.catalog import KnowledgeCatalog
from Runtime.Knowledge.stores import StorePaths


class LibrarySearchTest(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        root = Path(self.temporary.name)
        self.filing = root / "Filing"
        self.bookshelf = root / "Bookshelf"
        self.filing.mkdir()
        (self.bookshelf / "Procedures").mkdir(parents=True)
        self.catalog = KnowledgeCatalog(root / "catalog.db")
        self.archivist = Archivist(StorePaths(self.filing, self.bookshelf), self.catalog)

    def tearDown(self):
        self.temporary.cleanup()

    def test_searches_passages_in_both_stores_with_origin(self):
        private = self.filing / "Personal" / "telescope.md"
        private.parent.mkdir()
        private.write_text(
            "# Telescope Case\n\nThe spare eyepiece is inside the blue telescope case.",
            encoding="utf-8",
        )
        shared = self.bookshelf / "Procedures" / "lens-care.md"
        shared.write_text(
            "---\ntype: Procedure\ntitle: Lens Care\n---\n\n"
            "# Lens Care\n\nTelescope lenses need a dedicated optical cloth.",
            encoding="utf-8",
        )
        originals = private.read_bytes(), shared.read_bytes()

        self.archivist.inventory()
        results = self.catalog.search("telescope")

        self.assertEqual({result.store for result in results}, {"filing_cabinet", "bookshelf"})
        self.assertTrue(any("optical cloth" in result.passage for result in results))
        self.assertEqual((private.read_bytes(), shared.read_bytes()), originals)

    def test_existing_catalogue_is_upgraded_without_file_changes(self):
        note = self.bookshelf / "Procedures" / "upgrade.md"
        note.write_text("# Upgrade\n\nExisting telescope knowledge.", encoding="utf-8")

        entries, _ = self.archivist._scan("bookshelf", self.bookshelf)
        self.catalog.replace_store("bookshelf", entries)
        self.assertEqual(self.catalog.search("telescope"), [])

        self.archivist.inventory()

        self.assertEqual(len(self.catalog.search("telescope")), 1)

    def test_changed_deleted_and_moved_files_refresh_the_index(self):
        note = self.bookshelf / "Procedures" / "care.md"
        note.write_text("# Care\n\nUse a cotton cloth.", encoding="utf-8")
        self.archivist.inventory()
        self.assertEqual(len(self.catalog.search("cotton")), 1)

        note.write_text("# Care\n\nUse a dedicated optical cloth.", encoding="utf-8")
        self.archivist.inventory()
        self.assertEqual(self.catalog.search("cotton"), [])
        self.assertEqual(len(self.catalog.search("optical")), 1)

        destination = self.bookshelf / "Reference" / note.name
        destination.parent.mkdir()
        note.rename(destination)
        self.archivist.inventory()
        self.assertEqual(self.catalog.search("optical")[0].relative_path, "Reference/care.md")

        destination.unlink()
        report = self.archivist.inventory()
        self.assertEqual(report.removed, 1)
        self.assertEqual(self.catalog.search("optical"), [])

    def test_library_command_returns_source_linked_passage(self):
        note = self.bookshelf / "Procedures" / "lens-care.md"
        note.write_text(
            "---\ntype: Procedure\ntitle: Lens Care\n---\n\n"
            "Telescope lenses should be cleaned with a dedicated optical cloth.",
            encoding="utf-8",
        )
        result = TeamDelegator(self.archivist).handle(
            "Ask the Library: What cloth should I use on telescope lenses?"
        )

        self.assertTrue(result.handled)
        self.assertIn("dedicated optical cloth", result.response)
        self.assertIn("Source: Bookshelf/Procedures/lens-care.md", result.response)
        self.assertEqual(result.response.count("Telescope lenses should be cleaned"), 1)

    def test_explicit_reindex_reports_stale_removal(self):
        note = self.filing / "old.md"
        note.write_text("# Old note\n\nTemporary knowledge.", encoding="utf-8")
        self.archivist.inventory()
        note.unlink()

        result = TeamDelegator(self.archivist).handle("Ask the Library to re-index")

        self.assertTrue(result.handled)
        self.assertIn("1 stale entry removed", result.response)


if __name__ == "__main__":
    unittest.main()
