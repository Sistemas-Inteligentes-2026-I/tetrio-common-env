"""Lightweight orchestrator for the observation-action loop."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from tetrio_env.agents.base import Agent
from tetrio_env.types import ActionName, Observation


class ObservationProvider(Protocol):
    """Adapter interface used by the runner to receive observations."""

    def get_observation(self) -> Observation:
        """Return the latest observation from capture+vision pipeline."""
        ...


class ActionSink(Protocol):
    """Adapter interface used by the runner to emit actions."""

    def emit(self, action: ActionName) -> None:
        """Emit one logical action through control backend."""
        ...


@dataclass(slots=True)
class Runner:
    """Coordinates one step of observe->act->emit execution."""

    agent: Agent
    observation_provider: ObservationProvider
    action_sink: ActionSink

    def reset(self) -> None:
        self.agent.reset()

    def step(self) -> ActionName:
        observation = self.observation_provider.get_observation()
        action = self.agent.act(observation)
        self.action_sink.emit(action)
        return action
