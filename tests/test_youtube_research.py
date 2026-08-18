import unittest

from Brain.Team.researcher import Researcher
from Runtime.Research.youtube import (
    TranscriptSnippet,
    TranscriptUnavailable,
    YouTubeTranscriptEvidence,
    YouTubeTranscriptProvider,
    youtube_video_id,
)


class FakeSnippet:
    def __init__(self, text, start, duration=2.0):
        self.text = text
        self.start = start
        self.duration = duration


class FakeTranscript(list):
    language = "English"
    is_generated = True


class FakeApi:
    def __init__(self, transcript=None, error=None):
        self.transcript = transcript
        self.error = error
        self.calls = []

    def fetch(self, video_id, languages):
        self.calls.append((video_id, languages))
        if self.error:
            raise self.error
        return self.transcript


class YouTubeResearchTest(unittest.TestCase):
    def test_video_id_accepts_public_forms_and_rejects_non_youtube(self):
        video_id = "dQw4w9WgXcQ"
        self.assertEqual(youtube_video_id(f"https://www.youtube.com/watch?v={video_id}"), video_id)
        self.assertEqual(youtube_video_id(f"https://youtu.be/{video_id}"), video_id)
        self.assertEqual(youtube_video_id(f"https://www.youtube.com/shorts/{video_id}"), video_id)
        with self.assertRaises(TranscriptUnavailable):
            youtube_video_id(f"https://example.com/watch?v={video_id}")

    def test_provider_returns_bounded_source_linked_transcript(self):
        api = FakeApi(FakeTranscript([FakeSnippet(" Harem adventure review ", 12.5)]))
        evidence = YouTubeTranscriptProvider(api).fetch("https://youtu.be/dQw4w9WgXcQ")
        self.assertEqual(api.calls, [("dQw4w9WgXcQ", ["en"])])
        self.assertEqual(evidence.source_url, "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(evidence.snippets[0].text, "Harem adventure review")
        self.assertTrue(evidence.is_generated)

    def test_provider_fails_closed_without_exposing_transport_error(self):
        provider = YouTubeTranscriptProvider(FakeApi(error=RuntimeError("secret transport detail")))
        with self.assertRaisesRegex(TranscriptUnavailable, "No usable public English transcript") as raised:
            provider.fetch("https://youtu.be/dQw4w9WgXcQ")
        self.assertNotIn("secret", str(raised.exception))

    def test_mixed_report_links_claims_and_preserves_source_roles(self):
        researcher = Researcher()
        story = researcher.story_page_evidence(
            {
                "title": "Sunlit Quest",
                "synopsis": "A warm household explores a bright fantasy world.",
                "genres": ["Adventure", "Harem"],
                "tags": ["Found Family"],
                "reviews": [],
            },
            "https://www.scribblehub.com/series/1/sunlit-quest/",
        )
        transcript = YouTubeTranscriptEvidence(
            "dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "English",
            True,
            (
                TranscriptSnippet("The harem and found family elements are handled well.", 65.0, 4.0),
                TranscriptSnippet("The harem gets dark later and some readers may drop it.", 120.0, 3.0),
            ),
        )
        report = researcher.report_mixed_story_youtube(story, transcript, "Does the story use harem and found-family elements without becoming grimdark?", "now")
        self.assertIn("Scribble Hub supplies observed", report)
        self.assertIn("YouTube supplies speaker-reported", report)
        self.assertIn("1:05", report)
        self.assertIn("&t=65s", report)
        self.assertIn("possible conflict", report)
        self.assertIn("Keyword overlap establishes relevance, not truth", report)

    def test_generic_single_keyword_does_not_fake_corroboration(self):
        researcher = Researcher()
        story = researcher.story_page_evidence(
            {"title": "Sunlit Quest", "synopsis": "A warm fantasy journey.", "genres": ["Harem"], "tags": [], "reviews": []},
            "https://www.scribblehub.com/series/1/sunlit-quest/",
        )
        transcript = YouTubeTranscriptEvidence(
            "dQw4w9WgXcQ", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "English", False,
            (TranscriptSnippet("Many unrelated stories use the word harem.", 4.0, 2.0),),
        )
        report = researcher.report_mixed_story_youtube(story, transcript, "Does this specific story match the video?", "now")
        self.assertIn("does not corroborate", report)
        self.assertNotIn("[0:04]", report)

    def test_focus_relevance_is_not_misreported_as_page_corroboration(self):
        researcher = Researcher()
        story = researcher.story_page_evidence(
            {"title": "Echoes of the Multiverse", "synopsis": "What-if stories from several universes.", "genres": ["Fanfiction"], "tags": [], "reviews": []},
            "https://www.scribblehub.com/series/1/echoes/",
        )
        transcript = YouTubeTranscriptEvidence(
            "DCrFkaZL254", "https://www.youtube.com/watch?v=DCrFkaZL254", "English", True,
            (TranscriptSnippet("I've come to bargain. This is endless looped time.", 30.0, 4.0),),
        )
        report = researcher.report_mixed_story_youtube(
            story, transcript, "How does the Dormammu bargain establish the endless time loop?", "now"
        )
        self.assertIn("relevant to the explicit research focus", report)
        self.assertIn("does not independently corroborate", report)


if __name__ == "__main__":
    unittest.main()
