"""
---------------------------------------------------------
Modesty Project

Module:
    Study Window

Purpose:
    Creates the application window and delegates all visual
    drawing to the Study Renderer.

Current through:
    0.14.0 — Time and Presence
---------------------------------------------------------
"""

import sys

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QTimer, Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from Runtime.Conversation import ConversationPanel
from Runtime.Conversation.briefing_hologram import BriefingHologram
from Runtime.Reading.reading_desk import ReadingDesk
from Runtime.Rendering.renderer import StudyRenderer
from Runtime.Time import PresenceSession


class ConversationDock(QWidget):
    """Keep chat on the right and leave a small restore tab when hidden."""

    def __init__(self, presence: PresenceSession | None = None):
        super().__init__()
        self.setMaximumWidth(420)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.show_row = QHBoxLayout()
        self.online_badge = QLabel("GRAND LIBRARY  ⚡  ONLINE")
        self.online_badge.setStyleSheet(
            "QLabel { background: rgba(7, 35, 51, 235); color: #c8f8ff; "
            "border: 1px solid #70e8ff; border-radius: 7px; padding: 7px 11px; "
            "font-weight: bold; }"
        )
        self.online_badge.hide()
        self.show_row.addWidget(self.online_badge)
        self.show_row.addStretch()
        self.show_button = QPushButton("Chat")
        self.show_button.setToolTip("Restore the conversation panel")
        self.show_button.setStyleSheet(
            "QPushButton { background: #9b6833; color: white; border: none; "
            "border-radius: 7px; padding: 9px 18px; font-weight: bold; }"
        )
        self.show_button.clicked.connect(self.show_panel)
        self.show_row.addWidget(self.show_button)

        self.panel = ConversationPanel(presence=presence)
        self.panel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.panel.hide_requested.connect(self.hide_panel)
        self.panel.grand_library_state_changed.connect(self._library_state_changed)
        layout.addWidget(self.panel, stretch=1)
        layout.addLayout(self.show_row)
        self.show_button.hide()
        self._library_auto_hidden = False

    def hide_panel(self):
        self.panel.hide()
        self.show_button.show()

    def show_panel(self):
        self._library_auto_hidden = False
        self.show_button.hide()
        self.panel.show()
        self.panel.input.setFocus()

    def _library_state_changed(self, state: str):
        self.online_badge.setVisible(state == "online")
        if state != "online" or not self.panel.isVisible():
            return
        self._library_auto_hidden = True
        self.panel.hide()
        self.show_button.show()
        QTimer.singleShot(5700, self._restore_after_library_opening)

    def _restore_after_library_opening(self):
        if not self._library_auto_hidden:
            return
        self._library_auto_hidden = False
        self.show_button.hide()
        self.panel.show()
        self.panel.input.setFocus()


class StudyView(QWidget):
    """Layer the conversation controls over the unchanged Study renderer."""

    def __init__(self, presence: PresenceSession | None = None):
        super().__init__()

        layers = QStackedLayout(self)
        layers.setContentsMargins(0, 0, 0, 0)
        layers.setStackingMode(QStackedLayout.StackingMode.StackAll)
        self.renderer = StudyRenderer()
        layers.addWidget(self.renderer)

        overlay = QWidget()
        overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.overlay_layout = QHBoxLayout(overlay)
        self.overlay_layout.setContentsMargins(24, 24, 24, 24)
        self.briefing = BriefingHologram()
        self.briefing.hide()
        self.overlay_layout.addWidget(
            self.briefing,
            stretch=1,
            alignment=Qt.AlignmentFlag.AlignVCenter,
        )
        self.reading_desk = ReadingDesk()
        self.reading_desk.hide()
        self.overlay_layout.addWidget(self.reading_desk, stretch=1)
        self.conversation = ConversationDock(presence)
        self.overlay_layout.addWidget(self.conversation, alignment=Qt.AlignmentFlag.AlignRight)
        self.conversation.panel.briefing_requested.connect(self._open_briefing)
        self.conversation.panel.reading_requested.connect(self._open_reading_desk)
        self.conversation.panel.response_received.connect(self._briefing_response)
        self.conversation.panel.response_received.connect(self._reading_response)
        self.conversation.panel.graceful_exit_requested.connect(self._graceful_exit)
        self.briefing.question_submitted.connect(self.conversation.panel.send_external)
        self.briefing.closed.connect(self._close_briefing)
        self.briefing.outcome_recorded.connect(self.conversation.panel.record_briefing_outcome)
        self.reading_desk.command_submitted.connect(self.conversation.panel.send_external)
        self.reading_desk.closed.connect(self._close_reading_desk)
        self.briefing_animation = None
        layers.addWidget(overlay)
        layers.setCurrentWidget(overlay)

    def _open_briefing(self, report_id: str):
        try:
            self.briefing.open_report(report_id)
        except ValueError as error:
            QMessageBox.warning(self, "Briefing unavailable", str(error))
            return
        self.conversation.hide()
        self.renderer.present_briefing()
        self.briefing.setMaximumWidth(max(640, int(self.contentsRect().width() * 0.72)))
        self.overlay_layout.setAlignment(
            self.briefing,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )
        target_height = max(420, self.contentsRect().height() - 48)
        self.briefing.setMinimumHeight(0)
        self.briefing.setMaximumHeight(8)
        self.briefing.show()
        self.briefing_animation = QPropertyAnimation(self.briefing, b"maximumHeight", self)
        self.briefing_animation.setDuration(1800)
        self.briefing_animation.setStartValue(8)
        self.briefing_animation.setEndValue(target_height)
        self.briefing_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.briefing_animation.finished.connect(self._finish_briefing_open)
        self.briefing_animation.start()
        self.briefing.question.setFocus()

    def _finish_briefing_open(self):
        self.overlay_layout.setAlignment(self.briefing, Qt.AlignmentFlag(0))
        self.briefing.setMaximumHeight(16777215)

    def _close_briefing(self):
        self.briefing.hide()
        self.briefing.setMinimumHeight(0)
        self.briefing.setMaximumHeight(16777215)
        self.conversation.show()
        self.renderer.dismiss_briefing()
        self.conversation.panel.input.setFocus()

    def _briefing_response(self, response: str):
        if self.briefing.isVisible():
            self.briefing.append_modesty_response(response)

    def _open_reading_desk(self, response: str):
        if self.reading_desk.isVisible():
            self.reading_desk.accept_response(response)
            return
        if not self.reading_desk.open_response(response):
            QMessageBox.warning(self, "Reading Desk unavailable", "The Librarian did not return a readable passage.")
            return
        self.conversation.hide()
        self.reading_desk.setMaximumWidth(max(720, int(self.contentsRect().width() * 0.72)))
        self.reading_desk.show()

    def _reading_response(self, response: str):
        if self.reading_desk.isVisible():
            self.reading_desk.accept_response(response)

    def _close_reading_desk(self):
        self.reading_desk.hide()
        self.conversation.show()
        self.conversation.panel.input.setFocus()

    @staticmethod
    def _graceful_exit():
        # Allow Modesty's goodbye to paint before the normal Qt shutdown.
        QTimer.singleShot(900, QApplication.instance().quit)


class StudyWindow(QMainWindow):
    """The Windows application shell containing the Study View."""

    def __init__(self, presence: PresenceSession | None = None):
        super().__init__()

        self.setWindowTitle("Modesty's Study")
        self.resize(1280, 720)
        self.presence = presence
        self.setCentralWidget(StudyView(presence))
        self.heartbeat_timer = None
        if presence is not None:
            presence.set_presence("present")
            self.heartbeat_timer = QTimer(self)
            self.heartbeat_timer.setInterval(30_000)
            self.heartbeat_timer.timeout.connect(presence.heartbeat)
            self.heartbeat_timer.start()


def run(presence: PresenceSession | None = None):
    """Start the Study View."""

    app = QApplication.instance() or QApplication(sys.argv)

    try:
        window = StudyWindow(presence)
    except (FileNotFoundError, ValueError, KeyError) as error:
        QMessageBox.critical(
            None,
            "Modesty could not enter the Study",
            str(error),
        )
        return

    window.showMaximized()
    app.exec()
