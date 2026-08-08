import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from Runtime.Knowledge.stores import KnowledgeStoreError, KnowledgeStores


class KnowledgeStoresTest(unittest.TestCase):
    def test_initializes_both_stores_without_overwriting(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            filing = root / "Filing Cabinet"
            bookshelf = root / "Bookshelf"
            config = self._write_config(project, filing, bookshelf)

            stores = KnowledgeStores(config, project)
            stores.initialize()
            custom = bookshelf / "index.md"
            custom.write_text("Drew's existing index", encoding="utf-8")
            stores.initialize()

            self.assertTrue((filing / ".obsidian").is_dir())
            self.assertTrue((filing / "Inbox").is_dir())
            self.assertTrue((bookshelf / "Workbench").is_dir())
            self.assertTrue((bookshelf / "_Templates" / "concept.md").is_file())
            self.assertEqual(custom.read_text(encoding="utf-8"), "Drew's existing index")

    def test_rejects_a_store_inside_the_public_repository(self):
        with TemporaryDirectory() as folder:
            project = Path(folder) / "project"
            project.mkdir()
            config = self._write_config(
                project,
                project / "private",
                Path(folder) / "Bookshelf",
            )

            with self.assertRaisesRegex(KnowledgeStoreError, "outside"):
                KnowledgeStores(config, project)

    def test_rejects_nested_stores(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            project.mkdir()
            filing = root / "Filing Cabinet"
            config = self._write_config(project, filing, filing / "Bookshelf")

            with self.assertRaisesRegex(KnowledgeStoreError, "inside"):
                KnowledgeStores(config, project)

    @staticmethod
    def _write_config(project: Path, filing: Path, bookshelf: Path) -> Path:
        config = project / "knowledge_stores.json"
        config.write_text(
            json.dumps(
                {
                    "filing_cabinet": {"path": str(filing)},
                    "bookshelf": {"path": str(bookshelf)},
                }
            ),
            encoding="utf-8",
        )
        return config


if __name__ == "__main__":
    unittest.main()
