# Technical Architecture (Phase 1)

## High-Level Pipeline

1. Capture frame from browser window.
2. Apply calibration profile and crop canonical regions.
3. Parse visual state (board, active piece, hold, next queue).
4. Build standardized `Observation`.
5. Agent selects logical `Action`.
6. Control layer maps action to keyboard events.
7. Telemetry records timing, snapshots, and action trace.

## Modules and Responsibilities

- `capture`: frame acquisition, window location, frame clock.
- `calibration`: anchor definitions, profile loading, region transform.
- `vision`: parsing utilities and state builder.
- `control`: keymap, rate limiting, focus/safety guards.
- `agents`: base interface and sample agents.
- `telemetry`: structured logs and session recording.

## Contract Types

Core domain types are defined in `src/tetrio_env/types.py`:

- `Observation`
- `ActionName`
- `BoardState`
- `PieceState`
- `SessionConfig`
- `CalibrationProfile`

## Key Decisions Closed In This Baseline

- Capture mode: window region crop driven by calibration profile.
- Target capture rate: 60 FPS (configurable).
- Calibration mode: manual-assisted (user picks anchors; profile saved).
- Minimum telemetry: action trace, stage timings, optional snapshots.
- Runner mode: single-session foreground loop with explicit safe stop.

## Error Policy

- Config and contract errors raise typed exceptions early.
- Safety preconditions must block keyboard output when invalid.
- Modules return explicit errors instead of silent fallback.

## Logging Policy

- Structured logs with timestamp and stage identifiers.
- Sensitive/private strategy data must not be logged.

## Configuration Loading

- JSON files under `configs/`.
- Default session config at `configs/session.default.json`.
- Validation performed on load; no hidden hardcoded runtime values.
