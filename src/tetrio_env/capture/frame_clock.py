"""Frame pacing utilities used by capture and benchmarking tools."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True, slots=True)
class FrameTick:
    """Timing metadata for one paced frame iteration."""

    frame_id: int
    scheduled_at_s: float
    started_at_s: float


class FrameClock:
    """Simple fixed-rate clock that minimizes drift over long capture runs."""

    def __init__(
        self,
        target_fps: int,
        *,
        time_fn: Callable[[], float] | None = None,
        sleep_fn: Callable[[float], None] | None = None,
    ) -> None:
        if target_fps <= 0:
            raise ValueError("target_fps must be positive")

        self.target_fps = target_fps
        self.period_s = 1.0 / float(target_fps)
        self._time_fn = time_fn or time.perf_counter
        self._sleep_fn = sleep_fn or time.sleep

        self._next_deadline_s: float | None = None
        self._frame_id = 0

    def reset(self) -> None:
        """Reset sequence and deadlines."""
        self._next_deadline_s = None
        self._frame_id = 0

    def wait_for_next_frame(self) -> FrameTick:
        """Block until next frame boundary and return timing metadata."""
        now = self._time_fn()

        if self._next_deadline_s is None:
            self._next_deadline_s = now

        deadline = self._next_deadline_s

        if now < deadline:
            self._sleep_fn(deadline - now)
            now = self._time_fn()
        elif now - deadline > self.period_s:
            skipped = int((now - deadline) // self.period_s)
            deadline += skipped * self.period_s

        tick = FrameTick(
            frame_id=self._frame_id,
            scheduled_at_s=deadline,
            started_at_s=now,
        )
        self._frame_id += 1

        next_deadline = deadline + self.period_s
        now_after_tick = self._time_fn()
        if now_after_tick > next_deadline + self.period_s:
            self._next_deadline_s = now_after_tick + self.period_s
        else:
            self._next_deadline_s = next_deadline

        return tick


def now_timestamp_ms() -> int:
    """Wall-clock timestamp for capture metadata."""
    return time.time_ns() // 1_000_000
