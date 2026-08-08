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

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from Runtime.Conversation import ConversationPanel
from Runtime.Rendering.renderer import StudyRenderer


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
        overlay_layout.addStretch()
        overlay_layout.addWidget(
            ConversationPanel(),
            alignment=Qt.AlignmentFlag.AlignHCenter,
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
