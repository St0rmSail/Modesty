"""
---------------------------------------------------------
Modesty Project

Module:
    Study Window

Purpose:
    Creates the application window and delegates all visual
    drawing to the Study Renderer.

Build:
    0.8.0 — Personal Memory
---------------------------------------------------------
"""

import sys

from PySide6.QtCore import QTimer, Qt
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
from Runtime.Rendering.renderer import StudyRenderer


class ConversationDock(QWidget):
    """Keep chat on the right and leave a small restore tab when hidden."""

    def __init__(self):
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

        self.panel = ConversationPanel()
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
        QTimer.singleShot(1400, self._restore_after_library_opening)

    def _restore_after_library_opening(self):
        if not self._library_auto_hidden:
            return
        self._library_auto_hidden = False
        self.show_button.hide()
        self.panel.show()
        self.panel.input.setFocus()


class StudyView(QWidget):
    """Layer the conversation controls over the unchanged Study renderer."""

    def __init__(self):
        super().__init__()

        layers = QStackedLayout(self)
        layers.setContentsMargins(0, 0, 0, 0)
        layers.setStackingMode(QStackedLayout.StackingMode.StackAll)
        layers.addWidget(StudyRenderer())

        overlay = QWidget()
        overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        overlay_layout = QVBoxLayout(overlay)
        overlay_layout.setContentsMargins(24, 24, 24, 24)
        overlay_layout.addWidget(
            ConversationDock(),
            stretch=1,
            alignment=Qt.AlignmentFlag.AlignRight,
        )
        layers.addWidget(overlay)
        layers.setCurrentWidget(overlay)


class StudyWindow(QMainWindow):
    """The Windows application shell containing the Study View."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Modesty's Study")
        self.resize(1280, 720)
        self.setCentralWidget(StudyView())


def run():
    """Start the Study View."""

    app = QApplication.instance() or QApplication(sys.argv)

    try:
        window = StudyWindow()
    except (FileNotFoundError, ValueError, KeyError) as error:
        QMessageBox.critical(
            None,
            "Modesty could not enter the Study",
            str(error),
        )
        return

    window.show()
    app.exec()
