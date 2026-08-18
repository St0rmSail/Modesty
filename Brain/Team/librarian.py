"""Bounded Librarian duties for catalogue and reversible text repair."""

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import secrets
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


@dataclass(frozen=True)
class RepairProposal:
    repair_id: str
    source_relative_path: str
    derivative_relative_path: str
    source_sha256: str
    derivative_sha256: str
    actions: tuple[str, ...]
    cautions: tuple[str, ...]
    created_at: str


class Librarian:
    """Catalogue Intake and create reviewable derivatives without changing originals."""

    MAX_FILES = 5_000
    MAX_REPAIR_BYTES = 2 * 1024 * 1024
    REPAIRABLE = {".md", ".txt"}
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

    def prepare_text_repair(self, relative_path: str) -> RepairProposal:
        """Create one mechanical UTF-8 derivative in Workbench for review."""

        source = self._safe_intake_path(relative_path)
        if source.suffix.casefold() not in self.REPAIRABLE:
            raise LibrarianError("The first repair duty accepts only UTF-8 Markdown or plain-text files.")
        if source.is_symlink() or not source.is_file():
            raise LibrarianError("That Intake reading file is unavailable or unsafe.")
        try:
            source_bytes = source.read_bytes()
        except OSError as error:
            raise LibrarianError("The Librarian could not read that Intake file safely.") from error
        if len(source_bytes) > self.MAX_REPAIR_BYTES:
            raise LibrarianError(
                f"The first repair duty is limited to {self.MAX_REPAIR_BYTES // (1024 * 1024)} MiB files."
            )
        try:
            original = source_bytes.decode("utf-8")
        except UnicodeDecodeError as error:
            raise LibrarianError("The first repair duty requires valid UTF-8 text.") from error

        repaired, actions, cautions = self._repair_text(original)
        if repaired == original:
            raise LibrarianError("The Librarian found no safe mechanical repair to propose.")

        repair_id = f"LR-{secrets.token_hex(4).upper()}"
        derivative_name = f"{source.stem}.repaired-{repair_id[3:].lower()}{source.suffix.casefold()}"
        derivative = self.paths.workbench / derivative_name
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.catalogue_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            temporary = derivative.with_suffix(f"{derivative.suffix}.tmp")
            temporary.write_text(repaired, encoding="utf-8", newline="\n")
            temporary.replace(derivative)
            proposal = RepairProposal(
                repair_id=repair_id,
                source_relative_path=source.relative_to(self.paths.intake).as_posix(),
                derivative_relative_path=derivative.relative_to(self.paths.root).as_posix(),
                source_sha256=self._sha256(source),
                derivative_sha256=self._sha256(derivative),
                actions=tuple(actions),
                cautions=tuple(cautions),
                created_at=timestamp,
            )
            connection = sqlite3.connect(self.catalogue_path)
            try:
                self._initialize_schema(connection)
                self._initialize_repair_schema(connection)
                with connection:
                    connection.execute(
                        """
                        INSERT INTO repair_jobs
                            (repair_id, source_relative_path, derivative_relative_path,
                             source_sha256, derivative_sha256, actions_json, cautions_json,
                             created_at, status, resolved_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', '')
                        """,
                        (
                            proposal.repair_id,
                            proposal.source_relative_path,
                            proposal.derivative_relative_path,
                            proposal.source_sha256,
                            proposal.derivative_sha256,
                            json.dumps(proposal.actions),
                            json.dumps(proposal.cautions),
                            proposal.created_at,
                        ),
                    )
            finally:
                connection.close()
            return proposal
        except (OSError, sqlite3.DatabaseError) as error:
            try:
                derivative.unlink(missing_ok=True)
            except OSError:
                pass
            raise LibrarianError("The Librarian could not create a reversible repair proposal.") from error

    def resolve_repair(self, repair_id: str, keep: bool) -> Path | None:
        """Keep a pending derivative in Workbench or discard only that derivative."""

        clean_id = self._clean_repair_id(repair_id)
        try:
            connection = sqlite3.connect(self.catalogue_path)
            try:
                self._initialize_repair_schema(connection)
                row = connection.execute(
                    """
                    SELECT source_relative_path, derivative_relative_path,
                           source_sha256, derivative_sha256, status
                    FROM repair_jobs WHERE repair_id = ?
                    """,
                    (clean_id,),
                ).fetchone()
                if row is None or row[4] != "pending":
                    raise LibrarianError("That repair proposal is unavailable or already resolved.")
                source = (self.paths.intake / row[0]).resolve()
                derivative = (self.paths.root / row[1]).resolve()
                try:
                    source.relative_to(self.paths.intake.resolve())
                    derivative.relative_to(self.paths.workbench.resolve())
                except ValueError as error:
                    raise LibrarianError("That repair proposal contains an unsafe path.") from error
                if keep:
                    if not source.is_file() or self._sha256(source) != row[2]:
                        raise LibrarianError(
                            "The original changed after the Briefing was prepared; prepare a new repair."
                        )
                    if not derivative.is_file() or self._sha256(derivative) != row[3]:
                        raise LibrarianError(
                            "The repaired derivative changed after the Briefing was prepared; prepare a new repair."
                        )
                    result = derivative
                    status = "kept"
                else:
                    derivative.unlink(missing_ok=True)
                    result = None
                    status = "discarded"
                with connection:
                    connection.execute(
                        "UPDATE repair_jobs SET status = ?, resolved_at = ? WHERE repair_id = ?",
                        (status, datetime.now(timezone.utc).isoformat(timespec="seconds"), clean_id),
                    )
            finally:
                connection.close()
            return result
        except LibrarianError:
            raise
        except (OSError, sqlite3.DatabaseError) as error:
            raise LibrarianError("The Librarian could not resolve that repair proposal safely.") from error

    @staticmethod
    def repair_briefing(proposal: RepairProposal) -> str:
        actions = "\n".join(f"- {action}" for action in proposal.actions)
        cautions = (
            "\n".join(f"- {caution}" for caution in proposal.cautions)
            if proposal.cautions
            else "- No uncertain or meaning-changing correction was applied."
        )
        return (
            "The Librarian prepared one reversible mechanical repair.\n\n"
            f"Repair: {proposal.repair_id}\n"
            f"Original: The Stacks/Intake/{proposal.source_relative_path}\n"
            f"Provisional derivative: The Stacks/{proposal.derivative_relative_path}\n"
            f"Original SHA-256: {proposal.source_sha256}\n"
            f"Derivative SHA-256: {proposal.derivative_sha256}\n\n"
            f"Applied changes:\n{actions}\n\n"
            f"Cautions and deferred judgement:\n{cautions}\n\n"
            "The original was not renamed, moved, overwritten, or deleted. "
            "Keep Repair leaves the derivative in Workbench; Toss Repair deletes only the derivative."
        )

    def _safe_intake_path(self, relative_path: str) -> Path:
        candidate = Path(relative_path.strip())
        if not relative_path.strip() or candidate.is_absolute() or candidate.name != relative_path.strip():
            raise LibrarianError("Name one file directly inside The Stacks Intake.")
        unresolved = self.paths.intake / candidate
        if unresolved.is_symlink():
            raise LibrarianError("Symbolic links are not accepted for repair.")
        source = unresolved.resolve()
        try:
            source.relative_to(self.paths.intake.resolve())
        except ValueError as error:
            raise LibrarianError("That Intake path is unsafe.") from error
        return source

    @staticmethod
    def _clean_repair_id(repair_id: str) -> str:
        clean = repair_id.strip().upper()
        if not re.fullmatch(r"LR-[A-F0-9]{8}", clean):
            raise LibrarianError("That repair identifier is invalid.")
        return clean

    @staticmethod
    def _repair_text(text: str) -> tuple[str, list[str], list[str]]:
        actions: list[str] = []
        cautions: list[str] = []
        repaired = text
        normalized = repaired.replace("\r\n", "\n").replace("\r", "\n")
        if normalized != repaired:
            actions.append("Normalized mixed line endings to LF.")
            repaired = normalized
        without_nbsp = repaired.replace("\u00a0", " ")
        if without_nbsp != repaired:
            actions.append("Replaced non-breaking spaces with ordinary spaces.")
            repaired = without_nbsp
        lines = repaired.split("\n")
        trimmed = [line.rstrip() for line in lines]
        if trimmed != lines:
            actions.append("Removed trailing spaces and tabs from lines.")
            lines = trimmed
        compacted: list[str] = []
        blank_run = 0
        for line in lines:
            if line:
                blank_run = 0
                compacted.append(line)
            else:
                blank_run += 1
                if blank_run <= 2:
                    compacted.append(line)
        if compacted != lines:
            actions.append("Reduced runs of more than two blank lines.")
        repaired = "\n".join(compacted)
        if repaired and not repaired.endswith("\n"):
            repaired += "\n"
            actions.append("Added one final newline.")
        if re.search(r"\w-\n\w", repaired):
            cautions.append("Possible line-break hyphenation remains unchanged for human review.")
        if any(line and not line.startswith(("#", "-", "*", ">", "    ")) and len(line) < 45 for line in repaired.splitlines()):
            cautions.append("Short wrapped lines remain unchanged because joining them could alter poetry, dialogue, or paragraph meaning.")
        return repaired, actions, cautions

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
    def _initialize_repair_schema(connection: sqlite3.Connection):
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS repair_jobs (
                repair_id TEXT PRIMARY KEY,
                source_relative_path TEXT NOT NULL,
                derivative_relative_path TEXT NOT NULL,
                source_sha256 TEXT NOT NULL,
                derivative_sha256 TEXT NOT NULL,
                actions_json TEXT NOT NULL,
                cautions_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL,
                resolved_at TEXT NOT NULL
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
