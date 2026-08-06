"""
study.py
========

Purpose:
    Creates Modesty's Study View and places Modesty relative to the Study.

Build:
    0.3.0
"""

import json
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox


PROJECT_ROOT = Path(__file__).resolve().parents[1]

STUDY_IMAGE = PROJECT_ROOT / "Assets" / "Study" / "study_master.png"
MODESTY_IMAGE = (
    PROJECT_ROOT
    / "Assets"
    / "Modesty"
    / "Standing"
    / "modesty_standing_v1.png"
)
POSITION_FILE = PROJECT_ROOT / "Config" / "modesty_position.json"
POSE_FILE = (
    PROJECT_ROOT
    / "Assets"
    / "Modesty"
    / "Standing"
    / "pose.json"
)


def load_json(path: Path) -> dict:
    """Load a JSON file and give a clear error if it is missing or invalid."""
    if not path.exists():
        raise FileNotFoundError(f"Required file is missing:\n{path}")

    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"JSON file could not be read:\n{path}\n\n{error}"
        ) from error


class StudyCanvas(QWidget):
    """Draws the Study and Modesty using one shared coordinate system."""

    def __init__(self):
        super().__init__()

        self.study = QPixmap(str(STUDY_IMAGE))
        self.modesty = QPixmap(str(MODESTY_IMAGE))

        if self.study.isNull():
            raise FileNotFoundError(
                f"Study image could not be loaded:\n{STUDY_IMAGE}"
            )

        if self.modesty.isNull():
            raise FileNotFoundError(
                f"Modesty image could not be loaded:\n{MODESTY_IMAGE}"
            )

        self.position = load_json(POSITION_FILE)
        self.pose = load_json(POSE_FILE)

        self.setMinimumSize(640, 360)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        # The Study fills the window without stretching.
        study_scale = max(
            self.width() / self.study.width(),
            self.height() / self.study.height(),
        )

        study_width = self.study.width() * study_scale
        study_height = self.study.height() * study_scale
        study_left = (self.width() - study_width) / 2
        study_top = (self.height() - study_height) / 2

        study_rect = QRectF(
            study_left,
            study_top,
            study_width,
            study_height,
        )
        painter.drawPixmap(study_rect, self.study, QRectF(self.study.rect()))

        # Modesty's position is stored relative to the original Study image.
        anchor_x = float(self.position["anchor_x"])
        anchor_y = float(self.position["anchor_y"])
        height_fraction = float(self.position["height"])

        pivot_x = float(self.pose["pivot_x"])
        pivot_y = float(self.pose["pivot_y"])

        character_height = self.study.height() * height_fraction * study_scale
        character_scale = character_height / self.modesty.height()
        character_width = self.modesty.width() * character_scale

        anchor_screen_x = study_left + anchor_x * study_width
        anchor_screen_y = study_top + anchor_y * study_height

        character_left = anchor_screen_x - pivot_x * character_width
        character_top = anchor_screen_y - pivot_y * character_height

        character_rect = QRectF(
            character_left,
            character_top,
            character_width,
            character_height,
        )

        painter.drawPixmap(
            character_rect,
            self.modesty,
            QRectF(self.modesty.rect()),
        )


class StudyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Modesty's Study")
        self.resize(1280, 720)
        self.setCentralWidget(StudyCanvas())


def run():
    app = QApplication.instance() or QApplication(sys.argv)

    try:
        window = StudyWindow()
    except (FileNotFoundError, ValueError, KeyError) as error:
        QMessageBox.critical(
            None,
            "Modesty could not enter the Study",
            (
                f"{error}\n\n"
                "Check the asset names and JSON files listed in the "
                "M1.2 placement instructions."
            ),
        )
        return

    window.show()
    app.exec()
