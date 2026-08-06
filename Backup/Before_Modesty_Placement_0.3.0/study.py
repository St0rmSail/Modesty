"""
study.py
========

Purpose:
    Creates Modesty's Study View window.

Build:
    0.2.1
"""

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STUDY_IMAGE = PROJECT_ROOT / "Assets" / "Study" / "study_master.png"


class StudyCanvas(QWidget):
    """Draws the Study image without stretching it."""

    def __init__(self, image_path: Path):
        super().__init__()

        self.image_path = image_path
        self.pixmap = QPixmap(str(image_path))

        if self.pixmap.isNull():
            raise FileNotFoundError(
                f"Study image could not be loaded:\n{image_path}"
            )

        self.setMinimumSize(640, 360)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        scaled = self.pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )

        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2

        painter.drawPixmap(QRect(x, y, scaled.width(), scaled.height()), scaled)


class StudyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Modesty's Study")
        self.resize(1280, 720)

        canvas = StudyCanvas(STUDY_IMAGE)
        self.setCentralWidget(canvas)


def run():
    app = QApplication.instance() or QApplication(sys.argv)

    try:
        window = StudyWindow()
    except FileNotFoundError as error:
        QMessageBox.critical(
            None,
            "Modesty's Study image is missing",
            (
                f"{error}\n\n"
                "Place the approved Study image here:\n"
                "E:\\Modesty\\Assets\\Study\\study_master.png"
            ),
        )
        return

    window.show()
    app.exec()
