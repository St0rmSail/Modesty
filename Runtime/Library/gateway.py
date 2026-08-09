"""Bounded, approval-gated transport for the Grand Library."""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import secrets

from Runtime.Knowledge.stores import StorePaths
from Runtime.Library.credentials import CredentialError
from Runtime.Library.models import LoanPacket, LoanSource
from Runtime.Library.providers import LoopbackProvider
from Runtime.Library.smithsonian import SmithsonianError


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUDIT_LOG = PROJECT_ROOT / "Data" / "grand_library_audit.jsonl"


class GatewayError(RuntimeError):
    """A Grand Library boundary refused an unsafe or invalid operation."""


@dataclass(frozen=True)
class GatewayReceipt:
    loan_id: str
    return_path: Path


class GrandLibraryGateway:
    """Start closed, approve exact packets, and quarantine every return."""

    MAX_PACKET_BYTES = 8192
    MAX_QUESTION_CHARS = 600
    MAX_SOURCES = 5
    MAX_PASSAGE_CHARS = 1200
    SECRET_PATTERN = re.compile(
        r"(?i)(?:api[_ -]?key|password|access[_ -]?token|secret)\s*[:=]\s*\S+"
    )
    ABSOLUTE_PATH_PATTERN = re.compile(r"(?i)(?:[a-z]:[\\/]|(?:^|\s)/(?:home|users|etc)/)")

    def __init__(
        self,
        paths: StorePaths,
        audit_path: Path = DEFAULT_AUDIT_LOG,
        provider=None,
    ):
        self.paths = paths
        self.audit_path = Path(audit_path)
        self.provider = provider or LoopbackProvider()
        self._open = False
        self._pending: dict[str, tuple[LoanPacket, str]] = {}

    @property
    def is_open(self) -> bool:
        return self._open

    def open(self) -> bool:
        changed = not self._open
        self._open = True
        self._audit("gateway_opened", provider=self.provider.name)
        return changed

    def select_provider(self, provider):
        if self._open:
            raise GatewayError("Close the Grand Library before changing its provider.")
        self._pending.clear()
        self.provider = provider

    def close(self) -> int:
        cancelled = len(self._pending)
        self._pending.clear()
        self._open = False
        self._audit("gateway_closed", cancelled_pending=cancelled)
        return cancelled

    def prepare(self, question: str, sources=()) -> LoanPacket:
        self._require_open()
        question = question.strip()
        loan_sources = tuple(
            source if isinstance(source, LoanSource) else LoanSource(
                store=source.store,
                relative_path=source.relative_path,
                title=source.title,
                passage=source.passage,
            )
            for source in sources
        )
        now = datetime.now(timezone.utc)
        packet = LoanPacket(
            loan_id=f"GL-{now:%Y%m%d}-{secrets.token_hex(4).upper()}",
            provider=self.provider.name,
            question=question,
            sources=loan_sources,
            created_at=now.isoformat(timespec="seconds"),
        )
        try:
            self._validate(packet)
        except GatewayError as error:
            self._audit(
                "loan_rejected",
                loan_id=packet.loan_id,
                provider=packet.provider,
                reason=str(error),
            )
            raise
        self._pending[packet.loan_id] = (packet, packet.fingerprint)
        self._audit(
            "loan_prepared",
            loan_id=packet.loan_id,
            provider=packet.provider,
            size_bytes=packet.size_bytes,
            bookshelf_sources=[source.relative_path for source in packet.sources],
        )
        return packet

    def approve(self, loan_id: str) -> GatewayReceipt:
        self._require_open()
        pending = self._pending.get(loan_id.strip())
        if pending is None:
            self._audit("loan_approval_refused", reason="pending_loan_not_found")
            raise GatewayError("That exact pending Grand Library loan does not exist.")
        packet, approved_fingerprint = pending
        self._validate(packet)
        if packet.fingerprint != approved_fingerprint:
            self._pending.pop(packet.loan_id, None)
            self._audit(
                "loan_approval_refused",
                loan_id=packet.loan_id,
                reason="packet_changed_after_preview",
            )
            raise GatewayError("The loan packet changed after preview; approval was cancelled.")
        self._audit(
            "loan_approved",
            loan_id=packet.loan_id,
            provider=packet.provider,
            size_bytes=packet.size_bytes,
        )
        try:
            returned = self.provider.execute(packet)
            return_path = self._quarantine(packet, returned.title, returned.body)
        except Exception as error:
            self._audit(
                "loan_failed",
                loan_id=packet.loan_id,
                provider=packet.provider,
                error_type=type(error).__name__,
            )
            if isinstance(error, (CredentialError, GatewayError, SmithsonianError)):
                message = str(error)
            else:
                message = (
                    f"The {self.provider.name} loan failed safely; no success was recorded."
                )
            raise GatewayError(message) from error
        self._pending.pop(packet.loan_id, None)
        self._audit(
            "loan_returned",
            loan_id=packet.loan_id,
            provider=packet.provider,
            return_file=return_path.name,
        )
        return GatewayReceipt(packet.loan_id, return_path)

    def _validate(self, packet: LoanPacket):
        if not packet.question:
            raise GatewayError("A Grand Library loan needs a research question.")
        if len(packet.question) > self.MAX_QUESTION_CHARS:
            raise GatewayError("The research question is too large for a bounded loan.")
        if len(packet.sources) > self.MAX_SOURCES:
            raise GatewayError("The loan contains too many Bookshelf passages.")
        strings = [packet.question]
        for source in packet.sources:
            if source.store != "bookshelf":
                raise GatewayError("Only Bookshelf passages may leave through the Grand Library.")
            relative = Path(source.relative_path)
            if relative.is_absolute() or ".." in relative.parts:
                raise GatewayError("A Bookshelf source contains an unsafe path.")
            if len(source.passage) > self.MAX_PASSAGE_CHARS:
                raise GatewayError("A Bookshelf passage exceeds the loan size limit.")
            strings.extend((source.relative_path, source.title, source.passage))
        outbound_text = "\n".join(strings)
        if "filing cabinet" in outbound_text.casefold():
            raise GatewayError("The loan appears to contain Filing Cabinet material.")
        if self.SECRET_PATTERN.search(outbound_text):
            raise GatewayError("The loan appears to contain a credential or secret.")
        if self.ABSOLUTE_PATH_PATTERN.search(outbound_text):
            raise GatewayError("The loan appears to contain an absolute local path.")
        if packet.size_bytes > self.MAX_PACKET_BYTES:
            raise GatewayError("The loan packet exceeds the outbound size limit.")

    def _quarantine(self, packet: LoanPacket, title: str, body: str) -> Path:
        inbox = self.paths.bookshelf / "Inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        filename = (
            f"{datetime.now():%Y-%m-%d}-grand-library-{packet.provider.casefold()}-"
            f"{packet.loan_id.casefold()}.md"
        )
        path = inbox / filename
        if path.exists():
            raise GatewayError("A return with this loan identifier already exists.")
        sources = "\n".join(
            f"- Bookshelf/{source.relative_path}" for source in packet.sources
        ) or "- No Bookshelf passages were loaned."
        document = (
            "---\n"
            "type: Research Return\n"
            f"title: {title}\n"
            "created_by: system:grand-library-loopback\n"
            f"verified: {'test-only' if packet.provider == 'loopback' else 'unverified'}\n"
            "provenance: grand-library-return\n"
            f"loan_id: {packet.loan_id}\n"
            f"provider: {packet.provider}\n"
            f"retrieved_at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n"
            "---\n\n"
            f"# {title}\n\n"
            f"## Approved question\n\n{packet.question}\n\n"
            f"## Returned research\n\n{body}\n\n"
            f"## Loaned sources\n\n{sources}\n"
        )
        path.write_text(document, encoding="utf-8", newline="\n")
        return path

    def _require_open(self):
        if not self._open:
            self._audit("loan_refused", reason="gateway_closed")
            raise GatewayError("The Grand Library is closed. No outbound loan was sent.")

    def _audit(self, event: str, **details):
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "event": event,
            **details,
        }
        with self.audit_path.open("a", encoding="utf-8", newline="\n") as audit:
            audit.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
