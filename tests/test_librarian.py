import json
from pathlib import Path
import re
import sqlite3
from tempfile import TemporaryDirectory
import unittest
import zipfile
from Brain.Team.delegation import TeamDelegator
from Brain.Team.librarian import Librarian, LibrarianError
from Runtime.Core import team_status
from Runtime.Reading import ReadingCollection, ReadingCollectionError
from Runtime.Research.pending_reports import PendingReportStore


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

    def test_text_repair_preserves_original_and_keeps_a_logged_derivative(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            catalogue = root / "catalogue.db"
            source = paths.intake / "rough-story.txt"
            original = b"Chapter One  \r\n\r\n\r\n\r\nA\xc2\xa0quiet line"
            source.write_bytes(original)
            librarian = Librarian(paths, catalogue)

            proposal = librarian.prepare_text_repair(source.name)

            self.assertEqual(source.read_bytes(), original)
            derivative = paths.root / proposal.derivative_relative_path
            self.assertEqual(
                derivative.read_text(encoding="utf-8"),
                "Chapter One\n\n\nA quiet line\n",
            )
            self.assertIn("trailing spaces", " ".join(proposal.actions))
            self.assertIn("non-breaking spaces", " ".join(proposal.actions))
            self.assertIn("Original SHA-256", librarian.repair_briefing(proposal))

            kept = librarian.resolve_repair(proposal.repair_id, keep=True)
            self.assertEqual(kept, derivative)
            self.assertTrue(derivative.exists())
            connection = sqlite3.connect(catalogue)
            try:
                status = connection.execute(
                    "SELECT status FROM repair_jobs WHERE repair_id = ?",
                    (proposal.repair_id,),
                ).fetchone()[0]
            finally:
                connection.close()
            self.assertEqual(status, "kept")

    def test_keep_refuses_stale_original_or_changed_derivative(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            source = paths.intake / "rough.txt"
            source.write_bytes(b"Rough line   ")
            librarian = Librarian(paths, root / "catalogue.db")

            stale_source = librarian.prepare_text_repair(source.name)
            source.write_bytes(b"Externally changed")
            with self.assertRaisesRegex(LibrarianError, "original changed"):
                librarian.resolve_repair(stale_source.repair_id, keep=True)

            source.write_bytes(b"Rough line   ")
            changed_derivative = librarian.prepare_text_repair(source.name)
            derivative = paths.root / changed_derivative.derivative_relative_path
            derivative.write_text("tampered", encoding="utf-8")
            with self.assertRaisesRegex(LibrarianError, "derivative changed"):
                librarian.resolve_repair(changed_derivative.repair_id, keep=True)

    def test_toss_removes_only_derivative_and_unsafe_repairs_fail_closed(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            source = paths.intake / "rough.md"
            source.write_bytes(b"Line with spaces   ")
            librarian = Librarian(paths, root / "catalogue.db")
            proposal = librarian.prepare_text_repair(source.name)
            derivative = paths.root / proposal.derivative_relative_path

            self.assertIsNone(librarian.resolve_repair(proposal.repair_id, keep=False))
            self.assertFalse(derivative.exists())
            self.assertEqual(source.read_bytes(), b"Line with spaces   ")
            with self.assertRaisesRegex(LibrarianError, "directly inside"):
                librarian.prepare_text_repair("../rough.md")
            (paths.intake / "book.pdf").write_bytes(b"%PDF-")
            with self.assertRaisesRegex(LibrarianError, "only UTF-8"):
                librarian.prepare_text_repair("book.pdf")
            (paths.intake / "clean.txt").write_bytes(b"Already clean\n")
            with self.assertRaisesRegex(LibrarianError, "no safe mechanical repair"):
                librarian.prepare_text_repair("clean.txt")

    def test_repair_command_creates_a_local_pending_briefing(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            (paths.intake / "rough.txt").write_bytes(b"Rough line   ")
            pending = PendingReportStore(root / "pending")
            delegator = TeamDelegator.__new__(TeamDelegator)
            delegator.librarian = Librarian(paths, root / "catalogue.db")
            delegator.pending_reports = pending
            delegator._help_active = False
            team_status.reset()

            result = delegator.handle("Ask the Librarian to repair: rough.txt")

            self.assertTrue(result.handled)
            self.assertIn("original is unchanged", result.response.casefold())
            self.assertTrue(result.action.startswith("open_briefing:BR-"))
            report = pending.load(result.action.partition(":")[2])
            self.assertTrue(report.provider.startswith("librarian:LR-"))
            self.assertIn("Provisional derivative", report.body)
            self.assertEqual(team_status.member_state("librarian"), "waiting")

    def test_inspection_reads_indexes_and_shelves_an_unchanged_nested_text(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            nested = paths.intake / "Loose"
            nested.mkdir()
            source = nested / "Voyage.txt"
            original = b"A voyage around Madagascar taught patience with every changing wind.\n"
            source.write_bytes(original)
            librarian = Librarian(paths, root / "catalogue.db")

            inspection = librarian.inspect_book("Loose/Voyage.txt")

            self.assertEqual(inspection.title, "Voyage")
            self.assertIn("Madagascar", inspection.preview)
            hits = librarian.search_reading("changing wind")
            self.assertEqual(len(hits), 1)
            self.assertIn("Madagascar", hits[0].passage)
            destination = librarian.approve_shelving(inspection.shelving_id)
            self.assertFalse(source.exists())
            self.assertEqual(destination.read_bytes(), original)
            self.assertEqual(destination.relative_to(paths.originals).as_posix(), "Unknown Author/Voyage/Voyage.txt")

    def test_epub_reader_uses_metadata_spine_and_nested_intake_path(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            source = paths.intake / "sample.epub"
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("META-INF/container.xml", '<container><rootfiles><rootfile full-path="OPS/package.opf"/></rootfiles></container>')
                archive.writestr(
                    "OPS/package.opf",
                    '<package xmlns:dc="urn:dc"><metadata><dc:title>The Lamp</dc:title><dc:creator>Alex Example</dc:creator></metadata>'
                    '<manifest><item id="c1" href="chapter.xhtml"/></manifest><spine><itemref idref="c1"/></spine></package>',
                )
                archive.writestr("OPS/chapter.xhtml", "<html><body><h1>Chapter One</h1><p>The Alexandrian lamp was lit.</p></body></html>")
            librarian = Librarian(paths, root / "catalogue.db")

            inspection = librarian.inspect_book("sample.epub")

            self.assertEqual(inspection.title, "The Lamp")
            self.assertEqual(inspection.author, "Alex Example")
            self.assertIn("Alexandrian lamp", inspection.preview)
            self.assertEqual(inspection.proposed_relative_path, "Alex Example/The Lamp/sample.epub")

    def test_inspection_refuses_unsafe_or_unreadable_input(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            librarian = Librarian(paths, root / "catalogue.db")
            with self.assertRaisesRegex(LibrarianError, "unsafe"):
                librarian.inspect_book("../outside.txt")
            (paths.intake / "locked.mobi").write_bytes(b"not readable")
            with self.assertRaisesRegex(LibrarianError, "not implemented"):
                librarian.inspect_book("locked.mobi")

    def test_commands_report_reading_search_and_require_exact_shelving_approval(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            (paths.intake / "story.txt").write_text("The brass telescope stood beside the window.", encoding="utf-8")
            delegator = TeamDelegator.__new__(TeamDelegator)
            delegator.librarian = Librarian(paths, root / "catalogue.db")
            delegator._help_active = False
            team_status.reset()

            inspected = delegator.handle("Ask the Librarian to examine: story.txt")
            self.assertIn("Nothing has moved", inspected.response)
            shelving_id = re.search(r"LS-[A-F0-9]{8}", inspected.response).group(0)
            found = delegator.handle("Ask the Librarian to find: brass telescope")
            self.assertIn("story.txt", found.response)
            approved = delegator.handle(f"Approve Librarian shelving: {shelving_id}")
            self.assertIn("unchanged original", approved.response)

    @staticmethod
    def _write_config(project: Path, stacks: Path) -> Path:
        config = project / "reading_collection.json"
        config.write_text(json.dumps({"stacks": {"path": str(stacks)}}), encoding="utf-8")
        return config


if __name__ == "__main__":
    unittest.main()
