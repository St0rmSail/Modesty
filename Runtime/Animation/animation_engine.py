"""Elapsed-time animation sampling with no frame-rate assumptions."""

from time import perf_counter
from typing import Callable, Protocol, TypeVar


Frame = TypeVar("Frame")


class Animation(Protocol[Frame]):
    def sample(self, elapsed_seconds: float) -> Frame:
        """Return the animation state at an elapsed time."""


class AnimationEngine:
    """Sample an animation from a monotonic clock."""

    def __init__(
        self,
        animation: Animation[Frame],
        clock: Callable[[], float] = perf_counter,
    ):
        self.animation = animation
        self.clock = clock
        self.started_at = clock()

    def reset(self):
        self.started_at = self.clock()

    def current_frame(self) -> Frame:
        elapsed_seconds = max(0.0, self.clock() - self.started_at)
        return self.animation.sample(elapsed_seconds)
