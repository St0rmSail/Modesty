"""
---------------------------------------------------------
Modesty Project

Module:
    Shadow Renderer

Purpose:
    Draws lightweight, reusable ground-contact shadows for
    Study residents and transient objects.

Owner:
    Study Renderer

Notes:
    Shadows belong to the Study, not to the character.
    Characters supply only an anchor/pivot and dimensions.

    A soft shadow is approximated with layered translucent
    ellipses. This avoids expensive real-time blur effects
    while remaining fast and convincing.

Current through:
    0.13.0 — The Researcher
---------------------------------------------------------
"""

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter, QBrush
from PySide6.QtCore import Qt


class ShadowRenderer:
    """Draw soft ground shadows using inexpensive layered ellipses."""

    def __init__(self, settings: dict):
        self.settings = settings

    def draw_ground_shadow(
        self,
        painter: QPainter,
        anchor_x: float,
        anchor_y: float,
        character_width: float,
        character_height: float,
        opacity_scale: float = 1.0,
    ):
        if not bool(self.settings.get("enabled", True)):
            return

        colour_values = self.settings.get("shadow_colour", [40, 30, 18])
        opacity = float(self.settings.get("shadow_opacity", 0.16)) * max(
            0.0, opacity_scale
        )
        width_factor = float(self.settings.get("shadow_width", 0.58))
        height_factor = float(self.settings.get("shadow_height", 0.075))
        offset_x_factor = float(self.settings.get("offset_x", 0.035))
        offset_y_factor = float(self.settings.get("offset_y", 0.006))
        softness_layers = int(self.settings.get("softness_layers", 18))

        softness_layers = max(4, min(40, softness_layers))

        width = character_height * width_factor
        height = character_height * height_factor

        centre_x = anchor_x + character_height * offset_x_factor
        centre_y = anchor_y + character_height * offset_y_factor

        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)

        # Draw broad, faint ellipses first and increasingly concentrated
        # ellipses toward the centre. The result resembles a blurred shadow.
        for layer in range(softness_layers, 0, -1):
            ratio = layer / softness_layers
            spread = 1.0 + ratio * 0.40

            layer_width = width * spread
            layer_height = height * spread

            # Outer layers are very faint; the centre remains subtle.
            layer_alpha = int(
                255
                * opacity
                * (1.0 - ratio * 0.78)
                / max(1, softness_layers / 4)
            )
            layer_alpha = max(1, min(255, layer_alpha))

            colour = QColor(
                int(colour_values[0]),
                int(colour_values[1]),
                int(colour_values[2]),
                layer_alpha,
            )
            painter.setBrush(QBrush(colour))

            rect = QRectF(
                centre_x - layer_width / 2,
                centre_y - layer_height / 2,
                layer_width,
                layer_height,
            )
            painter.drawEllipse(rect)

        painter.restore()
