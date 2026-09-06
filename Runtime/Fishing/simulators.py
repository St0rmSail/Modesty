"""Bounded, read-only discovery for supported fishing simulators."""

from __future__ import annotations

from dataclasses import dataclass
from contextlib import closing
import json
import os
from pathlib import Path
import re
import sqlite3


GAMES = (
    ("russian-fishing-4", "Russian Fishing 4", None, "standalone"),
    ("fisher-online", "Fisher Online", "1094780", "steam"),
    ("professional-fishing-2", "Professional Fishing 2", "1232220", "steam"),
    ("call-of-the-wild-the-angler", "Call of the Wild: The Angler", "1408610", "steam"),
)


@dataclass(frozen=True)
class SimulatorDiscovery:
    key: str
    name: str
    installation: str
    installed: bool
    data_status: str
    data_path: str = ""


@dataclass(frozen=True)
class SpeciesEntry:
    game_key: str
    species_name: str
    fishing_style: str
    best_tackle: str
    basis: str
    source: str


class FishingCodex:
    """Own the private codex skeleton and inspect paths without reading game data."""

    SECTIONS = ("Locations", "Species", "Tackle", "Techniques", "Maps", "Sources", "Sessions")

    def __init__(self, root: Path | None = None):
        self.root = Path(root or Path(__file__).resolve().parents[2] / "Data" / "Fishing")
        self.database_path = self.root / "fishing_codex.db"

    def initialize(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        for key, name, _, _ in GAMES:
            game_root = self.root / key
            for section in self.SECTIONS:
                (game_root / section).mkdir(parents=True, exist_ok=True)
            index = game_root / "index.json"
            if not index.exists():
                index.write_text(
                    json.dumps({"game": name, "schema": 1, "observations": []}, indent=2) + "\n",
                    encoding="utf-8",
                )
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS schema_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS games (
                    game_key TEXT PRIMARY KEY,
                    game_name TEXT NOT NULL,
                    install_channel TEXT NOT NULL
                )"""
            )
            connection.executemany(
                "INSERT OR IGNORE INTO games (game_key, game_name, install_channel) VALUES (?, ?, ?)",
                ((key, name, channel) for key, name, _, channel in GAMES),
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS species (
                    game_key TEXT NOT NULL,
                    species_name TEXT NOT NULL,
                    PRIMARY KEY (game_key, species_name)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS species_tackle (
                    game_key TEXT NOT NULL,
                    species_name TEXT NOT NULL,
                    fishing_style TEXT NOT NULL,
                    best_tackle TEXT NOT NULL DEFAULT 'Not yet established',
                    basis TEXT NOT NULL DEFAULT 'unverified',
                    source TEXT NOT NULL DEFAULT '',
                    updated_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (game_key, species_name, fishing_style),
                    FOREIGN KEY (game_key, species_name)
                        REFERENCES species (game_key, species_name)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS game_versions (
                    version_id INTEGER PRIMARY KEY,
                    game_key TEXT NOT NULL,
                    version_label TEXT NOT NULL,
                    observed_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    source TEXT NOT NULL DEFAULT '',
                    UNIQUE (game_key, version_label),
                    FOREIGN KEY (game_key) REFERENCES games (game_key)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS fishing_methods (
                    game_key TEXT NOT NULL,
                    method_name TEXT NOT NULL,
                    PRIMARY KEY (game_key, method_name),
                    FOREIGN KEY (game_key) REFERENCES games (game_key)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS locations (
                    location_id INTEGER PRIMARY KEY,
                    game_key TEXT NOT NULL,
                    waterbody TEXT NOT NULL,
                    area TEXT NOT NULL DEFAULT '',
                    coordinates TEXT NOT NULL DEFAULT '',
                    landmark TEXT NOT NULL DEFAULT '',
                    cast_direction TEXT NOT NULL DEFAULT '',
                    cast_distance REAL,
                    fishing_depth REAL,
                    bottom_or_structure TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY (game_key) REFERENCES games (game_key)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS tackle_setups (
                    setup_id INTEGER PRIMARY KEY,
                    game_key TEXT NOT NULL,
                    setup_name TEXT NOT NULL,
                    fishing_style TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    rod TEXT NOT NULL DEFAULT '', reel TEXT NOT NULL DEFAULT '',
                    main_line TEXT NOT NULL DEFAULT '', leader TEXT NOT NULL DEFAULT '',
                    hook TEXT NOT NULL DEFAULT '', terminal_component TEXT NOT NULL DEFAULT '',
                    bait_or_lure TEXT NOT NULL DEFAULT '', groundbait TEXT NOT NULL DEFAULT '',
                    accessories TEXT NOT NULL DEFAULT '', drag_or_brake TEXT NOT NULL DEFAULT '',
                    retrieve_method TEXT NOT NULL DEFAULT '', retrieve_speed TEXT NOT NULL DEFAULT '',
                    UNIQUE (game_key, setup_name),
                    FOREIGN KEY (game_key) REFERENCES games (game_key)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS tackle_components (
                    component_id INTEGER PRIMARY KEY,
                    game_key TEXT NOT NULL,
                    component_type TEXT NOT NULL,
                    component_name TEXT NOT NULL,
                    variant TEXT NOT NULL DEFAULT '',
                    statistics TEXT NOT NULL DEFAULT '',
                    minimum_level INTEGER,
                    purchase_cost REAL,
                    owned INTEGER NOT NULL DEFAULT 0 CHECK (owned IN (0, 1)),
                    UNIQUE (game_key, component_type, component_name, variant),
                    FOREIGN KEY (game_key) REFERENCES games (game_key)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS setup_components (
                    setup_id INTEGER NOT NULL,
                    component_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    quantity REAL NOT NULL DEFAULT 1,
                    PRIMARY KEY (setup_id, component_id, role),
                    FOREIGN KEY (setup_id) REFERENCES tackle_setups (setup_id),
                    FOREIGN KEY (component_id) REFERENCES tackle_components (component_id)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS sources (
                    source_id INTEGER PRIMARY KEY,
                    game_key TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    title TEXT NOT NULL DEFAULT '',
                    locator TEXT NOT NULL,
                    retrieved_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    game_version TEXT NOT NULL DEFAULT '',
                    evidence_status TEXT NOT NULL DEFAULT 'unverified',
                    UNIQUE (game_key, locator),
                    FOREIGN KEY (game_key) REFERENCES games (game_key)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS species_reference (
                    game_key TEXT NOT NULL,
                    species_name TEXT NOT NULL,
                    source_id INTEGER NOT NULL,
                    trophy_weight_grams INTEGER,
                    super_trophy_weight_grams INTEGER,
                    activity TEXT NOT NULL DEFAULT '',
                    active_time TEXT NOT NULL DEFAULT '',
                    depth_guidance TEXT NOT NULL DEFAULT '',
                    hook_guidance TEXT NOT NULL DEFAULT '',
                    notes TEXT NOT NULL DEFAULT '',
                    confidence TEXT NOT NULL DEFAULT 'seed_weakest',
                    last_seen_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (game_key, species_name, source_id),
                    FOREIGN KEY (game_key, species_name) REFERENCES species (game_key, species_name),
                    FOREIGN KEY (source_id) REFERENCES sources (source_id)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS species_locations (
                    game_key TEXT NOT NULL,
                    species_name TEXT NOT NULL,
                    location_id INTEGER NOT NULL,
                    source_id INTEGER NOT NULL,
                    confidence TEXT NOT NULL DEFAULT 'seed_weakest',
                    last_seen_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (game_key, species_name, location_id, source_id),
                    FOREIGN KEY (game_key, species_name) REFERENCES species (game_key, species_name),
                    FOREIGN KEY (location_id) REFERENCES locations (location_id),
                    FOREIGN KEY (source_id) REFERENCES sources (source_id)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS hotspots (
                    hotspot_id INTEGER PRIMARY KEY,
                    game_key TEXT NOT NULL,
                    location_id INTEGER NOT NULL,
                    species_name TEXT NOT NULL DEFAULT '',
                    fishing_style TEXT NOT NULL DEFAULT '',
                    category TEXT NOT NULL DEFAULT 'rumoured'
                        CHECK (category IN ('rumoured', 'known', 'favourite')),
                    summary TEXT NOT NULL DEFAULT '',
                    source_id INTEGER,
                    first_seen_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    last_seen_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    locally_tested_utc TEXT NOT NULL DEFAULT '',
                    supporting_local_sessions INTEGER NOT NULL DEFAULT 0,
                    favourite_selected_utc TEXT NOT NULL DEFAULT '',
                    UNIQUE (game_key, location_id, species_name, fishing_style, source_id),
                    FOREIGN KEY (location_id) REFERENCES locations (location_id),
                    FOREIGN KEY (source_id) REFERENCES sources (source_id)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS source_import_runs (
                    import_id INTEGER PRIMARY KEY,
                    game_key TEXT NOT NULL,
                    source_id INTEGER NOT NULL,
                    retrieved_utc TEXT NOT NULL,
                    content_sha256 TEXT NOT NULL,
                    species_count INTEGER NOT NULL,
                    bait_links_count INTEGER NOT NULL,
                    location_links_count INTEGER NOT NULL,
                    integrity_check TEXT NOT NULL,
                    FOREIGN KEY (source_id) REFERENCES sources (source_id)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS baits (
                    bait_id INTEGER PRIMARY KEY,
                    game_key TEXT NOT NULL,
                    bait_name TEXT NOT NULL,
                    bait_type TEXT NOT NULL DEFAULT 'hookbait',
                    size_or_variant TEXT NOT NULL DEFAULT '',
                    condition_or_freshness TEXT NOT NULL DEFAULT '',
                    UNIQUE (game_key, bait_name, size_or_variant),
                    FOREIGN KEY (game_key) REFERENCES games (game_key)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS species_bait_effectiveness (
                    game_key TEXT NOT NULL,
                    species_name TEXT NOT NULL,
                    fishing_style TEXT NOT NULL,
                    bait_id INTEGER NOT NULL,
                    effectiveness TEXT NOT NULL DEFAULT 'unknown',
                    relative_score REAL,
                    selectivity TEXT NOT NULL DEFAULT '',
                    presentation TEXT NOT NULL DEFAULT '',
                    compatible_hook_range TEXT NOT NULL DEFAULT '',
                    conditions TEXT NOT NULL DEFAULT '',
                    supporting_catches INTEGER NOT NULL DEFAULT 0,
                    confidence TEXT NOT NULL DEFAULT 'unverified',
                    game_version TEXT NOT NULL DEFAULT '',
                    source_id INTEGER,
                    updated_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (game_key, species_name, fishing_style, bait_id),
                    FOREIGN KEY (game_key, species_name) REFERENCES species (game_key, species_name),
                    FOREIGN KEY (game_key, fishing_style) REFERENCES fishing_methods (game_key, method_name),
                    FOREIGN KEY (bait_id) REFERENCES baits (bait_id),
                    FOREIGN KEY (source_id) REFERENCES sources (source_id)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS groundbait_recipes (
                    recipe_id INTEGER PRIMARY KEY,
                    game_key TEXT NOT NULL,
                    recipe_name TEXT NOT NULL,
                    preparation TEXT NOT NULL DEFAULT '',
                    delivery_method TEXT NOT NULL DEFAULT '',
                    batch_cost REAL,
                    UNIQUE (game_key, recipe_name),
                    FOREIGN KEY (game_key) REFERENCES games (game_key)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS groundbait_ingredients (
                    recipe_id INTEGER NOT NULL,
                    component_id INTEGER NOT NULL,
                    amount TEXT NOT NULL DEFAULT '',
                    PRIMARY KEY (recipe_id, component_id),
                    FOREIGN KEY (recipe_id) REFERENCES groundbait_recipes (recipe_id),
                    FOREIGN KEY (component_id) REFERENCES tackle_components (component_id)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS species_groundbait_effectiveness (
                    game_key TEXT NOT NULL,
                    species_name TEXT NOT NULL,
                    fishing_style TEXT NOT NULL,
                    recipe_id INTEGER NOT NULL,
                    location_id INTEGER,
                    relative_strength REAL,
                    selectivity TEXT NOT NULL DEFAULT '',
                    effective_duration TEXT NOT NULL DEFAULT '',
                    overfeeding_risk TEXT NOT NULL DEFAULT '',
                    conditions TEXT NOT NULL DEFAULT '',
                    supporting_sessions INTEGER NOT NULL DEFAULT 0,
                    confidence TEXT NOT NULL DEFAULT 'unverified',
                    game_version TEXT NOT NULL DEFAULT '',
                    source_id INTEGER,
                    updated_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (game_key, species_name, fishing_style, recipe_id, location_id),
                    FOREIGN KEY (game_key, species_name) REFERENCES species (game_key, species_name),
                    FOREIGN KEY (game_key, fishing_style) REFERENCES fishing_methods (game_key, method_name),
                    FOREIGN KEY (recipe_id) REFERENCES groundbait_recipes (recipe_id),
                    FOREIGN KEY (location_id) REFERENCES locations (location_id),
                    FOREIGN KEY (source_id) REFERENCES sources (source_id)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS component_effects (
                    effect_id INTEGER PRIMARY KEY,
                    game_key TEXT NOT NULL,
                    component_id INTEGER NOT NULL,
                    species_name TEXT,
                    fishing_style TEXT NOT NULL DEFAULT '',
                    location_id INTEGER,
                    target_class TEXT NOT NULL DEFAULT '',
                    conditions TEXT NOT NULL DEFAULT '',
                    effect_type TEXT NOT NULL,
                    relative_strength REAL,
                    supporting_observations INTEGER NOT NULL DEFAULT 0,
                    confidence TEXT NOT NULL DEFAULT 'unverified',
                    game_version TEXT NOT NULL DEFAULT '',
                    source_id INTEGER,
                    FOREIGN KEY (game_key) REFERENCES games (game_key),
                    FOREIGN KEY (component_id) REFERENCES tackle_components (component_id),
                    FOREIGN KEY (location_id) REFERENCES locations (location_id),
                    FOREIGN KEY (source_id) REFERENCES sources (source_id)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS component_compatibility (
                    game_key TEXT NOT NULL,
                    first_component_id INTEGER NOT NULL,
                    second_component_id INTEGER NOT NULL,
                    compatible INTEGER NOT NULL CHECK (compatible IN (0, 1)),
                    reason TEXT NOT NULL DEFAULT '',
                    game_version TEXT NOT NULL DEFAULT '',
                    source_id INTEGER,
                    PRIMARY KEY (game_key, first_component_id, second_component_id),
                    FOREIGN KEY (first_component_id) REFERENCES tackle_components (component_id),
                    FOREIGN KEY (second_component_id) REFERENCES tackle_components (component_id),
                    FOREIGN KEY (source_id) REFERENCES sources (source_id)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS component_substitutions (
                    game_key TEXT NOT NULL,
                    original_component_id INTEGER NOT NULL,
                    substitute_component_id INTEGER NOT NULL,
                    species_name TEXT NOT NULL DEFAULT '',
                    fishing_style TEXT NOT NULL DEFAULT '',
                    location_id INTEGER,
                    suitability_loss REAL,
                    reason TEXT NOT NULL DEFAULT '',
                    confidence TEXT NOT NULL DEFAULT 'unverified',
                    source_id INTEGER,
                    PRIMARY KEY (game_key, original_component_id, substitute_component_id, species_name, fishing_style),
                    FOREIGN KEY (original_component_id) REFERENCES tackle_components (component_id),
                    FOREIGN KEY (substitute_component_id) REFERENCES tackle_components (component_id),
                    FOREIGN KEY (location_id) REFERENCES locations (location_id),
                    FOREIGN KEY (source_id) REFERENCES sources (source_id)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS location_method_suitability (
                    game_key TEXT NOT NULL,
                    location_id INTEGER NOT NULL,
                    fishing_style TEXT NOT NULL,
                    species_name TEXT NOT NULL DEFAULT '',
                    relative_strength REAL,
                    conditions TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'unverified',
                    supporting_observations INTEGER NOT NULL DEFAULT 0,
                    confidence TEXT NOT NULL DEFAULT 'unverified',
                    source_id INTEGER,
                    PRIMARY KEY (game_key, location_id, fishing_style, species_name),
                    FOREIGN KEY (location_id) REFERENCES locations (location_id),
                    FOREIGN KEY (source_id) REFERENCES sources (source_id)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS companion_preferences (
                    preference_id INTEGER PRIMARY KEY,
                    owner TEXT NOT NULL CHECK (owner IN ('Modesty', 'Drew')),
                    game_key TEXT,
                    subject_type TEXT NOT NULL,
                    subject_reference TEXT NOT NULL,
                    sentiment REAL NOT NULL CHECK (sentiment BETWEEN -1 AND 1),
                    strength REAL NOT NULL DEFAULT 0.5 CHECK (strength BETWEEN 0 AND 1),
                    reason TEXT NOT NULL DEFAULT '',
                    origin TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
                    updated_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (owner, game_key, subject_type, subject_reference),
                    FOREIGN KEY (game_key) REFERENCES games (game_key)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS fishing_memory_links (
                    memory_id INTEGER PRIMARY KEY,
                    chronicle_reference TEXT NOT NULL DEFAULT '',
                    game_key TEXT,
                    species_name TEXT NOT NULL DEFAULT '',
                    fishing_style TEXT NOT NULL DEFAULT '',
                    location_id INTEGER,
                    catch_id INTEGER,
                    memory_type TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    truth_status TEXT NOT NULL CHECK (truth_status IN
                        ('observed', 'Drew confirmed', 'shared narrative', 'fictional colour')),
                    emotional_tone TEXT NOT NULL DEFAULT '',
                    salience REAL NOT NULL DEFAULT 0.5 CHECK (salience BETWEEN 0 AND 1),
                    last_recalled_utc TEXT NOT NULL DEFAULT '',
                    recall_count INTEGER NOT NULL DEFAULT 0,
                    cooldown_until_utc TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'active',
                    FOREIGN KEY (game_key) REFERENCES games (game_key),
                    FOREIGN KEY (location_id) REFERENCES locations (location_id),
                    FOREIGN KEY (catch_id) REFERENCES catches (catch_id)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS recommendation_history (
                    history_id INTEGER PRIMARY KEY,
                    created_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    game_key TEXT NOT NULL,
                    species_name TEXT NOT NULL DEFAULT '',
                    fishing_style TEXT NOT NULL DEFAULT '',
                    location_id INTEGER,
                    semantic_summary TEXT NOT NULL,
                    response_fingerprint TEXT NOT NULL DEFAULT '',
                    personality_context TEXT NOT NULL DEFAULT '',
                    outcome TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY (game_key) REFERENCES games (game_key),
                    FOREIGN KEY (location_id) REFERENCES locations (location_id)
                )"""
            )
            self._ensure_columns(
                connection,
                "species_tackle",
                {
                    "setup_id": "INTEGER",
                    "location_id": "INTEGER",
                    "target_class": "TEXT NOT NULL DEFAULT ''",
                    "minimum_weight": "REAL",
                    "maximum_weight": "REAL",
                    "objective": "TEXT NOT NULL DEFAULT 'general'",
                    "conditions": "TEXT NOT NULL DEFAULT ''",
                    "minimum_level": "INTEGER",
                    "required_skills": "TEXT NOT NULL DEFAULT ''",
                    "purchase_cost": "REAL",
                    "expected_income": "REAL",
                    "expected_xp": "REAL",
                    "ownership_status": "TEXT NOT NULL DEFAULT 'unknown'",
                    "recommendation_kind": "TEXT NOT NULL DEFAULT 'best proven'",
                    "confidence": "TEXT NOT NULL DEFAULT 'unverified'",
                    "supporting_catches": "INTEGER NOT NULL DEFAULT 0",
                    "last_success_utc": "TEXT NOT NULL DEFAULT ''",
                    "status": "TEXT NOT NULL DEFAULT 'unverified'",
                    "game_version": "TEXT NOT NULL DEFAULT ''",
                    "source_id": "INTEGER",
                    "notes": "TEXT NOT NULL DEFAULT ''",
                },
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS recommendations (
                    recommendation_id INTEGER PRIMARY KEY,
                    game_key TEXT NOT NULL,
                    species_name TEXT NOT NULL,
                    fishing_style TEXT NOT NULL,
                    best_tackle TEXT NOT NULL,
                    setup_id INTEGER,
                    location_id INTEGER,
                    target_class TEXT NOT NULL DEFAULT '',
                    minimum_weight REAL,
                    maximum_weight REAL,
                    objective TEXT NOT NULL DEFAULT 'general',
                    conditions TEXT NOT NULL DEFAULT '',
                    minimum_level INTEGER,
                    required_skills TEXT NOT NULL DEFAULT '',
                    purchase_cost REAL,
                    expected_income REAL,
                    expected_xp REAL,
                    ownership_status TEXT NOT NULL DEFAULT 'unknown',
                    recommendation_kind TEXT NOT NULL DEFAULT 'best proven',
                    confidence TEXT NOT NULL DEFAULT 'unverified',
                    supporting_catches INTEGER NOT NULL DEFAULT 0,
                    last_success_utc TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'unverified',
                    game_version TEXT NOT NULL DEFAULT '',
                    source_id INTEGER,
                    notes TEXT NOT NULL DEFAULT '',
                    updated_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_key, species_name) REFERENCES species (game_key, species_name),
                    FOREIGN KEY (game_key, fishing_style) REFERENCES fishing_methods (game_key, method_name),
                    FOREIGN KEY (setup_id) REFERENCES tackle_setups (setup_id),
                    FOREIGN KEY (location_id) REFERENCES locations (location_id),
                    FOREIGN KEY (source_id) REFERENCES sources (source_id)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS player_state (
                    game_key TEXT PRIMARY KEY,
                    player_level INTEGER,
                    cash REAL,
                    unlocks TEXT NOT NULL DEFAULT '',
                    inventory_summary TEXT NOT NULL DEFAULT '',
                    observed_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    source TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY (game_key) REFERENCES games (game_key)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS catches (
                    catch_id INTEGER PRIMARY KEY,
                    game_key TEXT NOT NULL,
                    species_name TEXT NOT NULL,
                    caught_utc TEXT NOT NULL,
                    fishing_style TEXT NOT NULL,
                    setup_id INTEGER,
                    location_id INTEGER,
                    weight REAL,
                    length REAL,
                    rank TEXT NOT NULL DEFAULT '',
                    conditions TEXT NOT NULL DEFAULT '',
                    fight_duration_seconds REAL,
                    disposition TEXT NOT NULL DEFAULT '',
                    sale_value REAL,
                    xp REAL,
                    outcome TEXT NOT NULL DEFAULT 'caught',
                    capture_method TEXT NOT NULL,
                    source_id INTEGER,
                    FOREIGN KEY (game_key, species_name) REFERENCES species (game_key, species_name),
                    FOREIGN KEY (setup_id) REFERENCES tackle_setups (setup_id),
                    FOREIGN KEY (location_id) REFERENCES locations (location_id),
                    FOREIGN KEY (source_id) REFERENCES sources (source_id)
                )"""
            )
            connection.execute(
                "INSERT OR REPLACE INTO schema_meta (key, value) VALUES ('schema_version', '7')"
            )
            connection.commit()

    @staticmethod
    def _ensure_columns(connection: sqlite3.Connection, table: str, columns: dict[str, str]) -> None:
        existing = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
        for name, declaration in columns.items():
            if name not in existing:
                connection.execute(f"ALTER TABLE {table} ADD COLUMN {name} {declaration}")

    def record_species(
        self,
        game_key: str,
        species_name: str,
        fishing_style: str = "General",
        best_tackle: str = "Not yet established",
        basis: str = "unverified",
        source: str = "",
    ) -> SpeciesEntry:
        """Add or update one species while always retaining an explicit tackle entry."""
        self.initialize()
        valid_games = {key for key, _, _, _ in GAMES}
        game_key = game_key.strip().casefold()
        species_name = species_name.strip()
        fishing_style = fishing_style.strip()
        best_tackle = best_tackle.strip()
        basis = basis.strip() or "unverified"
        source = source.strip()
        if game_key not in valid_games:
            raise ValueError(f"Unknown fishing simulator: {game_key}")
        if not species_name:
            raise ValueError("Species name is required")
        if not fishing_style:
            raise ValueError("Fishing style is required")
        if not best_tackle:
            raise ValueError("Every species requires a best-tackle entry")
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.execute(
                "INSERT OR IGNORE INTO species (game_key, species_name) VALUES (?, ?)",
                (game_key, species_name),
            )
            connection.execute(
                "INSERT OR IGNORE INTO fishing_methods (game_key, method_name) VALUES (?, ?)",
                (game_key, fishing_style),
            )
            connection.execute(
                """INSERT INTO species_tackle
                   (game_key, species_name, fishing_style, best_tackle, basis, source, updated_utc)
                   VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                   ON CONFLICT(game_key, species_name, fishing_style) DO UPDATE SET
                       best_tackle=excluded.best_tackle,
                       basis=excluded.basis,
                       source=excluded.source,
                       updated_utc=CURRENT_TIMESTAMP""",
                (game_key, species_name, fishing_style, best_tackle, basis, source),
            )
            connection.commit()
        return SpeciesEntry(game_key, species_name, fishing_style, best_tackle, basis, source)

    def species_entries(self, game_key: str | None = None) -> tuple[SpeciesEntry, ...]:
        self.initialize()
        query = "SELECT game_key, species_name, fishing_style, best_tackle, basis, source FROM species_tackle"
        parameters: tuple[str, ...] = ()
        if game_key:
            query += " WHERE game_key = ?"
            parameters = (game_key.strip().casefold(),)
        query += " ORDER BY game_key, species_name COLLATE NOCASE, fishing_style COLLATE NOCASE"
        with closing(sqlite3.connect(self.database_path)) as connection:
            return tuple(SpeciesEntry(*row) for row in connection.execute(query, parameters))

    def inspect(
        self,
        steam_roots: tuple[Path, ...] | None = None,
        drive_roots: tuple[Path, ...] | None = None,
        home: Path | None = None,
    ) -> tuple[SimulatorDiscovery, ...]:
        self.initialize()
        home = Path(home or Path.home())
        steam = self._steam_installs(steam_roots)
        rf4 = self._find_rf4(drive_roots, home)
        results = []
        for key, name, app_id, channel in GAMES:
            install = rf4 if channel == "standalone" else steam.get(app_id or "")
            data_path = ""
            data_status = "unsupported"
            if key == "call-of-the-wild-the-angler":
                saves = home / "Saved Games" / "Avalanche Studios" / "CotWTheAngler" / "Saves"
                if saves.is_dir():
                    data_path, data_status = str(saves), "candidate read-only source"
            elif install:
                data_status = "installation found; progress source not yet verified"
            results.append(SimulatorDiscovery(key, name, str(install or ""), bool(install), data_status, data_path))
        return tuple(results)

    @staticmethod
    def _steam_installs(steam_roots: tuple[Path, ...] | None) -> dict[str, Path]:
        roots = list(steam_roots or ())
        if not roots:
            roots.append(Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Steam")
        libraries = list(roots)
        for root in tuple(roots):
            vdf = root / "steamapps" / "libraryfolders.vdf"
            if vdf.is_file():
                text = vdf.read_text(encoding="utf-8", errors="ignore")
                libraries.extend(Path(value.replace("\\\\", "\\")) for value in re.findall(r'"path"\s+"([^"]+)"', text))
        found = {}
        wanted = {app_id for _, _, app_id, _ in GAMES if app_id}
        for library in dict.fromkeys(libraries):
            for app_id in wanted:
                manifest = library / "steamapps" / f"appmanifest_{app_id}.acf"
                if not manifest.is_file():
                    continue
                text = manifest.read_text(encoding="utf-8", errors="ignore")
                match = re.search(r'"installdir"\s+"([^"]+)"', text)
                if match:
                    candidate = library / "steamapps" / "common" / match.group(1)
                    if candidate.is_dir():
                        found[app_id] = candidate
        return found

    @staticmethod
    def _find_rf4(drive_roots: tuple[Path, ...] | None, home: Path) -> Path | None:
        roots = list(drive_roots or ())
        if not roots and os.name == "nt":
            roots = [Path(f"{letter}:/") for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ" if Path(f"{letter}:/").exists()]
        for root in roots:
            try:
                candidates = (entry for entry in root.iterdir() if entry.is_dir() and entry.name.casefold().startswith("rf4"))
                for candidate in candidates:
                    if (candidate / "RF4Launcher.exe").is_file():
                        return candidate
            except OSError:
                continue
        launcher_state = home / "AppData" / "Local" / "RF4Launcher"
        return launcher_state if launcher_state.is_dir() else None
