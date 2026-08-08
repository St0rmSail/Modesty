import unittest

from Runtime.Core import team_status


class TeamStatusTest(unittest.TestCase):
    def setUp(self):
        team_status.reset()

    def test_lamp_requires_core_and_enabled_team(self):
        team_status.set_core_ready(True)
        self.assertFalse(team_status.system_ready())
        team_status.set_member_state("archivist", "ready")
        self.assertTrue(team_status.system_ready())

    def test_missing_member_stays_visibly_offline(self):
        self.assertEqual(team_status.member_state("archivist"), "offline")
        self.assertEqual(team_status.member_state("unimplemented"), "offline")


if __name__ == "__main__":
    unittest.main()
