"""Screen capture backend with pluggable provider and debug frame serialization."""

from __future__ import annotations

import struct
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from tetrio_env.capture.frame_clock import now_timestamp_ms


class CaptureBackendError(RuntimeError):
    """Raised when the capture backend is unavailable."""


class CaptureError(RuntimeError):
    """Raised when a frame capture call fails."""


@dataclass(frozen=True, slots=True)
class CaptureRegion:
    """Capture region in screen pixel coordinates."""

    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("CaptureRegion width and height must be positive")

    def as_monitor(self) -> dict[str, int]:
        return {
            "left": self.x,
            "top": self.y,
            "width": self.width,
            "height": self.height,
        }


@dataclass(frozen=True, slots=True)
class CapturedFrame:
    """Raw BGRA frame and metadata."""

    frame_id: int
    timestamp_ms: int
    region: CaptureRegion
    width: int
    height: int
    bgra: bytes

    def __post_init__(self) -> None:
        if self.frame_id < 0:
            raise ValueError("frame_id must be >= 0")
        if self.timestamp_ms < 0:
            raise ValueError("timestamp_ms must be >= 0")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Frame dimensions must be positive")

        expected = self.width * self.height * 4
        if len(self.bgra) != expected:
            raise ValueError(
                "Invalid BGRA payload length: "
                f"expected={expected} actual={len(self.bgra)}"
            )

    def save_bmp(self, path: str | Path) -> Path:
        """Write frame as 24-bit BMP for debugging and fixtures."""
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(_bgra_to_bmp_bytes(self.width, self.height, self.bgra))
        return output


class _GrabResult(Protocol):
    width: int
    height: int
    bgra: bytes


class _Backend(Protocol):
    def grab(self, monitor: Mapping[str, int]) -> _GrabResult:
        ...

    def close(self) -> None:
        ...


BackendFactory = Callable[[], _Backend]


def _default_backend_factory() -> _Backend:
    try:
        from mss import mss
    except ModuleNotFoundError as exc:
        raise CaptureBackendError(
            "mss is required for screen capture. Install with: pip install mss"
        ) from exc

    return mss()


class ScreenGrabber:
    """Stateful frame grabber for a fixed screen region."""

    def __init__(
        self,
        region: CaptureRegion,
        *,
        backend_factory: BackendFactory | None = None,
    ) -> None:
        self._region = region
        self._backend_factory = backend_factory or _default_backend_factory
        self._backend: _Backend | None = None
        self._next_frame_id = 0

    @property
    def region(self) -> CaptureRegion:
        return self._region

    def set_region(self, region: CaptureRegion) -> None:
        self._region = region

    def start(self) -> None:
        if self._backend is None:
            self._backend = self._backend_factory()

    def close(self) -> None:
        if self._backend is not None:
            self._backend.close()
            self._backend = None

    def __enter__(self) -> ScreenGrabber:
        self.start()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        _ = exc_type
        _ = exc
        _ = tb
        self.close()

    def grab(self) -> CapturedFrame:
        if self._backend is None:
            self.start()

        assert self._backend is not None
        monitor = self._region.as_monitor()

        try:
            shot = self._backend.grab(monitor)
        except Exception as exc:  # pragma: no cover - backend-specific errors
            raise CaptureError(f"Failed to capture frame for region={monitor}") from exc

        frame = CapturedFrame(
            frame_id=self._next_frame_id,
            timestamp_ms=now_timestamp_ms(),
            region=self._region,
            width=int(shot.width),
            height=int(shot.height),
            bgra=bytes(shot.bgra),
        )
        self._next_frame_id += 1
        return frame


def grab_region_once(
    region: CaptureRegion,
    *,
    backend_factory: BackendFactory | None = None,
) -> CapturedFrame:
    """Convenience helper to capture one frame without managing lifecycle."""
    with ScreenGrabber(region, backend_factory=backend_factory) as grabber:
        return grabber.grab()


def _bgra_to_bmp_bytes(width: int, height: int, bgra: bytes) -> bytes:
    row_in = width * 4
    row_out = width * 3
    padding = (4 - (row_out % 4)) % 4
    row_stride = row_out + padding
    pixel_data_size = row_stride * height

    file_header_size = 14
    dib_header_size = 40
    pixel_data_offset = file_header_size + dib_header_size
    file_size = pixel_data_offset + pixel_data_size

    file_header = struct.pack(
        "<2sIHHI",
        b"BM",
        file_size,
        0,
        0,
        pixel_data_offset,
    )
    dib_header = struct.pack(
        "<IIIHHIIIIII",
        dib_header_size,
        width,
        height,
        1,
        24,
        0,
        pixel_data_size,
        2835,
        2835,
        0,
        0,
    )

    pixels = bytearray(pixel_data_size)
    write_at = 0
    for y in range(height - 1, -1, -1):
        start = y * row_in
        end = start + row_in
        row = bgra[start:end]

        for x in range(width):
            pixel_start = x * 4
            pixels[write_at : write_at + 3] = row[pixel_start : pixel_start + 3]
            write_at += 3

        if padding:
            pixels[write_at : write_at + padding] = b"\x00" * padding
            write_at += padding

    return file_header + dib_header + bytes(pixels)
