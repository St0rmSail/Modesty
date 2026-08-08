"""SQLite-backed conversation persistence for Modesty."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE = PROJECT_ROOT / "Data" / "modesty.db"


class MemoryStoreError(RuntimeError):
    """Raised when Modesty's local conversation store cannot be used."""


class ConversationMemory:
    """Store conversations and messages in a small local SQLite database."""

    def __init__(self, database_path: Path = DEFAULT_DATABASE):
        self.database_path = Path(database_path)
        database_existed = self.database_path.exists()

        try:
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
            self._initialize()
            if database_existed:
                self._backup_once_today()
        except (OSError, sqlite3.DatabaseError) as error:
            raise MemoryStoreError(
                "Modesty could not open her conversation memory."
            ) from error

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        try:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("PRAGMA journal_mode = WAL")
            return connection
        except sqlite3.DatabaseError:
            connection.close()
            raise

    @contextmanager
    def _connection(self):
        connection = self._connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize(self):
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL DEFAULT 'New conversation',
                    model TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    model TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id)
                        REFERENCES conversations(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS messages_conversation_order
                    ON messages(conversation_id, id);

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

    def _backup_once_today(self):
        backup_directory = self.database_path.parent / "Backups"
        backup_directory.mkdir(parents=True, exist_ok=True)
        date = datetime.now().astimezone().date().isoformat()
        backup_path = backup_directory / f"modesty-{date}.db"
        if backup_path.exists():
            return

        source = self._connect()
        destination = sqlite3.connect(backup_path)
        try:
            source.backup(destination)
        finally:
            destination.close()
            source.close()

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    def start_conversation(self, model: str) -> int:
        timestamp = self._timestamp()
        try:
            with self._connection() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO conversations (model, created_at, updated_at)
                    VALUES (?, ?, ?)
                    """,
                    (model, timestamp, timestamp),
                )
                conversation_id = int(cursor.lastrowid)
                self._set_active(connection, conversation_id)
                return conversation_id
        except sqlite3.DatabaseError as error:
            raise MemoryStoreError("The new conversation could not be saved.") from error

    def get_or_create_active(self, model: str) -> int:
        try:
            with self._connection() as connection:
                row = connection.execute(
                    "SELECT value FROM settings WHERE key = 'active_conversation_id'"
                ).fetchone()
                if row is not None:
                    conversation = connection.execute(
                        "SELECT id FROM conversations WHERE id = ?",
                        (int(row["value"]),),
                    ).fetchone()
                    if conversation is not None:
                        return int(conversation["id"])
        except (ValueError, sqlite3.DatabaseError) as error:
            raise MemoryStoreError("The active conversation could not be restored.") from error

        return self.start_conversation(model)

    def set_active(self, conversation_id: int):
        try:
            with self._connection() as connection:
                exists = connection.execute(
                    "SELECT 1 FROM conversations WHERE id = ?",
                    (conversation_id,),
                ).fetchone()
                if exists is None:
                    raise MemoryStoreError("That conversation no longer exists.")
                self._set_active(connection, conversation_id)
        except sqlite3.DatabaseError as error:
            raise MemoryStoreError("The conversation could not be opened.") from error

    @staticmethod
    def _set_active(connection: sqlite3.Connection, conversation_id: int):
        connection.execute(
            """
            INSERT INTO settings (key, value)
            VALUES ('active_conversation_id', ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (str(conversation_id),),
        )

    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        model: str | None = None,
    ):
        if role not in {"user", "assistant"}:
            raise ValueError("Only user and assistant messages may be stored.")

        timestamp = self._timestamp()
        try:
            with self._connection() as connection:
                connection.execute(
                    """
                    INSERT INTO messages
                        (conversation_id, role, content, model, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (conversation_id, role, content, model, timestamp),
                )
                connection.execute(
                    "UPDATE conversations SET updated_at = ? WHERE id = ?",
                    (timestamp, conversation_id),
                )

                if role == "user":
                    conversation = connection.execute(
                        "SELECT title FROM conversations WHERE id = ?",
                        (conversation_id,),
                    ).fetchone()
                    if conversation and conversation["title"] == "New conversation":
                        title = " ".join(content.split())[:48] or "New conversation"
                        connection.execute(
                            "UPDATE conversations SET title = ? WHERE id = ?",
                            (title, conversation_id),
                        )
        except sqlite3.DatabaseError as error:
            raise MemoryStoreError("The message could not be saved.") from error

    def messages(self, conversation_id: int, limit: int = 200) -> list[dict]:
        try:
            with self._connection() as connection:
                rows = connection.execute(
                    """
                    SELECT role, content, model, created_at
                    FROM (
                        SELECT id, role, content, model, created_at
                        FROM messages
                        WHERE conversation_id = ?
                        ORDER BY id DESC
                        LIMIT ?
                    )
                    ORDER BY id
                    """,
                    (conversation_id, max(1, limit)),
                ).fetchall()
        except sqlite3.DatabaseError as error:
            raise MemoryStoreError("Conversation messages could not be restored.") from error

        return [dict(row) for row in rows]

    def conversations(self, limit: int = 20) -> list[dict]:
        try:
            with self._connection() as connection:
                rows = connection.execute(
                    """
                    SELECT id, title, model, created_at, updated_at
                    FROM conversations
                    ORDER BY updated_at DESC, id DESC
                    LIMIT ?
                    """,
                    (max(1, limit),),
                ).fetchall()
        except sqlite3.DatabaseError as error:
            raise MemoryStoreError("Conversation history could not be listed.") from error

        return [dict(row) for row in rows]

    def delete_conversation(self, conversation_id: int):
        try:
            with self._connection() as connection:
                connection.execute(
                    "DELETE FROM conversations WHERE id = ?",
                    (conversation_id,),
                )
                connection.execute(
                    "DELETE FROM settings WHERE key = 'active_conversation_id'",
                )
        except sqlite3.DatabaseError as error:
            raise MemoryStoreError("The conversation could not be deleted.") from error
