import unittest
import json
from pathlib import Path

from Runtime.Animation.duty_transition import DutyTransition


class DutyTransitionTest(unittest.TestCase):
    def test_outward_transition_has_exact_endpoints(self):
        animation = DutyTransition(2.0)
        self.assertEqual(animation.sample(0.0).progress, 0.0)
        self.assertEqual(animation.sample(2.0).progress, 1.0)
        self.assertTrue(animation.sample(2.0).complete)

    def test_current_primitive_has_reciprocal_outward_and_return_progress(self):
        animation = DutyTransition(2.0)
        for elapsed in (0.0, 0.25, 0.75, 1.25, 2.0):
            outward = animation.sample(elapsed).progress
            returning = animation.sample(elapsed, returning=True).progress
            self.assertAlmostEqual(outward + returning, 1.0)

    def test_sampling_depends_on_elapsed_time_not_frame_count(self):
        animation = DutyTransition(1.8)
        direct = animation.sample(0.9).progress
        after_many_hypothetical_frames = animation.sample(0.9).progress
        self.assertEqual(direct, after_many_hypothetical_frames)

    def test_invalid_duration_is_rejected(self):
        with self.assertRaises(ValueError):
            DutyTransition(0.0)

    def test_briefing_geometry_is_separate_and_comes_forward(self):
        root = Path(__file__).resolve().parents[1]
        position = json.loads(
            (root / "Config" / "modesty_position.json").read_text(encoding="utf-8")
        )
        duty = position["briefing_presentation"]
        self.assertGreater(duty["anchor_x"], position["anchor_x"])
        self.assertGreater(duty["anchor_y"], position["anchor_y"])
        self.assertGreater(duty["height"], position["height"])


if __name__ == "__main__":
    unittest.main()
