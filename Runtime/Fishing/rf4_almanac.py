"""Bounded, provenance-preserving intake for the RF4 Tackle Box fish catalogue."""

from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
import sqlite3
from typing import Callable
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from .simulators import FishingCodex


GAME_KEY = "russian-fishing-4"
SOURCE_URL = "https://rf4almanac.pages.dev/"
SOURCE_TITLE = "RF4 Tackle Box fish catalogue"
EVIDENCE_STATUS = "community_reference_weakest"
USER_AGENT = "Modesty/0.35 bounded RF4 community-reference intake"
ANCHOR = '[{name:"Albino barbel",nameRu:'
EXPECTED_KEYS = {
    "name", "nameRu", "locations", "baits", "bite", "time", "depth", "hookSize",
    "trophyWeight", "superTrophyWeight", "weightKg", "weightPrice", "weightXp",
    "assemblies", "tip",
}
INTEGRITY_SPECIES = ("Common Roach", "Tench", "Bream", "Atlantic cod", "Pike")


@dataclass(frozen=True)
class RF4ImportReport:
    species: int
    baits: int
    bait_links: int
    locations: int
    location_links: int
    integrity_species: tuple[str, ...]
    source_sha256: str


class RF4AlmanacImporter:
    MAX_PAGE_BYTES = 512 * 1024
    MAX_BUNDLE_BYTES = 2 * 1024 * 1024
    MAX_RECORDS = 400

    def __init__(
        self,
        codex: FishingCodex | None = None,
        fetcher: Callable[[str, int], bytes] | None = None,
        minimum_records: int = 200,
    ):
        self.codex = codex or FishingCodex()
        self.fetcher = fetcher or self._fetch
        self.minimum_records = minimum_records

    def import_catalogue(self) -> RF4ImportReport:
        page = self.fetcher(SOURCE_URL, self.MAX_PAGE_BYTES)
        bundle_url = self._bundle_url(page)
        bundle = self.fetcher(bundle_url, self.MAX_BUNDLE_BYTES)
        records = self._parse_records(bundle)
        checked = self._validate_records(records)
        digest = hashlib.sha256(bundle).hexdigest()
        return self._store(records, checked, digest)

    @staticmethod
    def _fetch(url: str, maximum: int) -> bytes:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != "rf4almanac.pages.dev":
            raise ValueError("RF4 Almanac intake refused an unexpected host")
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"})
        with urlopen(request, timeout=25) as response:
            content_type = response.headers.get_content_type()
            if content_type not in {"text/html", "text/javascript", "application/javascript"}:
                raise ValueError("RF4 Almanac returned an unexpected content type")
            data = response.read(maximum + 1)
        if len(data) > maximum:
            raise ValueError("RF4 Almanac response exceeded the bounded intake limit")
        return data

    @staticmethod
    def _bundle_url(page: bytes) -> str:
        text = page.decode("utf-8")
        matches = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', text, re.IGNORECASE)
        candidates = [value for value in matches if re.fullmatch(r"/assets/index-[A-Za-z0-9_-]+\.js", value)]
        if len(candidates) != 1:
            raise ValueError("RF4 Almanac did not expose one expected application bundle")
        return urljoin(SOURCE_URL, candidates[0])

    def _parse_records(self, bundle: bytes) -> list[dict[str, object]]:
        text = bundle.decode("utf-8")
        start = text.find(ANCHOR)
        if start < 0:
            raise ValueError("RF4 Almanac fish catalogue anchor was not found")
        end = self._balanced_array_end(text, start)
        literal = text[start:end]
        quoted = re.sub(r'([,{])([A-Za-z][A-Za-z0-9_]*):', r'\1"\2":', literal)
        try:
            records = json.loads(quoted)
        except json.JSONDecodeError as error:
            raise ValueError("RF4 Almanac fish catalogue was not safely parseable") from error
        if not isinstance(records, list):
            raise ValueError("RF4 Almanac fish catalogue was not a list")
        return records

    @staticmethod
    def _balanced_array_end(text: str, start: int) -> int:
        depth = 0
        in_string = False
        escaped = False
        for index in range(start, len(text)):
            character = text[index]
            if in_string:
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == '"':
                    in_string = False
                continue
            if character == '"':
                in_string = True
            elif character == "[":
                depth += 1
            elif character == "]":
                depth -= 1
                if depth == 0:
                    return index + 1
        raise ValueError("RF4 Almanac fish catalogue was incomplete")

    def _validate_records(self, records: list[dict[str, object]]) -> tuple[str, ...]:
        if not self.minimum_records <= len(records) <= self.MAX_RECORDS:
            raise ValueError("RF4 Almanac fish count fell outside the reviewed bounds")
        names: set[str] = set()
        for record in records:
            if not isinstance(record, dict) or set(record) != EXPECTED_KEYS:
                raise ValueError("RF4 Almanac fish record structure changed")
            name = self._text(record["name"], "species name")
            if name.casefold() in names:
                raise ValueError("RF4 Almanac contained a duplicate species")
            names.add(name.casefold())
            self._text_list(record["locations"], "locations")
            self._text_list(record["baits"], "baits")
            self._optional_weight(record["trophyWeight"])
            self._optional_weight(record["superTrophyWeight"])
        checked = tuple(name for name in INTEGRITY_SPECIES if name.casefold() in names)
        if len(checked) != len(INTEGRITY_SPECIES):
            raise ValueError("RF4 Almanac failed the five-species integrity check")
        return checked

    @staticmethod
    def _text(value: object, label: str) -> str:
        if not isinstance(value, str) or not value.strip() or len(value) > 500:
            raise ValueError(f"RF4 Almanac supplied an invalid {label}")
        if any(character in value for character in ("\x00", "\r", "\n")):
            raise ValueError(f"RF4 Almanac supplied unsafe {label}")
        return value.strip()

    @classmethod
    def _text_list(cls, value: object, label: str) -> tuple[str, ...]:
        if not isinstance(value, list) or len(value) > 50:
            raise ValueError(f"RF4 Almanac supplied invalid {label}")
        return tuple(cls._text(item, label) for item in value)

    @staticmethod
    def _optional_weight(value: object) -> int | None:
        if value in ("", None):
            return None
        if not isinstance(value, str) or not value.isdigit():
            raise ValueError("RF4 Almanac supplied an invalid trophy weight")
        number = int(value)
        if number == 9_999_999:
            return None
        if not 0 < number <= 5_000_000:
            raise ValueError("RF4 Almanac trophy weight was outside reviewed bounds")
        return number

    def _store(
        self, records: list[dict[str, object]], checked: tuple[str, ...], digest: str
    ) -> RF4ImportReport:
        self.codex.initialize()
        retrieved = datetime.now(timezone.utc).isoformat()
        baits: set[str] = set()
        locations: set[str] = set()
        bait_link_keys: set[tuple[str, str]] = set()
        location_link_keys: set[tuple[str, str]] = set()
        with closing(sqlite3.connect(self.codex.database_path)) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            with connection:
                connection.execute(
                    """INSERT INTO sources
                       (game_key, source_type, title, locator, retrieved_utc, evidence_status)
                       VALUES (?, 'community_reference', ?, ?, ?, ?)
                       ON CONFLICT(game_key, locator) DO UPDATE SET
                           title=excluded.title, retrieved_utc=excluded.retrieved_utc,
                           evidence_status=excluded.evidence_status""",
                    (GAME_KEY, SOURCE_TITLE, SOURCE_URL, retrieved, EVIDENCE_STATUS),
                )
                source_id = connection.execute(
                    "SELECT source_id FROM sources WHERE game_key=? AND locator=?",
                    (GAME_KEY, SOURCE_URL),
                ).fetchone()[0]
                connection.execute(
                    "INSERT OR IGNORE INTO fishing_methods VALUES (?, 'General')", (GAME_KEY,)
                )
                for record in records:
                    name = self._text(record["name"], "species name")
                    connection.execute(
                        "INSERT OR IGNORE INTO species VALUES (?, ?)", (GAME_KEY, name)
                    )
                    connection.execute(
                        """INSERT OR IGNORE INTO species_tackle
                           (game_key, species_name, fishing_style, best_tackle, basis, source)
                           VALUES (?, ?, 'General', 'Not yet established', ?, ?)""",
                        (GAME_KEY, name, EVIDENCE_STATUS, SOURCE_URL),
                    )
                    connection.execute(
                        """INSERT INTO species_reference
                           (game_key, species_name, source_id, trophy_weight_grams,
                            super_trophy_weight_grams, activity, active_time, depth_guidance,
                            hook_guidance, notes, confidence, last_seen_utc)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           ON CONFLICT(game_key, species_name, source_id) DO UPDATE SET
                            trophy_weight_grams=excluded.trophy_weight_grams,
                            super_trophy_weight_grams=excluded.super_trophy_weight_grams,
                            activity=excluded.activity, active_time=excluded.active_time,
                            depth_guidance=excluded.depth_guidance,
                            hook_guidance=excluded.hook_guidance, notes=excluded.notes,
                            confidence=excluded.confidence, last_seen_utc=excluded.last_seen_utc""",
                        (
                            GAME_KEY, name, source_id,
                            self._optional_weight(record["trophyWeight"]),
                            self._optional_weight(record["superTrophyWeight"]),
                            str(record["bite"]).strip(), str(record["time"]).strip(),
                            str(record["depth"]).strip(), str(record["hookSize"]).strip(),
                            str(record["tip"]).strip(), EVIDENCE_STATUS, retrieved,
                        ),
                    )
                    for bait in self._text_list(record["baits"], "baits"):
                        baits.add(bait)
                        connection.execute(
                            "INSERT OR IGNORE INTO baits (game_key, bait_name) VALUES (?, ?)",
                            (GAME_KEY, bait),
                        )
                        bait_id = connection.execute(
                            """SELECT bait_id FROM baits
                               WHERE game_key=? AND bait_name=? AND size_or_variant=''""",
                            (GAME_KEY, bait),
                        ).fetchone()[0]
                        connection.execute(
                            """INSERT INTO species_bait_effectiveness
                               (game_key, species_name, fishing_style, bait_id, effectiveness,
                                confidence, source_id, updated_utc)
                               VALUES (?, ?, 'General', ?, 'community suggested', ?, ?, ?)
                               ON CONFLICT(game_key, species_name, fishing_style, bait_id) DO UPDATE SET
                                effectiveness=excluded.effectiveness, confidence=excluded.confidence,
                                source_id=excluded.source_id, updated_utc=excluded.updated_utc""",
                            (GAME_KEY, name, bait_id, EVIDENCE_STATUS, source_id, retrieved),
                        )
                        bait_link_keys.add((name, bait))
                    for waterbody in self._text_list(record["locations"], "locations"):
                        locations.add(waterbody)
                        row = connection.execute(
                            """SELECT location_id FROM locations WHERE game_key=? AND waterbody=?
                               AND area='' AND coordinates='' ORDER BY location_id LIMIT 1""",
                            (GAME_KEY, waterbody),
                        ).fetchone()
                        if row:
                            location_id = row[0]
                        else:
                            location_id = connection.execute(
                                "INSERT INTO locations (game_key, waterbody) VALUES (?, ?)",
                                (GAME_KEY, waterbody),
                            ).lastrowid
                        connection.execute(
                            """INSERT INTO species_locations
                               (game_key, species_name, location_id, source_id, confidence, last_seen_utc)
                               VALUES (?, ?, ?, ?, ?, ?)
                               ON CONFLICT(game_key, species_name, location_id, source_id) DO UPDATE SET
                                confidence=excluded.confidence, last_seen_utc=excluded.last_seen_utc""",
                            (GAME_KEY, name, location_id, source_id, EVIDENCE_STATUS, retrieved),
                        )
                        location_link_keys.add((name, waterbody))
                connection.execute(
                    """INSERT INTO source_import_runs
                       (game_key, source_id, retrieved_utc, content_sha256, species_count,
                        bait_links_count, location_links_count, integrity_check)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        GAME_KEY, source_id, retrieved, digest, len(records), len(bait_link_keys),
                        len(location_link_keys), "passed: " + ", ".join(checked),
                    ),
                )
        return RF4ImportReport(
            len(records), len(baits), len(bait_link_keys), len(locations),
            len(location_link_keys), checked, digest
        )
