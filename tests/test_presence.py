from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from Runtime.Time.presence import PresenceSession


class MutableClock:
    def __init__(self, value: datetime):
        self.value = value

    def __call__(self) -> datetime:
        return self.value


class PresenceSessionTest(unittest.TestCase):
    def test_first_run_has_truthful_time_greeting_without_invented_absence(self):
        with TemporaryDirectory() as temporary:
            clock = MutableClock(datetime(2026, 8, 15, 8, 0, tzinfo=timezone.utc))
            session = PresenceSession(Path(temporary) / "presence.json", clock).begin()
            self.assertEqual(session.opening_greeting(), "Good morning, Drew.")
            self.assertNotIn("away", session.opening_greeting())

    def test_clean_shutdown_is_reported_on_next_start(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "presence.json"
            clock = MutableClock(datetime(2026, 8, 15, 8, 0, tzinfo=timezone.utc))
            first = PresenceSession(path, clock).begin()
            clock.value += timedelta(hours=1)
            first.shutdown()
            clock.value += timedelta(hours=8, minutes=12)
            second = PresenceSession(path, clock).begin()
            greeting = second.opening_greeting()
            self.assertIn("8 hours and 12 minutes", greeting)
            self.assertIn("closed cleanly", greeting)

    def test_missing_shutdown_uses_last_heartbeat_and_reports_interruption(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "presence.json"
            clock = MutableClock(datetime(2026, 8, 15, 8, 0, tzinfo=timezone.utc))
            abandoned = PresenceSession(path, clock).begin()
            clock.value += timedelta(minutes=10)
            abandoned.heartbeat()
            clock.value += timedelta(minutes=25)
            resumed = PresenceSession(path, clock).begin()
            greeting = resumed.opening_greeting()
            self.assertIn("25 minutes", greeting)
            self.assertIn("did not close cleanly", greeting)

    def test_presence_states_are_persisted_and_validated(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "presence.json"
            clock = MutableClock(datetime(2026, 8, 15, 8, 0, tzinfo=timezone.utc))
            session = PresenceSession(path, clock).begin()
            session.set_presence("background")
            self.assertEqual(json.loads(path.read_text())["presence"], "background")
            session.set_presence("working")
            self.assertEqual(json.loads(path.read_text())["presence"], "working")
            with self.assertRaises(ValueError):
                session.set_presence("imaginary")
            session.shutdown()
            state = json.loads(path.read_text())
            self.assertEqual(state["presence"], "offline")
            self.assertTrue(state["shutdown_clean"])

    def test_model_context_contains_current_time_and_offline_truth_rule(self):
        with TemporaryDirectory() as temporary:
            clock = MutableClock(datetime(2026, 8, 15, 19, 30, tzinfo=timezone.utc))
            session = PresenceSession(Path(temporary) / "presence.json", clock).begin()
            context = session.context_summary()
            self.assertIn(clock.value.astimezone().strftime("%Y-%m-%d %H:%M:%S"), context)
            self.assertIn("program was offline", context)


if __name__ == "__main__":
    unittest.main()
