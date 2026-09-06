import tempfile
from pathlib import Path
import unittest

from Runtime.Fishing import FishingCodex


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


if __name__ == "__main__":
    unittest.main()
