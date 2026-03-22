"""Abstract base class for environment agents."""

from __future__ import annotations

from abc import ABC, abstractmethod

from tetrio_env.types import ActionName, Observation


class Agent(ABC):
    """Common interface each agent implementation must satisfy."""

    @abstractmethod
    def reset(self) -> None:
        """Reset agent state at session boundary."""
        ...

    @abstractmethod
    def act(self, observation: Observation) -> ActionName:
        """Return one logical action for the provided observation."""
        ...
