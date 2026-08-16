import unittest

from Brain.Team.researcher import Researcher, StoryFinding
from Runtime.Research.story_page import decode_story_evidence
from Runtime.Research.scribblehub import ScribbleHubListingParser, latest_harem_url


class ResearcherTest(unittest.TestCase):
    def test_embedded_browser_story_evidence_uses_explicit_json_transport(self):
        evidence = decode_story_evidence('{"title":"A Story","synopsis":"Visible synopsis"}')
        self.assertEqual(evidence["title"], "A Story")
        self.assertEqual(decode_story_evidence({"title": "unreliable Qt object"}), {})
        self.assertEqual(decode_story_evidence('["not", "an", "object"]'), {})

    def test_query_is_exact_and_reproducible(self):
        url = latest_harem_url()
        self.assertIn("gi=1015", url)
        self.assertIn("sort=dateadded", url)
        self.assertIn("order=desc", url)

    def test_report_returns_findings_assessment_sources_and_limits(self):
        report = Researcher().report_latest_harem(
            (
                StoryFinding(
                    "A New Quest",
                    "https://www.scribblehub.com/series/1/a-new-quest/",
                    "Author",
                    ("Adventure", "Harem", "Romance"),
                    "A bounded synopsis.",
                    8,
                    12,
                    "today",
                    ("Academy",),
                ),
                StoryFinding(
                    "Barely Begun",
                    "https://www.scribblehub.com/series/2/barely-begun/",
                    "Author Two",
                    ("Harem", "Smut"),
                    "Another synopsis.",
                    1,
                    0,
                    "today",
                    (),
                    ("Gore", "Sexual Content"),
                ),
            )
        )
        self.assertIn("The Researcher found 2", report)
        self.assertIn("Worth a closer look", report)
        self.assertIn("Too early to judge", report)
        self.assertIn("adult sexual content", report)
        self.assertIn("possible grim or distressing material signalled by Gore", report)
        self.assertIn("discovery candidates, not endorsements", report)
        self.assertIn("Nothing has been filed", report)
        self.assertEqual(report.count("https://www.scribblehub.com/series/"), 2)

    def test_empty_results_do_not_fake_a_report(self):
        report = Researcher().report_latest_harem(())
        self.assertIn("no usable current listings", report)
        self.assertIn("Nothing was filed", report)

    def test_public_listing_parser_extracts_bounded_metadata(self):
        parser = ScribbleHubListingParser(limit=1)
        parser.feed(
            '<div class="search_main_box"><div class="search_body">'
            '<div class="search_title"><a href="https://www.scribblehub.com/series/1/test/">Test Story</a></div>'
            '<div class="search_stats"><span>7 Chapters</span><span>12 Readers</span>'
            '<span title="Last Updated">2 hours ago</span>'
            '<span title="Author"><a href="https://www.scribblehub.com/profile/1/author/">Writer</a></span></div>'
            '<div class="search_genre"><a>Adventure</a><a>Harem</a></div>'
            'A short synopsis.</div></div>'
        )
        self.assertEqual(len(parser.findings), 1)
        finding = parser.findings[0]
        self.assertEqual(finding.title, "Test Story")
        self.assertEqual(finding.author, "Writer")
        self.assertEqual(finding.genres, ("Adventure", "Harem"))
        self.assertEqual((finding.chapters, finding.readers), (7, 12))
        self.assertEqual(finding.last_updated, "2 hours ago")

    def test_story_investigation_separates_facts_reviews_and_limits(self):
        report = Researcher().report_story_page(
            {
                "title": "A Complicated Voyage",
                "synopsis": "A heroine explores a difficult fantasy world.",
                "genres": ["Adventure", "Harem"],
                "tags": ["Character Growth", "R-18"],
                "stats": "20 Chapters 100 Readers",
                "reviews": ["Well written and creative worldbuilding.", "I had to drop it after a stalking reveal ruined the romance."],
            },
            "https://www.scribblehub.com/series/1/a-complicated-voyage/",
            "2026-08-16T10:00:00+02:00",
        )
        self.assertIn("Observed on the source page", report)
        self.assertIn("Reader-reported evidence", report)
        self.assertIn("Recommendation: MIXED", report)
        self.assertIn("late-story concern", report)
        self.assertIn("Nothing has been filed", report)

    def test_story_investigation_refuses_incomplete_or_non_https_evidence(self):
        with self.assertRaises(ValueError):
            Researcher().report_story_page({"title": "Missing synopsis"}, "https://www.scribblehub.com/series/1/test/", "now")

    def test_story_comparison_separates_agreement_differences_and_sources(self):
        researcher = Researcher()
        first = researcher.story_page_evidence(
            {"title": "Sunlit Quest", "synopsis": "A hero builds a warm household while exploring a bright new world.", "genres": ["Adventure", "Harem"], "tags": ["Found Family", "R-18"], "stats": "20 Chapters", "reviews": ["Creative worldbuilding and well written."]},
            "https://www.scribblehub.com/series/1/sunlit-quest/",
        )
        second = researcher.story_page_evidence(
            {"title": "Stormbound Court", "synopsis": "A heroine gathers allies while surviving a dangerous magical court.", "genres": ["Adventure", "Harem"], "tags": ["Politics", "Gore"], "stats": "30 Chapters", "reviews": ["I had to drop it after the abuse reveal."]},
            "https://www.scribblehub.com/series/2/stormbound-court/",
        )
        report = researcher.report_story_comparison((first, second), "2026-08-16T12:00:00+02:00")
        self.assertIn("compared 2 public", report)
        self.assertIn("Shared genres: Adventure, Harem", report)
        self.assertIn("Distinguishing signals", report)
        self.assertIn("one source type", report)
        self.assertEqual(report.count("https://www.scribblehub.com/series/"), 2)

    def test_story_comparison_flags_likely_duplicate_without_claiming_proof(self):
        researcher = Researcher()
        page = {"title": "Same Tale", "synopsis": "A long and unusually specific synopsis about a magical household journey.", "genres": ["Harem"], "tags": [], "reviews": []}
        first = researcher.story_page_evidence(page, "https://www.scribblehub.com/series/1/same-tale/")
        second = researcher.story_page_evidence(page, "https://www.scribblehub.com/series/2/same-tale-copy/")
        report = researcher.report_story_comparison((first, second), "now")
        self.assertIn("duplicate or cross-posted editions", report)
        self.assertIn("lead, not proof", report)

    def test_story_comparison_requires_distinct_bounded_set(self):
        researcher = Researcher()
        story = researcher.story_page_evidence(
            {"title": "One", "synopsis": "A complete synopsis.", "genres": [], "tags": [], "reviews": []},
            "https://www.scribblehub.com/series/1/one/",
        )
        with self.assertRaises(ValueError):
            researcher.report_story_comparison((story,), "now")
        with self.assertRaises(ValueError):
            researcher.report_story_comparison((story, story), "now")


if __name__ == "__main__":
    unittest.main()
