"""
study.py
========

Purpose:
    Creates Modesty's Study window.

Build:
    0.2.0
"""

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMainWindow

from PySide6.QtCore import Qt


class StudyWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Modesty's Study")

        self.resize(1280, 720)

        label = QLabel("Good afternoon, Drew.")

        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setCentralWidget(label)


def run():

    app = QApplication(sys.argv)

    window = StudyWindow()

    window.show()

    app.exec()