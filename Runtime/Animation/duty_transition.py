"""Reversible, elapsed-time movement between neutral and a duty position."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DutyTransitionFrame:
    progress: float
    complete: bool


class DutyTransition:
    """Return a smooth progress value without depending on frame rate."""

    def __init__(self, duration_seconds: float = 1.8):
        if duration_seconds <= 0:
            raise ValueError("Duty transition must be longer than zero.")
        self.duration_seconds = duration_seconds

    def sample(
        self,
        elapsed_seconds: float,
        *,
        returning: bool = False,
    ) -> DutyTransitionFrame:
        linear = min(1.0, max(0.0, elapsed_seconds / self.duration_seconds))
        eased = linear * linear * (3.0 - 2.0 * linear)
        progress = 1.0 - eased if returning else eased
        return DutyTransitionFrame(progress=progress, complete=linear >= 1.0)
