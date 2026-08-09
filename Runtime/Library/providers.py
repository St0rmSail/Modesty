"""Transport providers for the Grand Library Gateway."""

from dataclasses import dataclass
import re
from urllib.parse import quote, urlparse, urlunparse

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
    FIRST_EXPEDITION_QUESTION = (
        "Retrieve the Smithsonian Open Access record for ENIAC Accumulator #2"
    )
    FIRST_EXPEDITION_QUERY = '"ENIAC Accumulator"'
    FIRST_EXPEDITION_TITLE = "ENIAC Accumulator #2"

    def __init__(self, access: SmithsonianAccess):
        self.access = access

    def execute(self, packet: LoanPacket) -> ProviderReturn:
        if packet.question.casefold() != self.FIRST_EXPEDITION_QUESTION.casefold():
            raise SmithsonianError(
                "This provider is currently restricted to the approved first expedition."
            )
        response = self.access.search(self.FIRST_EXPEDITION_QUERY, rows=self.MAX_RESULTS)
        rows = [
            row
            for row in response.get("rows", [])[:self.MAX_RESULTS]
            if isinstance(row, dict) and self._is_relevant(row)
        ]
        if not rows:
            raise SmithsonianError(
                "The Smithsonian returned no exact ENIAC Accumulator #2 record; "
                "no substitute research note was filed."
            )
        sections = []
        for index, row in enumerate(rows, 1):
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
            title="ENIAC Accumulator #2 — first Smithsonian expedition",
            body=body,
        )

    @classmethod
    def _plain(cls, value) -> str:
        if not isinstance(value, str):
            return ""
        text = re.sub(r"\s+", " ", value).strip()
        if len(text) <= cls.MAX_EXCERPT_CHARS:
            return text
        shortened = text[: cls.MAX_EXCERPT_CHARS + 1].rsplit(" ", 1)[0]
        return shortened.rstrip(" ,;:-") + "…"

    @classmethod
    def _is_relevant(cls, row: dict) -> bool:
        title = re.sub(r"[^a-z0-9]+", " ", str(row.get("title", "")).casefold()).strip()
        expected = re.sub(
            r"[^a-z0-9]+", " ", cls.FIRST_EXPEDITION_TITLE.casefold()
        ).strip()
        return title == expected

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
            if parsed.scheme in ("http", "https") and (
                host == "si.edu" or host.endswith(".si.edu") or host == "n2t.net"
            ):
                return urlunparse(parsed._replace(scheme="https"))
        identifier = row.get("id")
        if isinstance(identifier, str) and identifier.strip():
            return f"https://www.si.edu/object/{quote(identifier.strip(), safe=':_-')}"
        return "https://www.si.edu/openaccess"

    @classmethod
    def _excerpt(cls, row: dict) -> str:
        content = row.get("content")
        if not isinstance(content, dict):
            return ""
        values = []

        def collect(value):
            if isinstance(value, dict):
                for child in value.values():
                    collect(child)
            elif isinstance(value, list):
                for child in value:
                    collect(child)
            elif isinstance(value, str):
                text = re.sub(r"\s+", " ", value).strip()
                if text and not text.startswith(("http://", "https://")):
                    values.append(text)

        collect(content)
        ranked = sorted(
            enumerate(values),
            key=lambda item: (
                "eniac" not in item[1].casefold(),
                "accumulator" not in item[1].casefold(),
                item[0],
            ),
        )
        selected = []
        seen = set()
        for _, value in ranked:
            normalized = value.casefold()
            if normalized in seen:
                continue
            if re.sub(r"[^a-z0-9]+", " ", normalized).strip() == re.sub(
                r"[^a-z0-9]+", " ", cls.FIRST_EXPEDITION_TITLE.casefold()
            ).strip():
                continue
            if not any(term in normalized for term in ("eniac", "accumulator")):
                continue
            selected.append(value)
            seen.add(normalized)
            if len(" ".join(selected)) >= cls.MAX_EXCERPT_CHARS:
                break
        excerpt = cls._plain(" ".join(selected))
        if excerpt.endswith("…"):
            complete = excerpt[:-1].rfind(". ")
            if complete >= cls.MAX_EXCERPT_CHARS // 2:
                excerpt = excerpt[: complete + 1]
        return excerpt
