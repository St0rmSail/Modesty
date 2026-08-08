"""Local SQLite catalogue for Modesty's knowledge stores."""

from dataclasses import dataclass
from contextlib import closing
from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = PROJECT_ROOT / "Data" / "knowledge_catalog.db"


@dataclass(frozen=True)
class CatalogEntry:
    store: str
    relative_path: str
    sha256: str
    size_bytes: int
    modified_ns: int
    title: str
    document_type: str | None
    validation_status: str
    validation_message: str


class KnowledgeCatalog:
    """Persist an inventory without storing document contents."""

    def __init__(self, path: Path = DEFAULT_CATALOG):
        self.path = Path(path)

    def replace_store(self, store: str, entries: list[CatalogEntry]) -> int:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as connection:
            self._create_schema(connection)
            old_paths = {
                row[0]
                for row in connection.execute(
                    "SELECT relative_path FROM documents WHERE store = ?", (store,)
                )
            }
            current_paths = {entry.relative_path for entry in entries}
            removed = len(old_paths - current_paths)
            connection.executemany(
                """
                INSERT INTO documents (
                    store, relative_path, sha256, size_bytes, modified_ns, title,
                    document_type, validation_status, validation_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(store, relative_path) DO UPDATE SET
                    sha256 = excluded.sha256,
                    size_bytes = excluded.size_bytes,
                    modified_ns = excluded.modified_ns,
                    title = excluded.title,
                    document_type = excluded.document_type,
                    validation_status = excluded.validation_status,
                    validation_message = excluded.validation_message
                """,
                [tuple(entry.__dict__.values()) for entry in entries],
            )
            if current_paths:
                connection.execute(
                    "DELETE FROM documents WHERE store = ? AND relative_path NOT IN ({})".format(
                        ",".join("?" for _ in current_paths)
                    ),
                    (store, *sorted(current_paths)),
                )
            else:
                connection.execute("DELETE FROM documents WHERE store = ?", (store,))
            connection.commit()
        return removed

    def entries(self) -> list[CatalogEntry]:
        if not self.path.exists():
            return []
        with closing(sqlite3.connect(self.path)) as connection:
            self._create_schema(connection)
            rows = connection.execute(
                """SELECT store, relative_path, sha256, size_bytes, modified_ns,
                          title, document_type, validation_status, validation_message
                   FROM documents ORDER BY store, relative_path"""
            ).fetchall()
        return [CatalogEntry(*row) for row in rows]

    @staticmethod
    def _create_schema(connection: sqlite3.Connection):
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                store TEXT NOT NULL,
                relative_path TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                modified_ns INTEGER NOT NULL,
                title TEXT NOT NULL,
                document_type TEXT,
                validation_status TEXT NOT NULL,
                validation_message TEXT NOT NULL,
                PRIMARY KEY (store, relative_path)
            )
            """
        )
