"""Bounded public YouTube transcript intake without account access."""

import re
from urllib.parse import parse_qs, urlparse

from Brain.Team.investigation import TranscriptSnippet, YouTubeTranscriptEvidence


MAX_TRANSCRIPT_CHARACTERS = 24_000
MAX_TRANSCRIPT_SNIPPETS = 300


class TranscriptUnavailable(ValueError):
    """A public transcript could not be obtained within the approved boundary."""


def youtube_video_id(value: str) -> str:
    """Extract a conservative video ID from ordinary public YouTube URLs."""
    parsed = urlparse(value.strip())
    host = (parsed.hostname or "").casefold()
    candidate = ""
    if host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            candidate = parse_qs(parsed.query).get("v", [""])[0]
        elif parsed.path.startswith(("/shorts/", "/embed/")):
            candidate = parsed.path.split("/")[2]
    elif host == "youtu.be":
        candidate = parsed.path.strip("/").split("/")[0]
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate):
        raise TranscriptUnavailable("Enter a complete public YouTube video URL.")
    return candidate


class YouTubeTranscriptProvider:
    """Retrieve one English public transcript with strict size limits."""

    def __init__(self, api=None):
        if api is None:
            try:
                from youtube_transcript_api import YouTubeTranscriptApi
            except ImportError as error:
                raise TranscriptUnavailable("YouTube transcript support is not installed.") from error
            api = YouTubeTranscriptApi()
        self.api = api

    def fetch(self, url: str) -> YouTubeTranscriptEvidence:
        video_id = youtube_video_id(url)
        try:
            transcript = self.api.fetch(video_id, languages=["en"])
        except Exception as error:
            raise TranscriptUnavailable(
                "No usable public English transcript was available. The video may have no captions or YouTube may have refused transcript access."
            ) from error

        snippets = []
        characters = 0
        for item in transcript:
            text = " ".join(str(item.text).split())[:1000]
            if not text:
                continue
            if characters + len(text) > MAX_TRANSCRIPT_CHARACTERS:
                break
            snippets.append(TranscriptSnippet(text, float(item.start), float(item.duration)))
            characters += len(text)
            if len(snippets) >= MAX_TRANSCRIPT_SNIPPETS:
                break
        if not snippets:
            raise TranscriptUnavailable("The public transcript was empty after safety limits were applied.")
        return YouTubeTranscriptEvidence(
            video_id=video_id,
            source_url=f"https://www.youtube.com/watch?v={video_id}",
            language=str(getattr(transcript, "language", "English")),
            is_generated=bool(getattr(transcript, "is_generated", False)),
            snippets=tuple(snippets),
        )
