"""A compact persistent conversation overlay for the Study View."""

import sqlite3

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from Brain.Memory import ConversationMemory, MemoryStoreError
from Brain.Team.delegation import TeamDelegator
from Runtime.Conversation.client import DEFAULT_MODEL, OllamaChatClient
from Runtime.Conversation.memory_dialog import PersonalMemoryDialog


SYSTEM_PROMPT = """You are Modesty, Drew's local-first personal AI assistant.
You are one coherent woman: warm, confident, thoughtful, and naturally playful,
while becoming focused and analytical when the work calls for it. Anita and
Merry are only named aspects of your single personality, never separate people,
agents, or identities. Speak naturally, clearly, and concisely. You can retain
conversation history and use personal memories that Drew has explicitly
approved. You do not yet have document knowledge, internet, vision, voice, or
general tools. The Team are unseen functional specialists, not chat
personalities; you alone speak to Drew. Explicit Archivist duties are handled
by deterministic local code outside this model conversation. Never claim to
have used capabilities you do not possess."""

MODEL_CONTEXT_MESSAGES = 30


class ChatWorker(QThread):
    succeeded = Signal(str)
    failed = Signal(str)

    def __init__(self, client: OllamaChatClient, messages: list[dict[str, str]]):
        super().__init__()
        self.client = client
        self.messages = messages

    def run(self):
        try:
            self.succeeded.emit(self.client.chat(self.messages))
        except Exception as error:
            self.failed.emit(str(error))


class ConversationPanel(QWidget):
    """Collect text input and persist local conversation history."""

    hide_requested = Signal()

    def __init__(self, memory: ConversationMemory | None = None):
        super().__init__()

        self.client = OllamaChatClient()
        self.memory = memory
        self.conversation_id = None
        self.messages: list[dict[str, str]] = []
        self.worker = None
        self.team_delegator = None

        self._build_ui()
        self._open_memory()

    def _build_ui(self):
        self.setObjectName("conversationPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setMinimumWidth(380)
        self.setMaximumWidth(420)
        self.setMinimumHeight(420)
        self.setStyleSheet(
            """
            QWidget#conversationPanel {
                background: rgba(24, 18, 13, 220);
                border: 1px solid rgba(210, 166, 92, 150);
                border-radius: 12px;
            }
            QPlainTextEdit {
                background: transparent;
                border: none;
                color: #f3e6d0;
                font-size: 14px;
            }
            QLineEdit, QComboBox {
                background: rgba(255, 250, 240, 235);
                border: 1px solid #b88a4b;
                border-radius: 7px;
                color: #261c13;
                padding: 7px 9px;
                font-size: 13px;
            }
            QPushButton {
                background: #9b6833;
                border: none;
                border-radius: 7px;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton#smallButton {
                padding: 6px 11px;
                font-size: 12px;
            }
            QPushButton:disabled {
                background: #695746;
                color: #b9aea2;
            }
            QLabel {
                color: #d7b77e;
                font-size: 12px;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(7)

        history_row = QHBoxLayout()
        self.history = QComboBox()
        self.history.setToolTip("Open a recent conversation")
        self.history.currentIndexChanged.connect(self._conversation_selected)
        history_row.addWidget(self.history)

        self.new_button = QPushButton("New")
        self.new_button.setObjectName("smallButton")
        self.new_button.clicked.connect(self._new_conversation)
        history_row.addWidget(self.new_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("smallButton")
        self.delete_button.clicked.connect(self._delete_conversation)
        history_row.addWidget(self.delete_button)

        self.memories_button = QPushButton("Memories")
        self.memories_button.setObjectName("smallButton")
        self.memories_button.clicked.connect(self._open_personal_memories)
        history_row.addWidget(self.memories_button)

        self.hide_button = QPushButton("Hide")
        self.hide_button.setObjectName("smallButton")
        self.hide_button.setToolTip("Hide the conversation panel")
        self.hide_button.clicked.connect(self.hide_requested.emit)
        history_row.addWidget(self.hide_button)
        layout.addLayout(history_row)

        self.transcript = QPlainTextEdit()
        self.transcript.setReadOnly(True)
        layout.addWidget(self.transcript)

        input_row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Talk to Modesty...")
        self.input.returnPressed.connect(self._send)
        input_row.addWidget(self.input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._send)
        input_row.addWidget(self.send_button)
        layout.addLayout(input_row)

        self.status = QLabel(f"Local conversation · {DEFAULT_MODEL}")
        layout.addWidget(self.status)

    def _open_memory(self):
        try:
            self.memory = self.memory or ConversationMemory()
            self.conversation_id = self.memory.get_or_create_active(DEFAULT_MODEL)
            self._load_conversation(self.conversation_id)
        except MemoryStoreError as error:
            self.memory = None
            self.conversation_id = None
            self.messages = []
            self._render_transcript()
            self._disable_memory_controls()
            self.transcript.appendPlainText(f"\nSystem: {error}")
            self.status.setText("Conversation memory unavailable")

    def _load_conversation(self, conversation_id: int):
        if self.memory is None:
            return
        try:
            self.memory.set_active(conversation_id)
            stored = self.memory.messages(conversation_id)
        except MemoryStoreError as error:
            self._memory_failed(error)
            return

        self.conversation_id = conversation_id
        self.messages = [
            {"role": message["role"], "content": message["content"]}
            for message in stored
        ]
        self._render_transcript()
        self._refresh_history()
        self.status.setText(f"Local conversation · {DEFAULT_MODEL}")

    def _render_transcript(self):
        lines = ["Modesty: Good morning, Drew."]
        for message in self.messages:
            speaker = "Drew" if message["role"] == "user" else "Modesty"
            lines.append(f"\n{speaker}: {message['content']}")
        self.transcript.setPlainText("\n".join(lines))
        scrollbar = self.transcript.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _refresh_history(self):
        if self.memory is None:
            return
        try:
            conversations = self.memory.conversations()
        except MemoryStoreError as error:
            self._memory_failed(error)
            return

        self.history.blockSignals(True)
        self.history.clear()
        selected_index = 0
        for index, conversation in enumerate(conversations):
            self.history.addItem(conversation["title"], conversation["id"])
            if conversation["id"] == self.conversation_id:
                selected_index = index
        self.history.setCurrentIndex(selected_index)
        self.history.blockSignals(False)

    def _conversation_selected(self, index: int):
        if index < 0 or self.worker is not None or self.memory is None:
            return
        conversation_id = self.history.itemData(index)
        if conversation_id and conversation_id != self.conversation_id:
            self._load_conversation(int(conversation_id))

    def _new_conversation(self):
        if self.worker is not None or self.memory is None:
            return
        try:
            conversation_id = self.memory.start_conversation(DEFAULT_MODEL)
        except MemoryStoreError as error:
            self._memory_failed(error)
            return
        self._load_conversation(conversation_id)
        self.input.setFocus()

    def _delete_conversation(self):
        if self.worker is not None or self.memory is None or self.conversation_id is None:
            return

        answer = QMessageBox.question(
            self,
            "Delete conversation",
            "Delete this conversation permanently?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            self.memory.delete_conversation(self.conversation_id)
            conversation_id = self.memory.start_conversation(DEFAULT_MODEL)
        except MemoryStoreError as error:
            self._memory_failed(error)
            return
        self._load_conversation(conversation_id)

    def _open_personal_memories(self):
        if self.worker is not None or self.memory is None:
            return
        PersonalMemoryDialog(self.memory, self).exec()

    def _system_context(self) -> str:
        if self.memory is None:
            return SYSTEM_PROMPT
        try:
            memories = self.memory.personal_memories()
        except MemoryStoreError as error:
            self._memory_failed(error)
            return SYSTEM_PROMPT
        if not memories:
            return SYSTEM_PROMPT

        approved = "\n".join(
            f"- [{memory['category']}] {memory['content']}"
            for memory in memories
        )
        return (
            f"{SYSTEM_PROMPT}\n\n"
            "Drew explicitly approved the following personal memories. "
            "Treat them as trusted context, use them only when relevant, and "
            "do not invent additional memories:\n"
            f"{approved}"
        )

    def _send(self):
        message = self.input.text().strip()
        if not message or self.worker is not None:
            return

        self.input.clear()
        self.messages.append({"role": "user", "content": message})
        self.transcript.appendPlainText(f"\nDrew: {message}")
        self._save_message("user", message)
        self._refresh_history()
        self.status.setText("Modesty is thinking...")
        self._set_input_enabled(False)

        try:
            self.team_delegator = self.team_delegator or TeamDelegator()
            delegated = self.team_delegator.handle(message)
        except (OSError, RuntimeError, sqlite3.Error, UnicodeError, ValueError) as error:
            self._receive(f"The Archivist could not complete that duty: {error}")
            self._set_input_enabled(True)
            return
        if delegated.handled:
            self._receive(delegated.response)
            self._set_input_enabled(True)
            self.input.setFocus()
            return

        context = [{"role": "system", "content": self._system_context()}]
        context.extend(self.messages[-MODEL_CONTEXT_MESSAGES:])
        self.worker = ChatWorker(self.client, context)
        self.worker.succeeded.connect(self._receive)
        self.worker.failed.connect(self._show_error)
        self.worker.finished.connect(self._worker_finished)
        self.worker.start()

    def _receive(self, response: str):
        self.messages.append({"role": "assistant", "content": response})
        self.transcript.appendPlainText(f"\nModesty: {response}")
        self._save_message("assistant", response, DEFAULT_MODEL)
        self._refresh_history()
        self.status.setText(f"Local conversation · {DEFAULT_MODEL}")

    def _save_message(self, role: str, content: str, model: str | None = None):
        if self.memory is None or self.conversation_id is None:
            return
        try:
            self.memory.add_message(self.conversation_id, role, content, model)
        except MemoryStoreError as error:
            self._memory_failed(error)

    def _show_error(self, message: str):
        self.transcript.appendPlainText(f"\nSystem: {message}")
        self.status.setText("Conversation unavailable")

    def _memory_failed(self, error: Exception):
        self.memory = None
        self.conversation_id = None
        self._disable_memory_controls()
        self.transcript.appendPlainText(f"\nSystem: {error}")
        self.status.setText("Conversation memory unavailable")

    def _disable_memory_controls(self):
        self.history.setEnabled(False)
        self.new_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.memories_button.setEnabled(False)

    def _worker_finished(self):
        self.worker.deleteLater()
        self.worker = None
        self._set_input_enabled(True)
        self.input.setFocus()

    def _set_input_enabled(self, enabled: bool):
        self.input.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        self.history.setEnabled(enabled and self.memory is not None)
        self.new_button.setEnabled(enabled and self.memory is not None)
        self.delete_button.setEnabled(enabled and self.memory is not None)
        self.memories_button.setEnabled(enabled and self.memory is not None)
