"""Evidence-led fishing recommendations with personality kept separate from facts."""

from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
import sqlite3

from Runtime.Fishing.simulators import FishingCodex


@dataclass(frozen=True)
class FishingAdvice:
    known: bool
    game_key: str
    species_name: str
    requested_style: str
    recommended_style: str = ""
    best_tackle: str = ""
    substitutions: tuple[str, ...] = ()
    suitability_warning: str = ""
    evidence_summary: str = ""
    personality_context: str = ""
    memory_context: str = ""


class FishingAdvisor:
    """Rank stored evidence privately and return semantic guidance, not canned prose."""

    CONFIDENCE = {"unverified": 0, "low": 1, "moderate": 2, "high": 3, "confirmed": 4}

    def __init__(self, codex: FishingCodex | None = None):
        self.codex = codex or FishingCodex()

    def advise(
        self,
        game_key: str,
        species_name: str,
        fishing_style: str,
        location_id: int | None = None,
        objective: str = "general",
    ) -> FishingAdvice:
        self.codex.initialize()
        game_key, species_name, fishing_style = (
            game_key.strip().casefold(), species_name.strip(), fishing_style.strip()
        )
        with closing(sqlite3.connect(self.codex.database_path)) as connection:
            connection.row_factory = sqlite3.Row
            style, warning = self._suitable_style(
                connection, game_key, species_name, fishing_style, location_id
            )
            rows = connection.execute(
                """SELECT * FROM recommendations
                   WHERE game_key=? AND species_name=? COLLATE NOCASE
                     AND fishing_style=? COLLATE NOCASE""",
                (game_key, species_name, style),
            ).fetchall()
            if not rows:
                rows = connection.execute(
                    """SELECT NULL AS recommendation_id, game_key, species_name, fishing_style,
                              best_tackle, setup_id, location_id, target_class, minimum_weight,
                              maximum_weight, objective, conditions, minimum_level, required_skills,
                              purchase_cost, expected_income, expected_xp, ownership_status,
                              recommendation_kind, confidence, supporting_catches, last_success_utc,
                              status, game_version, source_id, notes, updated_utc
                       FROM species_tackle WHERE game_key=? AND species_name=? COLLATE NOCASE
                         AND fishing_style=? COLLATE NOCASE""",
                    (game_key, species_name, style),
                ).fetchall()
            if not rows:
                return FishingAdvice(False, game_key, species_name, fishing_style, suitability_warning=warning)
            ranked = sorted(
                rows,
                key=lambda row: (
                    row["status"] in {"confirmed", "active"},
                    self.CONFIDENCE.get(row["confidence"].casefold(), 0),
                    row["objective"].casefold() == objective.casefold(),
                    location_id is not None and row["location_id"] == location_id,
                    row["supporting_catches"],
                ),
                reverse=True,
            )
            chosen = ranked[0]
            substitutions = self._owned_substitutions(connection, chosen["setup_id"], species_name, style, location_id)
            preference = self._preference_context(connection, game_key, style)
            memory = self._memory_context(connection, game_key, species_name, style, location_id)
            evidence = (
                f"{chosen['confidence']} confidence; {chosen['supporting_catches']} supporting catch"
                f"{'es' if chosen['supporting_catches'] != 1 else ''}; status {chosen['status']}"
            )
            semantic = f"{species_name}|{style}|{chosen['best_tackle']}|{warning}|{'|'.join(substitutions)}"
            connection.execute(
                """INSERT INTO recommendation_history
                   (game_key, species_name, fishing_style, location_id, semantic_summary, personality_context)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (game_key, species_name, style, location_id, semantic, preference),
            )
            connection.commit()
            return FishingAdvice(
                True, game_key, species_name, fishing_style, style, chosen["best_tackle"],
                substitutions, warning, evidence, preference, memory,
            )

    @staticmethod
    def _suitable_style(connection, game_key, species_name, requested, location_id):
        if location_id is None:
            return requested, ""
        rows = connection.execute(
            """SELECT fishing_style, relative_strength, status FROM location_method_suitability
               WHERE game_key=? AND location_id=? AND (species_name='' OR species_name=? COLLATE NOCASE)
               ORDER BY relative_strength DESC""",
            (game_key, location_id, species_name),
        ).fetchall()
        requested_row = next((row for row in rows if row["fishing_style"].casefold() == requested.casefold()), None)
        if requested_row and requested_row["relative_strength"] is not None and requested_row["relative_strength"] < 0:
            alternative = next((row for row in rows if row["relative_strength"] is not None and row["relative_strength"] > 0), None)
            if alternative:
                return alternative["fishing_style"], f"{requested} is poorly suited here; {alternative['fishing_style']} has stronger evidence"
            return requested, f"{requested} is poorly suited at this location"
        return requested, ""

    @staticmethod
    def _owned_substitutions(connection, setup_id, species_name, style, location_id):
        if setup_id is None:
            return ()
        missing = connection.execute(
            """SELECT tc.component_id, tc.component_name FROM setup_components sc
               JOIN tackle_components tc ON tc.component_id=sc.component_id
               WHERE sc.setup_id=? AND tc.owned=0""", (setup_id,)
        ).fetchall()
        suggestions = []
        for component in missing:
            match = connection.execute(
                """SELECT replacement.component_name FROM component_substitutions substitutions
                   JOIN tackle_components replacement
                     ON replacement.component_id=substitutions.substitute_component_id
                   WHERE substitutions.original_component_id=? AND replacement.owned=1
                     AND (substitutions.species_name='' OR substitutions.species_name=? COLLATE NOCASE)
                     AND (substitutions.fishing_style='' OR substitutions.fishing_style=? COLLATE NOCASE)
                     AND (substitutions.location_id IS NULL OR substitutions.location_id=?)
                   ORDER BY substitutions.suitability_loss ASC LIMIT 1""",
                (component["component_id"], species_name, style, location_id),
            ).fetchone()
            suggestions.append(
                f"Use {match['component_name']} instead of unavailable {component['component_name']}"
                if match else f"No owned substitute is recorded for {component['component_name']}"
            )
        return tuple(suggestions)

    @staticmethod
    def _preference_context(connection, game_key, style):
        row = connection.execute(
            """SELECT sentiment, reason FROM companion_preferences
               WHERE owner='Modesty' AND active=1 AND (game_key IS NULL OR game_key=?)
                 AND subject_type='fishing style' AND subject_reference=? COLLATE NOCASE
               ORDER BY strength DESC LIMIT 1""", (game_key, style)
        ).fetchone()
        if not row:
            return ""
        feeling = "likes" if row["sentiment"] > 0 else "dislikes" if row["sentiment"] < 0 else "is neutral about"
        return f"Modesty {feeling} {style}" + (f" because {row['reason']}" if row["reason"] else "")

    @staticmethod
    def _memory_context(connection, game_key, species_name, style, location_id):
        now = datetime.now(timezone.utc).isoformat()
        row = connection.execute(
            """SELECT * FROM fishing_memory_links WHERE status='active'
               AND (game_key IS NULL OR game_key=?)
               AND (species_name='' OR species_name=? COLLATE NOCASE)
               AND (fishing_style='' OR fishing_style=? COLLATE NOCASE)
               AND (location_id IS NULL OR location_id=?)
               AND (cooldown_until_utc='' OR cooldown_until_utc<=?)
               ORDER BY salience DESC, recall_count ASC LIMIT 1""",
            (game_key, species_name, style, location_id, now),
        ).fetchone()
        if not row:
            return ""
        connection.execute(
            """UPDATE fishing_memory_links SET last_recalled_utc=?, recall_count=recall_count+1
               WHERE memory_id=?""", (now, row["memory_id"])
        )
        return f"[{row['truth_status']}] {row['summary']}"
