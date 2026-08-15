from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from Runtime.Time.schedule import ReminderStore, handle_schedule_command


class ScheduleTest(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.store = ReminderStore(Path(self.temp.name) / "modesty.db", lambda: datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc))

    def tearDown(self): self.temp.cleanup()

    def test_add_list_complete_delete_lifecycle(self):
        answer = handle_schedule_command("Remind me on 2026-08-16 at 09:30: Call the office", self.store)
        self.assertIn("#1", answer)
        self.assertIn("Call the office", handle_schedule_command("Show my reminders", self.store))
        self.assertIn("Completed reminder #1", handle_schedule_command("Complete reminder 1", self.store))
        self.assertEqual("You have no pending reminders.", handle_schedule_command("List my reminders", self.store))
        handle_schedule_command("Remind me on 2026-08-17 at 10:00: Test deletion", self.store)
        self.assertEqual("Deleted reminder #2.", handle_schedule_command("Delete reminder #2", self.store))

    def test_restart_persists_and_invalid_dates_fail_plainly(self):
        self.store.add_local("2026-08-16", "09:30", "Persistent reminder")
        reopened = ReminderStore(Path(self.temp.name) / "modesty.db", self.store.clock)
        self.assertEqual("Persistent reminder", reopened.pending()[0]["text"])
        self.assertIn("valid local date", handle_schedule_command("Remind me on 2026-02-30 at 09:00: impossible", reopened))

    def test_unrelated_conversation_is_not_claimed(self):
        self.assertIsNone(handle_schedule_command("Tell me about tomorrow", self.store))

    def test_opening_summary_reports_only_due_or_overdue_items(self):
        self.store.add_local("2026-08-14", "09:00", "Overdue task")
        self.store.add_local("2026-08-16", "09:00", "Future task")
        summary = self.store.opening_summary()
        self.assertIn("1 overdue reminder", summary)
        self.assertIn("Overdue task", summary)
        self.assertNotIn("Future task", summary)


if __name__ == "__main__": unittest.main()
