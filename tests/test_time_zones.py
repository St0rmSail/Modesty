from datetime import datetime, timezone
import unittest
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from Brain.Team.delegation import TeamDelegator
from Runtime.Core.command_help import command_help
from Runtime.Time.zones import handle_time_command

try:
    ZoneInfo("Europe/London")
    HAS_TZDATA = True
except ZoneInfoNotFoundError:
    HAS_TZDATA = False


class TimeZoneCommandTest(unittest.TestCase):
    def test_current_east_african_time_is_offline_and_deterministic(self):
        instant = datetime(2026, 8, 15, 12, 30, tzinfo=timezone.utc)
        answer = handle_time_command("What time is it in Uganda?", instant)
        self.assertIn("15:30", answer)
        self.assertIn("Uganda", answer)
        self.assertIn("UTC+03:00", answer)

    def test_south_africa_to_uganda_conversion(self):
        answer = handle_time_command("Convert 14:00 in South Africa to Uganda")
        self.assertEqual(answer, "14:00 in South Africa is 15:00 in Uganda.")

    def test_twelve_hour_conversion(self):
        answer = handle_time_command("Convert 9:30 PM in Uganda to South Africa")
        self.assertEqual(answer, "21:30 in Uganda is 20:30 in South Africa.")

    def test_gmt_crosses_into_following_day(self):
        answer = handle_time_command("Convert 23:30 in GMT to Tanzania")
        self.assertEqual(
            answer,
            "23:30 in GMT is 02:30 in Tanzania on the following day.",
        )

    def test_unrelated_conversation_is_not_claimed(self):
        self.assertIsNone(handle_time_command("Tell me about time travel"))

    def test_australia_requires_a_city(self):
        answer = handle_time_command("What time is it in Australia?")
        self.assertIn("Sydney", answer)
        self.assertIn("Perth", answer)

    @unittest.skipUnless(HAS_TZDATA, "tzdata is not installed")
    def test_london_and_marseille_follow_summer_time_offline(self):
        instant = datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc)
        self.assertIn("13:00", handle_time_command("What time is it in London?", instant))
        self.assertIn("14:00", handle_time_command("What time is it in Marseille?", instant))

    @unittest.skipUnless(HAS_TZDATA, "tzdata is not installed")
    def test_dated_conversion_uses_the_correct_seasonal_rule(self):
        winter = handle_time_command("Convert 12:00 on 2026-01-15 in London to South Africa")
        summer = handle_time_command("Convert 12:00 on 2026-07-15 in London to South Africa")
        self.assertIn("14:00", winter)
        self.assertIn("13:00", summer)

    @unittest.skipUnless(HAS_TZDATA, "tzdata is not installed")
    def test_new_zealand_us_and_thailand_named_zones(self):
        instant = datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc)
        self.assertIn("00:00", handle_time_command("What time is it in New Zealand?", instant))
        self.assertIn("08:00", handle_time_command("What time is it in US East Coast?", instant))
        self.assertIn("05:00", handle_time_command("What time is it in US West Coast?", instant))
        self.assertIn("19:00", handle_time_command("What time is it in Chiang Mai?", instant))

    def test_delegator_and_help_route_without_model(self):
        delegator = TeamDelegator.__new__(TeamDelegator)
        result = delegator.handle("What time is it in Kenya?")
        self.assertTrue(result.handled)
        self.assertIn("Kenya", result.response)
        help_result = delegator.handle("Help with time zones")
        self.assertTrue(help_result.handled)
        self.assertIn("Convert 14:00", help_result.response)
        self.assertIn("Uganda", command_help("time"))


if __name__ == "__main__":
    unittest.main()
