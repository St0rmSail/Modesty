"""Transport providers for the Grand Library Gateway."""

from dataclasses import dataclass
import re
from urllib.parse import urlparse

from Runtime.Library.models import LoanPacket
from Runtime.Library.smithsonian import SmithsonianAccess, SmithsonianError


@dataclass(frozen=True)
class ProviderReturn:
    title: str
    body: str


class LoopbackProvider:
    """Exercise the complete transport contract without using a network."""

    name = "loopback"

    def execute(self, packet: LoanPacket) -> ProviderReturn:
        count = len(packet.sources)
        body = (
            "The local loopback provider received the exact approved loan packet. "
            f"It contained {count} Bookshelf passage{'s' if count != 1 else ''}. "
            "No network request was made."
        )
        return ProviderReturn(
            title=f"Grand Library loopback receipt {packet.loan_id}",
            body=body,
        )


class SmithsonianProvider:
    """Execute a bounded, source-linked Smithsonian Open Access search."""

    name = "smithsonian"
    MAX_RESULTS = 5
    MAX_EXCERPT_CHARS = 700
    FIRST_EXPEDITION_QUESTION = "Research Kathleen McNulty and the first ENIAC programmers"

    def __init__(self, access: SmithsonianAccess):
        self.access = access

    def execute(self, packet: LoanPacket) -> ProviderReturn:
        if packet.question.casefold() != self.FIRST_EXPEDITION_QUESTION.casefold():
            raise SmithsonianError(
                "This provider is currently restricted to the approved first expedition."
            )
        response = self.access.search(packet.question, rows=self.MAX_RESULTS)
        rows = response.get("rows", [])[:self.MAX_RESULTS]
        if not rows:
            raise SmithsonianError(
                "The Smithsonian returned no matching records; no empty research note was filed."
            )
        sections = []
        for index, row in enumerate(rows, 1):
            if not isinstance(row, dict):
                continue
            title = self._plain(row.get("title")) or "Untitled Smithsonian record"
            unit = self._plain(row.get("unitCode"))
            source = self._source_url(row)
            excerpt = self._excerpt(row)
            lines = [f"{index}. {title}"]
            if excerpt:
                lines.append(excerpt)
            if unit:
                lines.append(f"Smithsonian unit: {unit}")
            lines.append(f"Source: {source}")
            sections.append("\n".join(lines))
        if not sections:
            raise SmithsonianError(
                "The Smithsonian response contained no usable records; nothing was filed."
            )
        body = (
            f"Smithsonian Open Access returned {len(sections)} bounded record"
            f"{'s' if len(sections) != 1 else ''} for the approved question.\n\n"
            + "\n\n".join(sections)
        )
        return ProviderReturn(
            title="Kathleen McNulty and the first ENIAC programmers — Smithsonian expedition",
            body=body,
        )

    @classmethod
    def _plain(cls, value) -> str:
        if not isinstance(value, str):
            return ""
        return re.sub(r"\s+", " ", value).strip()[: cls.MAX_EXCERPT_CHARS]

    @classmethod
    def _source_url(cls, row: dict) -> str:
        candidates = [row.get("url")]
        content = row.get("content")
        if isinstance(content, dict):
            descriptive = content.get("descriptiveNonRepeating")
            if isinstance(descriptive, dict):
                candidates.extend((descriptive.get("record_link"), descriptive.get("guid")))
        for candidate in candidates:
            if not isinstance(candidate, str):
                continue
            parsed = urlparse(candidate)
            host = (parsed.hostname or "").casefold()
            if parsed.scheme == "https" and (host == "si.edu" or host.endswith(".si.edu")):
                return candidate
        return SmithsonianAccess.SEARCH_ENDPOINT

    @classmethod
    def _excerpt(cls, row: dict) -> str:
        content = row.get("content")
        if not isinstance(content, dict):
            return ""
        freetext = content.get("freetext")
        if not isinstance(freetext, dict):
            return ""
        candidates = []
        for field in ("notes", "date", "name"):
            values = freetext.get(field, [])
            if not isinstance(values, list):
                continue
            for value in values:
                if isinstance(value, dict):
                    text = cls._plain(value.get("content"))
                    if text:
                        candidates.append(text)
        return " ".join(candidates)[: cls.MAX_EXCERPT_CHARS]
