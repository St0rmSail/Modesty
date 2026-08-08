"""A compact conversation overlay for the Study View."""

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from Runtime.Conversation.client import DEFAULT_MODEL, OllamaChatClient


SYSTEM_PROMPT = """You are Modesty, Drew's local-first personal AI assistant.
You are one coherent woman: warm, confident, thoughtful, and naturally playful,
while becoming focused and analytical when the work calls for it. Anita and
Merry are only named aspects of your single personality, never separate people,
agents, or identities. Speak naturally, clearly, and concisely. You currently
have no internet, vision, voice, tools, or persistent memory, so never claim to
have used capabilities you do not possess."""


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
    """Collect text input and display the current local conversation."""

    def __init__(self):
        super().__init__()

        self.client = OllamaChatClient()
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.worker = None

        self.setObjectName("conversationPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setMaximumWidth(900)
        self.setMinimumHeight(210)
        self.setMaximumHeight(240)
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
            QLineEdit {
                background: rgba(255, 250, 240, 235);
                border: 1px solid #b88a4b;
                border-radius: 7px;
                color: #261c13;
                padding: 8px 10px;
                font-size: 14px;
            }
            QPushButton {
                background: #9b6833;
                border: none;
                border-radius: 7px;
                color: white;
                padding: 9px 18px;
                font-weight: bold;
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
        layout.setSpacing(8)

        self.transcript = QPlainTextEdit()
        self.transcript.setReadOnly(True)
        self.transcript.setMaximumHeight(135)
        self.transcript.setPlainText("Modesty: Good morning, Drew.")
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

    def _send(self):
        message = self.input.text().strip()
        if not message or self.worker is not None:
            return

        self.input.clear()
        self.messages.append({"role": "user", "content": message})
        self.transcript.appendPlainText(f"\nDrew: {message}")
        self.status.setText("Modesty is thinking...")
        self._set_input_enabled(False)

        self.worker = ChatWorker(self.client, list(self.messages))
        self.worker.succeeded.connect(self._receive)
        self.worker.failed.connect(self._show_error)
        self.worker.finished.connect(self._worker_finished)
        self.worker.start()

    def _receive(self, response: str):
        self.messages.append({"role": "assistant", "content": response})
        self.transcript.appendPlainText(f"\nModesty: {response}")
        self.status.setText(f"Local conversation · {DEFAULT_MODEL}")

    def _show_error(self, message: str):
        self.transcript.appendPlainText(f"\nSystem: {message}")
        self.status.setText("Conversation unavailable")

    def _worker_finished(self):
        self.worker.deleteLater()
        self.worker = None
        self._set_input_enabled(True)
        self.input.setFocus()

    def _set_input_enabled(self, enabled: bool):
        self.input.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
