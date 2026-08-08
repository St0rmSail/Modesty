"""Create and validate Modesty's Filing Cabinet and Bookshelf."""

from dataclasses import dataclass
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "Config" / "knowledge_stores.json"


class KnowledgeStoreError(RuntimeError):
    """Raised when a configured knowledge store is unsafe or unavailable."""


@dataclass(frozen=True)
class StorePaths:
    filing_cabinet: Path
    bookshelf: Path


class KnowledgeStores:
    """Initialize the two local stores without overwriting existing material."""

    FILING_DIRECTORIES = (
        ".obsidian",
        "Inbox",
        "Personal",
        "Conversations",
        "Projects",
        "Decisions",
        "Archive",
    )
    BOOKSHELF_DIRECTORIES = (
        "Inbox",
        "Workbench",
        "Projects",
        "Research",
        "Reference",
        "Procedures",
        "Media",
        "Archive",
        "_Templates",
    )

    def __init__(
        self,
        config_path: Path = DEFAULT_CONFIG,
        project_root: Path = PROJECT_ROOT,
    ):
        self.config_path = Path(config_path)
        self.project_root = Path(project_root).resolve()
        self.paths = self._load_paths()
        self._validate_paths()

    def _load_paths(self) -> StorePaths:
        try:
            settings = json.loads(self.config_path.read_text(encoding="utf-8"))
            filing = Path(settings["filing_cabinet"]["path"])
            bookshelf = Path(settings["bookshelf"]["path"])
        except FileNotFoundError as error:
            raise KnowledgeStoreError(
                f"Knowledge-store configuration is missing: {self.config_path}"
            ) from error
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            raise KnowledgeStoreError(
                f"Knowledge-store configuration is invalid: {self.config_path}"
            ) from error

        return StorePaths(filing.resolve(), bookshelf.resolve())

    def _validate_paths(self):
        filing = self.paths.filing_cabinet
        bookshelf = self.paths.bookshelf

        for name, path in (("Filing Cabinet", filing), ("Bookshelf", bookshelf)):
            if not path.is_absolute() or path == Path(path.anchor):
                raise KnowledgeStoreError(f"{name} must use a safe absolute folder path.")
            if self._contains(self.project_root, path):
                raise KnowledgeStoreError(
                    f"{name} must live outside the public Modesty repository."
                )

        if filing == bookshelf:
            raise KnowledgeStoreError(
                "The Filing Cabinet and Bookshelf must be separate folders."
            )
        if self._contains(filing, bookshelf) or self._contains(bookshelf, filing):
            raise KnowledgeStoreError(
                "Neither knowledge store may be placed inside the other."
            )

    @staticmethod
    def _contains(parent: Path, child: Path) -> bool:
        try:
            child.relative_to(parent)
            return True
        except ValueError:
            return False

    def initialize(self) -> StorePaths:
        """Create missing foundations and preserve every existing file."""

        try:
            self._make_directories(
                self.paths.filing_cabinet,
                self.FILING_DIRECTORIES,
            )
            self._make_directories(
                self.paths.bookshelf,
                self.BOOKSHELF_DIRECTORIES,
            )
            self._write_new(
                self.paths.filing_cabinet / "index.md",
                FILING_INDEX,
            )
            self._write_new(
                self.paths.bookshelf / "index.md",
                BOOKSHELF_INDEX,
            )
            self._write_new(
                self.paths.bookshelf / "log.md",
                BOOKSHELF_LOG,
            )
            self._write_new(
                self.paths.bookshelf / "_Templates" / "concept.md",
                BOOKSHELF_CONCEPT_TEMPLATE,
            )
        except OSError as error:
            raise KnowledgeStoreError(
                f"Modesty could not initialize her knowledge stores: {error}"
            ) from error

        return self.paths

    @staticmethod
    def _make_directories(root: Path, directories: tuple[str, ...]):
        root.mkdir(parents=True, exist_ok=True)
        for directory in directories:
            (root / directory).mkdir(exist_ok=True)

    @staticmethod
    def _write_new(path: Path, content: str):
        if path.exists():
            return
        path.write_text(content, encoding="utf-8", newline="\n")


FILING_INDEX = """# Modesty's Filing Cabinet

This is Modesty's private local memory and working-record vault.

Nothing in this vault may be supplied to an online agent. Moving or copying
material from here to the Bookshelf requires Drew's explicit approval.

## Drawers

- [[Inbox]] - new private material awaiting filing
- [[Personal]] - personal knowledge and preferences
- [[Conversations]] - durable conversation notes and summaries
- [[Projects]] - private working material
- [[Decisions]] - personal and project decisions
- [[Archive]] - retained material no longer in active use
"""


BOOKSHELF_INDEX = """# Modesty's Bookshelf

This is Modesty's living, curated local collection of shared knowledge and
resources. It contains more than books and is designed to grow through useful,
sourced contributions.

The Bookshelf remains local. Online agents may borrow bounded packets only when
the Grand Library is explicitly online; they never receive filesystem access.

## Collection

- [Inbox](Inbox/) - newly created or returned material
- [Workbench](Workbench/) - material being checked and integrated
- [Projects](Projects/) - shared project knowledge
- [Research](Research/) - sourced findings
- [Reference](Reference/) - stable reference material
- [Procedures](Procedures/) - reusable methods and instructions
- [Media](Media/) - images, maps, datasets, and other resources
- [Archive](Archive/) - superseded or retired material
"""


BOOKSHELF_LOG = """# Bookshelf Log

## 2026-08-08

- Bookshelf initialized for Build 0.9.0.
"""


BOOKSHELF_CONCEPT_TEMPLATE = """---
type: Reference
title: Replace with a clear title
description: Replace with a one-sentence description.
tags: []
modesty_trust: normal
created_by: human:drew
verified: unverified
---

# Replace with a clear title

Write one focused unit of useful knowledge here.

## Sources

- Add the source or provenance for this knowledge.
"""
