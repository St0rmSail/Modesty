"""SQLite-backed conversation persistence for Modesty."""

import sqlite3
import re
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

                CREATE TABLE IF NOT EXISTS personal_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(category, content)
                );

                CREATE TABLE IF NOT EXISTS chronicle_episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    narrative_date TEXT NOT NULL DEFAULT '',
                    setting TEXT NOT NULL DEFAULT '',
                    participants TEXT NOT NULL DEFAULT '',
                    themes TEXT NOT NULL DEFAULT '',
                    consequences TEXT NOT NULL DEFAULT '',
                    parent_arc TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'consolidated', 'retired', 'contradicted')),
                    provenance TEXT NOT NULL DEFAULT 'Drew-approved'
                        CHECK (provenance IN ('self-authored', 'Drew-approved', 'conversation-derived')),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_recalled_at TEXT
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

    @staticmethod
    def _clean_memory_fields(category: str, content: str) -> tuple[str, str]:
        category = " ".join(category.split())[:40]
        content = " ".join(content.split())[:500]
        if not category or not content:
            raise ValueError("A memory needs both a category and some text.")
        return category, content

    def add_personal_memory(
        self,
        category: str,
        content: str,
        source: str = "Added by Drew",
    ) -> int:
        category, content = self._clean_memory_fields(category, content)
        source = " ".join(source.split())[:120] or "Added by Drew"
        timestamp = self._timestamp()
        try:
            with self._connection() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO personal_memories
                        (category, content, source, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (category, content, source, timestamp, timestamp),
                )
                return int(cursor.lastrowid)
        except sqlite3.IntegrityError as error:
            raise MemoryStoreError("That personal memory already exists.") from error
        except sqlite3.DatabaseError as error:
            raise MemoryStoreError("The personal memory could not be saved.") from error

    def update_personal_memory(self, memory_id: int, category: str, content: str):
        category, content = self._clean_memory_fields(category, content)
        timestamp = self._timestamp()
        try:
            with self._connection() as connection:
                cursor = connection.execute(
                    """
                    UPDATE personal_memories
                    SET category = ?, content = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (category, content, timestamp, memory_id),
                )
                if cursor.rowcount == 0:
                    raise MemoryStoreError("That personal memory no longer exists.")
        except sqlite3.IntegrityError as error:
            raise MemoryStoreError("That personal memory already exists.") from error
        except sqlite3.DatabaseError as error:
            raise MemoryStoreError("The personal memory could not be updated.") from error

    def personal_memories(self, limit: int = 100) -> list[dict]:
        try:
            with self._connection() as connection:
                rows = connection.execute(
                    """
                    SELECT id, category, content, source, created_at, updated_at
                    FROM personal_memories
                    ORDER BY category COLLATE NOCASE, id
                    LIMIT ?
                    """,
                    (max(1, limit),),
                ).fetchall()
        except sqlite3.DatabaseError as error:
            raise MemoryStoreError("Personal memories could not be listed.") from error
        return [dict(row) for row in rows]

    def delete_personal_memory(self, memory_id: int):
        try:
            with self._connection() as connection:
                connection.execute(
                    "DELETE FROM personal_memories WHERE id = ?",
                    (memory_id,),
                )
        except sqlite3.DatabaseError as error:
            raise MemoryStoreError("The personal memory could not be deleted.") from error

    CHRONICLE_STATUSES = {"active", "consolidated", "retired", "contradicted"}
    CHRONICLE_PROVENANCE = {"self-authored", "Drew-approved", "conversation-derived"}
    CHRONICLE_QUERY_STOPWORDS = {
        "about", "before", "does", "from", "have", "near", "remind", "that",
        "this", "what", "when", "where", "which", "with", "your", "you",
    }

    @staticmethod
    def _clean_chronicle_text(value: str, maximum: int) -> str:
        return " ".join(value.split())[:maximum]

    def _clean_chronicle(self, episode: dict) -> dict:
        cleaned = {
            "title": self._clean_chronicle_text(episode.get("title", ""), 120),
            "summary": self._clean_chronicle_text(episode.get("summary", ""), 1200),
            "narrative_date": self._clean_chronicle_text(episode.get("narrative_date", ""), 80),
            "setting": self._clean_chronicle_text(episode.get("setting", ""), 160),
            "participants": self._clean_chronicle_text(episode.get("participants", ""), 240),
            "themes": self._clean_chronicle_text(episode.get("themes", ""), 240),
            "consequences": self._clean_chronicle_text(episode.get("consequences", ""), 500),
            "parent_arc": self._clean_chronicle_text(episode.get("parent_arc", ""), 120),
            "status": episode.get("status", "active").strip(),
            "provenance": episode.get("provenance", "Drew-approved").strip(),
        }
        if not cleaned["title"] or not cleaned["summary"]:
            raise ValueError("A Chronicle episode needs a title and summary.")
        if cleaned["status"] not in self.CHRONICLE_STATUSES:
            raise ValueError("Unknown Chronicle status.")
        if cleaned["provenance"] not in self.CHRONICLE_PROVENANCE:
            raise ValueError("Unknown Chronicle provenance.")
        return cleaned

    def add_chronicle_episode(self, **episode) -> int:
        values = self._clean_chronicle(episode)
        timestamp = self._timestamp()
        columns = tuple(values)
        try:
            with self._connection() as connection:
                cursor = connection.execute(
                    f"INSERT INTO chronicle_episodes ({', '.join(columns)}, created_at, updated_at) "
                    f"VALUES ({', '.join('?' for _ in columns)}, ?, ?)",
                    (*values.values(), timestamp, timestamp),
                )
                return int(cursor.lastrowid)
        except sqlite3.DatabaseError as error:
            raise MemoryStoreError("The Chronicle episode could not be saved.") from error

    def update_chronicle_episode(self, episode_id: int, **episode):
        values = self._clean_chronicle(episode)
        timestamp = self._timestamp()
        assignments = ", ".join(f"{column} = ?" for column in values)
        try:
            with self._connection() as connection:
                cursor = connection.execute(
                    f"UPDATE chronicle_episodes SET {assignments}, updated_at = ? WHERE id = ?",
                    (*values.values(), timestamp, episode_id),
                )
                if cursor.rowcount == 0:
                    raise MemoryStoreError("That Chronicle episode no longer exists.")
        except sqlite3.DatabaseError as error:
            raise MemoryStoreError("The Chronicle episode could not be updated.") from error

    def chronicle_episodes(self, limit: int = 100) -> list[dict]:
        try:
            with self._connection() as connection:
                rows = connection.execute(
                    "SELECT * FROM chronicle_episodes ORDER BY id DESC LIMIT ?",
                    (max(1, limit),),
                ).fetchall()
        except sqlite3.DatabaseError as error:
            raise MemoryStoreError("Chronicle episodes could not be listed.") from error
        return [dict(row) for row in rows]

    def relevant_chronicle(self, query: str, limit: int = 3) -> list[dict]:
        terms = {
            term.lower() for term in re.findall(r"[A-Za-z0-9']{3,}", query)
            if term.lower() not in self.CHRONICLE_QUERY_STOPWORDS
        }
        if not terms:
            return []
        candidates = [
            episode for episode in self.chronicle_episodes(200)
            if episode["status"] == "active"
        ]
        scored = []
        for episode in candidates:
            searchable = " ".join(
                str(episode[field]).lower()
                for field in ("title", "summary", "setting", "participants", "themes", "consequences", "parent_arc")
            )
            score = sum(1 for term in terms if term in searchable)
            required = 1 if len(terms) == 1 else 2
            if score >= required:
                scored.append((score, episode["id"], episode))
        selected = [item[2] for item in sorted(scored, reverse=True)[:max(1, limit)]]
        if selected:
            timestamp = self._timestamp()
            try:
                with self._connection() as connection:
                    connection.executemany(
                        "UPDATE chronicle_episodes SET last_recalled_at = ? WHERE id = ?",
                        ((timestamp, episode["id"]) for episode in selected),
                    )
            except sqlite3.DatabaseError as error:
                raise MemoryStoreError("Chronicle recall could not be recorded.") from error
            for episode in selected:
                episode["last_recalled_at"] = timestamp
        return selected

    def delete_chronicle_episode(self, episode_id: int):
        try:
            with self._connection() as connection:
                connection.execute("DELETE FROM chronicle_episodes WHERE id = ?", (episode_id,))
        except sqlite3.DatabaseError as error:
            raise MemoryStoreError("The Chronicle episode could not be deleted.") from error
