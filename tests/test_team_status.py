import unittest

from Runtime.Core import team_status


class TeamStatusTest(unittest.TestCase):
    def setUp(self):
        team_status.reset()

    def test_lamp_requires_core_and_enabled_team(self):
        team_status.set_core_ready(True)
        self.assertFalse(team_status.system_ready())
        team_status.set_member_state("archivist", "ready")
        self.assertFalse(team_status.system_ready())
        team_status.set_member_state("researcher", "ready")
        self.assertTrue(team_status.system_ready())

    def test_missing_member_stays_visibly_offline(self):
        self.assertEqual(team_status.member_state("archivist"), "offline")
        self.assertEqual(team_status.member_state("researcher"), "offline")
        self.assertEqual(team_status.member_state("unimplemented"), "offline")

    def test_ready_member_is_available_but_not_on_headset(self):
        team_status.set_member_state("researcher", "ready")
        self.assertTrue(team_status.any_member_available())
        self.assertFalse(team_status.any_member_active())

    def test_headset_duty_reflects_an_active_enabled_member(self):
        self.assertFalse(team_status.any_member_active())
        team_status.set_member_state("researcher", "working")
        self.assertTrue(team_status.any_member_active())
        team_status.set_member_state("researcher", "waiting")
        self.assertTrue(team_status.any_member_active())

    def test_grand_library_state_is_truthful_and_resets_closed(self):
        self.assertEqual(team_status.grand_library_state(), "closed")
        team_status.set_grand_library_state("loopback")
        self.assertEqual(team_status.grand_library_state(), "loopback")
        team_status.set_grand_library_state("online")
        self.assertEqual(team_status.grand_library_state(), "online")
        team_status.reset()
        self.assertEqual(team_status.grand_library_state(), "closed")

        with self.assertRaises(ValueError):
            team_status.set_grand_library_state("internet-ish")


if __name__ == "__main__":
    unittest.main()
