"""Visible, user-controlled review of Modesty's narrative Chronicle."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QLineEdit,
    QMessageBox, QPlainTextEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout,
)

from Brain.Memory import ConversationMemory, MemoryStoreError


class ChronicleEditDialog(QDialog):
    def __init__(self, episode=None, parent=None):
        super().__init__(parent)
        episode = episode or {}
        self.setWindowTitle("Chronicle episode")
        self.setMinimumWidth(620)
        layout = QFormLayout(self)
        self.fields = {}
        for key, label in (
            ("title", "Title"), ("narrative_date", "Narrative date"),
            ("setting", "Setting"), ("participants", "Participants"),
            ("themes", "Themes"), ("consequences", "Consequences"),
            ("parent_arc", "Parent arc"),
        ):
            field = QLineEdit(str(episode.get(key, "")))
            self.fields[key] = field
            layout.addRow(label, field)
        self.summary = QPlainTextEdit(str(episode.get("summary", "")))
        self.summary.setMaximumHeight(130)
        self.summary.setPlaceholderText("A compact narrative summary, not a transcript.")
        layout.addRow("Summary", self.summary)
        self.status = QComboBox()
        self.status.addItems(("active", "consolidated", "retired", "contradicted"))
        self.status.setCurrentText(episode.get("status", "active"))
        layout.addRow("Status", self.status)
        self.provenance = QComboBox()
        self.provenance.addItems(("Drew-approved", "conversation-derived", "self-authored"))
        self.provenance.setCurrentText(episode.get("provenance", "Drew-approved"))
        layout.addRow("Provenance", self.provenance)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._accept_if_valid)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _accept_if_valid(self):
        if not self.fields["title"].text().strip() or not self.summary.toPlainText().strip():
            QMessageBox.warning(self, "Incomplete episode", "Enter a title and summary.")
            return
        self.accept()

    def values(self):
        values = {key: field.text().strip() for key, field in self.fields.items()}
        values.update(summary=self.summary.toPlainText().strip(), status=self.status.currentText(), provenance=self.provenance.currentText())
        return values


class ChronicleDialog(QDialog):
    def __init__(self, memory: ConversationMemory, parent=None):
        super().__init__(parent)
        self.memory = memory
        self.setWindowTitle("Modesty's Personal Chronicle — Narrative")
        self.resize(940, 500)
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(("Title", "Date", "Themes", "Status", "Provenance"))
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(0, self.table.horizontalHeader().ResizeMode.Stretch)
        self.table.doubleClicked.connect(self._edit)
        layout.addWidget(self.table)
        actions = QHBoxLayout()
        for label, handler in (("Add", self._add), ("Edit", self._edit), ("Retire", self._retire), ("Delete", self._delete)):
            button = QPushButton(label); button.clicked.connect(handler); actions.addWidget(button)
        actions.addStretch()
        close = QPushButton("Close"); close.clicked.connect(self.accept); actions.addWidget(close)
        layout.addLayout(actions)
        self._refresh()

    def _refresh(self):
        try: episodes = self.memory.chronicle_episodes()
        except MemoryStoreError as error:
            QMessageBox.critical(self, "Chronicle unavailable", str(error)); return
        self.table.setRowCount(0)
        for episode in episodes:
            row = self.table.rowCount(); self.table.insertRow(row)
            title = QTableWidgetItem(episode["title"]); title.setData(Qt.ItemDataRole.UserRole, episode)
            self.table.setItem(row, 0, title)
            for column, key in enumerate(("narrative_date", "themes", "status", "provenance"), 1):
                self.table.setItem(row, column, QTableWidgetItem(episode[key]))

    def _selected(self):
        row = self.table.currentRow()
        return None if row < 0 else self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def _add(self):
        dialog = ChronicleEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try: self.memory.add_chronicle_episode(**dialog.values())
            except (MemoryStoreError, ValueError) as error: QMessageBox.warning(self, "Episode not saved", str(error))
            self._refresh()

    def _edit(self):
        episode = self._selected()
        if episode is None: return
        dialog = ChronicleEditDialog(episode, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try: self.memory.update_chronicle_episode(episode["id"], **dialog.values())
            except (MemoryStoreError, ValueError) as error: QMessageBox.warning(self, "Episode not updated", str(error))
            self._refresh()

    def _retire(self):
        episode = self._selected()
        if episode is None: return
        episode["status"] = "retired"
        try: self.memory.update_chronicle_episode(episode["id"], **episode)
        except (MemoryStoreError, ValueError) as error: QMessageBox.warning(self, "Episode not retired", str(error))
        self._refresh()

    def _delete(self):
        episode = self._selected()
        if episode is None: return
        answer = QMessageBox.question(self, "Delete Chronicle episode", f"Delete '{episode['title']}' permanently?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            try: self.memory.delete_chronicle_episode(episode["id"])
            except MemoryStoreError as error: QMessageBox.warning(self, "Episode not deleted", str(error))
            self._refresh()
