"""The Librarian's first bounded duty: a read-only Intake catalogue."""

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sqlite3
import zipfile

from Runtime.Reading import DEFAULT_CATALOGUE, StacksPaths


class LibrarianError(RuntimeError):
    """Raised when a bounded catalogue cannot be completed safely."""


@dataclass(frozen=True)
class InventoryReport:
    scanned: int
    supported: int
    unsupported: int
    attention: int
    duplicate_groups: int
    stale_removed: int


class Librarian:
    """Catalogue copied Intake files without changing their names or bytes."""

    MAX_FILES = 5_000
    SUPPORTED = {
        ".epub": "EPUB",
        ".pdf": "PDF",
        ".docx": "Word document",
        ".doc": "legacy Word document",
        ".md": "Markdown",
        ".txt": "plain text",
        ".rtf": "rich text",
        ".html": "HTML",
        ".htm": "HTML",
        ".mobi": "Mobipocket",
        ".azw3": "Kindle AZW3",
    }

    def __init__(self, paths: StacksPaths, catalogue_path: Path = DEFAULT_CATALOGUE):
        self.paths = paths
        self.catalogue_path = Path(catalogue_path)

    def inventory(self) -> InventoryReport:
        files = sorted(
            (path for path in self.paths.intake.rglob("*") if path.is_file()),
            key=lambda path: path.as_posix().casefold(),
        )
        if len(files) > self.MAX_FILES:
            raise LibrarianError(
                f"The Stacks Intake contains more than {self.MAX_FILES} files; use a smaller bounded sample."
            )

        self.catalogue_path.parent.mkdir(parents=True, exist_ok=True)
        seen: set[str] = set()
        supported = unsupported = attention = 0
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        connection = None
        try:
            connection = sqlite3.connect(self.catalogue_path)
            with connection:
                self._initialize_schema(connection)
                for path in files:
                    relative = path.relative_to(self.paths.intake).as_posix()
                    seen.add(relative)
                    extension = path.suffix.casefold()
                    format_name = self.SUPPORTED.get(extension, "unsupported")
                    warning = ""
                    digest = ""
                    if path.is_symlink():
                        warning = "Symbolic links are not catalogued."
                    elif format_name == "unsupported":
                        unsupported += 1
                        warning = "Unsupported format; retained untouched."
                    else:
                        supported += 1
                        digest = self._sha256(path)
                        warning = self._health_warning(path, extension)
                    if warning:
                        attention += 1
                    stat = path.stat()
                    connection.execute(
                        """
                        INSERT INTO reading_items
                            (relative_path, filename, extension, format_name, size_bytes,
                             modified_ns, sha256, warning, last_seen_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(relative_path) DO UPDATE SET
                            filename=excluded.filename,
                            extension=excluded.extension,
                            format_name=excluded.format_name,
                            size_bytes=excluded.size_bytes,
                            modified_ns=excluded.modified_ns,
                            sha256=excluded.sha256,
                            warning=excluded.warning,
                            last_seen_at=excluded.last_seen_at
                        """,
                        (
                            relative, path.name, extension, format_name, stat.st_size,
                            stat.st_mtime_ns, digest, warning, timestamp,
                        ),
                    )
                stale_removed = self._remove_stale(connection, seen)
                duplicate_groups = connection.execute(
                    """
                    SELECT COUNT(*) FROM (
                        SELECT sha256 FROM reading_items
                        WHERE sha256 <> '' GROUP BY sha256 HAVING COUNT(*) > 1
                    )
                    """
                ).fetchone()[0]
        except (OSError, sqlite3.DatabaseError) as error:
            raise LibrarianError("The Librarian could not complete the read-only catalogue.") from error
        finally:
            if connection is not None:
                connection.close()

        return InventoryReport(
            scanned=len(files),
            supported=supported,
            unsupported=unsupported,
            attention=attention,
            duplicate_groups=int(duplicate_groups),
            stale_removed=stale_removed,
        )

    @staticmethod
    def _initialize_schema(connection: sqlite3.Connection):
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reading_items (
                relative_path TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                extension TEXT NOT NULL,
                format_name TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                modified_ns INTEGER NOT NULL,
                sha256 TEXT NOT NULL,
                warning TEXT NOT NULL,
                last_seen_at TEXT NOT NULL
            )
            """
        )

    @staticmethod
    def _remove_stale(connection: sqlite3.Connection, seen: set[str]) -> int:
        rows = connection.execute("SELECT relative_path FROM reading_items").fetchall()
        stale = [(row[0],) for row in rows if row[0] not in seen]
        connection.executemany("DELETE FROM reading_items WHERE relative_path = ?", stale)
        return len(stale)

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    @staticmethod
    def _health_warning(path: Path, extension: str) -> str:
        if extension in {".epub", ".docx"}:
            if not zipfile.is_zipfile(path):
                return "The document container is not a readable ZIP archive."
            try:
                with zipfile.ZipFile(path) as archive:
                    damaged = archive.testzip()
                    names = set(archive.namelist())
            except (OSError, zipfile.BadZipFile):
                return "The document container could not be read."
            if damaged:
                return f"The document container has a damaged member: {damaged}"
            if extension == ".epub" and "META-INF/container.xml" not in names:
                return "The EPUB container metadata is missing."
            if extension == ".docx" and "[Content_Types].xml" not in names:
                return "The Word document content map is missing."
        elif extension == ".pdf":
            with path.open("rb") as stream:
                if stream.read(5) != b"%PDF-":
                    return "The PDF signature is missing."
        return ""
