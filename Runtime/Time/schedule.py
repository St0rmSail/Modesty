"""Small local schedule with explicit, timezone-aware reminder commands."""

import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE = PROJECT_ROOT / "Data" / "modesty.db"


class ReminderStore:
    def __init__(self, database_path: Path = DEFAULT_DATABASE, clock=None):
        self.database_path = Path(database_path)
        self.clock = clock or (lambda: datetime.now().astimezone())
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    due_at TEXT NOT NULL,
                    text TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'completed')),
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                )"""
            )

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def add_local(self, date_text: str, time_text: str, text: str) -> dict:
        local_now = self.clock()
        if local_now.tzinfo is None:
            raise ValueError("The schedule clock must be timezone-aware.")
        try:
            naive = datetime.strptime(f"{date_text} {time_text}", "%Y-%m-%d %H:%M")
        except ValueError as error:
            raise ValueError("Use a valid local date and 24-hour time: YYYY-MM-DD at HH:MM.") from error
        text = " ".join(text.split())[:500]
        if not text:
            raise ValueError("A reminder needs some text.")
        due = naive.replace(tzinfo=local_now.tzinfo).astimezone(timezone.utc)
        created = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO reminders (due_at, text, created_at) VALUES (?, ?, ?)",
                (due.isoformat(timespec="seconds"), text, created),
            )
            reminder_id = int(cursor.lastrowid)
        return self.get(reminder_id)

    def get(self, reminder_id: int) -> dict:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM reminders WHERE id = ?", (reminder_id,)).fetchone()
        if row is None:
            raise ValueError("That reminder does not exist.")
        return dict(row)

    def pending(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM reminders WHERE status = 'pending' ORDER BY due_at, id"
            ).fetchall()
        return [dict(row) for row in rows]

    def all(self, limit: int = 200) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM reminders ORDER BY status, due_at, id LIMIT ?", (max(1, limit),)
            ).fetchall()
        return [dict(row) for row in rows]

    def opening_summary(self, limit: int = 3) -> str:
        now = self.clock().astimezone()
        due = []
        for reminder in self.pending():
            local_due = datetime.fromisoformat(reminder["due_at"]).astimezone(now.tzinfo)
            if local_due.date() <= now.date():
                due.append((local_due, reminder))
        if not due:
            return ""
        overdue = sum(1 for local_due, _ in due if local_due < now)
        label = f"{overdue} overdue" if overdue else f"{len(due)} due today"
        shown = "; ".join(self.format_due(reminder) for _, reminder in due[:max(1, limit)])
        extra = len(due) - min(len(due), max(1, limit))
        suffix = f"; and {extra} more" if extra else ""
        return f"You have {label} reminder{'s' if (overdue or len(due)) != 1 else ''}: {shown}{suffix}."

    def complete(self, reminder_id: int) -> dict:
        completed = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE reminders SET status = 'completed', completed_at = ? WHERE id = ? AND status = 'pending'",
                (completed, reminder_id),
            )
        if cursor.rowcount == 0:
            raise ValueError("That pending reminder does not exist.")
        return self.get(reminder_id)

    def delete(self, reminder_id: int) -> None:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        if cursor.rowcount == 0:
            raise ValueError("That reminder does not exist.")

    def format_due(self, reminder: dict) -> str:
        due = datetime.fromisoformat(reminder["due_at"]).astimezone(self.clock().tzinfo)
        return f"#{reminder['id']} — {due:%Y-%m-%d %H:%M} — {reminder['text']}"


ADD_PATTERN = re.compile(r"^(?:please\s+)?remind\s+me\s+on\s+(?P<date>\d{4}-\d{2}-\d{2})\s+at\s+(?P<time>\d{1,2}:\d{2})\s*:\s*(?P<text>.+)$", re.I | re.S)
LIST_PATTERN = re.compile(r"^(?:please\s+)?(?:show|list)\s+(?:me\s+)?my\s+reminders\??$", re.I)
COMPLETE_PATTERN = re.compile(r"^(?:please\s+)?complete\s+reminder\s+#?(?P<id>\d+)\s*$", re.I)
DELETE_PATTERN = re.compile(r"^(?:please\s+)?delete\s+reminder\s+#?(?P<id>\d+)\s*$", re.I)


def handle_schedule_command(message: str, store: ReminderStore | None) -> str | None:
    text = message.strip()
    match = ADD_PATTERN.match(text)
    is_schedule = bool(match or LIST_PATTERN.match(text) or COMPLETE_PATTERN.match(text) or DELETE_PATTERN.match(text))
    if not is_schedule:
        return None
    if store is None:
        return "The local schedule is unavailable."
    try:
        if match:
            reminder = store.add_local(match.group("date"), match.group("time"), match.group("text"))
            return f"Scheduled locally: {store.format_due(reminder)}"
        if LIST_PATTERN.match(text):
            reminders = store.pending()
            if not reminders:
                return "You have no pending reminders."
            return "Pending reminders:\n\n" + "\n".join(store.format_due(item) for item in reminders)
        match = COMPLETE_PATTERN.match(text)
        if match:
            reminder = store.complete(int(match.group("id")))
            return f"Completed reminder #{reminder['id']}: {reminder['text']}"
        match = DELETE_PATTERN.match(text)
        if match:
            reminder_id = int(match.group("id")); store.delete(reminder_id)
            return f"Deleted reminder #{reminder_id}."
    except (ValueError, sqlite3.Error) as error:
        return str(error)
    return None
