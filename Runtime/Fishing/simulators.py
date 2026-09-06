"""Bounded, read-only discovery for supported fishing simulators."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re


GAMES = (
    ("russian-fishing-4", "Russian Fishing 4", None, "standalone"),
    ("fisher-online", "Fisher Online", "1094780", "steam"),
    ("professional-fishing-2", "Professional Fishing 2", "1232220", "steam"),
    ("call-of-the-wild-the-angler", "Call of the Wild: The Angler", "1408610", "steam"),
)


@dataclass(frozen=True)
class SimulatorDiscovery:
    key: str
    name: str
    installation: str
    installed: bool
    data_status: str
    data_path: str = ""


class FishingCodex:
    """Own the private codex skeleton and inspect paths without reading game data."""

    SECTIONS = ("Locations", "Species", "Tackle", "Techniques", "Maps", "Sources", "Sessions")

    def __init__(self, root: Path | None = None):
        self.root = Path(root or Path(__file__).resolve().parents[2] / "Data" / "Fishing")

    def initialize(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        for key, name, _, _ in GAMES:
            game_root = self.root / key
            for section in self.SECTIONS:
                (game_root / section).mkdir(parents=True, exist_ok=True)
            index = game_root / "index.json"
            if not index.exists():
                index.write_text(
                    json.dumps({"game": name, "schema": 1, "observations": []}, indent=2) + "\n",
                    encoding="utf-8",
                )

    def inspect(
        self,
        steam_roots: tuple[Path, ...] | None = None,
        drive_roots: tuple[Path, ...] | None = None,
        home: Path | None = None,
    ) -> tuple[SimulatorDiscovery, ...]:
        self.initialize()
        home = Path(home or Path.home())
        steam = self._steam_installs(steam_roots)
        rf4 = self._find_rf4(drive_roots, home)
        results = []
        for key, name, app_id, channel in GAMES:
            install = rf4 if channel == "standalone" else steam.get(app_id or "")
            data_path = ""
            data_status = "unsupported"
            if key == "call-of-the-wild-the-angler":
                saves = home / "Saved Games" / "Avalanche Studios" / "CotWTheAngler" / "Saves"
                if saves.is_dir():
                    data_path, data_status = str(saves), "candidate read-only source"
            elif install:
                data_status = "installation found; progress source not yet verified"
            results.append(SimulatorDiscovery(key, name, str(install or ""), bool(install), data_status, data_path))
        return tuple(results)

    @staticmethod
    def _steam_installs(steam_roots: tuple[Path, ...] | None) -> dict[str, Path]:
        roots = list(steam_roots or ())
        if not roots:
            roots.append(Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Steam")
        libraries = list(roots)
        for root in tuple(roots):
            vdf = root / "steamapps" / "libraryfolders.vdf"
            if vdf.is_file():
                text = vdf.read_text(encoding="utf-8", errors="ignore")
                libraries.extend(Path(value.replace("\\\\", "\\")) for value in re.findall(r'"path"\s+"([^"]+)"', text))
        found = {}
        wanted = {app_id for _, _, app_id, _ in GAMES if app_id}
        for library in dict.fromkeys(libraries):
            for app_id in wanted:
                manifest = library / "steamapps" / f"appmanifest_{app_id}.acf"
                if not manifest.is_file():
                    continue
                text = manifest.read_text(encoding="utf-8", errors="ignore")
                match = re.search(r'"installdir"\s+"([^"]+)"', text)
                if match:
                    candidate = library / "steamapps" / "common" / match.group(1)
                    if candidate.is_dir():
                        found[app_id] = candidate
        return found

    @staticmethod
    def _find_rf4(drive_roots: tuple[Path, ...] | None, home: Path) -> Path | None:
        roots = list(drive_roots or ())
        if not roots and os.name == "nt":
            roots = [Path(f"{letter}:/") for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ" if Path(f"{letter}:/").exists()]
        for root in roots:
            try:
                candidates = (entry for entry in root.iterdir() if entry.is_dir() and entry.name.casefold().startswith("rf4"))
                for candidate in candidates:
                    if (candidate / "RF4Launcher.exe").is_file():
                        return candidate
            except OSError:
                continue
        launcher_state = home / "AppData" / "Local" / "RF4Launcher"
        return launcher_state if launcher_state.is_dir() else None
