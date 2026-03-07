# Agent Interface Contract (Phase 1)

## Required Interface

An agent must implement:

```python
class Agent:
    def reset(self) -> None: ...
    def act(self, observation: Observation) -> ActionName: ...
```

## Observation Contract

`Observation` includes:

- `board`: canonical 20x10 occupancy matrix.
- `active_piece`: optional current falling piece state.
- `hold_piece`: optional hold piece id.
- `next_queue`: ordered tuple of upcoming piece ids.
- `is_game_over`: terminal visibility flag.
- `frame`: timestamp and frame index metadata.

## Action Contract

Allowed logical actions:

- `left`
- `right`
- `rotate_cw`
- `rotate_ccw`
- `soft_drop`
- `hard_drop`
- `hold`
- `noop`

Actions outside this set are invalid.

## Execution Semantics

- Runner requests one action per observation tick.
- `noop` is valid and means no keyboard emission.
- Agent should be pure over observation whenever possible.

## Safety Semantics

Runner/control must block action emission when:

- no valid calibration profile is loaded
- target window is not focused
- system safe mode is enabled
- panic stop is active

## Versioning

Any change to observation or action schema requires contract versioning and migration notes.
