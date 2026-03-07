# Work Roadmap

## Phase Sequence

1. Framework definition (scope, standards, governance).
2. Architecture contract and type boundaries.
3. Repository bootstrap and tooling.
4. Config and domain type foundations.
5. Stable capture module.
6. Calibration workflows and reusable profiles.
7. Minimal viable visual parser.
8. Safe keyboard control module.
9. Agent runner end-to-end integration.
10. Telemetry, hardening, and stable release.

## Current Priorities

High:

- repo structure and tooling
- domain types and config loader
- stable frame capture
- basic calibration
- minimum board parser
- safe keyboard backend

Medium:

- visual overlays
- benchmark tooling
- replay export
- multi-profile browser support

Low:

- advanced auto calibration
- rich debugging UI
- advanced multi-monitor support

## Definition Of Done (Component)

A component is done when:

- responsibility is explicit
- interface is documented and typed
- behavior is config-driven
- useful logs exist
- at least one validation path exists

## Definition Of Usable Environment

Environment is usable when it can:

- capture stable frames
- load a calibration profile
- emit a valid observation
- run a sample agent
- safely map actions to keyboard
- save debugging evidence
