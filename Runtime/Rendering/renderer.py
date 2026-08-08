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
    0.5.0 — First Blink
---------------------------------------------------------
"""

import json
from pathlib import Path

from PySide6.QtCore import QRectF, QTimer, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap, QRadialGradient
from PySide6.QtWidgets import QWidget

from Runtime.Animation import AnimationEngine, BlinkAnimation, BreathingAnimation
from Runtime.Rendering.shadows import ShadowRenderer
from Runtime.Core import team_status


PROJECT_ROOT = Path(__file__).resolve().parents[2]

STUDY_IMAGE = PROJECT_ROOT / "Assets" / "Study" / "study_team_roster_base_v1.png"
ARCHIVIST_IMAGE = (
    PROJECT_ROOT / "Assets" / "Team" / "Archivist" / "archivist_bobblehead_v1.png"
)
MODESTY_IMAGE = (
    PROJECT_ROOT
    / "Assets"
    / "Modesty"
    / "Standing"
    / "modesty_standing_v1.png"
)
MODESTY_BLINK_IMAGE = (
    PROJECT_ROOT
    / "Assets"
    / "Modesty"
    / "Standing"
    / "modesty_standing_blink_v1.png"
)
MODESTY_HEADSET_IMAGE = (
    PROJECT_ROOT
    / "Assets"
    / "Modesty"
    / "Accessories"
    / "modesty_headset_overlay_v1.png"
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
TEAM_DISPLAY_FILE = PROJECT_ROOT / "Config" / "team_display.json"


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
        self.modesty_blink = QPixmap(str(MODESTY_BLINK_IMAGE))
        self.modesty_headset = QPixmap(str(MODESTY_HEADSET_IMAGE))
        self.archivist = QPixmap(str(ARCHIVIST_IMAGE))

        if self.study.isNull():
            raise FileNotFoundError(
                f"Study image could not be loaded:\n{STUDY_IMAGE}"
            )

        if self.modesty.isNull():
            raise FileNotFoundError(
                f"Modesty image could not be loaded:\n{MODESTY_IMAGE}"
            )

        if self.modesty_blink.isNull():
            raise FileNotFoundError(
                f"Blink image could not be loaded:\n{MODESTY_BLINK_IMAGE}"
            )

        if self.modesty_blink.size() != self.modesty.size():
            raise ValueError("Blink image must match the standing image dimensions.")

        if self.modesty_headset.isNull():
            raise FileNotFoundError(
                f"Modesty's headset could not be loaded:\n{MODESTY_HEADSET_IMAGE}"
            )

        if self.modesty_headset.size() != self.modesty.size():
            raise ValueError("Headset overlay must match the standing image dimensions.")

        if self.archivist.isNull():
            raise FileNotFoundError(
                f"Archivist Bobblehead could not be loaded:\n{ARCHIVIST_IMAGE}"
            )

        self.position = load_json(POSITION_FILE)
        self.pose = load_json(POSE_FILE)
        self.lighting = load_json(LIGHTING_FILE)
        self.team_display = load_json(TEAM_DISPLAY_FILE)

        self.shadow_renderer = ShadowRenderer(self.lighting)
        self.animation_engine = AnimationEngine(BreathingAnimation())
        self.blink_engine = AnimationEngine(BlinkAnimation())

        self.animation_timer = QTimer(self)
        self.animation_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.animation_timer.setInterval(16)
        self.animation_timer.timeout.connect(self.update)
        self.animation_timer.start()

        self.setMinimumSize(640, 360)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        geometry = self._calculate_geometry()

        self._draw_background(painter, geometry)
        self._draw_readiness_lamp(painter, geometry)
        self._draw_team(painter, geometry)
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

    def _draw_readiness_lamp(self, painter: QPainter, geometry: dict):
        settings = self.team_display["lamp"]
        study_rect = geometry["study_rect"]
        centre_x = study_rect.left() + float(settings["centre_x"]) * study_rect.width()
        centre_y = study_rect.top() + float(settings["centre_y"]) * study_rect.height()
        radius = float(settings["glow_radius"]) * study_rect.height()
        angle = float(settings["angle_degrees"])
        bulb_width = study_rect.height() * 0.014
        bulb_height = study_rect.height() * 0.008

        painter.save()
        painter.translate(centre_x, centre_y)
        painter.rotate(angle)
        painter.setPen(Qt.PenStyle.NoPen)

        if not team_status.system_ready():
            painter.setBrush(QColor(48, 40, 28, 238))
            painter.drawEllipse(
                QRectF(-bulb_width / 2, -bulb_height / 2, bulb_width, bulb_height)
            )
            painter.restore()
            return

        glow = QRadialGradient(0, 0, radius)
        glow.setColorAt(0.0, QColor(255, 239, 174, 120))
        glow.setColorAt(0.35, QColor(255, 205, 92, 62))
        glow.setColorAt(0.68, QColor(255, 183, 62, 24))
        glow.setColorAt(1.0, QColor(255, 170, 60, 0))
        painter.setClipRect(
            QRectF(
                -radius,
                -bulb_height / 2,
                radius * 2,
                radius + bulb_height / 2,
            )
        )
        painter.setBrush(glow)
        painter.drawEllipse(QRectF(-radius, -radius, radius * 2, radius * 2))
        painter.setBrush(QColor(255, 244, 184, 245))
        painter.drawEllipse(
            QRectF(-bulb_width / 2, -bulb_height / 2, bulb_width, bulb_height)
        )
        painter.restore()

    def _draw_team(self, painter: QPainter, geometry: dict):
        state = team_status.member_state("archivist")
        settings = self.team_display["members"]["archivist"]
        if state in {"offline", "attention"}:
            message = "LATE FOR\nWORK" if state == "offline" else "NEEDS\nATTENTION"
            self._draw_absence_sign(painter, geometry, settings, message)
            return
        if state not in {"ready", "working", "waiting"}:
            return
        study_rect = geometry["study_rect"]
        height = float(settings["height"]) * study_rect.height()
        width = height * self.archivist.width() / self.archivist.height()
        anchor_x = study_rect.left() + float(settings["anchor_x"]) * study_rect.width()
        anchor_y = study_rect.top() + float(settings["anchor_y"]) * study_rect.height()
        destination = QRectF(anchor_x - width / 2, anchor_y - height, width, height)
        painter.drawPixmap(destination, self.archivist, QRectF(self.archivist.rect()))

    @staticmethod
    def _draw_absence_sign(painter: QPainter, geometry: dict, settings: dict, message: str):
        study_rect = geometry["study_rect"]
        anchor_x = study_rect.left() + float(settings["anchor_x"]) * study_rect.width()
        anchor_y = study_rect.top() + float(settings["anchor_y"]) * study_rect.height()
        sign_width = study_rect.width() * 0.047
        sign_height = study_rect.height() * 0.046
        sign_rect = QRectF(
            anchor_x - sign_width / 2,
            anchor_y - sign_height - study_rect.height() * 0.018,
            sign_width,
            sign_height,
        )
        painter.save()
        painter.setPen(QColor(63, 38, 20, 235))
        painter.setBrush(QColor(194, 143, 76, 245))
        painter.drawRoundedRect(sign_rect, 4, 4)
        painter.drawLine(
            int(anchor_x),
            int(sign_rect.bottom()),
            int(anchor_x),
            int(anchor_y),
        )
        StudyRenderer._draw_pixel_text(painter, sign_rect, message)
        painter.restore()

    @staticmethod
    def _draw_pixel_text(painter: QPainter, rect: QRectF, message: str):
        glyphs = {
            "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
            "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
            "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
            "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
            "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
            "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
            "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
            "N": ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
            "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
            "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
            "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
            "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
            "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
        }
        lines = message.splitlines()
        unit_widths = [sum(3 if char == " " else 6 for char in line) - 1 for line in lines]
        pixel = max(1, int(min(rect.width() / max(unit_widths), rect.height() / (len(lines) * 8 - 1))))
        total_height = (len(lines) * 8 - 1) * pixel
        y = rect.top() + (rect.height() - total_height) / 2
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(53, 31, 17, 255))
        for line, units in zip(lines, unit_widths):
            x = rect.left() + (rect.width() - units * pixel) / 2
            for char in line:
                if char == " ":
                    x += 3 * pixel
                    continue
                for row, pattern in enumerate(glyphs[char]):
                    for column, filled in enumerate(pattern):
                        if filled == "1":
                            painter.drawRect(
                                QRectF(x + column * pixel, y + row * pixel, pixel, pixel)
                            )
                x += 6 * pixel
            y += 8 * pixel

    def _draw_ground_effects(self, painter: QPainter, geometry: dict):
        self.shadow_renderer.draw_ground_shadow(
            painter=painter,
            anchor_x=geometry["anchor_x"],
            anchor_y=geometry["anchor_y"],
            character_width=geometry["character_width"],
            character_height=geometry["character_height"],
        )

    def _draw_characters(self, painter: QPainter, geometry: dict):
        breath = self.animation_engine.current_frame()
        blink = self.blink_engine.current_frame()
        character_width = geometry["character_width"] * breath.scale_x
        character_height = geometry["character_height"] * breath.scale_y

        # Scale around the configured pose pivot so the feet never leave the
        # Study anchor while the rest of the character breathes.
        character_rect = QRectF(
            geometry["anchor_x"] - float(self.pose["pivot_x"]) * character_width,
            geometry["anchor_y"] - float(self.pose["pivot_y"]) * character_height,
            character_width,
            character_height,
        )

        character_image = self.modesty_blink if blink.closed else self.modesty

        painter.drawPixmap(
            character_rect,
            character_image,
            QRectF(character_image.rect()),
        )

        if team_status.member_state("archivist") in {"ready", "working", "waiting"}:
            painter.drawPixmap(
                character_rect,
                self.modesty_headset,
                QRectF(self.modesty_headset.rect()),
            )

    def _draw_foreground(self, painter: QPainter, geometry: dict):
        # Reserved for desk edges, transient furniture, and other occluders.
        pass

    def _draw_ui_overlay(self, painter: QPainter, geometry: dict):
        # Reserved for future developer controls and status overlays.
        pass
