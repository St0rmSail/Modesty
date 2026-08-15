import tempfile
import unittest
from pathlib import Path

from Brain.Memory import ConversationMemory


class ChronicleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / "modesty.db"
        self.memory = ConversationMemory(self.database)

    def tearDown(self):
        self.temp.cleanup()

    def episode(self, **changes):
        values = dict(title="Mallorca under sail", summary="Modesty spent a week learning the rhythms of a sailboat near Mallorca.", narrative_date="Summer", setting="Mallorca", participants="Modesty", themes="sailing, patience", consequences="More patient with ropes and weather", parent_arc="Learning holidays", status="active", provenance="Drew-approved")
        values.update(changes)
        return values

    def test_episode_persists_with_explicit_narrative_metadata(self):
        episode_id = self.memory.add_chronicle_episode(**self.episode())
        reopened = ConversationMemory(self.database)
        episode = reopened.chronicle_episodes()[0]
        self.assertEqual(episode_id, episode["id"])
        self.assertEqual("Drew-approved", episode["provenance"])
        self.assertEqual("active", episode["status"])

    def test_recall_is_relevant_bounded_and_excludes_retired(self):
        self.memory.add_chronicle_episode(**self.episode())
        self.memory.add_chronicle_episode(**self.episode(title="Calamari dispute", summary="The Fishing Buddy brought pungent calamari.", themes="food", status="retired"))
        recalled = self.memory.relevant_chronicle("What did sailing in Mallorca teach you?", limit=1)
        self.assertEqual(["Mallorca under sail"], [item["title"] for item in recalled])
        self.assertIsNotNone(recalled[0]["last_recalled_at"] if "last_recalled_at" in recalled[0] else self.memory.chronicle_episodes()[1]["last_recalled_at"])

    def test_changed_place_does_not_match_old_place_on_generic_theme_alone(self):
        self.memory.add_chronicle_episode(**self.episode(
            title="Madigascar sailing week",
            summary="Modesty spent a week sailing near Madigascar.",
            setting="Madigascar",
        ))
        self.assertEqual([], self.memory.relevant_chronicle("What does sailing near Mallorca remind you about?"))
        recalled = self.memory.relevant_chronicle("What does sailing near Madigascar remind you about?")
        self.assertEqual(["Madigascar sailing week"], [item["title"] for item in recalled])

    def test_update_retire_and_delete_are_user_controllable(self):
        episode_id = self.memory.add_chronicle_episode(**self.episode())
        changed = self.episode(summary="Corrected compact account.", status="retired")
        self.memory.update_chronicle_episode(episode_id, **changed)
        self.assertEqual([], self.memory.relevant_chronicle("Mallorca sailing"))
        self.memory.delete_chronicle_episode(episode_id)
        self.assertEqual([], self.memory.chronicle_episodes())

    def test_invalid_truth_labels_are_rejected(self):
        with self.assertRaises(ValueError):
            self.memory.add_chronicle_episode(**self.episode(provenance="fact"))


if __name__ == "__main__":
    unittest.main()
