"""Natural, source-ranked questions over the private RF4 fish catalogue."""

from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from difflib import SequenceMatcher
import re
import sqlite3

from .simulators import FishingCodex


GAME_KEY = "russian-fishing-4"


@dataclass(frozen=True)
class RF4SpeciesBrief:
    species_name: str
    trophy_weight_grams: int | None
    super_trophy_weight_grams: int | None
    activity: str
    active_time: str
    depth_guidance: str
    hook_guidance: str
    notes: str
    baits: tuple[str, ...]
    locations: tuple[str, ...]
    source_title: str
    source_locator: str
    confidence: str
    approximate_match: bool = False


class RF4CodexQuestions:
    """Resolve a species naturally, then return facts without inventing missing fields."""

    MATCH_THRESHOLD = 0.78

    def __init__(self, codex: FishingCodex | None = None):
        self.codex = codex or FishingCodex()

    def lookup(self, question: str) -> RF4SpeciesBrief | None:
        self.codex.initialize()
        with closing(sqlite3.connect(self.codex.database_path)) as connection:
            names = tuple(
                row[0] for row in connection.execute(
                    "SELECT species_name FROM species WHERE game_key=? ORDER BY species_name COLLATE NOCASE",
                    (GAME_KEY,),
                )
            )
            resolved = self._resolve_species(question, names)
            if resolved is None:
                return None
            species_name, approximate = resolved
            reference = connection.execute(
                """SELECT r.trophy_weight_grams, r.super_trophy_weight_grams,
                          r.activity, r.active_time, r.depth_guidance, r.hook_guidance,
                          r.notes, s.title, s.locator, r.confidence
                   FROM species_reference r JOIN sources s ON s.source_id=r.source_id
                   WHERE r.game_key=? AND r.species_name=?
                   ORDER BY CASE r.confidence
                       WHEN 'Drew confirmed' THEN 0 WHEN 'confirmed' THEN 1
                       WHEN 'known' THEN 2 ELSE 9 END,
                       r.last_seen_utc DESC LIMIT 1""",
                (GAME_KEY, species_name),
            ).fetchone()
            if reference is None:
                return None
            baits = tuple(
                row[0] for row in connection.execute(
                    """SELECT DISTINCT b.bait_name
                       FROM species_bait_effectiveness e
                       JOIN baits b ON b.bait_id=e.bait_id
                       WHERE e.game_key=? AND e.species_name=?
                       ORDER BY b.bait_name COLLATE NOCASE""",
                    (GAME_KEY, species_name),
                )
            )
            locations = tuple(
                row[0] for row in connection.execute(
                    """SELECT DISTINCT l.waterbody
                       FROM species_locations sl
                       JOIN locations l ON l.location_id=sl.location_id
                       WHERE sl.game_key=? AND sl.species_name=?
                       ORDER BY l.waterbody COLLATE NOCASE""",
                    (GAME_KEY, species_name),
                )
            )
        return RF4SpeciesBrief(
            species_name,
            reference[0], reference[1], reference[2], reference[3], reference[4],
            reference[5], reference[6], baits, locations, reference[7], reference[8],
            reference[9], approximate,
        )

    @classmethod
    def _resolve_species(
        cls, question: str, species_names: tuple[str, ...]
    ) -> tuple[str, bool] | None:
        query = cls._normalise(question)
        exact = [name for name in species_names if cls._contains_phrase(query, cls._normalise(name))]
        if exact:
            return max(exact, key=lambda value: len(cls._normalise(value))), False
        query_words = query.split()
        scored: list[tuple[float, str]] = []
        for name in species_names:
            target = cls._normalise(name)
            length = len(target.split())
            candidates = (
                " ".join(query_words[start:start + width])
                for width in range(max(1, length - 1), min(len(query_words), length + 1) + 1)
                for start in range(0, len(query_words) - width + 1)
            )
            score = max((SequenceMatcher(None, target, value).ratio() for value in candidates), default=0.0)
            scored.append((score, name))
        scored.sort(reverse=True)
        if not scored or scored[0][0] < cls.MATCH_THRESHOLD:
            return None
        if len(scored) > 1 and scored[0][0] - scored[1][0] < 0.025:
            return None
        return scored[0][1], True

    @staticmethod
    def _normalise(value: str) -> str:
        return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))

    @staticmethod
    def _contains_phrase(text: str, phrase: str) -> bool:
        return f" {phrase} " in f" {text} "
