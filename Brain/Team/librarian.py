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
from Runtime.Reading.book_reader import BookReadError, BookText, read_book, read_book_metadata


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


@dataclass(frozen=True)
class BookInspection:
    shelving_id: str
    source_relative_path: str
    source_sha256: str
    title: str
    author: str
    format_name: str
    word_count: int
    section_count: int
    proposed_relative_path: str
    preview: str
    truncated: bool


@dataclass(frozen=True)
class ReadingHit:
    title: str
    author: str
    source_relative_path: str
    section: str
    passage: str


@dataclass(frozen=True)
class ReadingExcerpt:
    session_id: str
    title: str
    author: str
    source_relative_path: str
    section: str
    text: str
    at_section_end: bool
    resumed: bool


@dataclass(frozen=True)
class EditionCatalogueReport:
    files_seen: int
    metadata_read: int
    reused: int
    attention: int
    identified_authors: int
    identified_series: int
    exact_duplicate_groups: int
    shared_identifier_groups: int
    possible_same_work_groups: int
    remaining_to_refresh: int


@dataclass(frozen=True)
class EditionReviewGroup:
    evidence: str
    identity: str
    files: tuple[tuple[str, str, int], ...]


@dataclass(frozen=True)
class DuplicateResolutionProposal:
    resolution_id: str
    sha256: str
    keep_relative_path: str
    archive_moves: tuple[tuple[str, str], ...]


class Librarian:
    """Catalogue Intake and create reviewable derivatives without changing originals."""

    MAX_FILES = 5_000
    MAX_REPAIR_BYTES = 2 * 1024 * 1024
    MAX_INDEX_PASSAGES = 10_000
    READING_CHUNK = 1_800
    IDENTITY_FORMATS = {".epub", ".pdf", ".docx", ".txt", ".md", ".html", ".htm"}
    EDITION_REFRESH_BATCH = 25
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

    def inspect_book(self, relative_path: str) -> BookInspection:
        """Read one named Intake file, index its text, and propose a shelf path."""

        source = self._safe_collection_path(self.paths.intake, relative_path)
        if source.is_symlink() or not source.is_file():
            raise LibrarianError("That Intake reading file is unavailable or unsafe.")
        try:
            book = read_book(source)
            digest = self._sha256(source)
        except (OSError, BookReadError) as error:
            raise LibrarianError(str(error)) from error
        shelving_id = f"LS-{secrets.token_hex(4).upper()}"
        proposed = self._proposed_original_path(book, source)
        preview = self._opening_preview(book)
        created = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.catalogue_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            connection = sqlite3.connect(self.catalogue_path)
            with connection:
                self._initialize_reading_schema(connection)
                self._replace_reading_index(connection, digest, f"Intake/{relative_path}", book)
                connection.execute(
                    """
                    INSERT INTO shelving_jobs
                        (shelving_id, source_relative_path, source_sha256, title, author,
                         proposed_relative_path, created_at, status, resolved_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', '')
                    """,
                    (shelving_id, relative_path, digest, book.title, book.author, proposed, created),
                )
        except sqlite3.DatabaseError as error:
            raise LibrarianError("The Librarian could not record that reading safely.") from error
        finally:
            if connection is not None:
                connection.close()
        return BookInspection(
            shelving_id=shelving_id,
            source_relative_path=relative_path,
            source_sha256=digest,
            title=book.title,
            author=book.author,
            format_name=self.SUPPORTED.get(source.suffix.casefold(), source.suffix),
            word_count=book.word_count,
            section_count=len(book.sections),
            proposed_relative_path=proposed,
            preview=preview,
            truncated=book.truncated,
        )

    def search_reading(self, query: str, limit: int = 5) -> tuple[ReadingHit, ...]:
        """Find bounded passages in works the Librarian has actually inspected."""

        terms = re.findall(r"[\w'-]+", query, flags=re.UNICODE)
        if not terms:
            raise LibrarianError("Give the Librarian a meaningful word or phrase to find.")
        expression = " AND ".join(f'"{term.replace(chr(34), chr(34) * 2)}"' for term in terms[:10])
        connection = None
        try:
            connection = sqlite3.connect(self.catalogue_path)
            self._initialize_reading_schema(connection)
            rows = connection.execute(
                """
                SELECT title, author, source_relative_path, section,
                       snippet(reading_passages, 5, '[', ']', ' ... ', 24)
                FROM reading_passages
                WHERE reading_passages MATCH ?
                ORDER BY bm25(reading_passages)
                LIMIT ?
                """,
                (expression, max(1, min(limit, 10))),
            ).fetchall()
        except sqlite3.DatabaseError as error:
            raise LibrarianError("The Librarian could not search her reading catalogue.") from error
        finally:
            if connection is not None:
                connection.close()
        return tuple(ReadingHit(*row) for row in rows)

    def catalogue_editions(self) -> EditionCatalogueReport:
        """Incrementally record source-supplied work and edition identity."""

        files = []
        for label, root in (("Intake", self.paths.intake), ("Originals", self.paths.originals)):
            files.extend(
                (label, root, path)
                for path in root.rglob("*")
                if path.is_file() and path.suffix.casefold() in self.IDENTITY_FORMATS
            )
        files.sort(key=lambda item: f"{item[0]}/{item[2].relative_to(item[1]).as_posix()}".casefold())
        if len(files) > self.MAX_FILES:
            raise LibrarianError(f"The Stacks contains more than {self.MAX_FILES} readable files; use a smaller bounded collection.")
        connection = sqlite3.connect(self.catalogue_path)
        read_count = reused = attention = remaining = 0
        seen = set()
        try:
            self._initialize_schema(connection)
            self._initialize_edition_schema(connection)
            for label, root, path in files:
                relative = f"{label}/{path.relative_to(root).as_posix()}"
                seen.add(relative)
                stat = path.stat()
                cached = connection.execute(
                    "SELECT size_bytes, modified_ns FROM edition_items WHERE source_relative_path=?",
                    (relative,),
                ).fetchone()
                if cached == (stat.st_size, stat.st_mtime_ns):
                    reused += 1
                    continue
                if read_count >= self.EDITION_REFRESH_BATCH:
                    remaining += 1
                    continue
                warning = ""
                try:
                    metadata = read_book_metadata(path)
                    digest = self._cached_intake_digest(connection, label, path, root, stat) or self._sha256(path)
                except (OSError, BookReadError) as error:
                    attention += 1
                    warning = str(error)
                    metadata = None
                    digest = ""
                read_count += 1
                with connection:
                    connection.execute(
                        """
                        INSERT INTO edition_items
                            (source_relative_path, filename, extension, size_bytes, modified_ns,
                             sha256, title, author, identifiers_json, series, series_index,
                             publisher, language, published, warning, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(source_relative_path) DO UPDATE SET
                            filename=excluded.filename, extension=excluded.extension,
                            size_bytes=excluded.size_bytes, modified_ns=excluded.modified_ns,
                            sha256=excluded.sha256, title=excluded.title, author=excluded.author,
                            identifiers_json=excluded.identifiers_json, series=excluded.series,
                            series_index=excluded.series_index, publisher=excluded.publisher,
                            language=excluded.language, published=excluded.published,
                            warning=excluded.warning, updated_at=excluded.updated_at
                        """,
                        (
                            relative, path.name, path.suffix.casefold(), stat.st_size, stat.st_mtime_ns,
                            digest, metadata.title if metadata else "", metadata.author if metadata else "",
                            json.dumps(metadata.identifiers if metadata else ()), metadata.series if metadata else "",
                            metadata.series_index if metadata else "", metadata.publisher if metadata else "",
                            metadata.language if metadata else "", metadata.published if metadata else "", warning,
                            datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        ),
                    )
            stale = [row[0] for row in connection.execute("SELECT source_relative_path FROM edition_items") if row[0] not in seen]
            with connection:
                connection.executemany("DELETE FROM edition_items WHERE source_relative_path=?", [(path,) for path in stale])
            rows = connection.execute(
                "SELECT sha256,title,author,identifiers_json,series,warning FROM edition_items"
            ).fetchall()
        finally:
            connection.close()
        exact = self._group_count(row[0] for row in rows if row[0])
        identifiers = []
        for row in rows:
            for scheme, value in json.loads(row[3] or "[]"):
                if scheme.casefold() not in {"uuid", "identifier"}:
                    identifiers.append(f"{scheme.casefold()}:{self._identity_key(value)}")
        shared_ids = self._group_count(value for value in identifiers if value.partition(":")[2])
        works = [f"{self._identity_key(row[2])}|{self._identity_key(row[1])}" for row in rows if row[1]]
        return EditionCatalogueReport(
            len(files), read_count, reused, attention,
            len({self._identity_key(row[2]) for row in rows if row[2] and row[2] != "Unknown Author"}),
            len({self._identity_key(row[4]) for row in rows if row[4]}),
            exact, shared_ids, self._group_count(works),
            remaining,
        )

    def edition_review_groups(self, limit: int = 20) -> tuple[EditionReviewGroup, ...]:
        """Return bounded relationship groups once, at their strongest evidence level."""

        connection = sqlite3.connect(self.catalogue_path)
        try:
            self._initialize_edition_schema(connection)
            rows = connection.execute(
                """SELECT source_relative_path,sha256,title,author,identifiers_json,
                          extension,size_bytes FROM edition_items ORDER BY source_relative_path COLLATE NOCASE"""
            ).fetchall()
        finally:
            connection.close()
        if not rows:
            raise LibrarianError("The edition catalogue is empty. Ask the Librarian to identify works and editions first.")
        groups: list[EditionReviewGroup] = []
        claimed: set[str] = set()

        exact = {}
        for row in rows:
            if row[1]:
                exact.setdefault(row[1], []).append(row)
        for digest, members in exact.items():
            if len(members) > 1:
                groups.append(self._review_group("Exact SHA-256 duplicate", digest[:16], members))
                claimed.update(row[0] for row in members)

        identifiers = {}
        for row in rows:
            for scheme, value in json.loads(row[4] or "[]"):
                if scheme.casefold() in {"uuid", "identifier"}:
                    continue
                key = (scheme.upper(), self._identity_key(value))
                if key[1]:
                    identifiers.setdefault(key, []).append(row)
        for (scheme, value), members in identifiers.items():
            unique = {row[0]: row for row in members}
            members = list(unique.values())
            if len(members) > 1 and not all(row[0] in claimed for row in members):
                groups.append(self._review_group("Shared strong identifier", f"{scheme} {value}", members))
                claimed.update(row[0] for row in members)

        works = {}
        for row in rows:
            title_key = self._identity_key(row[2])
            author_key = self._identity_key(row[3])
            if title_key in {"", "untitled", "unknown"} or author_key in {"", "unknownauthor"}:
                continue
            works.setdefault((author_key, title_key), []).append(row)
        for _, members in works.items():
            if len(members) > 1 and not all(row[0] in claimed for row in members):
                identity = f"{members[0][2]} — {members[0][3]}"
                groups.append(self._review_group("Possible same work", identity, members))
                claimed.update(row[0] for row in members)
        return tuple(groups[: max(1, min(limit, 50))])

    def prepare_exact_duplicate_resolution(
        self,
        hash_prefix: str,
        keep_relative_path: str,
    ) -> DuplicateResolutionProposal:
        """Prepare one reversible archive plan for a proven exact duplicate group."""

        prefix = hash_prefix.strip().casefold()
        if not re.fullmatch(r"[a-f0-9]{12,64}", prefix):
            raise LibrarianError("Give the Librarian at least 12 hexadecimal characters from the exact group hash.")
        keep = keep_relative_path.strip().replace("\\", "/")
        connection = sqlite3.connect(self.catalogue_path)
        try:
            self._initialize_edition_schema(connection)
            self._initialize_reading_schema(connection)
            self._initialize_duplicate_resolution_schema(connection)
            rows = connection.execute(
                "SELECT source_relative_path,sha256 FROM edition_items WHERE sha256 LIKE ? ORDER BY source_relative_path COLLATE NOCASE",
                (f"{prefix}%",),
            ).fetchall()
            hashes = {row[1] for row in rows}
            if len(hashes) != 1 or len(rows) < 2:
                raise LibrarianError("That hash prefix does not identify one current exact-duplicate group.")
            members = [row[0] for row in rows]
            if keep not in members:
                raise LibrarianError("The chosen keep path is not a member of that exact-duplicate group.")
            digest = rows[0][1]
            moves = []
            for source_relative in members:
                source = self._path_from_stacks_relative(source_relative)
                if not source.is_file() or self._sha256(source) != digest:
                    raise LibrarianError("An exact-duplicate source changed after cataloguing; refresh the edition catalogue.")
                if source_relative == keep:
                    continue
                archive_relative = (Path("Exact Duplicates") / digest[:16] / Path(source_relative)).as_posix()
                destination = self._safe_collection_path(self.paths.archive, archive_relative, require_exists=False)
                if destination.exists():
                    raise LibrarianError("A proposed duplicate archive destination already exists; nothing was prepared.")
                moves.append((source_relative, archive_relative))
            resolution_id = f"DR-{secrets.token_hex(4).upper()}"
            with connection:
                connection.execute(
                    """
                    INSERT INTO duplicate_resolution_jobs
                        (resolution_id,sha256,keep_relative_path,archive_moves_json,
                         created_at,status,resolved_at)
                    VALUES (?, ?, ?, ?, ?, 'pending', '')
                    """,
                    (
                        resolution_id, digest, keep, json.dumps(moves),
                        datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    ),
                )
        finally:
            connection.close()
        return DuplicateResolutionProposal(resolution_id, digest, keep, tuple(moves))

    def approve_exact_duplicate_resolution(self, resolution_id: str) -> tuple[str, tuple[str, ...]]:
        """Archive redundant exact copies after complete preflight, with rollback on failure."""

        clean_id = resolution_id.strip().upper()
        if not re.fullmatch(r"DR-[A-F0-9]{8}", clean_id):
            raise LibrarianError("That duplicate-resolution identifier is invalid.")
        connection = sqlite3.connect(self.catalogue_path)
        moved: list[tuple[Path, Path, str]] = []
        try:
            self._initialize_edition_schema(connection)
            self._initialize_reading_schema(connection)
            self._initialize_duplicate_resolution_schema(connection)
            row = connection.execute(
                """SELECT sha256,keep_relative_path,archive_moves_json,status
                   FROM duplicate_resolution_jobs WHERE resolution_id=?""",
                (clean_id,),
            ).fetchone()
            if row is None or row[3] != "pending":
                raise LibrarianError("That duplicate-resolution proposal is unavailable or already resolved.")
            digest, keep, moves_json, _ = row
            keep_path = self._path_from_stacks_relative(keep)
            if not keep_path.is_file() or self._sha256(keep_path) != digest:
                raise LibrarianError("The selected canonical copy changed after review; prepare a new resolution.")
            prepared = []
            for source_relative, archive_relative in json.loads(moves_json):
                source = self._path_from_stacks_relative(source_relative)
                destination = self._safe_collection_path(self.paths.archive, archive_relative, require_exists=False)
                if not source.is_file() or self._sha256(source) != digest:
                    raise LibrarianError("A redundant copy changed after review; prepare a new resolution.")
                if destination.exists():
                    raise LibrarianError("An archive destination now exists; nothing was moved.")
                prepared.append((source, destination, source_relative))
            try:
                for source, destination, source_relative in prepared:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    source.replace(destination)
                    moved.append((source, destination, source_relative))
            except OSError:
                for source, destination, _ in reversed(moved):
                    if destination.exists() and not source.exists():
                        source.parent.mkdir(parents=True, exist_ok=True)
                        destination.replace(source)
                raise
            with connection:
                connection.executemany(
                    "DELETE FROM edition_items WHERE source_relative_path=?",
                    [(source_relative,) for _, _, source_relative in moved],
                )
                connection.execute(
                    "UPDATE reading_positions SET source_relative_path=? WHERE source_sha256=?",
                    (keep, digest),
                )
                connection.execute(
                    "UPDATE reading_sessions SET source_relative_path=? WHERE source_sha256=?",
                    (keep, digest),
                )
                connection.execute(
                    "UPDATE duplicate_resolution_jobs SET status='archived',resolved_at=? WHERE resolution_id=?",
                    (datetime.now(timezone.utc).isoformat(timespec="seconds"), clean_id),
                )
            return keep, tuple(destination.relative_to(self.paths.root).as_posix() for _, destination, _ in moved)
        except LibrarianError:
            raise
        except (OSError, sqlite3.DatabaseError) as error:
            raise LibrarianError("The Librarian could not complete that duplicate resolution safely.") from error
        finally:
            connection.close()

    @staticmethod
    def duplicate_resolution_response(proposal: DuplicateResolutionProposal) -> str:
        moves = "\n".join(
            f"- The Stacks/{source} -> The Stacks/Archive/{destination}"
            for source, destination in proposal.archive_moves
        )
        return (
            "The Librarian prepared one reversible exact-duplicate resolution.\n\n"
            f"Resolution: {proposal.resolution_id}\n"
            f"Proven SHA-256: {proposal.sha256}\n"
            f"Canonical copy staying in place: The Stacks/{proposal.keep_relative_path}\n"
            f"Redundant copies proposed for Archive:\n{moves}\n\n"
            "Nothing has moved and nothing will be deleted. To approve this exact plan, say: "
            f"Approve Librarian duplicate resolution: {proposal.resolution_id}"
        )

    @staticmethod
    def edition_review_response(groups: tuple[EditionReviewGroup, ...]) -> str:
        if not groups:
            return "The Librarian found no reviewable edition relationship groups. No file was changed."
        rendered = []
        for index, group in enumerate(groups, 1):
            files = "\n".join(
                f"- The Stacks/{path} [{extension or 'file'}, {size:,} bytes]"
                for path, extension, size in group.files
            )
            rendered.append(f"{index}. {group.evidence}: {group.identity}\n{files}")
        return (
            f"The Librarian found {len(groups)} bounded edition relationship group(s):\n\n"
            + "\n\n".join(rendered)
            + "\n\nNo preferred edition was selected and no file was renamed, moved, merged, deleted, or overwritten. "
              "Generic unknown-author or untitled metadata was excluded from possible-work matching."
        )

    @staticmethod
    def _review_group(evidence: str, identity: str, members) -> EditionReviewGroup:
        return EditionReviewGroup(
            evidence,
            identity,
            tuple((row[0], row[5], int(row[6])) for row in members),
        )

    @staticmethod
    def edition_catalogue_response(report: EditionCatalogueReport) -> str:
        return (
            "The Librarian completed an incremental work-and-edition catalogue.\n\n"
            f"Readable files seen: {report.files_seen}\n"
            f"Metadata newly read or refreshed: {report.metadata_read}\n"
            f"Unchanged catalogue entries reused: {report.reused}\n"
            f"Items needing attention: {report.attention}\n"
            f"Named authors represented: {report.identified_authors}\n"
            f"Named series represented: {report.identified_series}\n"
            f"Exact duplicate groups: {report.exact_duplicate_groups}\n"
            f"Shared strong-identifier groups: {report.shared_identifier_groups}\n"
            f"Possible same-work title/author groups: {report.possible_same_work_groups}\n\n"
            f"Files still awaiting metadata refresh: {report.remaining_to_refresh}\n\n"
            "No file was renamed, moved, merged, deleted, converted, or overwritten. "
            "Exact hashes prove identical bytes; shared identifiers and similar title/author records are review leads, not permission to consolidate."
        )

    def approve_shelving(self, shelving_id: str) -> Path:
        """Move one unchanged Intake original to its reviewed Originals shelf."""

        clean_id = shelving_id.strip().upper()
        if not re.fullmatch(r"LS-[A-F0-9]{8}", clean_id):
            raise LibrarianError("That shelving identifier is invalid.")
        connection = None
        try:
            connection = sqlite3.connect(self.catalogue_path)
            self._initialize_reading_schema(connection)
            row = connection.execute(
                """SELECT source_relative_path, source_sha256, proposed_relative_path, status
                   FROM shelving_jobs WHERE shelving_id = ?""",
                (clean_id,),
            ).fetchone()
            if row is None or row[3] != "pending":
                raise LibrarianError("That shelving proposal is unavailable or already resolved.")
            source = self._safe_collection_path(self.paths.intake, row[0])
            destination = self._safe_collection_path(self.paths.originals, row[2], require_exists=False)
            if not source.is_file() or self._sha256(source) != row[1]:
                raise LibrarianError("The Intake original changed after inspection; inspect it again.")
            if destination.exists():
                raise LibrarianError("The proposed shelf destination already exists; nothing was moved.")
            destination.parent.mkdir(parents=True, exist_ok=True)
            source.replace(destination)
            if self._sha256(destination) != row[1]:
                raise LibrarianError("The shelved original did not retain its recorded identity.")
            with connection:
                connection.execute(
                    "UPDATE shelving_jobs SET status='shelved', resolved_at=? WHERE shelving_id=?",
                    (datetime.now(timezone.utc).isoformat(timespec="seconds"), clean_id),
                )
                connection.execute(
                    "UPDATE reading_passages SET source_relative_path=? WHERE source_sha256=?",
                    (f"Originals/{row[2]}", row[1]),
                )
            return destination
        except LibrarianError:
            raise
        except (OSError, sqlite3.DatabaseError) as error:
            raise LibrarianError("The Librarian could not complete that approved shelving safely.") from error
        finally:
            if connection is not None:
                connection.close()

    def open_reading(self, reference: str, chapter: str = "", resume: bool = False) -> ReadingExcerpt:
        """Open a bounded excerpt and create a pending, explicitly confirmable position."""

        source, source_relative = self._resolve_reading_source(reference)
        try:
            digest = self._sha256(source)
            book = read_book(source)
        except (OSError, BookReadError) as error:
            raise LibrarianError(str(error)) from error
        section_index = 0
        offset = 0
        resumed = False
        connection = sqlite3.connect(self.catalogue_path)
        try:
            self._initialize_reading_schema(connection)
            with connection:
                self._replace_reading_index(connection, digest, source_relative, book)
            if chapter:
                wanted = self._normalize_chapter(chapter)
                matches = [index for index, (label, _) in enumerate(book.sections) if self._normalize_chapter(label) == wanted]
                if not matches:
                    raise LibrarianError(f"The Librarian could not find {chapter.strip()} in {book.title}.")
                section_index = matches[0]
            elif resume:
                row = connection.execute(
                    "SELECT section_index, character_offset FROM reading_positions WHERE source_sha256 = ?",
                    (digest,),
                ).fetchone()
                if row is None:
                    raise LibrarianError("No confirmed reading position exists for that exact edition.")
                section_index, offset = int(row[0]), int(row[1])
                resumed = True
            section_index, offset = self._valid_position(book, section_index, offset)
            if offset >= len(book.sections[section_index][1]) and section_index + 1 < len(book.sections):
                section_index += 1
                offset = 0
            excerpt, displayed_until = self._reading_chunk(book.sections[section_index][1], offset)
            session_id = f"RP-{secrets.token_hex(4).upper()}"
            with connection:
                connection.execute(
                    """
                    INSERT INTO reading_sessions
                        (session_id, source_sha256, source_relative_path, title, section_index,
                         displayed_from, displayed_until, created_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
                    """,
                    (
                        session_id, digest, source_relative, book.title, section_index,
                        offset, displayed_until, datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    ),
                )
        finally:
            connection.close()
        return ReadingExcerpt(
            session_id, book.title, book.author, source_relative,
            book.sections[section_index][0], excerpt,
            displayed_until >= len(book.sections[section_index][1]), resumed,
        )

    def continue_reading(self, session_id: str) -> ReadingExcerpt:
        """Display the next excerpt without silently advancing confirmed progress."""

        clean_id = self._clean_position_id(session_id)
        connection = sqlite3.connect(self.catalogue_path)
        try:
            self._initialize_reading_schema(connection)
            row = connection.execute(
                """SELECT source_sha256, source_relative_path, section_index, displayed_until, status
                   FROM reading_sessions WHERE session_id = ?""",
                (clean_id,),
            ).fetchone()
            if row is None or row[4] != "pending":
                raise LibrarianError("That reading session is unavailable or already closed.")
            source = self._path_from_stacks_relative(row[1])
            if not source.is_file() or self._sha256(source) != row[0]:
                raise LibrarianError("That exact reading edition changed or moved; open it again.")
            book = read_book(source)
            section_index, offset = self._valid_position(book, int(row[2]), int(row[3]))
            if offset >= len(book.sections[section_index][1]) and section_index + 1 < len(book.sections):
                section_index += 1
                offset = 0
            excerpt, displayed_until = self._reading_chunk(book.sections[section_index][1], offset)
            with connection:
                connection.execute(
                    "UPDATE reading_sessions SET section_index=?, displayed_from=?, displayed_until=? WHERE session_id=?",
                    (section_index, offset, displayed_until, clean_id),
                )
        except (OSError, BookReadError) as error:
            raise LibrarianError(str(error)) from error
        finally:
            connection.close()
        return ReadingExcerpt(
            clean_id, book.title, book.author, row[1], book.sections[section_index][0],
            excerpt, displayed_until >= len(book.sections[section_index][1]), False,
        )

    def mark_reading_position(self, session_id: str) -> tuple[str, str]:
        """Confirm that the displayed endpoint is the next unread position."""

        clean_id = self._clean_position_id(session_id)
        connection = sqlite3.connect(self.catalogue_path)
        try:
            self._initialize_reading_schema(connection)
            row = connection.execute(
                """SELECT source_sha256, source_relative_path, title, section_index,
                          displayed_until, status
                   FROM reading_sessions WHERE session_id = ?""",
                (clean_id,),
            ).fetchone()
            if row is None or row[5] != "pending":
                raise LibrarianError("That reading session is unavailable or already closed.")
            timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
            with connection:
                connection.execute(
                    """
                    INSERT INTO reading_positions
                        (source_sha256, source_relative_path, title, section_index,
                         character_offset, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(source_sha256) DO UPDATE SET
                        source_relative_path=excluded.source_relative_path,
                        title=excluded.title,
                        section_index=excluded.section_index,
                        character_offset=excluded.character_offset,
                        updated_at=excluded.updated_at
                    """,
                    (row[0], row[1], row[2], int(row[3]), int(row[4]), timestamp),
                )
                connection.execute("UPDATE reading_sessions SET status='marked' WHERE session_id=?", (clean_id,))
            source = self._path_from_stacks_relative(row[1])
            book = read_book(source)
            section_index, _ = self._valid_position(book, int(row[3]), int(row[4]))
            return row[2], book.sections[section_index][0]
        except (OSError, BookReadError) as error:
            raise LibrarianError(str(error)) from error
        finally:
            connection.close()

    @staticmethod
    def reading_response(excerpt: ReadingExcerpt) -> str:
        introduction = "The Librarian resumed" if excerpt.resumed else "The Librarian opened"
        ending = "End of this chapter." if excerpt.at_section_end else "More remains in this chapter."
        return (
            f"{introduction} {excerpt.title} — {excerpt.author}\n"
            f"{excerpt.section}\nSource: The Stacks/{excerpt.source_relative_path}\n\n"
            f"{excerpt.text}\n\n{ending}\n"
            f"To continue without changing your saved place, say: Continue reading: {excerpt.session_id}\n"
            f"To confirm the end of this displayed passage as your next unread position, say: "
            f"Mark my place: {excerpt.session_id}"
        )

    @staticmethod
    def inspection_report(inspection: BookInspection) -> str:
        extent = " (bounded extraction; more text remains)" if inspection.truncated else ""
        return (
            f"The Librarian read and catalogued one Intake work.\n\n"
            f"Title: {inspection.title}\nAuthor: {inspection.author}\n"
            f"Format: {inspection.format_name}\n"
            f"Readable extent: {inspection.word_count:,} words in {inspection.section_count} sections{extent}\n"
            f"Source: The Stacks/Intake/{inspection.source_relative_path}\n"
            f"SHA-256: {inspection.source_sha256}\n\n"
            f"Opening text:\n{inspection.preview}\n\n"
            f"Proposed shelf: The Stacks/Originals/{inspection.proposed_relative_path}\n"
            f"Shelving proposal: {inspection.shelving_id}\n\n"
            f"Nothing has moved. To approve this exact destination, say: "
            f"Approve Librarian shelving: {inspection.shelving_id}"
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
    def _safe_collection_path(root: Path, relative_path: str, require_exists: bool = True) -> Path:
        raw = relative_path.strip().replace("\\", "/")
        candidate = Path(raw)
        if not raw or candidate.is_absolute() or ".." in candidate.parts:
            raise LibrarianError("That reading path is unsafe.")
        path = (root / candidate).resolve()
        try:
            path.relative_to(root.resolve())
        except ValueError as error:
            raise LibrarianError("That reading path is unsafe.") from error
        if require_exists and not path.exists():
            raise LibrarianError("That reading file was not found.")
        return path

    @classmethod
    def _proposed_original_path(cls, book: BookText, source: Path) -> str:
        author = cls._safe_shelf_name(book.author, "Unknown Author")
        title = cls._safe_shelf_name(book.title, source.stem)
        return (Path(author) / title / source.name).as_posix()

    @staticmethod
    def _safe_shelf_name(value: str, fallback: str) -> str:
        cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", value)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
        return (cleaned or fallback)[:120]

    def _resolve_reading_source(self, reference: str) -> tuple[Path, str]:
        raw = reference.strip().replace("\\", "/")
        if not raw:
            raise LibrarianError("Name one work for the Librarian to open.")
        for prefix, root in (("Intake/", self.paths.intake), ("Originals/", self.paths.originals)):
            if raw.casefold().startswith(prefix.casefold()):
                relative = raw[len(prefix):]
                path = self._safe_collection_path(root, relative)
                return path, f"{prefix}{Path(relative).as_posix()}"
        direct_intake = self.paths.intake / Path(raw)
        if direct_intake.is_file():
            path = self._safe_collection_path(self.paths.intake, raw)
            return path, f"Intake/{Path(raw).as_posix()}"
        connection = sqlite3.connect(self.catalogue_path)
        try:
            self._initialize_reading_schema(connection)
            rows = connection.execute(
                """SELECT title, status, source_relative_path, proposed_relative_path
                   FROM shelving_jobs
                   WHERE title = ? COLLATE NOCASE OR source_relative_path = ? COLLATE NOCASE
                   ORDER BY created_at DESC""",
                (raw, raw),
            ).fetchall()
        finally:
            connection.close()
        candidates = []
        for _, status, intake_relative, proposed in rows:
            relative = f"Originals/{proposed}" if status == "shelved" else f"Intake/{intake_relative}"
            try:
                path = self._path_from_stacks_relative(relative)
            except LibrarianError:
                continue
            if path.is_file() and all(existing[0] != path for existing in candidates):
                candidates.append((path, relative))
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            raise LibrarianError("That title identifies more than one edition; use its exact Stacks path.")
        raise LibrarianError("The Librarian could not identify that work. Examine it first or use its exact Stacks path.")

    def _path_from_stacks_relative(self, relative: str) -> Path:
        raw = relative.replace("\\", "/")
        if raw.casefold().startswith("intake/"):
            return self._safe_collection_path(self.paths.intake, raw[7:])
        if raw.casefold().startswith("originals/"):
            return self._safe_collection_path(self.paths.originals, raw[10:])
        raise LibrarianError("That saved reading path is unsafe.")

    @staticmethod
    def _normalize_chapter(label: str) -> str:
        value = re.sub(r"\s+", " ", label.strip().casefold())
        if re.fullmatch(r"\d+", value):
            return f"chapter {int(value)}"
        if value.startswith("chapter "):
            number = value[8:].split(" ", 1)[0].rstrip(":-–—")
            return f"chapter {int(number)}" if number.isdigit() else f"chapter {number}"
        return value

    @staticmethod
    def _valid_position(book: BookText, section_index: int, offset: int) -> tuple[int, int]:
        if not 0 <= section_index < len(book.sections):
            raise LibrarianError("The saved chapter no longer exists in that edition.")
        return section_index, max(0, min(offset, len(book.sections[section_index][1])))

    @classmethod
    def _reading_chunk(cls, text: str, offset: int) -> tuple[str, int]:
        if offset >= len(text):
            return "[End of chapter]", len(text)
        target = min(len(text), offset + cls.READING_CHUNK)
        if target < len(text):
            boundary = text.rfind("\n\n", offset + cls.READING_CHUNK // 2, target)
            if boundary > offset:
                target = boundary
        return text[offset:target].strip(), target

    @staticmethod
    def _clean_position_id(session_id: str) -> str:
        clean = session_id.strip().upper()
        if not re.fullmatch(r"RP-[A-F0-9]{8}", clean):
            raise LibrarianError("That reading-session identifier is invalid.")
        return clean

    @staticmethod
    def _cached_intake_digest(
        connection: sqlite3.Connection,
        label: str,
        path: Path,
        root: Path,
        stat,
    ) -> str:
        if label != "Intake":
            return ""
        relative = path.relative_to(root).as_posix()
        row = connection.execute(
            "SELECT sha256,size_bytes,modified_ns FROM reading_items WHERE relative_path=?",
            (relative,),
        ).fetchone()
        if row and row[0] and row[1] == stat.st_size and row[2] == stat.st_mtime_ns:
            return row[0]
        return ""

    @staticmethod
    def _identity_key(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", value.casefold())

    @staticmethod
    def _group_count(values) -> int:
        counts = {}
        for value in values:
            counts[value] = counts.get(value, 0) + 1
        return sum(1 for count in counts.values() if count > 1)

    @staticmethod
    def _opening_preview(book: BookText, limit: int = 900) -> str:
        text = next((text for _, text in book.sections if text.strip()), "")
        preview = text[:limit].strip()
        return preview + (" ..." if len(text) > limit else "")

    @staticmethod
    def _passages(book: BookText, size: int = 1600) -> list[tuple[str, str]]:
        passages = []
        for section, text in book.sections:
            paragraphs = [part.strip() for part in re.split(r"\n{2,}", text) if part.strip()]
            current = ""
            for paragraph in paragraphs:
                if current and len(current) + len(paragraph) + 2 > size:
                    passages.append((section, current))
                    current = ""
                if len(paragraph) > size:
                    if current:
                        passages.append((section, current))
                        current = ""
                    passages.extend((section, paragraph[index:index + size]) for index in range(0, len(paragraph), size))
                else:
                    current = f"{current}\n\n{paragraph}".strip()
            if current:
                passages.append((section, current))
        return passages

    def _replace_reading_index(
        self,
        connection: sqlite3.Connection,
        digest: str,
        source_relative: str,
        book: BookText,
    ):
        connection.execute("DELETE FROM reading_passages WHERE source_sha256 = ?", (digest,))
        passages = self._passages(book)[: self.MAX_INDEX_PASSAGES]
        connection.executemany(
            """
            INSERT INTO reading_passages
                (source_sha256, source_relative_path, title, author, section, passage)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (digest, source_relative, book.title, book.author, section, passage)
                for section, passage in passages
            ],
        )

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
    def _initialize_reading_schema(connection: sqlite3.Connection):
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS shelving_jobs (
                shelving_id TEXT PRIMARY KEY,
                source_relative_path TEXT NOT NULL,
                source_sha256 TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                proposed_relative_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL,
                resolved_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reading_sessions (
                session_id TEXT PRIMARY KEY,
                source_sha256 TEXT NOT NULL,
                source_relative_path TEXT NOT NULL,
                title TEXT NOT NULL,
                section_index INTEGER NOT NULL,
                displayed_from INTEGER NOT NULL,
                displayed_until INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reading_positions (
                source_sha256 TEXT PRIMARY KEY,
                source_relative_path TEXT NOT NULL,
                title TEXT NOT NULL,
                section_index INTEGER NOT NULL,
                character_offset INTEGER NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS reading_passages USING fts5(
                source_sha256 UNINDEXED,
                source_relative_path UNINDEXED,
                title,
                author,
                section,
                passage
            )
            """
        )

    @staticmethod
    def _initialize_edition_schema(connection: sqlite3.Connection):
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS edition_items (
                source_relative_path TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                extension TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                modified_ns INTEGER NOT NULL,
                sha256 TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                identifiers_json TEXT NOT NULL,
                series TEXT NOT NULL,
                series_index TEXT NOT NULL,
                publisher TEXT NOT NULL,
                language TEXT NOT NULL,
                published TEXT NOT NULL,
                warning TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

    @staticmethod
    def _initialize_duplicate_resolution_schema(connection: sqlite3.Connection):
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS duplicate_resolution_jobs (
                resolution_id TEXT PRIMARY KEY,
                sha256 TEXT NOT NULL,
                keep_relative_path TEXT NOT NULL,
                archive_moves_json TEXT NOT NULL,
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
