"""
---------------------------------------------------------
Modesty Project

Module:
    Study Renderer

Purpose:
    Draws the Study View in a fixed layer order:

        1. Background
        2. Ground effects
        3. Characters
        4. Foreground effects
        5. UI overlay

Owner:
    Study Renderer

Notes:
    The Study is the master coordinate system. Modesty's
    position, scale, pose pivot, and shadow remain relative
    to the Study when the window is resized or cropped.

Build:
    0.3.1 — Grounded
---------------------------------------------------------
"""

import json
from pathlib import Path

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QWidget

from Runtime.Rendering.shadows import ShadowRenderer


PROJECT_ROOT = Path(__file__).resolve().parents[2]

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
LIGHTING_FILE = PROJECT_ROOT / "Config" / "study_lighting.json"


def load_json(path: Path) -> dict:
    """Load a JSON file and report a useful error if it cannot be read."""

    if not path.exists():
        raise FileNotFoundError(f"Required file is missing:\n{path}")

    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"JSON file could not be read:\n{path}\n\n{error}"
        ) from error


class StudyRenderer(QWidget):
    """Composites the Study, ground effects, and characters."""

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
        self.lighting = load_json(LIGHTING_FILE)

        self.shadow_renderer = ShadowRenderer(self.lighting)

        self.setMinimumSize(640, 360)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        geometry = self._calculate_geometry()

        self._draw_background(painter, geometry)
        self._draw_ground_effects(painter, geometry)
        self._draw_characters(painter, geometry)
        self._draw_foreground(painter, geometry)
        self._draw_ui_overlay(painter, geometry)

    def _calculate_geometry(self) -> dict:
        """
        Calculate one shared transform for both the Study and Modesty.
        """

        study_scale = max(
            self.width() / self.study.width(),
            self.height() / self.study.height(),
        )

        study_width = self.study.width() * study_scale
        study_height = self.study.height() * study_scale
        study_left = (self.width() - study_width) / 2
        study_top = (self.height() - study_height) / 2

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

        return {
            "study_rect": QRectF(
                study_left,
                study_top,
                study_width,
                study_height,
            ),
            "character_rect": QRectF(
                character_left,
                character_top,
                character_width,
                character_height,
            ),
            "anchor_x": anchor_screen_x,
            "anchor_y": anchor_screen_y,
            "character_width": character_width,
            "character_height": character_height,
        }

    def _draw_background(self, painter: QPainter, geometry: dict):
        painter.drawPixmap(
            geometry["study_rect"],
            self.study,
            QRectF(self.study.rect()),
        )

    def _draw_ground_effects(self, painter: QPainter, geometry: dict):
        self.shadow_renderer.draw_ground_shadow(
            painter=painter,
            anchor_x=geometry["anchor_x"],
            anchor_y=geometry["anchor_y"],
            character_width=geometry["character_width"],
            character_height=geometry["character_height"],
        )

    def _draw_characters(self, painter: QPainter, geometry: dict):
        painter.drawPixmap(
            geometry["character_rect"],
            self.modesty,
            QRectF(self.modesty.rect()),
        )

    def _draw_foreground(self, painter: QPainter, geometry: dict):
        # Reserved for desk edges, transient furniture, and other occluders.
        pass

    def _draw_ui_overlay(self, painter: QPainter, geometry: dict):
        # Reserved for future developer controls and status overlays.
        pass
