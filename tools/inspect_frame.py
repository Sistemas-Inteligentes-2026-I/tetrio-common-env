"""Capture and save inspection frames from the target TETR.IO window."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from tetrio_env.capture.frame_clock import FrameClock
from tetrio_env.capture.screen_grabber import CaptureBackendError, CaptureRegion, ScreenGrabber
from tetrio_env.capture.window_locator import (
    WindowApiError,
    WindowNotFoundError,
    is_window_focused,
    list_visible_windows,
    locate_window,
)
from tetrio_env.config import load_session_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture inspection frames for calibration/debug")
    parser.add_argument("--config", type=str, default=None, help="Optional session config path")
    parser.add_argument("--title-hint", type=str, default=None, help="Override window title hint")
    parser.add_argument("--frames", type=int, default=3, help="Number of frames to capture")
    parser.add_argument("--fps", type=int, default=None, help="Capture pacing FPS")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="artifacts/frames",
        help="Directory to store captured frames",
    )
    parser.add_argument(
        "--include-window-frame",
        action="store_true",
        help="Capture full outer window instead of client area",
    )
    parser.add_argument(
        "--allow-unfocused",
        action="store_true",
        help="Capture even if target window is not currently focused",
    )
    parser.add_argument(
        "--list-windows",
        action="store_true",
        help="List visible matching windows and exit",
    )
    return parser


def _build_capture_region(x: int, y: int, width: int, height: int) -> CaptureRegion:
    return CaptureRegion(x=x, y=y, width=width, height=height)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.frames <= 0:
        parser.error("--frames must be positive")
    if args.fps is not None and args.fps <= 0:
        parser.error("--fps must be positive")

    session = load_session_config(args.config)
    title_hint = args.title_hint or session.window_title_hint

    try:
        if args.list_windows:
            windows = list_visible_windows(title_hint)
            if not windows:
                print(f"No visible windows matched '{title_hint}'.")
                return 1

            print(f"Found {len(windows)} visible window(s) matching '{title_hint}':")
            for window in windows:
                rect = window.rect
                print(
                    f"- hwnd={window.hwnd} title='{window.title}' "
                    f"rect=({rect.x},{rect.y},{rect.width},{rect.height})"
                )
            return 0

        window = locate_window(title_hint, use_client_rect=not args.include_window_frame)
        if not args.allow_unfocused and not is_window_focused(window.hwnd):
            print("Target window is not focused. Use --allow-unfocused to override.")
            return 2

        region = _build_capture_region(
            x=window.rect.x,
            y=window.rect.y,
            width=window.rect.width,
            height=window.rect.height,
        )

        fps = args.fps or session.capture_fps
        clock = FrameClock(target_fps=fps)

        session_dir = Path(args.output_dir) / datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir.mkdir(parents=True, exist_ok=True)

        print(
            f"Capturing {args.frames} frame(s) from hwnd={window.hwnd} "
            f"at {fps} FPS into {session_dir}"
        )

        with ScreenGrabber(region) as grabber:
            for _ in range(args.frames):
                tick = clock.wait_for_next_frame()
                frame = grabber.grab()
                out_path = session_dir / f"frame_{frame.frame_id:05d}_{frame.timestamp_ms}.bmp"
                frame.save_bmp(out_path)

                print(
                    f"frame={frame.frame_id} tick={tick.frame_id} "
                    f"ts_ms={frame.timestamp_ms} size={frame.width}x{frame.height} "
                    f"file={out_path.name}"
                )

        print("Capture complete.")
        return 0

    except (WindowApiError, WindowNotFoundError, CaptureBackendError) as exc:
        print(f"inspect_frame error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
