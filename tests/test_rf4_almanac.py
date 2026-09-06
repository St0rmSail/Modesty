from contextlib import closing
import json
from pathlib import Path
import re
import sqlite3
import tempfile
import unittest

from Runtime.Fishing import FishingCodex, RF4AlmanacImporter


def record(name: str) -> dict[str, object]:
    return {
        "name": name, "nameRu": "", "locations": ["Test Lake"],
        "baits": ["Worm", "Cheese"], "bite": "Active", "time": "Day",
        "depth": "1 m", "hookSize": "S8 - S2", "trophyWeight": "1000",
        "superTrophyWeight": "1500", "weightKg": "", "weightPrice": "",
        "weightXp": "", "assemblies": [], "tip": "Community note",
    }


class RF4AlmanacImporterTest(unittest.TestCase):
    def test_placeholder_trophy_weight_remains_unknown(self):
        self.assertIsNone(RF4AlmanacImporter._optional_weight("9999999"))

    def test_imports_only_rf4_with_weak_provenance(self):
        records = [record(name) for name in (
            "Albino barbel", "Common Roach", "Tench", "Bream", "Atlantic cod", "Pike"
        )]
        literal = json.dumps(records, separators=(",", ":"))
        literal = re.sub(r'"([A-Za-z][A-Za-z0-9_]*)":', r'\1:', literal)
        bundle = ("const qi=" + literal + ",n3={};").encode()
        page = b'<script type="module" src="/assets/index-TEST.js"></script>'

        def fetcher(url: str, maximum: int) -> bytes:
            value = page if url.endswith("/") else bundle
            self.assertLessEqual(len(value), maximum)
            return value

        with tempfile.TemporaryDirectory() as folder:
            codex = FishingCodex(Path(folder) / "Fishing")
            report = RF4AlmanacImporter(codex, fetcher, minimum_records=6).import_catalogue()
            self.assertEqual(report.species, 6)
            self.assertEqual(report.baits, 2)
            with closing(sqlite3.connect(codex.database_path)) as connection:
                source = connection.execute(
                    "SELECT game_key, source_type, locator, evidence_status FROM sources"
                ).fetchone()
                self.assertEqual(source, (
                    "russian-fishing-4", "community_reference",
                    "https://rf4almanac.pages.dev/", "community_reference_weakest",
                ))
                self.assertEqual(connection.execute("SELECT count(*) FROM species").fetchone()[0], 6)
                self.assertEqual(connection.execute("SELECT count(*) FROM species_reference").fetchone()[0], 6)
                self.assertEqual(connection.execute("SELECT count(*) FROM hotspots").fetchone()[0], 0)
                self.assertEqual(
                    connection.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()[0],
                    "7",
                )
                hotspot_sql = connection.execute(
                    "SELECT sql FROM sqlite_master WHERE name='hotspots'"
                ).fetchone()[0]
                self.assertIn("'rumoured', 'known', 'favourite'", hotspot_sql)

    def test_rejects_changed_catalogue_shape_before_writing(self):
        malformed = b'const x=[{name:"Albino barbel",nameRu:""}],n3={};'
        page = b'<script src="/assets/index-TEST.js"></script>'
        values = iter((page, malformed))
        with tempfile.TemporaryDirectory() as folder:
            codex = FishingCodex(Path(folder) / "Fishing")
            importer = RF4AlmanacImporter(codex, lambda _url, _maximum: next(values), minimum_records=1)
            with self.assertRaisesRegex(ValueError, "structure changed"):
                importer.import_catalogue()
            self.assertFalse(codex.database_path.exists())


if __name__ == "__main__":
    unittest.main()
