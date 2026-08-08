"""
---------------------------------------------------------
Modesty Project

Module:
    Study Window

Purpose:
    Creates the application window and delegates all visual
    drawing to the Study Renderer.

Build:
    0.5.0 — First Blink
---------------------------------------------------------
"""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox

from Runtime.Rendering.renderer import StudyRenderer


class StudyWindow(QMainWindow):
    """The Windows application shell containing the Study View."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Modesty's Study")
        self.resize(1280, 720)
        self.setCentralWidget(StudyRenderer())


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
