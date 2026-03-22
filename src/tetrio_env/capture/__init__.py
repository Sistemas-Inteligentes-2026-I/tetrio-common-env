"""Capture module public surface."""

from tetrio_env.capture.frame_clock import FrameClock, FrameTick, now_timestamp_ms
from tetrio_env.capture.screen_grabber import (
    CaptureBackendError,
    CaptureError,
    CapturedFrame,
    CaptureRegion,
    ScreenGrabber,
    grab_region_once,
)
from tetrio_env.capture.window_locator import (
    WindowApiError,
    WindowInfo,
    WindowNotFoundError,
    WindowRect,
    find_window,
    get_client_rect,
    get_foreground_window_handle,
    get_window_rect,
    is_window_focused,
    list_visible_windows,
    locate_window,
    select_best_window,
)

__all__ = [
    "CaptureBackendError",
    "CaptureError",
    "CaptureRegion",
    "CapturedFrame",
    "FrameClock",
    "FrameTick",
    "grab_region_once",
    "ScreenGrabber",
    "find_window",
    "get_client_rect",
    "get_foreground_window_handle",
    "get_window_rect",
    "is_window_focused",
    "list_visible_windows",
    "locate_window",
    "now_timestamp_ms",
    "select_best_window",
    "WindowApiError",
    "WindowInfo",
    "WindowNotFoundError",
    "WindowRect",
]
