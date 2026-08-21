import unittest

from Runtime.Reading.reading_desk import ReadingDesk


class ReadingDeskTest(unittest.TestCase):
    def test_parses_only_complete_librarian_reading_response(self):
        response = (
            "The Librarian opened Test Book — Test Author\n"
            "Chapter 3\nSource: The Stacks/Originals/Test Book.epub\n\n"
            "A complete bounded passage.\n\nMore remains in this chapter.\n"
            "To continue without changing your saved place, say: Continue reading: RP-1234ABCD\n"
            "To confirm the end of this displayed passage as your next unread position, say: "
            "Mark my place: RP-1234ABCD"
        )
        page = ReadingDesk._parse(response)
        self.assertEqual(page["title"], "Test Book")
        self.assertEqual(page["section"], "Chapter 3")
        self.assertEqual(page["text"], "A complete bounded passage.")
        self.assertEqual(page["session_id"], "RP-1234ABCD")
        self.assertIsNone(ReadingDesk._parse("The Librarian found a book."))


if __name__ == "__main__":
    unittest.main()
