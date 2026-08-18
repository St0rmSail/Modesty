from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from Runtime.Research.pending_reports import PendingReportStore

try:
    from PySide6.QtWidgets import QApplication
    from Runtime.Conversation.briefing_hologram import BriefingHologram
except ModuleNotFoundError:
    QApplication = None
    BriefingHologram = None


class PendingReportStoreTest(unittest.TestCase):
    def test_report_survives_new_store_instance_until_explicit_discard(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary) / "Pending"
            report = PendingReportStore(root).create("First briefing", "Useful evidence", "scribblehub")
            recovered = PendingReportStore(root).latest()
            self.assertEqual(recovered, report)
            PendingReportStore(root).discard(report.report_id)
            self.assertIsNone(PendingReportStore(root).latest())

    def test_invalid_or_empty_reports_are_rejected(self):
        with TemporaryDirectory() as temporary:
            store = PendingReportStore(Path(temporary))
            with self.assertRaises(ValueError):
                store.create("", "body", "provider")
            with self.assertRaises(ValueError):
                store.load("../private")

    @unittest.skipUnless(QApplication is not None, "Qt runtime is not installed")
    def test_briefing_requires_disposition_before_close(self):
        app = QApplication.instance() or QApplication([])
        with TemporaryDirectory() as temporary:
            store = PendingReportStore(Path(temporary))
            pending = store.create("Decision", "Evidence", "local")
            briefing = BriefingHologram(store)
            briefing.open_report(pending.report_id)
            self.assertFalse(briefing.close_button.isEnabled())
            briefing._resolve("toss")
            self.assertTrue(briefing.close_button.isEnabled())
            self.assertEqual(briefing.selected_destination, "toss")
            self.assertTrue(briefing.disposition_buttons["toss"].property("selected"))

    @unittest.skipUnless(QApplication is not None, "Qt runtime is not installed")
    def test_librarian_repair_briefing_uses_local_keep_or_toss_controls(self):
        app = QApplication.instance() or QApplication([])
        with TemporaryDirectory() as temporary:
            store = PendingReportStore(Path(temporary))
            pending = store.create(
                "Repair",
                "Mechanical repair details",
                "librarian:LR-1234ABCD",
            )
            briefing = BriefingHologram(store)

            briefing.open_report(pending.report_id)

            self.assertEqual(briefing.mode.text(), "LOCAL BRIEFING")
            self.assertEqual(briefing.disposition_buttons["private"].text(), "Keep Repair")
            self.assertEqual(briefing.disposition_buttons["toss"].text(), "Toss Repair")
            self.assertFalse(briefing.disposition_buttons["bookshelf"].isVisible())
            self.assertFalse(briefing.close_button.isEnabled())


if __name__ == "__main__":
    unittest.main()
