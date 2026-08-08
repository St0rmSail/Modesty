"""The Archivist's read-only knowledge inventory."""

from dataclasses import dataclass
import hashlib
from pathlib import Path

from Runtime.Knowledge.catalog import CatalogEntry, KnowledgeCatalog
from Runtime.Knowledge.stores import StorePaths


@dataclass(frozen=True)
class ArchivistReport:
    documents: int
    warnings: int
    removed: int


class Archivist:
    """Observe the two stores and report their catalogue health."""

    RESERVED_BOOKSHELF_FILES = {"index.md", "log.md"}
    IGNORED_DIRECTORIES = {".obsidian", "_Templates"}

    def __init__(self, paths: StorePaths, catalog: KnowledgeCatalog | None = None):
        self.paths = paths
        self.catalog = catalog or KnowledgeCatalog()

    def inventory(self) -> ArchivistReport:
        filing = self._scan("filing_cabinet", self.paths.filing_cabinet)
        bookshelf = self._scan("bookshelf", self.paths.bookshelf)
        removed = self.catalog.replace_store("filing_cabinet", filing)
        removed += self.catalog.replace_store("bookshelf", bookshelf)
        entries = filing + bookshelf
        return ArchivistReport(
            documents=len(entries),
            warnings=sum(entry.validation_status == "warning" for entry in entries),
            removed=removed,
        )

    def _scan(self, store: str, root: Path) -> list[CatalogEntry]:
        entries = []
        for path in sorted(root.rglob("*.md")):
            relative = path.relative_to(root)
            if any(part in self.IGNORED_DIRECTORIES for part in relative.parts):
                continue
            data = path.read_bytes()
            text = data.decode("utf-8-sig", errors="replace")
            metadata, metadata_error = self._frontmatter(text)
            title = metadata.get("title") or self._heading(text) or path.stem
            document_type = metadata.get("type")
            status, message = "ok", ""
            if store == "bookshelf" and relative.as_posix() not in self.RESERVED_BOOKSHELF_FILES:
                if metadata_error:
                    status, message = "warning", metadata_error
                elif not document_type:
                    status, message = "warning", "Bookshelf document has no type metadata"
            stat = path.stat()
            entries.append(
                CatalogEntry(
                    store=store,
                    relative_path=relative.as_posix(),
                    sha256=hashlib.sha256(data).hexdigest(),
                    size_bytes=len(data),
                    modified_ns=stat.st_mtime_ns,
                    title=str(title),
                    document_type=str(document_type) if document_type else None,
                    validation_status=status,
                    validation_message=message,
                )
            )
        return entries

    @staticmethod
    def _frontmatter(text: str) -> tuple[dict[str, str], str | None]:
        lines = text.splitlines()
        if not lines or lines[0].strip() != "---":
            return {}, "Bookshelf document has no OKF frontmatter"
        try:
            end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
        except StopIteration:
            return {}, "Bookshelf frontmatter is not closed"
        metadata = {}
        for line in lines[1:end]:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or ":" not in stripped:
                continue
            key, value = stripped.split(":", 1)
            if key.strip() and value.strip():
                metadata[key.strip()] = value.strip().strip('"\'')
        return metadata, None

    @staticmethod
    def _heading(text: str) -> str | None:
        for line in text.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return None
