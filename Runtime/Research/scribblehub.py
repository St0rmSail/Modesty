"""Parse public Scribble Hub discovery listings without downloading story text."""

from html.parser import HTMLParser
from urllib.parse import urlencode

from Brain.Team.researcher import StoryFinding


SERIES_FINDER_URL = "https://www.scribblehub.com/series-finder/"


def latest_harem_url() -> str:
    """Return the reproducible Series Finder query approved for first research."""
    return f"{SERIES_FINDER_URL}?{urlencode({'sf': 1, 'gi': 1015, 'mgi': 'or', 'sort': 'dateadded', 'order': 'desc'})}"


class ScribbleHubListingParser(HTMLParser):
    """Extract only visible discovery metadata from Series Finder result cards."""

    def __init__(self, limit: int = 10):
        super().__init__(convert_charrefs=True)
        self.limit = limit
        self._cards: list[dict] = []
        self._card: dict | None = None
        self._div_depth = 0
        self._card_depth = 0
        self._capture: str | None = None
        self._capture_depth = 0
        self._buffer: list[str] = []
        self._genre_text: list[str] | None = None
        self._author_text: list[str] | None = None
        self._updated_text: list[str] | None = None

    @property
    def findings(self) -> tuple[StoryFinding, ...]:
        results = []
        for card in self._cards[: self.limit]:
            stats = " ".join(card.get("stats", "").split())
            results.append(
                StoryFinding(
                    title=card.get("title", "Untitled"),
                    url=card.get("url", ""),
                    author=card.get("author", "Unknown"),
                    genres=tuple(card.get("genres", ())),
                    synopsis=" ".join(card.get("synopsis", "").split()),
                    chapters=self._number_before(stats, "Chapters"),
                    readers=self._number_before(stats, "Readers"),
                    last_updated=card.get("updated", "unknown time"),
                )
            )
        return tuple(results)

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set(attributes.get("class", "").split())
        if tag == "div":
            self._div_depth += 1
        if tag == "div" and "search_main_box" in classes and len(self._cards) < self.limit:
            self._card = {"genres": []}
            self._card_depth = self._div_depth
        if self._card is None:
            return
        if tag == "div" and "search_title" in classes:
            self._capture = "title"
            self._capture_depth = self._div_depth
        elif tag == "div" and "search_stats" in classes:
            self._capture = "stats"
            self._capture_depth = self._div_depth
        elif tag == "div" and "search_genre" in classes:
            self._capture = "genres"
            self._capture_depth = self._div_depth
        elif tag == "a" and self._capture == "title" and "/series/" in attributes.get("href", ""):
            self._card["url"] = attributes["href"]
        elif tag == "a" and self._capture == "genres":
            self._genre_text = []
        elif tag == "a" and self._capture == "stats" and "/profile/" in attributes.get("href", ""):
            self._author_text = []
        elif tag == "span" and self._capture == "stats" and attributes.get("title") == "Last Updated":
            self._updated_text = []

    def handle_data(self, data):
        if self._card is not None and self._capture:
            self._buffer.append(data)
            if self._genre_text is not None:
                self._genre_text.append(data)
            if self._author_text is not None:
                self._author_text.append(data)
            if self._updated_text is not None:
                self._updated_text.append(data)

    def handle_endtag(self, tag):
        if self._card is None:
            if tag == "div":
                self._div_depth = max(0, self._div_depth - 1)
            return
        if tag == "a" and self._genre_text is not None:
            genre = " ".join(" ".join(self._genre_text).split())
            if genre:
                self._card["genres"].append(genre)
            self._genre_text = None
        elif tag == "a" and self._author_text is not None:
            self._card["author"] = " ".join(" ".join(self._author_text).split())
            self._author_text = None
        elif tag == "span" and self._updated_text is not None:
            self._card["updated"] = " ".join(" ".join(self._updated_text).split())
            self._updated_text = None

        if tag == "div" and self._div_depth == self._capture_depth:
            text = " ".join(" ".join(self._buffer).split())
            if self._capture == "title":
                self._card["title"] = text
            elif self._capture == "stats":
                self._card["stats"] = text
            self._capture = None
            self._buffer = []

        if tag == "div" and self._div_depth == self._card_depth:
            self._cards.append(self._card)
            self._card = None
            self._capture = None
            self._buffer = []
        if tag == "div":
            self._div_depth = max(0, self._div_depth - 1)

    @staticmethod
    def _number_before(text: str, label: str) -> int:
        words = text.replace(",", "").split()
        for index, word in enumerate(words):
            if word == label and index:
                try:
                    return int(words[index - 1])
                except ValueError:
                    return 0
        return 0
