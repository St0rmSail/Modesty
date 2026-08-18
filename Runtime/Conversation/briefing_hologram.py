"""Large-format translucent surface for an undecided Pending Report."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from Brain.Team.archivist import Archivist
from Brain.Team.librarian import Librarian, LibrarianError
from Runtime.Core import team_status
from Runtime.Knowledge.catalog import KnowledgeCatalog
from Runtime.Knowledge.stores import KnowledgeStores
from Runtime.Research.pending_reports import PendingReportStore
from Runtime.Reading import ReadingCollection


class BriefingHologram(QWidget):
    closed = Signal()
    question_submitted = Signal(str)
    outcome_recorded = Signal(str)

    def __init__(self, store: PendingReportStore | None = None):
        super().__init__()
        self.report_id = None
        self.store = store or PendingReportStore()
        self.selected_destination = None
        self.repair_id = None
        self.setObjectName("briefingHologram")
        self.setStyleSheet(
            """
            QWidget#briefingHologram { background: rgba(4, 35, 49, 225); border: 2px solid #63e6ff; border-radius: 14px; }
            QLabel { color: #c8f8ff; font-size: 15px; }
            QLabel#briefingTitle { font-size: 23px; font-weight: bold; }
            QPlainTextEdit { background: rgba(0, 18, 28, 205); color: #e8fbff; border: 1px solid #3ebfd8; padding: 14px; font-size: 17px; }
            QLineEdit { background: rgba(235, 252, 255, 240); color: #072531; border: 1px solid #63e6ff; border-radius: 7px; padding: 9px; font-size: 15px; }
            QPushButton { background: #126d83; color: white; border: 1px solid #63e6ff; border-radius: 7px; padding: 9px 13px; font-size: 14px; font-weight: bold; }
            QPushButton:disabled { background: #34464d; color: #83949a; border-color: #52656c; }
            QPushButton[selected="true"] { background: #159a72; color: white; border: 2px solid #b8ffe9; }
            """
        )
        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        self.title = QLabel()
        self.title.setObjectName("briefingTitle")
        header.addWidget(self.title)
        header.addStretch()
        self.mode = QLabel()
        self.mode.setStyleSheet(
            "QLabel { background: rgba(8, 72, 91, 220); border: 1px solid #63e6ff; "
            "border-radius: 7px; padding: 6px 10px; font-weight: bold; }"
        )
        header.addWidget(self.mode)
        layout.addLayout(header)
        self.report = QPlainTextEdit()
        self.report.setReadOnly(True)
        layout.addWidget(self.report, stretch=1)
        self.status = QLabel("Pending — choose what happens to this report.")
        layout.addWidget(self.status)
        question_row = QHBoxLayout()
        self.question = QLineEdit()
        self.question.setPlaceholderText("Ask Modesty about this briefing...")
        self.question.returnPressed.connect(self._ask)
        question_row.addWidget(self.question)
        ask = QPushButton("Ask")
        ask.clicked.connect(self._ask)
        question_row.addWidget(ask)
        layout.addLayout(question_row)
        buttons = QHBoxLayout()
        self.disposition_buttons = {}
        for label, destination in (("Keep Privately", "private"), ("Bookshelf Inbox", "bookshelf"), ("Toss", "toss")):
            button = QPushButton(label)
            button.clicked.connect(lambda checked=False, choice=destination: self._resolve(choice))
            self.disposition_buttons[destination] = button
            buttons.addWidget(button)
        self.close_button = QPushButton("Close")
        self.close_button.setEnabled(False)
        self.close_button.setToolTip("Choose Keep Privately, Bookshelf Inbox, or Toss first")
        self.close_button.clicked.connect(self._close)
        buttons.addWidget(self.close_button)
        layout.addLayout(buttons)

    def open_report(self, report_id: str):
        pending = self.store.load(report_id)
        self.report_id = pending.report_id
        self.repair_id = (
            pending.provider.partition(":")[2]
            if pending.provider.casefold().startswith("librarian:")
            else None
        )
        self.selected_destination = None
        self.close_button.setEnabled(False)
        self.close_button.setToolTip("Choose Keep Privately, Bookshelf Inbox, or Toss first")
        for button in self.disposition_buttons.values():
            button.setEnabled(True)
            button.setVisible(True)
            button.setProperty("selected", False)
            button.style().unpolish(button)
            button.style().polish(button)
        if self.repair_id:
            self.disposition_buttons["private"].setText("Keep Repair")
            self.disposition_buttons["bookshelf"].setVisible(False)
            self.disposition_buttons["toss"].setText("Toss Repair")
            self.close_button.setToolTip("Choose Keep Repair or Toss Repair first")
        else:
            self.disposition_buttons["private"].setText("Keep Privately")
            self.disposition_buttons["bookshelf"].setText("Bookshelf Inbox")
            self.disposition_buttons["toss"].setText("Toss")
        self.title.setText(pending.title)
        self.mode.setText(
            f"⚡ ONLINE · {pending.provider.upper()}"
            if pending.provider.casefold() not in {"local"} and not self.repair_id
            else "LOCAL BRIEFING"
        )
        self.report.setPlainText(pending.body)
        self.status.setText(
            f"Pending Repair {self.repair_id} — provisional Workbench derivative awaiting decision."
            if self.repair_id
            else f"Pending Report {pending.report_id} — nothing has been filed."
        )

    def append_modesty_response(self, response: str):
        self.report.appendPlainText(f"\n\nModesty: {response}")

    def _ask(self):
        question = self.question.text().strip()
        if question:
            self.question.clear()
            self.question_submitted.emit(question)

    def _resolve(self, destination: str):
        if not self.report_id:
            return
        pending = self.store.load(self.report_id)
        if self.repair_id:
            if destination not in {"private", "toss"}:
                return
            try:
                librarian = Librarian(ReadingCollection().initialize())
                path = librarian.resolve_repair(self.repair_id, keep=destination == "private")
            except (LibrarianError, RuntimeError) as error:
                self.status.setText(str(error))
                return
            self.store.discard(pending.report_id)
            team_status.set_member_state("librarian", "ready")
            if path is None:
                self.status.setText("Repair tossed. The original remains unchanged.")
                outcome = (
                    "You reviewed the Librarian's proposed repair and tossed it. "
                    "The provisional derivative was deleted; the original remains unchanged."
                )
            else:
                self.status.setText(f"Repair kept in The Stacks Workbench: {path.name}")
                outcome = (
                    "You reviewed the Librarian's proposed repair and kept the derivative in "
                    f"The Stacks Workbench: {path.name}. The original remains unchanged."
                )
            self._finish_resolution(destination, outcome)
            return
        if destination == "toss":
            self.store.discard(pending.report_id)
            self.status.setText("Report tossed. No report content was filed.")
            outcome = (
                "You reviewed the Researcher's briefing and chose to toss it. "
                "No report content was filed."
            )
        else:
            paths = KnowledgeStores().initialize()
            archivist = Archivist(paths, KnowledgeCatalog())
            content = f"{pending.title}\n\n{pending.body}\n\nProvider: {pending.provider}\nCreated: {pending.created_at}"
            path = archivist.file_note("filing_cabinet" if destination == "private" else "bookshelf", content)
            self.store.discard(pending.report_id)
            self.status.setText(f"The Archivist received the report: {path.name}")
            if destination == "private":
                outcome = (
                    "You reviewed the Researcher's briefing and chose to keep it privately. "
                    f"The Archivist filed it in the Filing Cabinet Inbox: {path.name}"
                )
            else:
                outcome = (
                    "You reviewed the Researcher's briefing and sent it to the Bookshelf Inbox: "
                    f"{path.name}"
                )
        self._finish_resolution(destination, outcome)

    def _finish_resolution(self, destination: str, outcome: str):
        self.report_id = None
        self.repair_id = None
        self.selected_destination = destination
        for choice, button in self.disposition_buttons.items():
            button.setEnabled(False)
            button.setProperty("selected", choice == destination)
            button.style().unpolish(button)
            button.style().polish(button)
        self.close_button.setEnabled(True)
        self.close_button.setToolTip("Close the completed Briefing")
        self.outcome_recorded.emit(outcome)

    def _close(self):
        if self.report_id:
            return
        self.closed.emit()
