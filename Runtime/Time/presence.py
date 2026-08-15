"""Persistent session timing and truthful presence state for Modesty."""

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import secrets
from typing import Callable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATE_PATH = PROJECT_ROOT / "Data" / "presence.json"
PRESENCE_STATES = {"offline", "background", "present", "working"}


class PresenceSession:
    """Record real process presence without inventing offline work."""

    def __init__(
        self,
        state_path: Path = DEFAULT_STATE_PATH,
        clock: Callable[[], datetime] | None = None,
    ):
        self.state_path = Path(state_path)
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.started = False
        self.previous_clean: bool | None = None
        self.absent_since: datetime | None = None
        self.started_at: datetime | None = None
        self.session_id: str | None = None
        self.presence = "offline"

    def begin(self) -> "PresenceSession":
        now = self._now()
        previous = self._load()
        if previous:
            self.previous_clean = bool(previous.get("shutdown_clean", False))
            last_seen = (
                previous.get("shutdown_at")
                if self.previous_clean
                else previous.get("heartbeat_at") or previous.get("started_at")
            )
            self.absent_since = self._parse(last_seen)

        self.started = True
        self.started_at = now
        self.session_id = secrets.token_hex(6).upper()
        self.presence = "present"
        self._write(now, shutdown_clean=False, shutdown_at=None)
        return self

    def set_presence(self, state: str) -> None:
        if state not in PRESENCE_STATES - {"offline"}:
            raise ValueError(f"Invalid active presence state: {state}")
        self._require_started()
        self.presence = state
        self.heartbeat()

    def heartbeat(self) -> None:
        self._require_started()
        self._write(self._now(), shutdown_clean=False, shutdown_at=None)

    def shutdown(self) -> None:
        if not self.started:
            return
        now = self._now()
        self.presence = "offline"
        self._write(now, shutdown_clean=True, shutdown_at=now)
        self.started = False

    def opening_greeting(self) -> str:
        now = self._now().astimezone()
        salutation = self._salutation(now.hour)
        greeting = f"{salutation}, Drew."
        elapsed = self.elapsed_absence(now.astimezone(timezone.utc))
        if elapsed is None:
            return greeting
        duration = self._format_duration(elapsed)
        if self.previous_clean:
            return f"{greeting} You were away for {duration}. Everything closed cleanly last time."
        return (
            f"{greeting} I last saw you {duration} ago. "
            "The previous session did not close cleanly."
        )

    def context_summary(self) -> str:
        now = self._now().astimezone()
        zone = now.tzname() or str(now.utcoffset())
        return (
            f"Current local date and time: {now:%A, %Y-%m-%d %H:%M:%S} ({zone}).\n"
            f"Current presence state: {self.presence}.\n"
            "Do not claim that operational work occurred while the program was offline."
        )

    def elapsed_absence(self, now: datetime | None = None) -> timedelta | None:
        if self.absent_since is None:
            return None
        current = now or self._now()
        return max(timedelta(0), current - self.absent_since)

    def _write(
        self,
        heartbeat_at: datetime,
        *,
        shutdown_clean: bool,
        shutdown_at: datetime | None,
    ) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 1,
            "session_id": self.session_id,
            "started_at": self._iso(self.started_at),
            "heartbeat_at": self._iso(heartbeat_at),
            "shutdown_at": self._iso(shutdown_at),
            "shutdown_clean": shutdown_clean,
            "presence": self.presence,
        }
        temporary = self.state_path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(self.state_path)

    def _load(self) -> dict:
        try:
            value = json.loads(self.state_path.read_text(encoding="utf-8"))
            return value if isinstance(value, dict) else {}
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

    def _now(self) -> datetime:
        value = self.clock()
        if value.tzinfo is None:
            raise ValueError("Presence clock must return a timezone-aware datetime.")
        return value.astimezone(timezone.utc)

    def _require_started(self) -> None:
        if not self.started:
            raise RuntimeError("Presence session has not started.")

    @staticmethod
    def _parse(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None
        return parsed.astimezone(timezone.utc) if parsed.tzinfo else None

    @staticmethod
    def _iso(value: datetime | None) -> str | None:
        return value.astimezone(timezone.utc).isoformat(timespec="seconds") if value else None

    @staticmethod
    def _salutation(hour: int) -> str:
        if 5 <= hour < 12:
            return "Good morning"
        if 12 <= hour < 17:
            return "Good afternoon"
        if 17 <= hour < 22:
            return "Good evening"
        return "You're up late"

    @staticmethod
    def _format_duration(duration: timedelta) -> str:
        seconds = max(0, int(duration.total_seconds()))
        if seconds < 60:
            return "less than a minute"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        hours, remaining_minutes = divmod(minutes, 60)
        if hours < 24:
            if remaining_minutes:
                return f"{hours} hour{'s' if hours != 1 else ''} and {remaining_minutes} minutes"
            return f"{hours} hour{'s' if hours != 1 else ''}"
        days, remaining_hours = divmod(hours, 24)
        if remaining_hours:
            return f"{days} day{'s' if days != 1 else ''} and {remaining_hours} hours"
        return f"{days} day{'s' if days != 1 else ''}"
