from abc import ABC, abstractmethod
from enum import Enum, auto

from strategyRLEnv.map import MapPosition


class ActionType(Enum):
    CLAIM = "claim"
    MOVE = "move"
    BUILD = auto()


class Action(ABC):
    def __init__(self, agent, position: MapPosition, action_type: ActionType):
        self.agent = agent

        if position is None:
            raise ValueError("Build position is None")
        self.position = position
        self.action_type = action_type

    def validate(self, env) -> bool:
        """
        Validate if the action is possible given the current state of the environment and the agent.
        """
        action_cost = self.get_cost(env)
        if self.agent.money < action_cost:
            return False

        if not env.map.check_position_on_map(self.position):
            return False

        return True

    @abstractmethod
    def execute(self, env) -> int:
        """
        Execute the action, updating the environment and the agent's state. Returns the reward.
        """
        pass

    def get_cost(self, env) -> float:
        """Return the cost of the action."""
        return env.env_settings.get("actions")[self.action_type.value]["cost"]

    def get_reward(self, env) -> float:
        """Return the reward for the action."""
        return env.env_settings.get("actions")[self.action_type.value]["reward"]
