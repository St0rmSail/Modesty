from pathlib import Path
from contextlib import closing
import json
import re
import sqlite3
import tempfile
import unittest

from Brain.Team.fishing_buddy import FishingBuddy
from Runtime.Fishing import FishingCodex, RF4AlmanacImporter, RF4CodexQuestions


def record(name, *, baits=None, locations=None, trophy="1000", super_trophy="1500"):
    return {
        "name": name, "nameRu": "", "locations": locations or ["Test Lake"],
        "baits": baits or ["Worm", "Cheese cube"], "bite": "Active",
        "time": "Day", "depth": "1 m", "hookSize": "S8 - S2",
        "trophyWeight": trophy, "superTrophyWeight": super_trophy,
        "weightKg": "", "weightPrice": "", "weightXp": "", "assemblies": [],
        "tip": "Community note",
    }


class RF4QuestionsTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.codex = FishingCodex(Path(self.folder.name) / "Fishing")
        records = [
            record("Albino barbel"),
            record("Common Roach", locations=["Winding Rivulet"]),
            record("Tench", locations=["Old Burg Lake"], baits=["Cheese cube", "Nightcrawler"]),
            record("Bream", trophy="3000", super_trophy="5000"),
            record("Atlantic cod", baits=["Marine worm"], locations=["Norwegian Sea"]),
            record("Pike"),
            record("European chimaera", trophy="9999999", super_trophy="9999999"),
        ]
        literal = json.dumps(records, separators=(",", ":"))
        literal = re.sub(r'"([A-Za-z][A-Za-z0-9_]*)":', r'\1:', literal)
        page = b'<script type="module" src="/assets/index-TEST.js"></script>'
        bundle = ("const qi=" + literal + ",n3={};").encode()
        RF4AlmanacImporter(
            self.codex,
            lambda url, _maximum: page if url.endswith("/") else bundle,
            minimum_records=6,
        ).import_catalogue()
        self.buddy = FishingBuddy(self.codex)

    def tearDown(self):
        self.folder.cleanup()

    def test_answers_bait_location_trophy_and_overview_questions(self):
        self.assertIn("Cheese cube", self.buddy.answer_rf4_question("What should I use for tench in RF4?"))
        self.assertIn("Winding Rivulet", self.buddy.answer_rf4_question("Where can I catch common roach?"))
        self.assertIn("trophy 3 kg", self.buddy.answer_rf4_question("What is trophy weight for bream?"))
        overview = self.buddy.answer_rf4_question("Tell me about Atlantic cod.")
        self.assertIn("Norwegian Sea", overview)
        self.assertIn("community reference weakest", overview)

    def test_checks_named_bait_without_turning_absence_into_proof(self):
        self.assertIn("Yes", self.buddy.answer_rf4_question("Would cheese work for tench?"))
        answer = self.buddy.answer_rf4_question("Would bread work for tench?")
        self.assertIn("does not list bread", answer)
        self.assertIn("not proof", answer)

    def test_approximate_species_and_unknown_fields_are_truthful(self):
        typo = self.buddy.answer_rf4_question("Where can I catch comman roch?")
        self.assertIn("approximately to Common Roach", typo)
        unknown = self.buddy.answer_rf4_question("What is trophy weight for European chimaera?")
        self.assertIn("not yet established", unknown)

    def test_nonexistent_or_ambiguous_species_is_not_guessed(self):
        with closing(sqlite3.connect(self.codex.database_path)) as connection, connection:
            connection.execute(
                "INSERT INTO species (game_key, species_name) VALUES (?, ?)",
                ("fisher-online", "Moonfish"),
            )
        self.assertIsNone(RF4CodexQuestions(self.codex).lookup("Tell me about moonfish"))
        self.assertIn("could not identify", self.buddy.answer_rf4_question("Tell me about moonfish"))

if __name__ == "__main__":
    unittest.main()
