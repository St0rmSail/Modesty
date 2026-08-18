"""Read Modesty's authoritative local command guide."""

from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMMAND_HELP_PATH = PROJECT_ROOT / "Documentation" / "COMMANDS.md"


TOPICS = {
    "grand library": "Grand Library",
    "researcher": "Researcher",
    "librarian": "Librarian",
    "briefing": "Briefings",
    "briefings": "Briefings",
    "archivist": "Archivist",
    "library": "Local Library search",
    "chat": "Conversation",
    "conversation": "Conversation",
    "time": "Time zones",
    "time zone": "Time zones",
    "time zones": "Time zones",
    "schedule": "Schedule and reminders",
    "reminders": "Schedule and reminders",
}


def command_help(topic: str | None = None) -> str:
    """Return a bounded section from the local guide, not model recollection."""
    text = COMMAND_HELP_PATH.read_text(encoding="utf-8-sig")
    if topic:
        heading = TOPICS.get(topic.casefold().strip())
        if heading:
            match = re.search(
                rf"^## {re.escape(heading)}\s*$\n(?P<body>.*?)(?=^## |\Z)",
                text,
                re.MULTILINE | re.DOTALL,
            )
            if match:
                return f"{heading}\n\n{match.group('body').strip()}"
    return (
        "Modesty's command help\n\n"
        "Available sections: Grand Library, Researcher, Librarian, Briefings, Archivist, Local Library search, Conversation, Time zones, and Schedule and reminders.\n\n"
        "Ask, for example: Help with the Grand Library"
    )
