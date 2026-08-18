import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from Brain.Team.delegation import TeamDelegator
from Brain.Team.librarian import Librarian, LibrarianError
from Runtime.Core import team_status
from Runtime.Reading import ReadingCollection, ReadingCollectionError


class LibrarianTest(unittest.TestCase):
    def test_initializes_the_stacks_without_overwriting(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            stacks = root / "The Stacks"
            config = self._write_config(project, stacks)
            collection = ReadingCollection(config, project)
            paths = collection.initialize()
            index = stacks / "index.md"
            index.write_text("Drew's existing Stacks index", encoding="utf-8")
            collection.initialize()

            self.assertTrue(paths.intake.is_dir())
            self.assertTrue(paths.originals.is_dir())
            self.assertTrue(paths.workbench.is_dir())
            self.assertEqual(index.read_text(encoding="utf-8"), "Drew's existing Stacks index")

    def test_rejects_a_collection_inside_the_public_repository(self):
        with TemporaryDirectory() as folder:
            project = Path(folder) / "project"
            project.mkdir()
            config = self._write_config(project, project / "Stacks")
            with self.assertRaisesRegex(ReadingCollectionError, "outside"):
                ReadingCollection(config, project)

    def test_inventory_is_read_only_and_records_damage_duplicates_and_stale_items(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            catalogue = root / "catalogue.db"
            first = paths.intake / "story.txt"
            duplicate = paths.intake / "story-copy.txt"
            invalid_epub = paths.intake / "broken.epub"
            unsupported = paths.intake / "cover.xyz"
            first.write_text("A preserved story", encoding="utf-8")
            duplicate.write_text("A preserved story", encoding="utf-8")
            invalid_epub.write_bytes(b"not an epub")
            unsupported.write_bytes(b"unknown")
            originals = {path: path.read_bytes() for path in paths.intake.iterdir()}

            librarian = Librarian(paths, catalogue)
            report = librarian.inventory()
            self.assertEqual(report.scanned, 4)
            self.assertEqual(report.supported, 3)
            self.assertEqual(report.unsupported, 1)
            self.assertEqual(report.attention, 2)
            self.assertEqual(report.duplicate_groups, 1)
            self.assertEqual(originals, {path: path.read_bytes() for path in paths.intake.iterdir()})

            duplicate.unlink()
            second = librarian.inventory()
            self.assertEqual(second.stale_removed, 1)
            connection = sqlite3.connect(catalogue)
            try:
                count = connection.execute("SELECT COUNT(*) FROM reading_items").fetchone()[0]
            finally:
                connection.close()
            self.assertEqual(count, 3)

    def test_inventory_refuses_an_unbounded_sample(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            librarian = Librarian(paths, root / "catalogue.db")
            librarian.MAX_FILES = 1
            (paths.intake / "one.txt").write_text("one", encoding="utf-8")
            (paths.intake / "two.txt").write_text("two", encoding="utf-8")
            with self.assertRaisesRegex(LibrarianError, "smaller bounded sample"):
                librarian.inventory()

    def test_modesty_reports_the_bounded_duty_without_model_fallback(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            (paths.intake / "sample.txt").write_text("sample", encoding="utf-8")
            delegator = TeamDelegator.__new__(TeamDelegator)
            delegator.librarian = Librarian(paths, root / "catalogue.db")
            delegator._help_active = False
            team_status.reset()

            result = delegator.handle("Ask the Librarian to inventory The Stacks")

            self.assertTrue(result.handled)
            self.assertIn("Files seen: 1", result.response)
            self.assertIn("No reading file was renamed", result.response)
            self.assertEqual(team_status.member_state("librarian"), "ready")

    @staticmethod
    def _write_config(project: Path, stacks: Path) -> Path:
        config = project / "reading_collection.json"
        config.write_text(json.dumps({"stacks": {"path": str(stacks)}}), encoding="utf-8")
        return config


if __name__ == "__main__":
    unittest.main()
