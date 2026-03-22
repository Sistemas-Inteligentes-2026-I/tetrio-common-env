"""Configuration loading and validation helpers."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .types import ACTION_NAMES, CalibrationProfile, Rect, SessionConfig, Size

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SESSION_CONFIG = REPO_ROOT / "configs" / "session.default.json"


class ConfigError(ValueError):
    """Raised when configuration files are missing or invalid."""


def load_session_config(path: str | Path | None = None) -> SessionConfig:
    """Load and validate the session configuration JSON file."""
    session_path = _resolve_config_path(path, fallback=DEFAULT_SESSION_CONFIG)
    payload = _load_json_object(session_path)

    base_resolution = _read_size(payload, "base_resolution", session_path)

    return SessionConfig(
        browser=_read_str(payload, "browser", session_path).lower(),
        window_title_hint=_read_str(payload, "window_title_hint", session_path),
        base_resolution=base_resolution,
        browser_zoom=_read_float(payload, "browser_zoom", session_path),
        capture_fps=_read_int(payload, "capture_fps", session_path),
        safe_mode=_read_bool(payload, "safe_mode", session_path),
        panic_key=_read_str(payload, "panic_key", session_path),
        calibration_profile=_read_str(payload, "calibration_profile", session_path),
        keymap_path=_read_str(payload, "keymap_path", session_path),
    )


def load_calibration_profile(
    path: str | Path | None = None,
    *,
    session_config: SessionConfig | None = None,
) -> CalibrationProfile:
    """Load and validate a calibration profile JSON file."""
    if path is None:
        active_session = session_config or load_session_config()
        profile_path = _resolve_config_path(active_session.calibration_profile)
    else:
        profile_path = _resolve_config_path(path)

    payload = _load_json_object(profile_path)

    return CalibrationProfile(
        name=_read_str(payload, "name", profile_path),
        browser=_read_str(payload, "browser", profile_path).lower(),
        base_resolution=_read_size(payload, "base_resolution", profile_path),
        board_rect=_read_rect(payload, "board_rect", profile_path),
        hold_rect=_read_rect(payload, "hold_rect", profile_path),
        next_queue_rect=_read_rect(payload, "next_queue_rect", profile_path),
    )


def load_keymap(
    path: str | Path | None = None,
    *,
    session_config: SessionConfig | None = None,
) -> dict[str, str]:
    """Load and validate the action-to-key mapping."""
    if path is None:
        active_session = session_config or load_session_config()
        keymap_path = _resolve_config_path(active_session.keymap_path)
    else:
        keymap_path = _resolve_config_path(path)

    payload = _load_json_object(keymap_path)

    missing_actions = [action for action in ACTION_NAMES if action not in payload]
    if missing_actions:
        missing = ", ".join(missing_actions)
        raise ConfigError(f"Missing action(s) in keymap '{keymap_path}': {missing}")

    keymap: dict[str, str] = {}
    for action in ACTION_NAMES:
        value = payload[action]
        if not isinstance(value, str):
            raise ConfigError(f"Action '{action}' in keymap must map to a string")
        keymap[action] = value

    return keymap


def _resolve_config_path(path: str | Path | None, *, fallback: Path | None = None) -> Path:
    if path is None:
        if fallback is None:
            raise ConfigError("No configuration path provided")
        return fallback

    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return REPO_ROOT / candidate


def _load_json_object(path: Path) -> Mapping[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"Could not read configuration file '{path}': {exc}") from exc

    try:
        data: Any = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in '{path}': {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError(f"Configuration '{path}' must be a JSON object")

    return data


def _read_mapping(source: Mapping[str, Any], key: str, origin: Path) -> Mapping[str, Any]:
    value = source.get(key)
    if not isinstance(value, dict):
        raise ConfigError(f"Field '{key}' in '{origin}' must be a JSON object")
    return value


def _read_str(source: Mapping[str, Any], key: str, origin: Path) -> str:
    value = source.get(key)
    if not isinstance(value, str) or value == "":
        raise ConfigError(f"Field '{key}' in '{origin}' must be a non-empty string")
    return value


def _read_int(source: Mapping[str, Any], key: str, origin: Path) -> int:
    value = source.get(key)
    if not isinstance(value, int):
        raise ConfigError(f"Field '{key}' in '{origin}' must be an integer")
    return value


def _read_float(source: Mapping[str, Any], key: str, origin: Path) -> float:
    value = source.get(key)
    if not isinstance(value, (int, float)):
        raise ConfigError(f"Field '{key}' in '{origin}' must be a number")
    return float(value)


def _read_bool(source: Mapping[str, Any], key: str, origin: Path) -> bool:
    value = source.get(key)
    if not isinstance(value, bool):
        raise ConfigError(f"Field '{key}' in '{origin}' must be a boolean")
    return value


def _read_size(source: Mapping[str, Any], key: str, origin: Path) -> Size:
    payload = _read_mapping(source, key, origin)
    width = _read_int(payload, "width", origin)
    height = _read_int(payload, "height", origin)
    return Size(width=width, height=height)


def _read_rect(source: Mapping[str, Any], key: str, origin: Path) -> Rect:
    payload = _read_mapping(source, key, origin)
    return Rect(
        x=_read_int(payload, "x", origin),
        y=_read_int(payload, "y", origin),
        width=_read_int(payload, "width", origin),
        height=_read_int(payload, "height", origin),
    )
