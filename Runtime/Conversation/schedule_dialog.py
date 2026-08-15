"""Visible review surface for Modesty's local schedule."""

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout

from Runtime.Time import ReminderStore


class ScheduleDialog(QDialog):
    def __init__(self, store: ReminderStore, parent=None):
        super().__init__(parent)
        self.store = store
        self.setWindowTitle("Modesty's Local Schedule")
        self.resize(800, 430)
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(("Due", "Reminder", "Status", "ID"))
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(1, self.table.horizontalHeader().ResizeMode.Stretch)
        layout.addWidget(self.table)
        actions = QHBoxLayout()
        complete = QPushButton("Complete"); complete.clicked.connect(self._complete); actions.addWidget(complete)
        delete = QPushButton("Delete"); delete.clicked.connect(self._delete); actions.addWidget(delete)
        actions.addStretch()
        close = QPushButton("Close"); close.clicked.connect(self.accept); actions.addWidget(close)
        layout.addLayout(actions)
        self._refresh()

    def _refresh(self):
        self.table.setRowCount(0)
        for reminder in self.store.all():
            row = self.table.rowCount(); self.table.insertRow(row)
            due = datetime.fromisoformat(reminder["due_at"]).astimezone().strftime("%Y-%m-%d %H:%M")
            due_item = QTableWidgetItem(due); due_item.setData(Qt.ItemDataRole.UserRole, reminder["id"])
            self.table.setItem(row, 0, due_item)
            self.table.setItem(row, 1, QTableWidgetItem(reminder["text"]))
            self.table.setItem(row, 2, QTableWidgetItem(reminder["status"]))
            self.table.setItem(row, 3, QTableWidgetItem(str(reminder["id"])))

    def _selected_id(self):
        row = self.table.currentRow()
        return None if row < 0 else int(self.table.item(row, 0).data(Qt.ItemDataRole.UserRole))

    def _complete(self):
        reminder_id = self._selected_id()
        if reminder_id is None: return
        try: self.store.complete(reminder_id)
        except ValueError as error: QMessageBox.warning(self, "Reminder not completed", str(error))
        self._refresh()

    def _delete(self):
        reminder_id = self._selected_id()
        if reminder_id is None: return
        answer = QMessageBox.question(self, "Delete reminder", f"Delete reminder #{reminder_id} permanently?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            try: self.store.delete(reminder_id)
            except ValueError as error: QMessageBox.warning(self, "Reminder not deleted", str(error))
            self._refresh()
