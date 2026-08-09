"""Immutable models crossing the Grand Library boundary."""

from dataclasses import asdict, dataclass
import hashlib
import json


@dataclass(frozen=True)
class LoanSource:
    store: str
    relative_path: str
    title: str
    passage: str


@dataclass(frozen=True)
class LoanPacket:
    loan_id: str
    provider: str
    question: str
    sources: tuple[LoanSource, ...]
    created_at: str

    def canonical_bytes(self) -> bytes:
        return json.dumps(
            asdict(self),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    @property
    def size_bytes(self) -> int:
        return len(self.canonical_bytes())

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()
