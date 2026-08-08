from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from Brain.Team.archivist import Archivist
from Brain.Team.delegation import TeamDelegator
from Runtime.Knowledge.catalog import KnowledgeCatalog
from Runtime.Knowledge.stores import StorePaths


class ArchivistDelegationTest(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        root = Path(self.temporary.name)
        self.filing = root / "Filing"
        self.bookshelf = root / "Bookshelf"
        (self.filing / "Inbox").mkdir(parents=True)
        (self.bookshelf / "Inbox").mkdir(parents=True)
        archivist = Archivist(
            StorePaths(self.filing, self.bookshelf),
            KnowledgeCatalog(root / "catalog.db"),
        )
        self.delegator = TeamDelegator(archivist)

    def tearDown(self):
        self.temporary.cleanup()

    def test_files_private_note_without_using_ollama(self):
        result = self.delegator.handle(
            "Ask the Archivist to file privately: Boat keys are in the blue drawer."
        )
        notes = list((self.filing / "Inbox").glob("*.md"))
        self.assertTrue(result.handled)
        self.assertEqual(len(notes), 1)
        self.assertIn("Source: filed by Drew through Modesty", notes[0].read_text(encoding="utf-8"))

    def test_files_okf_bookshelf_note_and_never_overwrites(self):
        command = "Ask the Archivist to file on the Bookshelf: Brass care procedure"
        self.delegator.handle(command)
        self.delegator.handle(command)
        notes = list((self.bookshelf / "Inbox").glob("*.md"))
        self.assertEqual(len(notes), 2)
        self.assertIn("type: Note", notes[0].read_text(encoding="utf-8"))

    def test_retrieves_with_origin_and_excerpt(self):
        self.delegator.handle(
            "Ask the Archivist to file privately: Boat keys are in the blue drawer."
        )
        result = self.delegator.handle("Ask the Archivist to retrieve: boat keys")
        self.assertTrue(result.handled)
        self.assertIn("Filing Cabinet/Inbox/", result.response)
        self.assertIn("blue drawer", result.response)

    def test_ambiguous_filing_asks_for_destination(self):
        result = self.delegator.handle("Ask the Archivist to file this note")
        self.assertTrue(result.handled)
        self.assertIn("privately", result.response)
        self.assertEqual(list((self.filing / "Inbox").glob("*.md")), [])


if __name__ == "__main__":
    unittest.main()
