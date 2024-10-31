from abc import ABC, abstractmethod
from typing import Tuple

from agents.Sim_Agent import Agent
from rl_env.actions.Action import Action
from rl_env.actions.ClaimAction import is_claimable


class BuildAction(Action, ABC):
    def __init__(self, agent: Agent, position: Tuple[int, int]):
        super().__init__(agent)
        if position is None:
            raise ValueError("Build position is None")
        self.build_position = position


    def validate(self, env) -> bool:
        build_cost = self.get_cost(env)
        if self.agent.money < build_cost:
            print(f"Agent {self.agent.id}: Not enough money to build {self.build_type()}.")
            return False
        if not env.action_manager.check_position_on_map(self.build_position):
            print(f"Agent {self.agent.id}: Build position {self.build_position} is out of bounds.")
            return False
        if not is_claimable(self.agent, self.build_position): # TODO: might have to adjust this, for road!!
            print(f"Agent {self.agent.id}: Tile at {self.build_position} is not claimable for building.")
            return False

        return True

    def execute(self, env) -> float:
        self.perform_build(env)
        self.agent.money -= self.get_cost(env)
        reward = self.get_reward(env)
        print(f"Agent {self.agent.id}: Built {self.build_type()} at {self.build_position}. Reward: {reward}")
        return reward

    @abstractmethod
    def perform_build(self, env):
        """Execute the build on the map."""
        pass

    @property
    def position(self) -> Tuple[int, int]:
        return self.build_position

    @abstractmethod
    def build_type(self) -> str:
        """Return the type of build (e.g., 'City', 'Road', 'Farm')."""
        pass

    @abstractmethod
    def get_cost(self, env) -> float:
        """Return the cost of the build action."""
        pass

    @abstractmethod
    def get_reward(self, env) -> float:
        """Return the reward for the build action."""
        pass