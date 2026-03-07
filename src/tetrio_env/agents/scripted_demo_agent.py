"""Deterministic scripted demonstration agent."""

from __future__ import annotations

from tetrio_env.agents.base import Agent
from tetrio_env.types import ActionName, Observation


class ScriptedDemoAgent(Agent):
    """Cycles through a predefined action script."""

    def __init__(self, script: tuple[ActionName, ...] | None = None) -> None:
        self._script = script or ("left", "right", "rotate_cw", "hard_drop", "noop")
        self._index = 0

    def reset(self) -> None:
        self._index = 0

    def act(self, observation: Observation) -> ActionName:
        _ = observation
        action = self._script[self._index]
        self._index = (self._index + 1) % len(self._script)
        return action
