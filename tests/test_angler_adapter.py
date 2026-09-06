import tempfile
from pathlib import Path
import unittest

from Runtime.Fishing import AnglerObservationStore, AnglerSaveInspector


class AnglerSaveInspectorTest(unittest.TestCase):
    def test_recognises_adf_and_matching_snapshot_without_decoding(self):
        with tempfile.TemporaryDirectory() as folder:
            account = Path(folder) / "Saves" / "12345"
            slot = account / "slots" / "0"
            slot.mkdir(parents=True)
            payload = bytes.fromhex("01 01 00 00 00 20 46 44 41") + b"opaque"
            (account / "player_save_data").write_bytes(payload)
            (slot / "player_save_data").write_bytes(payload)
            report = AnglerSaveInspector(Path(folder) / "Saves").inspect()
            self.assertTrue(report.account_found)
            self.assertEqual(report.duplicate_snapshots, 1)
            self.assertTrue(all(item.format == "Avalanche ADF binary container" for item in report.containers))
            self.assertIn("no level, cash, inventory", report.status)

    def test_missing_account_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as folder:
            report = AnglerSaveInspector(Path(folder) / "missing").inspect()
            self.assertFalse(report.account_found)
            self.assertEqual(report.containers, ())

    def test_refuses_oversized_known_file(self):
        with tempfile.TemporaryDirectory() as folder:
            account = Path(folder) / "Saves" / "12345"
            account.mkdir(parents=True)
            path = account / "player_save_data"
            path.write_bytes(b"x")
            inspector = AnglerSaveInspector(Path(folder) / "Saves")
            inspector.MAX_FILE_BYTES = 0
            with self.assertRaisesRegex(ValueError, "bounded inspection limit"):
                inspector.inspect()

    def test_observation_reports_only_changed_relative_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            account = root / "Saves" / "12345"
            account.mkdir(parents=True)
            save = account / "player_save_data"
            save.write_bytes(bytes.fromhex("01 01 00 00 00 20 46 44 41") + b"before")
            store = AnglerObservationStore(
                AnglerSaveInspector(root / "Saves"), root / "private" / "baseline.json"
            )
            store.begin()
            save.write_bytes(bytes.fromhex("01 01 00 00 00 20 46 44 41") + b"after")
            difference = store.compare()
            self.assertEqual(difference.changed, ("player_save_data",))
            self.assertEqual(difference.added, ())
            self.assertEqual(difference.removed, ())
            self.assertEqual(difference.structural[0].relative_path, "player_save_data")
            self.assertEqual(difference.structural[0].changed_blocks, 1)
            self.assertEqual(difference.structural[0].byte_ranges, ("0-14",))
            baseline = (root / "private" / "baseline.json").read_text(encoding="utf-8")
            self.assertNotIn("12345", baseline)
            self.assertNotIn("before", baseline)
            self.assertIn('"schema": 2', baseline)

    def test_structural_diff_coalesces_adjacent_changed_blocks(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            account = root / "Saves" / "12345"
            account.mkdir(parents=True)
            save = account / "player_save_data"
            prefix = bytes.fromhex("01 01 00 00 00 20 46 44 41")
            save.write_bytes(prefix + b"a" * 9000)
            store = AnglerObservationStore(
                AnglerSaveInspector(root / "Saves"), root / "private" / "baseline.json"
            )
            store.begin()
            save.write_bytes(prefix + b"b" * 9000)
            structural = store.compare().structural[0]
            self.assertEqual(structural.changed_blocks, 3)
            self.assertEqual(structural.byte_ranges, ("0-9008",))


if __name__ == "__main__":
    unittest.main()
