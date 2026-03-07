"""Simple random baseline agent implementation."""

from __future__ import annotations

import random

from tetrio_env.agents.base import Agent
from tetrio_env.types import ACTION_NAMES, ActionName, Observation


class RandomAgent(Agent):
    """Randomly selects actions from the shared action space."""

    def __init__(self, *, include_noop: bool = True) -> None:
        self._actions: tuple[ActionName, ...]
        if include_noop:
            self._actions = ACTION_NAMES
        else:
            self._actions = tuple(action for action in ACTION_NAMES if action != "noop")

    def reset(self) -> None:
        return None

    def act(self, observation: Observation) -> ActionName:
        _ = observation
        return random.choice(self._actions)
