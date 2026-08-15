"""Evidence-led reports from the unseen Researcher Team member."""

from dataclasses import dataclass
from typing import Iterable


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
