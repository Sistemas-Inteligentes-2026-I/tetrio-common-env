from __future__ import annotations

import unittest

from tetrio_env.capture.frame_clock import FrameClock
from tetrio_env.capture.screen_grabber import CaptureRegion, ScreenGrabber, grab_region_once


class _FakeTime:
    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def time(self) -> float:
        return self.now

    def sleep(self, duration: float) -> None:
        self.sleeps.append(duration)
        self.now += duration


class _FakeShot:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.bgra = bytes([10, 20, 30, 255] * width * height)


class _FakeBackend:
    def __init__(self) -> None:
        self.closed = False
        self.calls = 0

    def grab(self, monitor: dict[str, int]) -> _FakeShot:
        self.calls += 1
        return _FakeShot(width=monitor["width"], height=monitor["height"])

    def close(self) -> None:
        self.closed = True


class CaptureTests(unittest.TestCase):
    def test_frame_clock_waits_for_next_interval(self) -> None:
        fake = _FakeTime()
        clock = FrameClock(target_fps=10, time_fn=fake.time, sleep_fn=fake.sleep)

        first = clock.wait_for_next_frame()
        second = clock.wait_for_next_frame()

        self.assertEqual(first.frame_id, 0)
        self.assertEqual(second.frame_id, 1)
        self.assertEqual(len(fake.sleeps), 1)
        self.assertAlmostEqual(fake.sleeps[0], 0.1, places=6)

    def test_screen_grabber_increments_frame_ids(self) -> None:
        backend = _FakeBackend()
        region = CaptureRegion(x=5, y=10, width=3, height=2)

        grabber = ScreenGrabber(region, backend_factory=lambda: backend)
        frame0 = grabber.grab()
        frame1 = grabber.grab()
        grabber.close()

        self.assertEqual(frame0.frame_id, 0)
        self.assertEqual(frame1.frame_id, 1)
        self.assertEqual(frame0.width, 3)
        self.assertEqual(frame0.height, 2)
        self.assertEqual(backend.calls, 2)
        self.assertTrue(backend.closed)

    def test_grab_region_once_returns_valid_frame(self) -> None:
        backend = _FakeBackend()
        region = CaptureRegion(x=0, y=0, width=2, height=2)

        frame = grab_region_once(region, backend_factory=lambda: backend)

        self.assertEqual(frame.width, 2)
        self.assertEqual(frame.height, 2)
        self.assertEqual(len(frame.bgra), 2 * 2 * 4)


if __name__ == "__main__":
    unittest.main()
