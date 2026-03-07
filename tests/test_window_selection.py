from __future__ import annotations

import unittest

from tetrio_env.capture.window_locator import WindowInfo, WindowRect, select_best_window


class WindowSelectionTests(unittest.TestCase):
    def test_select_best_window_prefers_exact_title(self) -> None:
        candidates = [
            WindowInfo(hwnd=1, title="TETR.IO - Chrome", rect=WindowRect(0, 0, 1200, 800)),
            WindowInfo(hwnd=2, title="TETR.IO", rect=WindowRect(10, 10, 900, 700)),
        ]

        selected = select_best_window(candidates, "TETR.IO")

        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(selected.hwnd, 2)

    def test_select_best_window_breaks_ties_by_area(self) -> None:
        candidates = [
            WindowInfo(hwnd=1, title="TETR.IO table", rect=WindowRect(0, 0, 800, 600)),
            WindowInfo(hwnd=2, title="TETR.IO lobby", rect=WindowRect(0, 0, 1200, 900)),
        ]

        selected = select_best_window(candidates, "TETR.IO")

        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(selected.hwnd, 2)

    def test_select_best_window_returns_none_when_no_match(self) -> None:
        candidates = [
            WindowInfo(hwnd=1, title="Notepad", rect=WindowRect(0, 0, 800, 600)),
        ]

        selected = select_best_window(candidates, "TETR.IO")

        self.assertIsNone(selected)


if __name__ == "__main__":
    unittest.main()
