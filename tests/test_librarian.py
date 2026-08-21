import json
from pathlib import Path
import re
import shutil
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

    def test_chapter_aware_reading_position_continues_and_resumes_after_restart(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            source = paths.intake / "continuity.epub"
            chapter_twelve = " ".join(f"twelve-word-{index}" for index in range(350))
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("META-INF/container.xml", '<container><rootfiles><rootfile full-path="OPS/package.opf"/></rootfiles></container>')
                archive.writestr(
                    "OPS/package.opf",
                    '<package xmlns:dc="urn:dc"><metadata><dc:title>Continuity</dc:title><dc:creator>Alex</dc:creator></metadata>'
                    '<manifest><item id="c1" href="chapters.xhtml"/></manifest><spine><itemref idref="c1"/></spine></package>',
                )
                archive.writestr(
                    "OPS/chapters.xhtml",
                    f"<html><body><h1>Chapter 11</h1><p>Earlier material.</p><h1>Chapter 12</h1><p>{chapter_twelve}</p>"
                    "<h1>Chapter 13</h1><p>Later material.</p></body></html>",
                )
            catalogue = root / "catalogue.db"
            librarian = Librarian(paths, catalogue)

            opened = librarian.open_reading("Intake/continuity.epub", chapter="12")
            self.assertEqual(opened.section, "Chapter 12")
            self.assertIn("twelve-word-0", opened.text)
            indexed = librarian.search_reading("twelve-word-0")
            self.assertEqual(indexed[0].section, "Chapter 12")
            continued = librarian.continue_reading(opened.session_id)
            self.assertIn("twelve-word", continued.text)
            title, section = librarian.mark_reading_position(opened.session_id)
            self.assertEqual((title, section), ("Continuity", "Chapter 12"))

            restarted = Librarian(paths, catalogue)
            resumed = restarted.open_reading("Intake/continuity.epub", resume=True)
            self.assertTrue(resumed.resumed)
            self.assertEqual(resumed.section, "Chapter 12")
            self.assertNotEqual(resumed.text, opened.text)
            self.assertNotEqual(resumed.text, continued.text)

    def test_progress_is_edition_specific_and_never_advances_without_marking(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            source = paths.intake / "story.txt"
            source.write_text("First paragraph. " * 300, encoding="utf-8")
            librarian = Librarian(paths, root / "catalogue.db")

            opened = librarian.open_reading("Intake/story.txt")
            librarian.continue_reading(opened.session_id)
            with self.assertRaisesRegex(LibrarianError, "No confirmed"):
                librarian.open_reading("Intake/story.txt", resume=True)
            librarian.mark_reading_position(opened.session_id)
            source.write_text("A changed edition.", encoding="utf-8")
            with self.assertRaisesRegex(LibrarianError, "No confirmed"):
                librarian.open_reading("Intake/story.txt", resume=True)

    def test_reading_commands_are_deterministic(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            (paths.intake / "story.txt").write_text("A long reading line. " * 300, encoding="utf-8")
            delegator = TeamDelegator.__new__(TeamDelegator)
            delegator.librarian = Librarian(paths, root / "catalogue.db")
            delegator._help_active = False
            team_status.reset()

            opened = delegator.handle("Ask the Librarian to open: Intake/story.txt")
            self.assertIn("Mark my place: RP-", opened.response)
            session_id = re.search(r"RP-[A-F0-9]{8}", opened.response).group(0)
            continued = delegator.handle(f"Continue reading: {session_id}")
            self.assertIn(session_id, continued.response)
            marked = delegator.handle(f"Mark my place: {session_id}")
            self.assertIn("confirmed place", marked.response)
            resumed = delegator.handle("Ask the Librarian to resume: Intake/story.txt")
            self.assertIn("resumed", resumed.response)

    def test_incremental_edition_catalogue_uses_source_metadata_without_merging(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            first = paths.intake / "first.epub"
            self._write_identity_epub(first, "Tangled Threads", "Jennifer Estep", "9781439192634", "Elemental Assassin", "4")
            exact = paths.intake / "exact-copy.epub"
            shutil.copyfile(first, exact)
            alternate = paths.intake / "alternate.epub"
            self._write_identity_epub(alternate, "Tangled Threads", "Jennifer Estep", "9781439192634", "Elemental Assassin", "4", extra="alternate")
            librarian = Librarian(paths, root / "catalogue.db")

            report = librarian.catalogue_editions()

            self.assertEqual(report.files_seen, 3)
            self.assertEqual(report.identified_authors, 1)
            self.assertEqual(report.identified_series, 1)
            self.assertEqual(report.exact_duplicate_groups, 1)
            self.assertEqual(report.shared_identifier_groups, 1)
            self.assertEqual(report.possible_same_work_groups, 1)
            self.assertEqual((report.metadata_read, report.reused), (3, 0))
            second = librarian.catalogue_editions()
            self.assertEqual((second.metadata_read, second.reused), (0, 3))
            groups = librarian.edition_review_groups()
            self.assertEqual([group.evidence for group in groups], ["Exact SHA-256 duplicate", "Shared strong identifier"])
            self.assertEqual(len(groups[1].files), 3)
            proposal = librarian.prepare_exact_duplicate_resolution(groups[0].identity, "Intake/first.epub")
            self.assertTrue(exact.exists())
            self.assertIn("Nothing has moved", librarian.duplicate_resolution_response(proposal))
            kept, archived = librarian.approve_exact_duplicate_resolution(proposal.resolution_id)
            self.assertEqual(kept, "Intake/first.epub")
            self.assertFalse(exact.exists())
            self.assertEqual(len(archived), 1)
            archived_path = paths.root / archived[0]
            self.assertEqual(archived_path.read_bytes(), first.read_bytes())
            self.assertTrue(first.exists() and alternate.exists())
            self.assertFalse(exact.exists())

    def test_edition_catalogue_command_is_truthful_and_non_mutating(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            self._write_identity_epub(paths.intake / "book.epub", "Book", "Writer", "123456789X", "Series", "1")
            delegator = TeamDelegator.__new__(TeamDelegator)
            delegator.librarian = Librarian(paths, root / "catalogue.db")
            delegator._help_active = False
            team_status.reset()

            result = delegator.handle("Ask the Librarian to identify works and editions")

            self.assertTrue(result.handled)
            self.assertIn("Readable files seen: 1", result.response)
            self.assertIn("No file was renamed", result.response)
            self.assertEqual(team_status.member_state("librarian"), "ready")

            reviewed = delegator.handle("Ask the Librarian to review edition groups")
            self.assertTrue(reviewed.handled)
            self.assertIn("no reviewable edition relationship", reviewed.response.casefold())

    def test_duplicate_resolution_refuses_changed_source_and_wrong_keep_member(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            first = paths.intake / "one.txt"
            second = paths.intake / "two.txt"
            first.write_bytes(b"identical")
            second.write_bytes(b"identical")
            librarian = Librarian(paths, root / "catalogue.db")
            librarian.catalogue_editions()
            group = librarian.edition_review_groups()[0]
            with self.assertRaisesRegex(LibrarianError, "not a member"):
                librarian.prepare_exact_duplicate_resolution(group.identity, "Intake/other.txt")
            proposal = librarian.prepare_exact_duplicate_resolution(group.identity, "Intake/one.txt")
            second.write_bytes(b"changed")
            with self.assertRaisesRegex(LibrarianError, "changed after review"):
                librarian.approve_exact_duplicate_resolution(proposal.resolution_id)
            self.assertTrue(first.exists() and second.exists())

    def test_natural_duplicate_review_choice_and_contextual_approval(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            handbooks = paths.intake / "Handbooks"
            handbooks.mkdir()
            canonical = handbooks / "Song and Silence.txt"
            redundant = paths.intake / "Song and Silence.txt"
            canonical.write_bytes(b"the same book")
            redundant.write_bytes(b"the same book")
            delegator = TeamDelegator.__new__(TeamDelegator)
            delegator.librarian = Librarian(paths, root / "catalogue.db")
            delegator._help_active = False
            team_status.reset()
            delegator.librarian.catalogue_editions()

            reviewed = delegator.handle("show me the duplicates")
            self.assertIn("Exact SHA-256 duplicate", reviewed.response)
            proposed = delegator.handle("keep the Handbooks copy of Song and Silence")
            self.assertIn("Nothing has moved", proposed.response)
            self.assertTrue(canonical.exists() and redundant.exists())
            approved = delegator.handle("yes, do that")

            self.assertIn("Nothing was deleted", approved.response)
            self.assertTrue(canonical.exists())
            self.assertFalse(redundant.exists())
            archived = list((paths.archive / "Exact Duplicates").rglob("Song and Silence.txt"))
            self.assertEqual(len(archived), 1)
            self.assertEqual(archived[0].read_bytes(), canonical.read_bytes())

    def test_natural_duplicate_choice_requires_unambiguous_displayed_path(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            handbooks = paths.intake / "Handbooks"
            handbooks.mkdir()
            for title, content in (("First", b"first"), ("Second", b"second")):
                (handbooks / f"{title}.txt").write_bytes(content)
                (paths.intake / f"{title}.txt").write_bytes(content)
            delegator = TeamDelegator.__new__(TeamDelegator)
            delegator.librarian = Librarian(paths, root / "catalogue.db")
            delegator._help_active = False
            team_status.reset()
            delegator.librarian.catalogue_editions()

            delegator.handle("show me the duplicates")
            ambiguous = delegator.handle("keep the Handbooks copy")

            self.assertIn("matches more than one", ambiguous.response)
            self.assertTrue((handbooks / "First.txt").exists())
            self.assertTrue((paths.intake / "First.txt").exists())
            self.assertTrue((handbooks / "Second.txt").exists())
            self.assertTrue((paths.intake / "Second.txt").exists())

    def test_natural_reading_flow_uses_current_session_and_persisted_place(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            source = paths.intake / "continuity.epub"
            chapter_twelve = " ".join(f"twelve-word-{index}" for index in range(350))
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("META-INF/container.xml", '<container><rootfiles><rootfile full-path="OPS/package.opf"/></rootfiles></container>')
                archive.writestr(
                    "OPS/package.opf",
                    '<package xmlns:dc="urn:dc"><metadata><dc:title>Continuity</dc:title><dc:creator>Alex</dc:creator></metadata>'
                    '<manifest><item id="c1" href="chapters.xhtml"/></manifest><spine><itemref idref="c1"/></spine></package>',
                )
                archive.writestr(
                    "OPS/chapters.xhtml",
                    f"<html><body><h1>Chapter 12</h1><p>{chapter_twelve}</p></body></html>",
                )
            catalogue = root / "catalogue.db"
            delegator = TeamDelegator.__new__(TeamDelegator)
            delegator.librarian = Librarian(paths, catalogue)
            delegator._help_active = False
            team_status.reset()

            opened = delegator.handle("open Intake/continuity.epub at chapter 12")
            self.assertIn("Chapter 12", opened.response)
            continued = delegator.handle("keep reading")
            self.assertIn("RP-", continued.response)
            marked = delegator.handle("save my place")
            self.assertIn("confirmed place", marked.response)

            restarted = TeamDelegator.__new__(TeamDelegator)
            restarted.librarian = Librarian(paths, catalogue)
            restarted._help_active = False
            resumed = restarted.handle("resume Intake/continuity.epub")
            self.assertIn("resumed", resumed.response)

    def test_natural_context_commands_fail_closed_without_context(self):
        delegator = TeamDelegator.__new__(TeamDelegator)
        delegator._help_active = False
        marked = delegator.handle("save my place")
        self.assertTrue(marked.handled)
        self.assertIn("no active", marked.response.casefold())
        self.assertIsNone(delegator._natural_librarian_command("yes, do that"))
        self.assertIsNone(delegator._natural_librarian_command("keep reading"))

    def test_bounded_shelving_batch_separates_ready_held_and_remaining(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            for index in range(7):
                self._write_identity_epub(
                    paths.intake / f"ready-{index}.epub",
                    f"Ready Book {index}",
                    f"Writer {index}",
                    f"97800000000{index}",
                    "Ready Series",
                    str(index),
                )
            self._write_identity_epub(
                paths.intake / "duplicate-a.epub", "Duplicate", "Writer D", "9781111111111", "", ""
            )
            shutil.copyfile(paths.intake / "duplicate-a.epub", paths.intake / "duplicate-b.epub")
            (paths.intake / "unknown.txt").write_text("Unknown author source", encoding="utf-8")
            librarian = Librarian(paths, root / "catalogue.db")
            librarian.catalogue_editions()

            proposal = librarian.prepare_shelving_batch()

            self.assertEqual(len(proposal.ready), 5)
            self.assertEqual(proposal.eligible_remaining, 2)
            self.assertEqual(proposal.held_count, 3)
            held = " ".join(item.reason for item in proposal.held)
            self.assertIn("edition relationship", held)
            self.assertIn("author metadata is unknown", held)
            self.assertTrue(all((paths.root / item.source_relative_path).exists() for item in proposal.ready))
            response = librarian.shelving_batch_response(proposal)
            self.assertIn("Nothing has moved", response)
            self.assertIn("maximum 5", response)

            destinations = librarian.approve_shelving_batch(proposal.batch_id)

            self.assertEqual(len(destinations), 5)
            self.assertTrue(all((paths.root / destination).is_file() for destination in destinations))
            self.assertTrue((paths.intake / "duplicate-a.epub").is_file())
            self.assertTrue((paths.intake / "duplicate-b.epub").is_file())
            self.assertTrue((paths.intake / "unknown.txt").is_file())

    def test_shelving_batch_rechecks_every_source_before_moving_anything(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            for index in range(2):
                self._write_identity_epub(
                    paths.intake / f"book-{index}.epub",
                    f"Book {index}",
                    f"Author {index}",
                    f"978222222222{index}",
                    "",
                    "",
                )
            librarian = Librarian(paths, root / "catalogue.db")
            librarian.catalogue_editions()
            proposal = librarian.prepare_shelving_batch()
            changed = paths.root / proposal.ready[-1].source_relative_path
            changed.write_bytes(b"changed after review")

            with self.assertRaisesRegex(LibrarianError, "changed after review"):
                librarian.approve_shelving_batch(proposal.batch_id)

            self.assertTrue((paths.intake / "book-0.epub").is_file())
            self.assertTrue((paths.intake / "book-1.epub").is_file())
            self.assertEqual(list(paths.originals.rglob("*.epub")), [])

    def test_natural_shelving_batch_preview_and_contextual_approval(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            self._write_identity_epub(
                paths.intake / "lamp.epub", "The Lamp", "Alex Example", "9783333333333", "", ""
            )
            (paths.intake / "unknown.txt").write_text("Held safely", encoding="utf-8")
            delegator = TeamDelegator.__new__(TeamDelegator)
            delegator.librarian = Librarian(paths, root / "catalogue.db")
            delegator._help_active = False
            team_status.reset()
            delegator.librarian.catalogue_editions()

            preview = delegator.handle("show me what can be shelved")
            self.assertIn("Ready (1", preview.response)
            self.assertIn("author metadata is unknown", preview.response)
            self.assertTrue((paths.intake / "lamp.epub").is_file())
            approved = delegator.handle("shelve those")

            self.assertIn("shelved 1 unchanged original", approved.response)
            self.assertTrue((paths.originals / "Alex Example" / "The Lamp" / "lamp.epub").is_file())
            self.assertTrue((paths.intake / "unknown.txt").is_file())

    def test_contextual_yes_refuses_two_pending_librarian_actions(self):
        delegator = TeamDelegator.__new__(TeamDelegator)
        delegator._help_active = False
        delegator._pending_duplicate_resolution_id = "DR-12345678"
        delegator._pending_shelving_batch_id = "LB-12345678"

        result = delegator._natural_librarian_command("yes, do that")

        self.assertTrue(result.handled)
        self.assertIn("Two Librarian actions", result.response)

    def test_natural_shelving_selection_can_only_remove_one_unambiguous_ready_item(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            self._write_identity_epub(
                paths.intake / "lamp.epub", "The Lamp", "Alex Example", "9784444444441", "", ""
            )
            self._write_identity_epub(
                paths.intake / "scroll.epub", "The Scroll", "Alex Example", "9784444444442", "", ""
            )
            delegator = TeamDelegator.__new__(TeamDelegator)
            delegator.librarian = Librarian(paths, root / "catalogue.db")
            delegator._help_active = False
            team_status.reset()
            delegator.librarian.catalogue_editions()

            delegator.handle("show me what can be shelved")
            vague = delegator.handle("leave Alex Example out")
            self.assertIn("matches more than one", vague.response)
            revised = delegator.handle("leave The Lamp out")
            self.assertIn("left The Lamp out", revised.response)
            self.assertIn("Updated Ready list (1)", revised.response)
            approved = delegator.handle("shelve those")

            self.assertIn("shelved 1 unchanged original", approved.response)
            self.assertTrue((paths.intake / "lamp.epub").is_file())
            self.assertTrue((paths.originals / "Alex Example" / "The Scroll" / "scroll.epub").is_file())

    def test_metadata_review_keeps_filename_suggestion_separate_and_unlocks_shelving(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            source = paths.intake / "The Brass Lamp.txt"
            source.write_text("An unchanged private book.", encoding="utf-8")
            original = source.read_bytes()
            librarian = Librarian(paths, root / "catalogue.db")
            librarian.catalogue_editions()

            items = librarian.metadata_review_items()
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].filename_title_suggestion, "The Brass Lamp")
            self.assertEqual(items[0].title_provenance, "filename")
            draft = librarian.begin_metadata_review(items[0].source_relative_path)
            self.assertEqual(draft.draft_title, "")
            librarian.update_metadata_review(draft.review_id, "title", "The Brass Lamp")
            librarian.update_metadata_review(draft.review_id, "author", "Alex Example")
            saved = librarian.confirm_metadata_review(draft.review_id)

            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(saved.status, "confirmed")
            proposal = librarian.prepare_shelving_batch()
            self.assertEqual(len(proposal.ready), 1)
            self.assertEqual(proposal.ready[0].title, "The Brass Lamp")
            self.assertEqual(proposal.ready[0].author, "Alex Example")

            librarian.catalogue_editions()
            connection = sqlite3.connect(root / "catalogue.db")
            try:
                row = connection.execute(
                    "SELECT title,author,title_provenance,author_provenance FROM edition_items"
                ).fetchone()
            finally:
                connection.close()
            self.assertEqual(row, ("The Brass Lamp", "Alex Example", "drew-confirmed", "drew-confirmed"))

    def test_metadata_review_refuses_changed_source_and_leave_preserves_catalogue(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            source = paths.intake / "Uncertain.txt"
            source.write_text("first", encoding="utf-8")
            librarian = Librarian(paths, root / "catalogue.db")
            librarian.catalogue_editions()
            first = librarian.begin_metadata_review("Intake/Uncertain.txt")
            librarian.update_metadata_review(first.review_id, "title", "Certain")
            librarian.update_metadata_review(first.review_id, "author", "Writer")
            source.write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(LibrarianError, "changed during review"):
                librarian.confirm_metadata_review(first.review_id)

            librarian.catalogue_editions()
            second = librarian.begin_metadata_review("Intake/Uncertain.txt")
            librarian.cancel_metadata_review(second.review_id)
            connection = sqlite3.connect(root / "catalogue.db")
            try:
                author = connection.execute("SELECT author FROM edition_items").fetchone()[0]
                overrides = connection.execute("SELECT COUNT(*) FROM metadata_overrides").fetchone()[0]
            finally:
                connection.close()
            self.assertEqual(author, "Unknown Author")
            self.assertEqual(overrides, 0)

    def test_natural_metadata_review_requires_displayed_context_and_explicit_save(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            source = paths.intake / "Nightmare Keep.txt"
            source.write_text("kept unchanged", encoding="utf-8")
            delegator = TeamDelegator.__new__(TeamDelegator)
            delegator.librarian = Librarian(paths, root / "catalogue.db")
            delegator._help_active = False
            team_status.reset()
            delegator.librarian.catalogue_editions()

            absent = delegator.handle("review Nightmare Keep")
            self.assertFalse(absent.handled)
            listed = delegator.handle("show me books needing metadata")
            self.assertIn("Filename suggestion only: Nightmare Keep", listed.response)
            opened = delegator.handle("review Nightmare Keep")
            self.assertIn("Nothing becomes canonical", opened.response)
            delegator.handle("title is Nightmare Keep")
            delegator.handle("author is Drew Example")
            saved = delegator.handle("save that")

            self.assertIn("book itself was not rewritten", saved.response)
            self.assertEqual(source.read_text(encoding="utf-8"), "kept unchanged")
            shelving = delegator.handle("show me what can be shelved")
            self.assertIn("Ready (1", shelving.response)

    def test_preferred_nonidentical_edition_unlocks_only_chosen_copy(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            first = paths.intake / "First" / "story.epub"
            second = paths.intake / "Second" / "story.epub"
            first.parent.mkdir()
            second.parent.mkdir()
            self._write_identity_epub(first, "Shared Story", "Alex Author", "9785555555555", "", "", "first")
            self._write_identity_epub(second, "Shared Story", "Alex Author", "9785555555555", "", "", "second")
            original_hashes = {first: Librarian._sha256(first), second: Librarian._sha256(second)}
            librarian = Librarian(paths, root / "catalogue.db")
            librarian.catalogue_editions()
            groups = librarian.edition_review_groups()
            group = next(group for group in groups if group.evidence == "Shared strong identifier")

            proposal = librarian.prepare_preferred_edition(
                group.evidence, group.identity, tuple(item[0] for item in group.files), "Intake/Second/story.epub"
            )
            self.assertIn("Nothing has moved or been deleted", librarian.preferred_edition_response(proposal))
            librarian.approve_preferred_edition(proposal.preference_id)
            batch = librarian.prepare_shelving_batch()

            self.assertEqual([item.source_relative_path for item in batch.ready], ["Intake/Second/story.epub"])
            self.assertTrue(any(
                item.source_relative_path == "Intake/First/story.epub" and "preferred" in item.reason
                for item in batch.held
            ))
            self.assertEqual(original_hashes, {first: Librarian._sha256(first), second: Librarian._sha256(second)})

    def test_natural_preferred_edition_uses_displayed_group_and_contextual_approval(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            first = paths.intake / "Early" / "story.epub"
            second = paths.intake / "Later" / "story.epub"
            first.parent.mkdir()
            second.parent.mkdir()
            self._write_identity_epub(first, "Story", "Writer", "9786666666666", "", "", "early")
            self._write_identity_epub(second, "Story", "Writer", "9786666666666", "", "", "later")
            delegator = TeamDelegator.__new__(TeamDelegator)
            delegator.librarian = Librarian(paths, root / "catalogue.db")
            delegator._help_active = False
            team_status.reset()
            delegator.librarian.catalogue_editions()

            missing = delegator.handle("prefer the Later copy")
            self.assertIn("Show me the edition choices", missing.response)
            shown = delegator.handle("show me the edition choices")
            self.assertIn("Shared strong identifier", shown.response)
            prepared = delegator.handle("prefer the Later copy")
            self.assertIn("preferred-edition decision", prepared.response)
            approved = delegator.handle("yes, do that")

            self.assertIn("preferred reading edition", approved.response)
            self.assertTrue(first.is_file())
            self.assertTrue(second.is_file())
            preview = delegator.handle("show me what can be shelved")
            self.assertIn("Intake/Later/story.epub", preview.response)
            self.assertIn("alternative remains retained", preview.response)

    def test_preferred_edition_approval_refuses_changed_member(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            first = paths.intake / "first.epub"
            second = paths.intake / "second.epub"
            self._write_identity_epub(first, "Story", "Writer", "9787777777777", "", "", "first")
            self._write_identity_epub(second, "Story", "Writer", "9787777777777", "", "", "second")
            librarian = Librarian(paths, root / "catalogue.db")
            librarian.catalogue_editions()
            group = next(group for group in librarian.edition_review_groups() if group.evidence == "Shared strong identifier")
            proposal = librarian.prepare_preferred_edition(
                group.evidence, group.identity, tuple(item[0] for item in group.files), "Intake/first.epub"
            )
            second.write_bytes(b"changed")

            with self.assertRaisesRegex(LibrarianError, "changed after review"):
                librarian.approve_preferred_edition(proposal.preference_id)

    def test_series_confirmation_creates_series_aware_shelving_without_rewriting_source(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            source = paths.intake / "volume.epub"
            self._write_identity_epub(source, "Second Story", "Alex Writer", "9788888888888", "Old Label", "1")
            original = source.read_bytes()
            librarian = Librarian(paths, root / "catalogue.db")
            librarian.catalogue_editions()

            items = librarian.series_review_items()
            self.assertEqual(len(items), 1)
            draft = librarian.begin_series_review(items[0].source_relative_path)
            librarian.update_series_review(draft.review_id, "series", "True Series")
            librarian.update_series_review(draft.review_id, "volume", "2")
            saved = librarian.resolve_series_review(draft.review_id, save=True)
            batch = librarian.prepare_shelving_batch()

            self.assertEqual(saved.status, "confirmed")
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(
                batch.ready[0].proposed_relative_path,
                "Alex Writer/True Series/02 - Second Story/volume.epub",
            )

    def test_series_review_leave_and_changed_source_fail_closed(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            source = paths.intake / "volume.epub"
            self._write_identity_epub(source, "Story", "Writer", "9789999999999", "Series", "1")
            librarian = Librarian(paths, root / "catalogue.db")
            librarian.catalogue_editions()
            left = librarian.begin_series_review("Intake/volume.epub")
            self.assertEqual(librarian.resolve_series_review(left.review_id, save=False).status, "left")
            changed = librarian.begin_series_review("Intake/volume.epub")
            librarian.update_series_review(changed.review_id, "volume", "2")
            source.write_bytes(b"changed")

            with self.assertRaisesRegex(LibrarianError, "changed during review"):
                librarian.resolve_series_review(changed.review_id, save=True)

    def test_natural_series_review_is_contextual_and_does_not_hijack_metadata_review(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            paths = ReadingCollection(self._write_config(project, root / "Stacks"), project).initialize()
            source = paths.intake / "gate.epub"
            self._write_identity_epub(source, "Magic at the Gate", "Devon Monk", "9781010101010", "Allie Beckstrom", "1")
            delegator = TeamDelegator.__new__(TeamDelegator)
            delegator.librarian = Librarian(paths, root / "catalogue.db")
            delegator._help_active = False
            team_status.reset()
            delegator.librarian.catalogue_editions()

            shown = delegator.handle("show me the series")
            self.assertIn("source-supplied fields", shown.response)
            opened = delegator.handle("review Magic at the Gate")
            self.assertIn("Series review:", opened.response)
            changed = delegator.handle("volume is 5")
            self.assertIn("Staged volume: 5", changed.response)
            saved = delegator.handle("save that")
            self.assertIn("volume 5", saved.response)
            preview = delegator.handle("show me what can be shelved")
            self.assertIn("Allie Beckstrom/05 - Magic at the Gate", preview.response)

    @staticmethod
    def _write_identity_epub(path, title, author, isbn, series, index, extra=""):
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("META-INF/container.xml", '<container><rootfiles><rootfile full-path="OPS/package.opf"/></rootfiles></container>')
            archive.writestr(
                "OPS/package.opf",
                f'<package xmlns:dc="urn:dc"><metadata><dc:title>{title}</dc:title><dc:creator>{author}</dc:creator>'
                f'<dc:identifier scheme="ISBN">{isbn}</dc:identifier><meta name="calibre:series" content="{series}"/>'
                f'<meta name="calibre:series_index" content="{index}"/></metadata><manifest><item id="c" href="c.xhtml"/>'
                f'</manifest><spine><itemref idref="c"/></spine></package>',
            )
            archive.writestr("OPS/c.xhtml", f"<html><body><p>{title} text {extra}</p></body></html>")

    @staticmethod
    def _write_config(project: Path, stacks: Path) -> Path:
        config = project / "reading_collection.json"
        config.write_text(json.dumps({"stacks": {"path": str(stacks)}}), encoding="utf-8")
        return config


if __name__ == "__main__":
    unittest.main()
