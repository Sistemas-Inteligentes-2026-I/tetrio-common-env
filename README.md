# TETR.IO Common Environment

Shared Windows environment for teams that build TETR.IO browser agents with visual input and keyboard output only.

## Goal

This repository provides common infrastructure to:

- capture game frames from the browser window
- calibrate the useful game region per machine
- reconstruct a standard visible board state
- expose a stable agent interface
- emit keyboard input with safety checks
- record telemetry for debugging and replay

This repository does not include private competitive strategy.

## Scope Rules

- No memory reading from game processes.
- No DOM manipulation to extract hidden game state.
- No private/internal game API usage for play decisions.
- Observation must come from screen pixels only.
- Actions must go through the shared safe keyboard backend.

## Baseline Environment

- OS: Windows
- Python: 3.11+
- Browser target: TETR.IO in Chrome (official baseline) and Edge (compatibility target)
- Base resolution: 1920x1080
- Browser zoom: 100%

## Repository Layout

- `src/tetrio_env/`: application package
- `configs/`: session, keymap, and calibration profiles
- `docs/`: scope, architecture, and interface contracts
- `tools/`: CLI helpers for calibration, inspection, and recording
- `tests/`: unit tests and fixture data
- `.github/`: CI and contribution templates

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev]
pytest
```

## Capture Inspect Tool (Phase 4)

```powershell
python tools/inspect_frame.py --frames 5
```

Useful flags:

- `--list-windows`
- `--title-hint "TETR.IO"`
- `--allow-unfocused`
- `--include-window-frame`

## Core Documents

- `docs/project_scope.md`
- `docs/architecture.md`
- `docs/agent_interface.md`
- `docs/roadmap.md`

## Current Status

The repository now includes the baseline for phases 0 to 4:

- governance decisions and architecture contracts
- Python package bootstrap and tooling
- config and domain types foundations
- capture utilities: window discovery, frame clock, screen grabber
- inspection tool that saves debug frames as BMP
- unit tests for config, types, and capture helpers
