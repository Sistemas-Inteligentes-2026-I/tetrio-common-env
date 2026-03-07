"""Domain types and contracts for the shared environment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ActionName = Literal[
    "left",
    "right",
    "rotate_cw",
    "rotate_ccw",
    "soft_drop",
    "hard_drop",
    "hold",
    "noop",
]

ACTION_NAMES: tuple[ActionName, ...] = (
    "left",
    "right",
    "rotate_cw",
    "rotate_ccw",
    "soft_drop",
    "hard_drop",
    "hold",
    "noop",
)

PIECE_NAMES: tuple[str, ...] = ("I", "O", "T", "S", "Z", "J", "L")
BOARD_ROWS = 20
BOARD_COLS = 10


@dataclass(frozen=True, slots=True)
class Size:
    """Pixel dimensions for a screen or window region."""

    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Size dimensions must be positive")


@dataclass(frozen=True, slots=True)
class Rect:
    """Rectangle in screen pixel coordinates."""

    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.x < 0 or self.y < 0:
            raise ValueError("Rect coordinates must be non-negative")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Rect dimensions must be positive")


@dataclass(frozen=True, slots=True)
class FrameMeta:
    """Metadata for one captured frame."""

    frame_id: int
    timestamp_ms: int

    def __post_init__(self) -> None:
        if self.frame_id < 0:
            raise ValueError("frame_id must be >= 0")
        if self.timestamp_ms < 0:
            raise ValueError("timestamp_ms must be >= 0")


@dataclass(frozen=True, slots=True)
class BoardState:
    """Canonical 20x10 board occupancy matrix."""

    cells: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        if len(self.cells) != BOARD_ROWS:
            raise ValueError(f"Board must have {BOARD_ROWS} rows")
        for row in self.cells:
            if len(row) != BOARD_COLS:
                raise ValueError(f"Each board row must have {BOARD_COLS} columns")
            if any(cell not in (0, 1) for cell in row):
                raise ValueError("Board cells must be binary occupancy values (0 or 1)")

    @classmethod
    def empty(cls) -> "BoardState":
        return cls(cells=tuple(tuple(0 for _ in range(BOARD_COLS)) for _ in range(BOARD_ROWS)))


@dataclass(frozen=True, slots=True)
class PieceState:
    """Visible state for the currently active piece."""

    piece: str
    x: int
    y: int
    rotation: int = 0

    def __post_init__(self) -> None:
        if self.piece not in PIECE_NAMES:
            raise ValueError(f"Unsupported piece id: {self.piece}")
        if not 0 <= self.rotation <= 3:
            raise ValueError("rotation must be between 0 and 3")


@dataclass(frozen=True, slots=True)
class Observation:
    """Standardized observation passed to an agent."""

    board: BoardState
    frame: FrameMeta
    active_piece: PieceState | None = None
    hold_piece: str | None = None
    next_queue: tuple[str, ...] = ()
    is_game_over: bool = False

    def __post_init__(self) -> None:
        if self.hold_piece is not None and self.hold_piece not in PIECE_NAMES:
            raise ValueError(f"Unsupported hold piece id: {self.hold_piece}")
        for piece in self.next_queue:
            if piece not in PIECE_NAMES:
                raise ValueError(f"Unsupported next queue piece id: {piece}")


@dataclass(frozen=True, slots=True)
class SessionConfig:
    """Shared runtime configuration for one environment session."""

    browser: str
    window_title_hint: str
    base_resolution: Size
    browser_zoom: float
    capture_fps: int
    safe_mode: bool
    panic_key: str
    calibration_profile: str
    keymap_path: str

    def __post_init__(self) -> None:
        supported_browsers = {"chrome", "edge"}
        if self.browser not in supported_browsers:
            raise ValueError(f"browser must be one of: {sorted(supported_browsers)}")
        if not 0.5 <= self.browser_zoom <= 3.0:
            raise ValueError("browser_zoom must be in [0.5, 3.0]")
        if self.capture_fps <= 0:
            raise ValueError("capture_fps must be positive")
        if not self.window_title_hint:
            raise ValueError("window_title_hint must not be empty")
        if not self.panic_key:
            raise ValueError("panic_key must not be empty")


@dataclass(frozen=True, slots=True)
class CalibrationProfile:
    """Pixel regions used by calibration-dependent modules."""

    name: str
    browser: str
    base_resolution: Size
    board_rect: Rect
    hold_rect: Rect
    next_queue_rect: Rect

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Calibration profile name must not be empty")
        if self.browser not in {"chrome", "edge"}:
            raise ValueError("Calibration profile browser must be chrome or edge")
