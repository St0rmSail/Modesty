"""Visible, user-controlled management of approved personal memories."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from Brain.Memory import ConversationMemory, MemoryStoreError


CATEGORIES = (
    "Identity",
    "Preference",
    "Relationship",
    "Health",
    "Project",
    "Routine",
    "Other",
)


class MemoryEditDialog(QDialog):
    def __init__(self, category: str = "Preference", content: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Personal memory")
        self.setMinimumWidth(520)

        layout = QFormLayout(self)
        self.category = QComboBox()
        self.category.setEditable(True)
        self.category.addItems(CATEGORIES)
        self.category.setCurrentText(category)
        layout.addRow("Category", self.category)

        self.content = QPlainTextEdit()
        self.content.setPlaceholderText("What should Modesty remember?")
        self.content.setPlainText(content)
        self.content.setMaximumHeight(120)
        layout.addRow("Memory", self.content)
        layout.addRow("Source", QLabel("Added by Drew"))

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._accept_if_valid)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _accept_if_valid(self):
        if not self.category.currentText().strip() or not self.content.toPlainText().strip():
            QMessageBox.warning(self, "Incomplete memory", "Enter a category and memory.")
            return
        self.accept()

    def values(self) -> tuple[str, str]:
        return self.category.currentText().strip(), self.content.toPlainText().strip()


class PersonalMemoryDialog(QDialog):
    """List, add, correct, and delete explicitly approved memories."""

    def __init__(self, memory: ConversationMemory, parent=None):
        super().__init__(parent)
        self.memory = memory
        self.setWindowTitle("Modesty's Personal Memory")
        self.resize(800, 420)

        layout = QVBoxLayout(self)
        explanation = QLabel(
            "Only memories explicitly added or approved here are given to Modesty."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(("Category", "Memory", "Source"))
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, self.table.horizontalHeader().ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, self.table.horizontalHeader().ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, self.table.horizontalHeader().ResizeMode.ResizeToContents)
        self.table.doubleClicked.connect(self._edit)
        layout.addWidget(self.table)

        actions = QHBoxLayout()
        add_button = QPushButton("Add")
        add_button.clicked.connect(self._add)
        actions.addWidget(add_button)

        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self._edit)
        actions.addWidget(edit_button)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self._delete)
        actions.addWidget(delete_button)
        actions.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        actions.addWidget(close_button)
        layout.addLayout(actions)

        self._refresh()

    def _refresh(self):
        try:
            memories = self.memory.personal_memories()
        except MemoryStoreError as error:
            QMessageBox.critical(self, "Memory unavailable", str(error))
            return

        self.table.setRowCount(0)
        for memory in memories:
            row = self.table.rowCount()
            self.table.insertRow(row)
            category = QTableWidgetItem(memory["category"])
            category.setData(Qt.ItemDataRole.UserRole, memory["id"])
            self.table.setItem(row, 0, category)
            self.table.setItem(row, 1, QTableWidgetItem(memory["content"]))
            self.table.setItem(row, 2, QTableWidgetItem(memory["source"]))

    def _selected(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return {
            "id": self.table.item(row, 0).data(Qt.ItemDataRole.UserRole),
            "category": self.table.item(row, 0).text(),
            "content": self.table.item(row, 1).text(),
        }

    def _add(self):
        dialog = MemoryEditDialog(parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.memory.add_personal_memory(*dialog.values())
        except (MemoryStoreError, ValueError) as error:
            QMessageBox.warning(self, "Memory not saved", str(error))
            return
        self._refresh()

    def _edit(self):
        selected = self._selected()
        if selected is None:
            return
        dialog = MemoryEditDialog(selected["category"], selected["content"], self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self.memory.update_personal_memory(selected["id"], *dialog.values())
        except (MemoryStoreError, ValueError) as error:
            QMessageBox.warning(self, "Memory not updated", str(error))
            return
        self._refresh()

    def _delete(self):
        selected = self._selected()
        if selected is None:
            return
        answer = QMessageBox.question(
            self,
            "Delete personal memory",
            f"Delete this memory?\n\n{selected['content']}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            self.memory.delete_personal_memory(selected["id"])
        except MemoryStoreError as error:
            QMessageBox.warning(self, "Memory not deleted", str(error))
            return
        self._refresh()
