"""Restart-safe temporary reports awaiting Drew's explicit decision."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import secrets


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PENDING_ROOT = PROJECT_ROOT / "Data" / "PendingReports"


@dataclass(frozen=True)
class PendingReport:
    report_id: str
    title: str
    body: str
    provider: str
    created_at: str


class PendingReportStore:
    """Persist undecided reports locally without promoting them to knowledge."""

    def __init__(self, root: Path = DEFAULT_PENDING_ROOT):
        self.root = Path(root)

    def create(self, title: str, body: str, provider: str) -> PendingReport:
        title = " ".join(title.split())
        if not title or not body.strip() or not provider.strip():
            raise ValueError("A pending report needs a title, body, and provider.")
        report = PendingReport(
            report_id=f"BR-{secrets.token_hex(4).upper()}",
            title=title,
            body=body.strip(),
            provider=provider.strip(),
            created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
        self.root.mkdir(parents=True, exist_ok=True)
        path = self._path(report.report_id)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(path)
        return report

    def load(self, report_id: str) -> PendingReport:
        path = self._path(report_id)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return PendingReport(**data)
        except (FileNotFoundError, json.JSONDecodeError, TypeError) as error:
            raise ValueError("That pending report is unavailable or invalid.") from error

    def latest(self) -> PendingReport | None:
        paths = sorted(self.root.glob("BR-*.json"), key=lambda item: item.stat().st_mtime, reverse=True) if self.root.exists() else []
        return self.load(paths[0].stem) if paths else None

    def discard(self, report_id: str) -> None:
        path = self._path(report_id)
        try:
            path.unlink()
        except FileNotFoundError as error:
            raise ValueError("That pending report no longer exists.") from error

    def _path(self, report_id: str) -> Path:
        clean = report_id.strip().upper()
        if not clean.startswith("BR-") or not clean[3:].isalnum():
            raise ValueError("That pending report identifier is invalid.")
        return self.root / f"{clean}.json"
