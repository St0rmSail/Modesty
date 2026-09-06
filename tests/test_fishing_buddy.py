import tempfile
from pathlib import Path
import unittest
import sqlite3
from contextlib import closing

from Runtime.Fishing import FishingCodex
from Runtime.Fishing import FishingAdvisor


class FishingCodexTest(unittest.TestCase):
    def test_initializes_four_private_codices_without_overwriting(self):
        with tempfile.TemporaryDirectory() as folder:
            codex = FishingCodex(Path(folder) / "Fishing")
            codex.initialize()
            index = codex.root / "russian-fishing-4" / "index.json"
            index.write_text("preserve me", encoding="utf-8")
            codex.initialize()
            self.assertEqual(index.read_text(encoding="utf-8"), "preserve me")
            self.assertTrue((codex.root / "fisher-online" / "Species").is_dir())

    def test_finds_standalone_rf4_and_steam_games_read_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            drive = root / "drive"
            rf4 = drive / "RF42026"
            rf4.mkdir(parents=True)
            (rf4 / "RF4Launcher.exe").touch()
            steam = root / "Steam"
            common = steam / "steamapps" / "common" / "theFisher Online"
            common.mkdir(parents=True)
            (steam / "steamapps" / "appmanifest_1094780.acf").write_text(
                '"AppState" { "installdir" "theFisher Online" }', encoding="utf-8"
            )
            results = FishingCodex(root / "codex").inspect((steam,), (drive,), root / "home")
            by_key = {item.key: item for item in results}
            self.assertEqual(Path(by_key["russian-fishing-4"].installation), rf4)
            self.assertEqual(Path(by_key["fisher-online"].installation), common)
            self.assertFalse(by_key["professional-fishing-2"].installed)

    def test_reports_angler_save_location_as_candidate_not_verified(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            saves = root / "home" / "Saved Games" / "Avalanche Studios" / "CotWTheAngler" / "Saves"
            saves.mkdir(parents=True)
            results = FishingCodex(root / "codex").inspect((), (root / "drive",), root / "home")
            angler = next(item for item in results if item.key == "call-of-the-wild-the-angler")
            self.assertEqual(angler.data_status, "candidate read-only source")
            self.assertEqual(Path(angler.data_path), saves)

    def test_every_species_has_an_explicit_best_tackle_entry(self):
        with tempfile.TemporaryDirectory() as folder:
            codex = FishingCodex(Path(folder) / "Fishing")
            unknown = codex.record_species("russian-fishing-4", "Common Roach")
            known = codex.record_species(
                "russian-fishing-4",
                "Common Roach",
                "Float fishing",
                "Light float rod, small hook, maggot",
                "Drew confirmed",
                "local observation",
            )
            self.assertEqual(unknown.best_tackle, "Not yet established")
            self.assertEqual(known.best_tackle, "Light float rod, small hook, maggot")
            self.assertEqual(codex.species_entries("russian-fishing-4"), (known, unknown))

    def test_same_species_can_have_different_tackle_by_fishing_style(self):
        with tempfile.TemporaryDirectory() as folder:
            codex = FishingCodex(Path(folder) / "Fishing")
            feeder = codex.record_species("professional-fishing-2", "Carp", "Feeder", "Heavy feeder rig")
            float_entry = codex.record_species("professional-fishing-2", "Carp", "Float", "Waggler rig")
            self.assertEqual(codex.species_entries("professional-fishing-2"), (feeder, float_entry))

    def test_rejects_a_blank_best_tackle_entry(self):
        with tempfile.TemporaryDirectory() as folder:
            codex = FishingCodex(Path(folder) / "Fishing")
            with self.assertRaisesRegex(ValueError, "best-tackle"):
                codex.record_species("fisher-online", "Perch", "Spinning", "   ")

    def test_codex_has_linked_context_and_evidence_foundations(self):
        with tempfile.TemporaryDirectory() as folder:
            codex = FishingCodex(Path(folder) / "Fishing")
            codex.initialize()
            with closing(sqlite3.connect(codex.database_path)) as connection:
                tables = {row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )}
                self.assertTrue({
                    "games", "game_versions", "species", "fishing_methods", "locations",
                    "tackle_setups", "tackle_components", "setup_components", "species_tackle",
                    "baits", "species_bait_effectiveness", "groundbait_recipes",
                    "groundbait_ingredients", "species_groundbait_effectiveness", "component_effects",
                    "component_compatibility", "component_substitutions", "location_method_suitability",
                    "companion_preferences", "fishing_memory_links", "recommendation_history",
                    "recommendations",
                    "sources", "player_state", "catches",
                }.issubset(tables))
                recommendation_columns = {
                    row[1] for row in connection.execute("PRAGMA table_info(species_tackle)")
                }
                self.assertTrue({
                    "target_class", "objective", "conditions", "minimum_level", "purchase_cost",
                    "recommendation_kind", "confidence", "supporting_catches", "game_version",
                }.issubset(recommendation_columns))
                self.assertEqual(
                    connection.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()[0],
                    "7",
                )
                bait_columns = {
                    row[1] for row in connection.execute("PRAGMA table_info(species_bait_effectiveness)")
                }
                self.assertTrue({
                    "effectiveness", "relative_score", "selectivity", "presentation",
                    "compatible_hook_range", "conditions", "supporting_catches", "confidence",
                }.issubset(bait_columns))
                groundbait_columns = {
                    row[1] for row in connection.execute("PRAGMA table_info(species_groundbait_effectiveness)")
                }
                self.assertTrue({
                    "relative_strength", "selectivity", "effective_duration", "overfeeding_risk",
                    "location_id", "supporting_sessions", "confidence",
                }.issubset(groundbait_columns))
                memory_columns = {
                    row[1] for row in connection.execute("PRAGMA table_info(fishing_memory_links)")
                }
                self.assertTrue({
                    "chronicle_reference", "truth_status", "emotional_tone", "salience",
                    "last_recalled_utc", "recall_count", "cooldown_until_utc",
                }.issubset(memory_columns))

    def test_advisor_changes_method_and_keeps_personality_separate(self):
        with tempfile.TemporaryDirectory() as folder:
            codex = FishingCodex(Path(folder) / "Fishing")
            codex.initialize()
            with closing(sqlite3.connect(codex.database_path)) as connection:
                connection.execute("PRAGMA foreign_keys=ON")
                connection.execute("INSERT INTO species VALUES ('russian-fishing-4', 'Tench')")
                connection.executemany(
                    "INSERT INTO fishing_methods VALUES ('russian-fishing-4', ?)",
                    (("Feeder",), ("Float",)),
                )
                location_id = connection.execute(
                    "INSERT INTO locations (game_key, waterbody) VALUES ('russian-fishing-4', 'Old Burg Lake')"
                ).lastrowid
                connection.executemany(
                    """INSERT INTO location_method_suitability
                       (game_key, location_id, fishing_style, species_name, relative_strength, status)
                       VALUES ('russian-fishing-4', ?, ?, 'Tench', ?, 'confirmed')""",
                    ((location_id, "Feeder", -0.5), (location_id, "Float", 0.8)),
                )
                connection.execute(
                    """INSERT INTO recommendations
                       (game_key, species_name, fishing_style, best_tackle, confidence,
                        supporting_catches, status, location_id)
                       VALUES ('russian-fishing-4', 'Tench', 'Float',
                               'Light float setup with cheese', 'confirmed', 12, 'confirmed', ?)""",
                    (location_id,),
                )
                connection.execute(
                    """INSERT INTO companion_preferences
                       (owner, game_key, subject_type, subject_reference, sentiment, origin)
                       VALUES ('Modesty', 'russian-fishing-4', 'fishing style', 'Float', 0.8, 'canon')"""
                )
                connection.execute(
                    """INSERT INTO fishing_memory_links
                       (game_key, species_name, fishing_style, location_id, memory_type, summary, truth_status)
                       VALUES ('russian-fishing-4', 'Tench', 'Float', ?, 'one that got away',
                               'A tench escaped beside the reeds.', 'Drew confirmed')""",
                    (location_id,),
                )
                connection.commit()
            advice = FishingAdvisor(codex).advise(
                "russian-fishing-4", "Tench", "Feeder", location_id
            )
            self.assertTrue(advice.known)
            self.assertEqual(advice.recommended_style, "Float")
            self.assertIn("poorly suited", advice.suitability_warning)
            self.assertEqual(advice.best_tackle, "Light float setup with cheese")
            self.assertIn("likes Float", advice.personality_context)
            self.assertIn("escaped beside the reeds", advice.memory_context)


if __name__ == "__main__":
    unittest.main()
