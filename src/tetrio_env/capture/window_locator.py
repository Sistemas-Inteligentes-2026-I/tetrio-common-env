"""Windows window discovery and focus utilities for capture."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from typing import Sequence

_IS_WINDOWS = ctypes.sizeof(ctypes.c_void_p) == ctypes.sizeof(wintypes.HWND)


class WindowApiError(RuntimeError):
    """Raised when Windows API calls fail."""


class WindowNotFoundError(WindowApiError):
    """Raised when no visible window matches the requested hint."""


@dataclass(frozen=True, slots=True)
class WindowRect:
    """Rectangle in screen pixels; x/y may be negative on multi-monitor setups."""

    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("WindowRect width and height must be positive")


@dataclass(frozen=True, slots=True)
class WindowInfo:
    """Minimal information needed by capture and safety checks."""

    hwnd: int
    title: str
    rect: WindowRect


class _RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


class _POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


if hasattr(ctypes, "WinDLL"):
    _USER32 = ctypes.WinDLL("user32", use_last_error=True)
    _ENUM_WINDOWS_PROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
else:
    _USER32 = None
    _ENUM_WINDOWS_PROC = None


def _require_windows_api() -> None:
    if _USER32 is None or _ENUM_WINDOWS_PROC is None:
        raise WindowApiError("Window APIs are available only on Windows")


def _last_error(message: str) -> WindowApiError:
    code = ctypes.get_last_error()
    return WindowApiError(f"{message} (winerror={code})")


def _window_title(hwnd: int) -> str:
    _require_windows_api()
    assert _USER32 is not None

    length = _USER32.GetWindowTextLengthW(wintypes.HWND(hwnd))
    if length <= 0:
        return ""

    buffer = ctypes.create_unicode_buffer(length + 1)
    _USER32.GetWindowTextW(wintypes.HWND(hwnd), buffer, length + 1)
    return buffer.value.strip()


def get_window_rect(hwnd: int) -> WindowRect:
    """Return the full outer window rectangle in screen coordinates."""
    _require_windows_api()
    assert _USER32 is not None

    native_rect = _RECT()
    ok = _USER32.GetWindowRect(wintypes.HWND(hwnd), ctypes.byref(native_rect))
    if not ok:
        raise _last_error(f"GetWindowRect failed for hwnd={hwnd}")

    width = int(native_rect.right - native_rect.left)
    height = int(native_rect.bottom - native_rect.top)
    return WindowRect(
        x=int(native_rect.left),
        y=int(native_rect.top),
        width=width,
        height=height,
    )


def get_client_rect(hwnd: int) -> WindowRect:
    """Return the client (content) rectangle in screen coordinates."""
    _require_windows_api()
    assert _USER32 is not None

    client = _RECT()
    ok = _USER32.GetClientRect(wintypes.HWND(hwnd), ctypes.byref(client))
    if not ok:
        raise _last_error(f"GetClientRect failed for hwnd={hwnd}")

    origin = _POINT(0, 0)
    ok = _USER32.ClientToScreen(wintypes.HWND(hwnd), ctypes.byref(origin))
    if not ok:
        raise _last_error(f"ClientToScreen failed for hwnd={hwnd}")

    width = int(client.right - client.left)
    height = int(client.bottom - client.top)
    return WindowRect(x=int(origin.x), y=int(origin.y), width=width, height=height)


def list_visible_windows(title_filter: str | None = None) -> list[WindowInfo]:
    """Enumerate visible top-level windows and optionally filter by title substring."""
    _require_windows_api()
    assert _USER32 is not None
    assert _ENUM_WINDOWS_PROC is not None

    windows: list[WindowInfo] = []
    title_filter_cf = title_filter.casefold() if title_filter else None

    @_ENUM_WINDOWS_PROC
    def _callback(hwnd: int, _: int) -> bool:
        visible = bool(_USER32.IsWindowVisible(wintypes.HWND(hwnd)))
        minimized = bool(_USER32.IsIconic(wintypes.HWND(hwnd)))
        if not visible or minimized:
            return True

        title = _window_title(hwnd)
        if not title:
            return True

        if title_filter_cf and title_filter_cf not in title.casefold():
            return True

        try:
            rect = get_client_rect(hwnd)
        except WindowApiError:
            return True

        windows.append(WindowInfo(hwnd=int(hwnd), title=title, rect=rect))
        return True

    ok = _USER32.EnumWindows(_callback, 0)
    if not ok:
        raise _last_error("EnumWindows failed")

    return windows


def _score_window_match(title: str, title_hint: str) -> int:
    normalized_title = title.casefold().strip()
    normalized_hint = title_hint.casefold().strip()
    if not normalized_hint:
        return 0
    if normalized_title == normalized_hint:
        return 300 + len(normalized_hint)
    if normalized_title.startswith(normalized_hint):
        return 200 + len(normalized_hint)
    if normalized_hint in normalized_title:
        return 100 + len(normalized_hint)
    return -1


def select_best_window(candidates: Sequence[WindowInfo], title_hint: str) -> WindowInfo | None:
    """Select the strongest title match, breaking ties by larger client area."""
    if not candidates:
        return None

    best: WindowInfo | None = None
    best_score = -1
    best_area = -1

    for candidate in candidates:
        score = _score_window_match(candidate.title, title_hint)
        if score < 0:
            continue

        area = candidate.rect.width * candidate.rect.height
        if score > best_score or (score == best_score and area > best_area):
            best = candidate
            best_score = score
            best_area = area

    return best


def find_window(title_hint: str) -> WindowInfo:
    """Find a visible non-minimized window by title hint."""
    candidates = list_visible_windows(title_hint)
    best = select_best_window(candidates, title_hint)
    if best is None:
        raise WindowNotFoundError(
            f"No visible window matched title hint '{title_hint}'"
        )
    return best


def locate_window(title_hint: str, *, use_client_rect: bool = True) -> WindowInfo:
    """Find target window and return refreshed geometry."""
    best = find_window(title_hint)
    rect = get_client_rect(best.hwnd) if use_client_rect else get_window_rect(best.hwnd)
    return WindowInfo(hwnd=best.hwnd, title=best.title, rect=rect)


def get_foreground_window_handle() -> int | None:
    """Return the current foreground window handle."""
    _require_windows_api()
    assert _USER32 is not None

    hwnd = _USER32.GetForegroundWindow()
    if hwnd == 0:
        return None
    return int(hwnd)


def is_window_focused(hwnd: int) -> bool:
    """Check whether the provided window handle is currently foreground."""
    foreground = get_foreground_window_handle()
    return foreground == hwnd
