"""Large, legible local surface for exact-edition reading passages."""

import re

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget


class ReadingDesk(QWidget):
    """Present bounded Librarian passages without turning them into reports."""

    closed = Signal()
    command_submitted = Signal(str)
    SESSION_PATTERN = re.compile(r"(?:Continue reading|Mark my place):\s*(RP-[A-F0-9]{8})")
    RESPONSE_PATTERN = re.compile(
        r"^The Librarian (?:opened|resumed) (?P<title>.+?) — (?P<author>.+?)\n"
        r"(?P<section>[^\n]+)\nSource: (?P<source>[^\n]+)\n\n(?P<text>.*?)\n\n"
        r"(?P<ending>End of this chapter\.|More remains in this chapter\.)\n"
        r"To continue.*?\nTo confirm.*$", re.DOTALL,
    )

    def __init__(self):
        super().__init__()
        self._pages: list[dict[str, str]] = []
        self._page_index = -1
        self.setObjectName("readingDesk")
        self.setStyleSheet("""
            QWidget#readingDesk { background: rgba(20, 15, 10, 242); border: 2px solid #d5ad66; border-radius: 14px; }
            QLabel { color: #ead8b8; font-size: 15px; }
            QLabel#readingTitle { color: #fff2d8; font-size: 24px; font-weight: bold; }
            QPlainTextEdit { background: rgba(250, 241, 220, 238); color: #241b13; border: 1px solid #b88a4b; padding: 22px; font-size: 19px; }
            QLineEdit { background: rgba(255, 250, 240, 245); color: #261c13; border: 1px solid #b88a4b; border-radius: 7px; padding: 9px; font-size: 15px; }
            QPushButton { background: #8b5d2e; color: white; border: 1px solid #d5ad66; border-radius: 7px; padding: 9px 13px; font-size: 14px; font-weight: bold; }
            QPushButton:disabled { background: #5e5144; color: #a99c8c; border-color: #776958; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        header = QHBoxLayout()
        self.title = QLabel("Reading Desk"); self.title.setObjectName("readingTitle")
        header.addWidget(self.title); header.addStretch()
        self.location = QLabel(); header.addWidget(self.location)
        layout.addLayout(header)
        self.source = QLabel(); layout.addWidget(self.source)
        self.text = QPlainTextEdit(); self.text.setReadOnly(True)
        layout.addWidget(self.text, stretch=1)
        self.status = QLabel("The book remains unchanged."); layout.addWidget(self.status)
        note_row = QHBoxLayout()
        self.note = QLineEdit(); self.note.setPlaceholderText("Optional private note for this passage...")
        note_row.addWidget(self.note)
        self.note_button = QPushButton("Bookmark with Note"); self.note_button.clicked.connect(self._bookmark_with_note)
        note_row.addWidget(self.note_button); layout.addLayout(note_row)
        controls = QHBoxLayout()
        self.previous_button = QPushButton("Previous"); self.previous_button.clicked.connect(self._previous)
        self.next_button = QPushButton("Next Passage"); self.next_button.clicked.connect(self._next)
        self.save_button = QPushButton("Save Place"); self.save_button.clicked.connect(lambda: self.command_submitted.emit("save my place"))
        self.bookmark_button = QPushButton("Bookmark"); self.bookmark_button.clicked.connect(lambda: self.command_submitted.emit("bookmark this"))
        for button in (self.previous_button, self.next_button, self.save_button, self.bookmark_button): controls.addWidget(button)
        controls.addStretch()
        close = QPushButton("Close"); close.clicked.connect(self.closed.emit); controls.addWidget(close)
        layout.addLayout(controls)
        self._refresh_controls()

    def open_response(self, response: str) -> bool:
        page = self._parse(response)
        if page is None:
            return False
        self._pages = [page]
        self._page_index = 0
        self._render_page()
        return True

    def accept_response(self, response: str):
        page = self._parse(response)
        if page is not None:
            if not self._pages or page != self._pages[-1]: self._pages.append(page)
            self._page_index = len(self._pages) - 1
            self._render_page()
            return
        self.status.setText(response.replace("\n", " ").strip())
        if "marked your confirmed place" in response and self._pages:
            self._pages[-1]["closed"] = "yes"
            self._refresh_controls()

    @classmethod
    def _parse(cls, response: str) -> dict[str, str] | None:
        match = cls.RESPONSE_PATTERN.match(response.strip())
        session = cls.SESSION_PATTERN.search(response)
        return {**match.groupdict(), "session_id": session.group(1)} if match and session else None

    def _render_page(self):
        page = self._pages[self._page_index]
        self.title.setText(f"{page['title']} — {page['author']}")
        self.location.setText(page["section"]); self.source.setText(page["source"])
        self.text.setPlainText(page["text"]); self.text.verticalScrollBar().setValue(0)
        self.status.setText(f"{page['ending']} The book remains unchanged.")
        self._refresh_controls()

    def _refresh_controls(self):
        latest = bool(self._pages) and self._page_index == len(self._pages) - 1
        open_session = latest and self._pages[-1].get("closed") != "yes" if self._pages else False
        self.previous_button.setEnabled(self._page_index > 0); self.next_button.setEnabled(bool(self._pages))
        self.next_button.setEnabled(bool(self._pages) and (not latest or open_session))
        self.save_button.setEnabled(open_session); self.bookmark_button.setEnabled(open_session); self.note_button.setEnabled(open_session)
        if not latest and self._pages:
            self.status.setText("Reviewing an earlier displayed passage. Return to the latest passage to save or bookmark.")

    def _previous(self):
        if self._page_index > 0:
            self._page_index -= 1; self._render_page()

    def _next(self):
        if self._page_index < len(self._pages) - 1:
            self._page_index += 1; self._render_page(); return
        if self._pages: self.command_submitted.emit(f"Continue reading: {self._pages[-1]['session_id']}")

    def _bookmark_with_note(self):
        note = self.note.text().strip()
        if not note:
            self.status.setText("Add a short private note first, or use Bookmark without a note."); return
        self.note.clear(); self.command_submitted.emit(f"remember this passage: {note}")
