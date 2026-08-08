"""The Archivist's read-only knowledge inventory."""

from dataclasses import dataclass
from datetime import datetime
import hashlib
from pathlib import Path
import re

from Runtime.Knowledge.catalog import CatalogEntry, KnowledgeCatalog
from Runtime.Knowledge.stores import StorePaths


@dataclass(frozen=True)
class ArchivistReport:
    documents: int
    warnings: int
    removed: int


@dataclass(frozen=True)
class RetrievedDocument:
    store: str
    relative_path: str
    title: str
    excerpt: str


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

    def file_note(self, store: str, content: str) -> Path:
        """Create a new Inbox note without overwriting existing material."""

        content = content.strip()
        if not content:
            raise ValueError("There is nothing to file.")
        roots = {
            "filing_cabinet": self.paths.filing_cabinet,
            "bookshelf": self.paths.bookshelf,
        }
        if store not in roots:
            raise ValueError("Choose the private Filing Cabinet or shared Bookshelf.")

        title = self._first_line_title(content)
        slug = re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-").lower()[:60] or "note"
        inbox = roots[store] / "Inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        path = self._unused_path(inbox, f"{datetime.now():%Y-%m-%d}-{slug}")
        if store == "bookshelf":
            document = (
                "---\n"
                "type: Note\n"
                f"title: {title}\n"
                "created_by: human:drew\n"
                "verified: unverified\n"
                "provenance: filed-through-modesty\n"
                "---\n\n"
                f"# {title}\n\n{content}\n"
            )
        else:
            document = f"# {title}\n\n{content}\n\n_Source: filed by Drew through Modesty._\n"
        path.write_text(document, encoding="utf-8", newline="\n")
        self.inventory()
        return path

    def retrieve(self, query: str, limit: int = 5) -> list[RetrievedDocument]:
        """Return small local excerpts matching every useful query term."""

        terms = [term.casefold() for term in re.findall(r"[\w'-]+", query) if len(term) > 1]
        if not terms:
            raise ValueError("Tell me what the Archivist should retrieve.")
        self.inventory()
        roots = {
            "filing_cabinet": self.paths.filing_cabinet,
            "bookshelf": self.paths.bookshelf,
        }
        matches = []
        for entry in self.catalog.entries():
            path = roots[entry.store] / Path(entry.relative_path)
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            haystack = f"{entry.title}\n{entry.relative_path}\n{text}".casefold()
            if all(term in haystack for term in terms):
                matches.append(
                    RetrievedDocument(
                        store=entry.store,
                        relative_path=entry.relative_path,
                        title=entry.title,
                        excerpt=self._excerpt(text, terms),
                    )
                )
            if len(matches) >= limit:
                break
        return matches

    @staticmethod
    def _first_line_title(content: str) -> str:
        first = content.splitlines()[0].strip().lstrip("#").strip()
        return first[:100] or "New note"

    @staticmethod
    def _unused_path(inbox: Path, stem: str) -> Path:
        candidate = inbox / f"{stem}.md"
        suffix = 2
        while candidate.exists():
            candidate = inbox / f"{stem}-{suffix}.md"
            suffix += 1
        return candidate

    @staticmethod
    def _excerpt(text: str, terms: list[str], length: int = 280) -> str:
        plain = " ".join(
            line.strip() for line in text.splitlines()
            if line.strip() and line.strip() != "---" and not line.lstrip().startswith(("type:", "title:", "created_by:", "verified:", "provenance:"))
        )
        folded = plain.casefold()
        positions = [folded.find(term) for term in terms if folded.find(term) >= 0]
        start = max(0, (min(positions) if positions else 0) - 60)
        excerpt = plain[start:start + length].strip()
        return ("..." if start else "") + excerpt + ("..." if start + length < len(plain) else "")

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
