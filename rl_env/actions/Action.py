from abc import ABC, abstractmethod
from typing import Tuple

from agents.Sim_Agent import Agent


class Action(ABC):
    def __init__(self, agent: Agent):
        self.agent = agent

    @abstractmethod
    def validate(self, env) -> bool:
        """
        Validate if the action is possible given the current state of the environment and the agent.
        """
        pass

    @abstractmethod
    def execute(self, env) -> int:
        """
        Execute the action, updating the environment and the agent's state. Returns the reward.
        """
        pass

    @property
    @abstractmethod
    def position(self) -> Tuple[int, int]:
        """
        The position relevant to the action, used for conflict detection.
        """
        pass
