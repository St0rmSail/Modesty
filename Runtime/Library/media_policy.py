"""Fail-closed rules for material returned through the Grand Library."""

from dataclasses import dataclass
import re


class ReturnPolicyError(ValueError):
    """A provider return is unsafe to write into the Bookshelf."""


@dataclass(frozen=True)
class TextReturnPolicy:
    """Permit inert Markdown text while rejecting active or embedded media."""

    max_title_chars: int = 200
    max_body_bytes: int = 64 * 1024

    _MARKDOWN_EMBED = re.compile(r"!\s*(?:\[|\[\[)")
    _RAW_HTML = re.compile(
        r"(?:<!--|<\s*/?\s*[a-z][a-z0-9-]*(?:\s|/?>))", re.IGNORECASE
    )
    _ACTIVE_URI = re.compile(r"(?:data|blob|file|javascript)\s*:", re.IGNORECASE)
    _CONTROL_CHAR = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

    def validate(self, title: str, body: str) -> None:
        if not isinstance(title, str) or not isinstance(body, str):
            raise ReturnPolicyError("Grand Library returns must be text only.")
        if not title.strip() or len(title) > self.max_title_chars:
            raise ReturnPolicyError("The returned title is missing or exceeds its limit.")
        if "\n" in title or "\r" in title:
            raise ReturnPolicyError("The returned title must be a single line.")
        if len(body.encode("utf-8")) > self.max_body_bytes:
            raise ReturnPolicyError("The returned text exceeds the quarantine size limit.")

        self.validate_content(f"{title}\n{body}")

    def validate_content(self, text: str) -> None:
        """Reject markup that could become active when copied into a note."""
        if not isinstance(text, str):
            raise ReturnPolicyError("Grand Library note content must be text only.")
        if self._CONTROL_CHAR.search(text):
            raise ReturnPolicyError("The return contains unsafe control characters.")
        if self._MARKDOWN_EMBED.search(text):
            raise ReturnPolicyError("Embedded Markdown media is not accepted.")
        if self._RAW_HTML.search(text):
            raise ReturnPolicyError("Raw HTML or embedded media is not accepted.")
        if self._ACTIVE_URI.search(text):
            raise ReturnPolicyError("Active, local, or inline media addresses are not accepted.")


TEXT_RETURN_POLICY = TextReturnPolicy()
