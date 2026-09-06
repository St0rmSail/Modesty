"""Fail-closed, read-only inspection of The Angler save containers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


ADF_MAGIC = bytes.fromhex("01 01 00 00 00 20 46 44 41")
KNOWN_FILES = {"player_save_data", "player_settings", "online_cache", "metadata", "steam_autocloud.vdf"}


@dataclass(frozen=True)
class SaveContainer:
    relative_path: str
    size: int
    sha256: str
    format: str


@dataclass(frozen=True)
class AnglerInspection:
    account_found: bool
    containers: tuple[SaveContainer, ...]
    duplicate_snapshots: int
    status: str


@dataclass(frozen=True)
class AnglerObservationDiff:
    baseline_utc: str
    changed: tuple[str, ...]
    added: tuple[str, ...]
    removed: tuple[str, ...]
    structural: tuple["StructuralChange", ...] = ()


@dataclass(frozen=True)
class StructuralChange:
    relative_path: str
    changed_blocks: int
    total_blocks: int
    byte_ranges: tuple[str, ...]


class AnglerSaveInspector:
    MAX_FILES = 64
    MAX_FILE_BYTES = 4 * 1024 * 1024

    def __init__(self, saves_root: Path | None = None):
        self.saves_root = Path(
            saves_root
            or Path.home() / "Saved Games" / "Avalanche Studios" / "CotWTheAngler" / "Saves"
        )

    def inspect(self) -> AnglerInspection:
        account = self._account_root()
        if account is None:
            return AnglerInspection(False, (), 0, "No local Steam save account was found.")
        files = [
            path for path in account.rglob("*")
            if path.is_file() and not path.is_symlink() and path.name in KNOWN_FILES
        ]
        if len(files) > self.MAX_FILES:
            raise ValueError("The Angler save contains more files than the bounded inspector permits")
        containers = tuple(self._inspect_file(account, path) for path in sorted(files))
        primary = next((item for item in containers if item.relative_path == "player_save_data"), None)
        duplicates = sum(
            1 for item in containers
            if primary and item.relative_path.startswith("slots/")
            and item.relative_path.endswith("/player_save_data")
            and item.sha256 == primary.sha256
        )
        binary = [item for item in containers if item.format == "Avalanche ADF binary container"]
        status = (
            f"Found {len(containers)} bounded save files; {len(binary)} use the recognised ADF container signature. "
            "Their internal fields remain opaque, so no level, cash, inventory, unlock, or catch claim was made."
        )
        return AnglerInspection(True, containers, duplicates, status)

    def _account_root(self) -> Path | None:
        if not self.saves_root.is_dir():
            return None
        candidates = sorted(
            path for path in self.saves_root.iterdir()
            if path.is_dir() and not path.is_symlink() and (path / "player_save_data").is_file()
        )
        return candidates[0] if candidates else None

    def _inspect_file(self, account: Path, path: Path) -> SaveContainer:
        resolved_account = account.resolve()
        resolved = path.resolve()
        if resolved_account not in resolved.parents:
            raise ValueError("The Angler save path escaped its account directory")
        before = path.stat()
        if before.st_size > self.MAX_FILE_BYTES:
            raise ValueError(f"The Angler save file exceeds the bounded inspection limit: {path.name}")
        digest = hashlib.sha256()
        header = b""
        with path.open("rb") as handle:
            while block := handle.read(64 * 1024):
                if not header:
                    header = block[:32]
                digest.update(block)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise RuntimeError(f"The Angler save changed during inspection: {path.name}")
        if header.startswith(ADF_MAGIC):
            format_name = "Avalanche ADF binary container"
        elif path.name == "steam_autocloud.vdf":
            format_name = "Steam cloud marker"
        else:
            format_name = "Opaque binary container"
        return SaveContainer(
            path.relative_to(account).as_posix(), before.st_size, digest.hexdigest(), format_name
        )


class AnglerObservationStore:
    """Persist content-free fingerprints outside the game and compare a later snapshot."""

    def __init__(
        self,
        inspector: AnglerSaveInspector | None = None,
        path: Path | None = None,
    ):
        self.inspector = inspector or AnglerSaveInspector()
        self.path = Path(
            path
            or Path(__file__).resolve().parents[2] / "Data" / "Fishing" / "angler_observation.json"
        )

    BLOCK_BYTES = 4096

    def begin(self) -> AnglerInspection:
        inspection = self.inspector.inspect()
        if not inspection.account_found:
            raise RuntimeError("No local The Angler save account is available for observation")
        payload = {
            "schema": 2,
            "block_bytes": self.BLOCK_BYTES,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "files": {
                item.relative_path: {
                    "size": item.size,
                    "sha256": item.sha256,
                    "format": item.format,
                    "block_hashes": self._block_hashes(item.relative_path),
                }
                for item in inspection.containers
            },
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.path)
        return inspection

    def compare(self) -> AnglerObservationDiff:
        if not self.path.is_file():
            raise RuntimeError("No Angler observation baseline exists. Begin one before playing.")
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if payload.get("schema") != 2 or not isinstance(payload.get("files"), dict):
                raise ValueError
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
            raise RuntimeError("The Angler observation baseline is unreadable") from error
        current_report = self.inspector.inspect()
        if not current_report.account_found:
            raise RuntimeError("The Angler save account is no longer available")
        before = payload["files"]
        current = {item.relative_path: item for item in current_report.containers}
        changed = tuple(sorted(
            path for path in before.keys() & current.keys()
            if before[path].get("sha256") != current[path].sha256
            or before[path].get("size") != current[path].size
        ))
        structural = tuple(
            self._structural_change(path, before[path], current[path])
            for path in changed
            if isinstance(before[path].get("block_hashes"), list)
        )
        return AnglerObservationDiff(
            str(payload.get("created_utc", "")),
            changed,
            tuple(sorted(current.keys() - before.keys())),
            tuple(sorted(before.keys() - current.keys())),
            structural,
        )

    def _block_hashes(self, relative_path: str) -> list[str]:
        account = self.inspector._account_root()
        if account is None:
            raise RuntimeError("The Angler save account is no longer available")
        path = account / Path(relative_path)
        resolved_account = account.resolve()
        resolved = path.resolve()
        if resolved_account not in resolved.parents or path.is_symlink():
            raise ValueError("The Angler observation path escaped its account directory")
        before = path.stat()
        hashes: list[str] = []
        with path.open("rb") as handle:
            while block := handle.read(self.BLOCK_BYTES):
                hashes.append(hashlib.sha256(block).hexdigest())
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise RuntimeError(f"The Angler save changed during observation: {path.name}")
        return hashes

    def _structural_change(
        self, relative_path: str, baseline: dict[str, object], current: SaveContainer
    ) -> StructuralChange:
        old_hashes = tuple(str(value) for value in baseline.get("block_hashes", []))
        new_hashes = tuple(self._block_hashes(relative_path))
        changed_indices = [
            index for index in range(max(len(old_hashes), len(new_hashes)))
            if index >= len(old_hashes)
            or index >= len(new_hashes)
            or old_hashes[index] != new_hashes[index]
        ]
        ranges: list[str] = []
        if changed_indices:
            start = previous = changed_indices[0]
            for index in changed_indices[1:] + [changed_indices[-1] + 2]:
                if index != previous + 1:
                    first = start * self.BLOCK_BYTES
                    extent = max(current.size, int(baseline.get("size", 0)))
                    last = min((previous + 1) * self.BLOCK_BYTES, extent) - 1
                    ranges.append(f"{first}-{max(first, last)}")
                    start = index
                previous = index
        return StructuralChange(
            relative_path,
            len(changed_indices),
            max(len(old_hashes), len(new_hashes)),
            tuple(ranges),
        )
