# Contributing Guide

## Branch and PR Policy

- Branch names for new work should use prefixes like `feature/`, `fix/`, or `docs/`.
- Keep each PR scoped to one concern.
- Include tests or a clear reason when tests are not added.
- Do not include team private strategy logic in this repository.

## Local Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

## Required Checks

Before opening a PR run:

```powershell
ruff check .
mypy src
pytest
```

## Code Rules

- Respect module boundaries (capture, calibration, vision, control, agent, telemetry).
- Keep observation and action logic decoupled.
- Prefer config-driven behavior over hardcoded values.
- Add logs that improve debugging without leaking private data.
