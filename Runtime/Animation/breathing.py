"""A restrained idle breath for Modesty's standing pose."""

from dataclasses import dataclass
from math import cos, tau


@dataclass(frozen=True)
class BreathingFrame:
    scale_x: float = 1.0
    scale_y: float = 1.0


class BreathingAnimation:
    """Produce a smooth breath cycle from absolute elapsed time."""

    def __init__(
        self,
        cycle_seconds: float = 4.8,
        vertical_amount: float = 0.003,
        horizontal_amount: float = 0.001,
    ):
        if cycle_seconds <= 0:
            raise ValueError("Breathing cycle must be longer than zero.")

        self.cycle_seconds = cycle_seconds
        self.vertical_amount = vertical_amount
        self.horizontal_amount = horizontal_amount

    def sample(self, elapsed_seconds: float) -> BreathingFrame:
        phase = tau * (max(0.0, elapsed_seconds) % self.cycle_seconds)
        phase /= self.cycle_seconds

        # Start and finish at the neutral pose, with a soft peak mid-cycle.
        breath = (1.0 - cos(phase)) / 2.0

        return BreathingFrame(
            scale_x=1.0 - self.horizontal_amount * breath,
            scale_y=1.0 + self.vertical_amount * breath,
        )
