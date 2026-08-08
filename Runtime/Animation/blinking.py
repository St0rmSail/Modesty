"""A small elapsed-time blink cycle for Modesty's idle pose."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BlinkFrame:
    closed: bool = False


class BlinkAnimation:
    """Return brief closed-eye frames at gently varied intervals."""

    def __init__(
        self,
        intervals: tuple[float, ...] = (4.2, 6.4, 3.8, 5.5),
        closed_seconds: float = 0.14,
    ):
        if not intervals or any(interval <= 0 for interval in intervals):
            raise ValueError("Blink intervals must be longer than zero.")
        if closed_seconds <= 0:
            raise ValueError("Blink duration must be longer than zero.")

        self.intervals = intervals
        self.closed_seconds = closed_seconds
        self.cycle_seconds = sum(intervals) + len(intervals) * closed_seconds

    def sample(self, elapsed_seconds: float) -> BlinkFrame:
        position = max(0.0, elapsed_seconds) % self.cycle_seconds

        for interval in self.intervals:
            if position < interval:
                return BlinkFrame()

            position -= interval
            if position < self.closed_seconds:
                return BlinkFrame(closed=True)

            position -= self.closed_seconds

        return BlinkFrame()
