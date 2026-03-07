# Project Scope (Phase 0)

## Mission

Build a shared Windows Python environment for TETR.IO browser experimentation that supports capture, calibration, vision, agent integration, keyboard control, and telemetry.

## In Scope

- Screen capture from browser window region.
- Calibration profile management.
- Visual parsing of board and basic game state.
- Standard observation/action contract for agents.
- Safe keyboard emission with emergency stop controls.
- Telemetry, snapshots, and replay export for debugging.

## Out of Scope

- Team-private decision policy or strategy logic.
- Reverse engineering of game internals.
- Direct memory or hidden API extraction.

## Baseline Decisions

- Official browser baseline: Chrome.
- Compatibility target: Edge.
- Baseline resolution: 1920x1080.
- Browser zoom baseline: 100%.
- Window baseline: centered and maximized on primary monitor.
- Keymap baseline: in `configs/keymap.default.json`.

## Repository Policy

Common repository includes only shared infrastructure. Team strategy remains in separate repositories.

## Git Policy

- Short-lived feature branches.
- Mandatory PR review for core modules.
- CI required before merge to main.

## Exit Criteria For Phase 0

No core implementation should start without this scope, baseline settings, and contracts approved.
