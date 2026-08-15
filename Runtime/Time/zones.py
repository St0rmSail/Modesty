"""Fast offline answers for Drew's regularly used fixed-offset time zones."""

from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
import re
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class NamedZone:
    name: str
    zone_key: str | None = None
    fixed_offset_hours: float | None = None
    abbreviation: str | None = None

    @property
    def tzinfo(self):
        if self.zone_key:
            return ZoneInfo(self.zone_key)
        hours = self.fixed_offset_hours or 0
        whole_hours = int(hours)
        minutes = int(round((abs(hours) - abs(whole_hours)) * 60))
        delta = timedelta(hours=whole_hours, minutes=minutes if hours >= 0 else -minutes)
        return timezone(delta)


SOUTH_AFRICA = NamedZone("South Africa", fixed_offset_hours=2, abbreviation="SAST")
EAST_AFRICA = NamedZone("East Africa", fixed_offset_hours=3, abbreviation="EAT")
GMT = NamedZone("GMT", fixed_offset_hours=0, abbreviation="GMT")

ZONE_ALIASES = {
    "south africa": SOUTH_AFRICA,
    "south african": SOUTH_AFRICA,
    "sast": SOUTH_AFRICA,
    "uganda": NamedZone("Uganda", fixed_offset_hours=3, abbreviation="EAT"),
    "kenya": NamedZone("Kenya", fixed_offset_hours=3, abbreviation="EAT"),
    "tanzania": NamedZone("Tanzania", fixed_offset_hours=3, abbreviation="EAT"),
    "east africa": EAST_AFRICA,
    "eat": EAST_AFRICA,
    "gmt": GMT,
    "utc": NamedZone("UTC", fixed_offset_hours=0, abbreviation="UTC"),
    "britain": NamedZone("Britain", "Europe/London"),
    "uk": NamedZone("Britain", "Europe/London"),
    "united kingdom": NamedZone("Britain", "Europe/London"),
    "london": NamedZone("London", "Europe/London"),
    "france": NamedZone("France", "Europe/Paris"),
    "paris": NamedZone("Paris", "Europe/Paris"),
    "marseille": NamedZone("Marseille", "Europe/Paris"),
    "germany": NamedZone("Germany", "Europe/Berlin"),
    "berlin": NamedZone("Berlin", "Europe/Berlin"),
    "thailand": NamedZone("Thailand", "Asia/Bangkok"),
    "bangkok": NamedZone("Bangkok", "Asia/Bangkok"),
    "chiang mai": NamedZone("Chiang Mai", "Asia/Bangkok"),
    "new zealand": NamedZone("New Zealand", "Pacific/Auckland"),
    "auckland": NamedZone("Auckland", "Pacific/Auckland"),
    "sydney": NamedZone("Sydney", "Australia/Sydney"),
    "melbourne": NamedZone("Melbourne", "Australia/Melbourne"),
    "brisbane": NamedZone("Brisbane", "Australia/Brisbane"),
    "adelaide": NamedZone("Adelaide", "Australia/Adelaide"),
    "perth": NamedZone("Perth", "Australia/Perth"),
    "us east coast": NamedZone("US East Coast", "America/New_York"),
    "us eastern": NamedZone("US Eastern", "America/New_York"),
    "eastern time": NamedZone("US Eastern", "America/New_York"),
    "new york": NamedZone("New York", "America/New_York"),
    "us central": NamedZone("US Central", "America/Chicago"),
    "central time": NamedZone("US Central", "America/Chicago"),
    "chicago": NamedZone("Chicago", "America/Chicago"),
    "us west coast": NamedZone("US West Coast", "America/Los_Angeles"),
    "us pacific": NamedZone("US Pacific", "America/Los_Angeles"),
    "pacific time": NamedZone("US Pacific", "America/Los_Angeles"),
    "los angeles": NamedZone("Los Angeles", "America/Los_Angeles"),
}

AMBIGUOUS_ZONES = {"australia", "usa", "united states"}

ZONE_PATTERN = "|".join(
    sorted(
        (re.escape(name) for name in {*ZONE_ALIASES, *AMBIGUOUS_ZONES}),
        key=len,
        reverse=True,
    )
)
CURRENT_TIME_PATTERN = re.compile(
    rf"^(?:what(?:'s|\s+is)\s+the\s+(?:current\s+)?time|what\s+time\s+is\s+it)"
    rf"(?:\s+right\s+now)?\s+in\s+(?P<zone>{ZONE_PATTERN})\??\s*$",
    re.IGNORECASE,
)
CONVERSION_PATTERN = re.compile(
    rf"^(?:convert\s+)?(?P<hour>\d{{1,2}})(?::(?P<minute>\d{{2}}))?\s*"
    rf"(?P<ampm>a\.?m\.?|p\.?m\.?)?(?:\s+on\s+(?P<date>\d{{4}}-\d{{2}}-\d{{2}}))?\s+"
    rf"(?:in|from)\s+"
    rf"(?P<source>{ZONE_PATTERN})\s+(?:to|into)\s+"
    rf"(?P<target>{ZONE_PATTERN})\??\s*$",
    re.IGNORECASE,
)


def handle_time_command(message: str, now: datetime | None = None) -> str | None:
    """Return a deterministic answer for a supported local time request."""

    current = CURRENT_TIME_PATTERN.match(message.strip())
    if current:
        ambiguity = _ambiguity(current.group("zone"))
        if ambiguity:
            return ambiguity
        zone = _zone(current.group("zone"))
        instant = now or datetime.now(timezone.utc)
        if instant.tzinfo is None:
            raise ValueError("Time conversion requires a timezone-aware instant.")
        local = instant.astimezone(zone.tzinfo)
        abbreviation = zone.abbreviation or local.tzname() or zone.name
        return (
            f"It is {local:%H:%M} on {local:%A, %d %B %Y} in {zone.name} "
            f"({abbreviation}, {_offset_label(local.utcoffset())})."
        )

    conversion = CONVERSION_PATTERN.match(message.strip())
    if not conversion:
        return None
    ambiguity = _ambiguity(conversion.group("source")) or _ambiguity(
        conversion.group("target")
    )
    if ambiguity:
        return ambiguity
    source = _zone(conversion.group("source"))
    target = _zone(conversion.group("target"))
    hour = int(conversion.group("hour"))
    minute = int(conversion.group("minute") or 0)
    ampm = conversion.group("ampm")
    if minute > 59:
        return "Minutes must be between 00 and 59."
    if ampm:
        if not 1 <= hour <= 12:
            return "Use an hour from 1 to 12 with AM or PM."
        normalized = ampm.casefold().replace(".", "")
        hour = hour % 12 + (12 if normalized == "pm" else 0)
    elif hour > 23:
        return "Use an hour from 00 to 23, or add AM or PM."

    try:
        reference_date = (
            datetime.strptime(conversion.group("date"), "%Y-%m-%d").date()
            if conversion.group("date")
            else datetime.now(source.tzinfo).date()
        )
    except ValueError:
        return "Use a valid date in YYYY-MM-DD format."
    reference = datetime.combine(
        reference_date,
        time(hour, minute),
        source.tzinfo,
    )
    converted = reference.astimezone(target.tzinfo)
    day_note = ""
    if converted.date() > reference.date():
        day_note = " on the following day"
    elif converted.date() < reference.date():
        day_note = " on the previous day"
    return (
        f"{hour:02d}:{minute:02d} in {source.name} is {converted:%H:%M} "
        f"in {target.name}{day_note}."
    )


def _zone(alias: str) -> NamedZone:
    return ZONE_ALIASES[" ".join(alias.casefold().split())]


def _ambiguity(alias: str) -> str | None:
    normalized = " ".join(alias.casefold().split())
    if normalized == "australia":
        return "Australia has several simultaneous time zones. Ask for Sydney, Melbourne, Brisbane, Adelaide, or Perth."
    if normalized in {"usa", "united states"}:
        return "The United States has several time zones. Ask for US East Coast, US Central, or US West Coast."
    return None


def _offset_label(offset: timedelta | None) -> str:
    total_minutes = int((offset or timedelta(0)).total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    hours, minutes = divmod(abs(total_minutes), 60)
    return f"UTC{sign}{hours:02d}:{minutes:02d}"
