import unittest

from Brain.Team.delegation import TeamDelegator
from Runtime.Core.command_help import command_help


class CommandHelpTest(unittest.TestCase):
    def test_grand_library_help_explains_local_and_online_difference(self):
        text = command_help("Grand Library")
        self.assertIn("Open the Grand Library`", text)
        self.assertIn("Open the Grand Library online`", text)
        self.assertIn("internet remains disconnected", text)
        self.assertIn("Opening it sends nothing", text)

    def test_delegator_returns_help_without_model_fallback(self):
        delegator = TeamDelegator.__new__(TeamDelegator)
        result = delegator.handle("Help with the Grand Library")
        self.assertTrue(result.handled)
        self.assertIn("Close the Grand Library", result.response)

        index = delegator.handle("What commands can I use?")
        self.assertTrue(index.handled)
        self.assertIn("Available sections", index.response)

        followup = delegator.handle("the Grand Library please")
        self.assertTrue(followup.handled)
        self.assertIn("Open the Grand Library online", followup.response)

    def test_natural_help_requests_and_chat_help_are_deterministic(self):
        delegator = TeamDelegator.__new__(TeamDelegator)
        reminder = delegator.handle("remind me how to open the Grand Library")
        self.assertTrue(reminder.handled)
        self.assertIn("local loopback test mode", reminder.response)

        chat = delegator.handle("Help with chat")
        self.assertTrue(chat.handled)
        self.assertIn("Ordinary conversation does not require a command", chat.response)

    def test_topic_fragment_is_not_hijacked_without_help_context(self):
        delegator = TeamDelegator.__new__(TeamDelegator)
        self.assertFalse(delegator.handle("the Grand Library please").handled)

    def test_graceful_exit_is_deterministic_and_documented(self):
        delegator = TeamDelegator.__new__(TeamDelegator)
        result = delegator.handle("Goodbye, Modesty")
        self.assertTrue(result.handled)
        self.assertEqual(result.response, "Goodbye, Drew.")
        self.assertEqual(result.action, "close_study")
        self.assertIn("`Bye`", command_help("chat"))

    def test_schedule_help_is_local_and_exact(self):
        delegator = TeamDelegator.__new__(TeamDelegator)
        result = delegator.handle("Help with reminders")
        self.assertTrue(result.handled)
        self.assertIn("Remind me on 2026-08-16 at 09:30", result.response)
        self.assertIn("not implemented yet", result.response)

    def test_researcher_help_explains_story_investigation_boundary(self):
        text = command_help("researcher")
        self.assertIn("Investigate current story page", text)
        self.assertIn("does not download chapters", text)
        self.assertIn("ordinary Briefing decision", text)
        self.assertIn("Add current story to comparison", text)
        self.assertIn("Return to latest listings", text)
        self.assertIn("two or three pages", text)
        self.assertIn("lead rather than proof", text)
        self.assertIn("Add YouTube transcript and prepare mixed-source briefing", text)
        self.assertIn("speaker-reported evidence", text)
        self.assertIn("without account access", text)
        self.assertIn("state the research focus", text)
        self.assertIn("focus-only relevance", text)

    def test_librarian_help_is_bounded_and_deterministic(self):
        text = command_help("librarian")
        self.assertIn("Ask the Librarian to inventory The Stacks", text)
        self.assertIn("Ask the Librarian to repair: <filename>", text)
        self.assertIn("Ask the Librarian to examine: <relative Intake path>", text)
        self.assertIn("Ask the Librarian to find: <words or phrase>", text)
        self.assertIn("Approve Librarian shelving: <LS-ID>", text)
        self.assertIn("Ask the Librarian to open: <title or Stacks path> at Chapter <number>", text)
        self.assertIn("Continue reading: <RP-ID>", text)
        self.assertIn("Mark my place: <RP-ID>", text)
        self.assertIn("Ask the Librarian to resume: <title or Stacks path>", text)
        self.assertIn("Ask the Librarian to identify works and editions", text)
        self.assertIn("Ask the Librarian to review edition groups", text)
        self.assertIn("Intake", text)
        self.assertIn("does not rename", text)
        self.assertIn("Keep Repair", text)
        self.assertIn("Toss Repair", text)
        self.assertIn("2 MiB", text)

        delegator = TeamDelegator.__new__(TeamDelegator)
        result = delegator.handle("Help with the Librarian")
        self.assertTrue(result.handled)
        self.assertIn("read-only", result.response)


if __name__ == "__main__":
    unittest.main()
