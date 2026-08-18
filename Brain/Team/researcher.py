"""Evidence-led reports from the unseen Researcher Team member."""

from dataclasses import dataclass
from difflib import SequenceMatcher
import re
from typing import Iterable

from Brain.Team.investigation import Investigation, YouTubeTranscriptEvidence, render_investigation


@dataclass(frozen=True)
class StoryFinding:
    title: str
    url: str
    author: str
    genres: tuple[str, ...]
    synopsis: str
    chapters: int
    readers: int
    last_updated: str
    tags: tuple[str, ...] = ()
    content_warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class StoryPageEvidence:
    title: str
    source_url: str
    synopsis: str
    genres: tuple[str, ...]
    tags: tuple[str, ...]
    stats: str
    reviews: tuple[str, ...]


class Researcher:
    """Assess bounded findings; Modesty remains the only conversational voice."""

    def report_latest_harem(self, findings: Iterable[StoryFinding]) -> str:
        stories = tuple(findings)
        if not stories:
            return (
                "The Researcher found no usable current listings. Nothing was filed, "
                "and no recommendation can be made from an empty result."
            )

        lines = [
            f"The Researcher found {len(stories)} recent Harem-tagged offering"
            f"{'s' if len(stories) != 1 else ''} on Scribble Hub.",
            "",
            "Initial assessment:",
        ]
        for index, story in enumerate(stories, 1):
            evidence = []
            cautions = []
            if story.chapters >= 5:
                evidence.append(f"{story.chapters} chapters give us something to assess")
            else:
                cautions.append(f"only {story.chapters} chapter{'s' if story.chapters != 1 else ''}")
            if story.readers:
                evidence.append(f"{story.readers} current reader{'s' if story.readers != 1 else ''}")
            else:
                cautions.append("no reader history yet")
            if "Fanfiction" in story.genres:
                cautions.append("fanfiction rather than an original setting")
            if "Boys Love" in story.genres:
                cautions.append("Boys Love is a prominent genre")
            if "Adult" in story.genres or "Smut" in story.genres:
                cautions.append("adult sexual content is explicitly signalled")
            if story.content_warnings:
                cautions.append(
                    "content warnings: " + ", ".join(story.content_warnings)
                )
            grim_signals = {
                "Gore",
                "Rape",
                "Sexual Violence",
                "Strong Violence",
                "Tragedy",
            }
            visible_grim_signals = sorted(grim_signals.intersection(story.content_warnings))
            if visible_grim_signals:
                cautions.append(
                    "possible grim or distressing material signalled by "
                    + ", ".join(visible_grim_signals)
                )

            verdict = "Worth a closer look" if story.chapters >= 5 else "Too early to judge"
            if "Boys Love" in story.genres:
                verdict = "Probably outside the requested target"
            lines.extend(
                (
                    f"{index}. {story.title} — {verdict}",
                    f"   By {story.author}; updated {story.last_updated}; genres: {', '.join(story.genres)}.",
                    f"   Evidence: {'; '.join(evidence) if evidence else 'the listing is too new for meaningful reception evidence'}.",
                    f"   Tags: {', '.join(story.tags) if story.tags else 'none supplied'}.",
                    f"   Cautions: {'; '.join(cautions) if cautions else 'none visible in the listing metadata'}.",
                    f"   Source: {story.url}",
                )
            )

        lines.extend(
            (
                "",
                "What this means:",
                "These are discovery candidates, not endorsements. A listing cannot reveal hidden "
                "grimdark turns or verify sustained quality. The strongest candidates should be "
                "investigated individually through their synopsis, tags, content warnings, reviews, "
                "and a bounded sample before Modesty recommends one.",
                "",
                "Nothing has been filed or added to a reading list.",
            )
        )
        return "\n".join(lines)

    def report_story_page(self, page: dict, source_url: str, retrieved_at: str) -> str:
        story = self.story_page_evidence(page, source_url)
        cautions, recommendation = self._assess_story(story)
        observed = [f"Synopsis: {story.synopsis}"]
        if story.genres: observed.append("Genres: " + ", ".join(story.genres))
        if story.tags: observed.append("Tags: " + ", ".join(story.tags))
        if story.stats: observed.append("Visible statistics: " + story.stats)
        missing = ["A bounded public page cannot rule out hidden tonal changes or establish sustained quality.", "No preference match is claimed unless Drew's approved preferences are supplied separately."]
        return render_investigation(Investigation(story.title, story.source_url, tuple(observed), story.reviews, cautions, tuple(missing), recommendation, retrieved_at))

    def story_page_evidence(self, page: dict, source_url: str) -> StoryPageEvidence:
        title = " ".join(str(page.get("title", "")).split())[:200]
        synopsis = " ".join(str(page.get("synopsis", "")).split())[:3000]
        genres = tuple(dict.fromkeys(str(value).strip() for value in page.get("genres", ()) if str(value).strip()))[:30]
        tags = tuple(dict.fromkeys(str(value).strip() for value in page.get("tags", ()) if str(value).strip()))[:60]
        stats = " ".join(str(page.get("stats", "")).split())[:500]
        reviews = tuple(" ".join(str(value).split())[:700] for value in page.get("reviews", ()) if str(value).strip())[:5]
        if not title or not synopsis:
            raise ValueError("This does not appear to be a complete public story page.")
        if not source_url.startswith("https://www.scribblehub.com/series/"):
            raise ValueError("The story evidence needs a public Scribble Hub source.")
        return StoryPageEvidence(title, source_url, synopsis, genres, tags, stats, reviews)

    def report_story_comparison(self, stories: Iterable[StoryPageEvidence], retrieved_at: str) -> str:
        items = tuple(stories)
        if not 2 <= len(items) <= 3:
            raise ValueError("A comparison needs two or three story pages.")
        if len({story.source_url for story in items}) != len(items):
            raise ValueError("A comparison cannot contain the same story page twice.")

        genre_sets = [set(story.genres) for story in items]
        tag_sets = [set(story.tags) for story in items]
        shared_genres = sorted(set.intersection(*genre_sets)) if all(genre_sets) else []
        shared_tags = sorted(set.intersection(*tag_sets)) if all(tag_sets) else []
        duplicate_pairs = []
        for left_index, left in enumerate(items):
            for right in items[left_index + 1:]:
                same_title = self._normalise_title(left.title) == self._normalise_title(right.title)
                synopsis_match = SequenceMatcher(None, left.synopsis.casefold(), right.synopsis.casefold()).ratio()
                if same_title or synopsis_match >= 0.82:
                    duplicate_pairs.append(
                        f"{left.title} and {right.title} may be duplicate or cross-posted editions "
                        f"(synopsis similarity {synopsis_match:.0%}); this is a lead, not proof."
                    )

        lines = [
            f"The Researcher compared {len(items)} public Scribble Hub story pages.",
            "",
            "Comparative assessment:",
        ]
        for index, story in enumerate(items, 1):
            cautions, recommendation = self._assess_story(story)
            unique_genres = sorted(set(story.genres) - set(shared_genres))
            unique_tags = sorted(set(story.tags) - set(shared_tags))
            lines.extend(
                (
                    f"{index}. {story.title} — {recommendation.upper()}",
                    f"   Observed genres: {', '.join(story.genres) if story.genres else 'none visible'}.",
                    f"   Distinguishing signals: {', '.join(unique_genres + unique_tags) if unique_genres or unique_tags else 'none in the bounded metadata'}.",
                    f"   Reader evidence: {len(story.reviews)} bounded review passage{'s' if len(story.reviews) != 1 else ''}.",
                    f"   Cautions: {'; '.join(cautions) if cautions else 'none explicit in the bounded evidence'}.",
                    f"   Source: {story.source_url}",
                )
            )

        lines.extend(("", "Agreement across the compared pages:"))
        lines.append("- Shared genres: " + (", ".join(shared_genres) if shared_genres else "none established across every page"))
        lines.append("- Shared tags: " + (", ".join(shared_tags) if shared_tags else "none established across every page"))
        lines.extend(("", "Duplicate or cross-post checks:"))
        lines.extend(f"- {finding}" for finding in duplicate_pairs)
        if not duplicate_pairs:
            lines.append("- No likely duplicate was detected from title and synopsis similarity.")
        lines.extend(
            (
                "",
                "Limits:",
                "- This compares public pages of one source type; it does not independently corroborate their claims.",
                "- Visible reviews are reader reports, not observed story facts.",
                "- No personal preference match or hidden-content guarantee is claimed.",
                "",
                f"Retrieved: {retrieved_at}",
                "Nothing has been filed or added to an account.",
            )
        )
        return "\n".join(lines)

    def report_mixed_story_youtube(
        self,
        story: StoryPageEvidence,
        transcript: YouTubeTranscriptEvidence,
        focus: str,
        retrieved_at: str,
    ) -> str:
        focus = " ".join(focus.split())[:500]
        if not focus:
            raise ValueError("Mixed-source research needs an explicit focus question.")
        story_terms = self._evidence_terms(story)
        focus_terms = self._focus_terms(focus)
        terms = tuple(dict.fromkeys((*story_terms, *focus_terms)))
        matched = []
        caution_phrases = (
            "not harem", "isn't harem", "not really harem", "gets dark",
            "grimdark", "stalking", "rape", "abuse", "dropped it", "drop it",
        )
        cautions = []
        page_overlap = False
        focus_overlap = False
        for snippet in transcript.snippets:
            lower = snippet.text.casefold()
            score = sum(1 for term in terms if term in lower)
            story_score = sum(1 for term in story_terms if term in lower)
            focus_score = sum(1 for term in focus_terms if term in lower)
            has_caution = score >= 1 and any(phrase in lower for phrase in caution_phrases)
            if has_caution:
                cautions.append((snippet, "The speaker raises a possible tonal or suitability concern."))
            if score >= 2 or has_caution:
                matched.append((score, snippet))
                page_overlap = page_overlap or story_score >= 2
                focus_overlap = focus_overlap or focus_score >= 2
        selected = []
        seen = set()
        for _, snippet in sorted(matched, key=lambda item: (-item[0], item[1].start)):
            key = (snippet.text.casefold(), int(snippet.start))
            if key not in seen:
                seen.add(key)
                selected.append(snippet)
            if len(selected) == 6:
                break

        lines = [
            f"Mixed-source investigation — {story.title}",
            "",
            f"Research focus: {focus}",
            "",
            "Source roles:",
            f"- Scribble Hub supplies observed public story-page metadata: {story.source_url}",
            f"- YouTube supplies speaker-reported transcript evidence ({transcript.language}; {'automatically generated' if transcript.is_generated else 'creator-supplied or unspecified'} captions): {transcript.source_url}",
            "",
            "Observed on the story page:",
            f"- Synopsis: {story.synopsis}",
            f"- Genres: {', '.join(story.genres) if story.genres else 'none visible'}",
            f"- Tags: {', '.join(story.tags) if story.tags else 'none visible'}",
            "",
            "Relevant YouTube transcript passages:",
        ]
        if selected:
            for snippet in selected:
                seconds = max(0, int(snippet.start))
                lines.append(
                    f"- [{seconds // 60}:{seconds % 60:02d}] {snippet.text} "
                    f"— {transcript.source_url}&t={seconds}s"
                )
        else:
            lines.append("- No transcript passage directly overlapped the bounded story-page signals.")

        lines.extend(("", "Agreement and conflict assessment:"))
        if page_overlap:
            lines.append("- The transcript overlaps multiple title, genre, or tag signals visible on the story page.")
        elif focus_overlap:
            lines.append("- The transcript is relevant to the explicit research focus, but the bounded story-page metadata does not independently corroborate that focus.")
        else:
            lines.append("- The transcript does not corroborate the selected story-page signals in this bounded pass.")
        if cautions:
            lines.append("- One or more speaker-reported passages raise a possible conflict or suitability concern; inspect the timestamped wording above.")
        else:
            lines.append("- No configured caution phrase was found; that is not proof that the video or story contains no concern.")
        lines.extend(
            (
                "",
                "Limits:",
                "- Story-page metadata is observed; transcript statements remain claims by the video's speaker.",
                "- Keyword overlap establishes relevance, not truth. The Researcher has not watched imagery or independently verified the speaker.",
                "- Missing, disabled, non-English, or YouTube-restricted captions fail closed.",
                "- No account action, cookie access, chapter acquisition, or filing occurred.",
                "",
                f"Retrieved: {retrieved_at}",
                "Nothing has been filed or added to an account.",
            )
        )
        return "\n".join(lines)

    @staticmethod
    def _assess_story(story: StoryPageEvidence) -> tuple[tuple[str, ...], str]:
        cautions = []
        caution_terms = {"Gore", "Rape", "Sexual Violence", "Tragedy", "Psychological", "Futanari", "R-18", "Pregnancy"}
        visible = sorted(caution_terms.intersection(set(story.tags) | set(story.genres)))
        if visible: cautions.append("Explicitly signalled: " + ", ".join(visible))
        negative_terms = ("drop", "stalking", "disgust", "ruin", "rape", "grim", "abuse")
        conflicts = [review for review in story.reviews if any(term in review.casefold() for term in negative_terms)]
        if conflicts: cautions.append("At least one visible reader report raises a substantive late-story concern.")
        positive = bool(story.reviews) and any(term in " ".join(story.reviews).casefold() for term in ("well written", "worldbuilding", "enjoy", "creative"))
        recommendation = "mixed" if cautions and positive else "unlikely" if cautions else "promising" if positive else "insufficient"
        return tuple(cautions), recommendation

    @staticmethod
    def _normalise_title(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", value.casefold())

    @staticmethod
    def _evidence_terms(story: StoryPageEvidence) -> tuple[str, ...]:
        raw = [story.title, *story.genres, *story.tags]
        stop = {"the", "and", "with", "from", "this", "that", "story", "novel"}
        terms = []
        for value in raw:
            clean = " ".join(str(value).casefold().split())
            if len(clean) >= 4 and clean not in stop:
                terms.append(clean)
            terms.extend(word for word in re.findall(r"[a-z0-9]+", clean) if len(word) >= 5 and word not in stop)
        return tuple(dict.fromkeys(terms))[:40]

    @staticmethod
    def _focus_terms(focus: str) -> tuple[str, ...]:
        stop = {"what", "when", "where", "which", "with", "that", "this", "from", "does", "about", "into", "have", "story"}
        words = [word for word in re.findall(r"[a-z0-9]+", focus.casefold()) if len(word) >= 4 and word not in stop]
        return tuple(dict.fromkeys(words))[:30]
