"""Local SQLite catalogue for Modesty's knowledge stores."""

from dataclasses import dataclass
from contextlib import closing
from pathlib import Path
import sqlite3
import re


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


@dataclass(frozen=True)
class PassageResult:
    store: str
    relative_path: str
    title: str
    passage: str


class KnowledgeCatalog:
    """Persist an inventory without storing document contents."""

    def __init__(self, path: Path = DEFAULT_CATALOG):
        self.path = Path(path)

    def replace_store(
        self,
        store: str,
        entries: list[CatalogEntry],
        passages: dict[str, list[str]] | None = None,
        force_reindex: bool = False,
    ) -> int:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as connection:
            self._create_schema(connection)
            old_paths = {
                row[0]
                for row in connection.execute(
                    "SELECT relative_path FROM documents WHERE store = ?", (store,)
                )
            }
            old_hashes = dict(
                connection.execute(
                    "SELECT relative_path, sha256 FROM documents WHERE store = ?",
                    (store,),
                )
            )
            indexed_paths = {
                row[0]
                for row in connection.execute(
                    "SELECT DISTINCT relative_path FROM passages_fts WHERE store = ?",
                    (store,),
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
            changed_paths = {
                entry.relative_path
                for entry in entries
                if old_hashes.get(entry.relative_path) != entry.sha256
            }
            if passages is not None:
                changed_paths.update(current_paths - indexed_paths)
                if force_reindex:
                    changed_paths.update(current_paths)
            stale_paths = old_paths - current_paths
            for relative_path in sorted(changed_paths | stale_paths):
                connection.execute(
                    "DELETE FROM passages_fts WHERE store = ? AND relative_path = ?",
                    (store, relative_path),
                )
            if passages is not None:
                by_path = {entry.relative_path: entry for entry in entries}
                rows = []
                for relative_path in sorted(changed_paths):
                    entry = by_path[relative_path]
                    rows.extend(
                        (store, relative_path, entry.title, passage)
                        for passage in passages.get(relative_path, [])
                        if passage.strip()
                    )
                connection.executemany(
                    "INSERT INTO passages_fts (store, relative_path, title, passage) VALUES (?, ?, ?, ?)",
                    rows,
                )
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

    def search(self, query: str, limit: int = 5) -> list[PassageResult]:
        """Find locally indexed passages while preserving their exact origin."""

        if not self.path.exists():
            return []
        terms = self._search_terms(query)
        if not terms:
            raise ValueError("Tell me what to ask the Library.")
        quoted = [f'"{term.replace(chr(34), chr(34) * 2)}"' for term in terms]
        with closing(sqlite3.connect(self.path)) as connection:
            self._create_schema(connection)
            rows = self._search_rows(connection, " AND ".join(quoted), limit)
            if not rows and len(quoted) > 1:
                rows = self._search_rows(connection, " OR ".join(quoted), limit)
        return [PassageResult(*row[:4]) for row in rows]

    @staticmethod
    def _search_rows(
        connection: sqlite3.Connection,
        match_query: str,
        limit: int,
    ) -> list[tuple]:
        return connection.execute(
            """
            SELECT store, relative_path, title, passage,
                   bm25(passages_fts, 0.0, 0.0, 4.0, 1.0) AS rank
            FROM passages_fts
            WHERE passages_fts MATCH ?
            ORDER BY rank, store, relative_path
            LIMIT ?
            """,
            (match_query, max(1, min(int(limit), 20))),
        ).fetchall()

    @staticmethod
    def _search_terms(query: str) -> list[str]:
        stop_words = {
            "about", "and", "are", "can", "could", "does", "for", "from",
            "have", "how", "into", "its", "should", "that", "the", "this",
            "use", "what", "when", "where", "which", "with", "would",
        }
        terms = []
        for term in re.findall(r"[\w'-]+", query.casefold()):
            if len(term) > 1 and term not in stop_words and term not in terms:
                terms.append(term)
        return terms[:12]

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
        connection.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS passages_fts USING fts5(
                store UNINDEXED,
                relative_path UNINDEXED,
                title,
                passage,
                tokenize = 'unicode61 remove_diacritics 2'
            )
            """
        )
