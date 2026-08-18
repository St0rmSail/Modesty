"""Create The Stacks without touching reading material already present."""

from dataclasses import dataclass
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "Config" / "reading_collection.json"
DEFAULT_CATALOGUE = PROJECT_ROOT / "Data" / "librarian_catalog.db"


class ReadingCollectionError(RuntimeError):
    """Raised when The Stacks configuration is unsafe or unavailable."""


@dataclass(frozen=True)
class StacksPaths:
    root: Path
    intake: Path
    originals: Path
    workbench: Path
    reading: Path
    archive: Path


class ReadingCollection:
    """Initialize a private collection while preserving every existing file."""

    DIRECTORIES = ("Intake", "Originals", "Workbench", "Reading", "Archive")

    def __init__(
        self,
        config_path: Path = DEFAULT_CONFIG,
        project_root: Path = PROJECT_ROOT,
    ):
        self.config_path = Path(config_path)
        self.project_root = Path(project_root).resolve()
        self.root = self._load_root()
        self._validate_root()

    def _load_root(self) -> Path:
        try:
            settings = json.loads(self.config_path.read_text(encoding="utf-8"))
            return Path(settings["stacks"]["path"]).resolve()
        except FileNotFoundError as error:
            raise ReadingCollectionError(
                f"Reading-collection configuration is missing: {self.config_path}"
            ) from error
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            raise ReadingCollectionError(
                f"Reading-collection configuration is invalid: {self.config_path}"
            ) from error

    def _validate_root(self):
        if not self.root.is_absolute() or self.root == Path(self.root.anchor):
            raise ReadingCollectionError("The Stacks must use a safe absolute folder path.")
        try:
            self.root.relative_to(self.project_root)
        except ValueError:
            return
        raise ReadingCollectionError("The Stacks must live outside the public Modesty repository.")

    def initialize(self) -> StacksPaths:
        """Create only missing collection foundations and never replace a file."""
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            for directory in self.DIRECTORIES:
                (self.root / directory).mkdir(exist_ok=True)
            index = self.root / "index.md"
            if not index.exists():
                index.write_text(STACKS_INDEX, encoding="utf-8", newline="\n")
        except OSError as error:
            raise ReadingCollectionError(
                f"Modesty could not initialize The Stacks: {error}"
            ) from error
        return StacksPaths(
            root=self.root,
            intake=self.root / "Intake",
            originals=self.root / "Originals",
            workbench=self.root / "Workbench",
            reading=self.root / "Reading",
            archive=self.root / "Archive",
        )


STACKS_INDEX = """# The Stacks

The Stacks is Drew's private reading collection, maintained through Modesty by
the Librarian. It is separate from the Filing Cabinet and Bookshelf.

- `Intake/` - copied sample material awaiting read-only inventory
- `Originals/` - preserved source editions; never overwritten
- `Workbench/` - approved repair and comparison work
- `Reading/` - approved reading editions and continuity
- `Archive/` - retained superseded derivatives and records

Initial inventory changes no reading file. Repair, conversion, rename, move,
deletion, and publication require later explicit duties and review boundaries.
"""
