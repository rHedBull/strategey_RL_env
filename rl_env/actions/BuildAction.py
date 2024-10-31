from abc import ABC, abstractmethod
from typing import Tuple

from agents.Sim_Agent import Agent
from map.map_settings import ALLOWED_BUILDING_PLACEMENTS
from rl_env.actions.Action import Action
from rl_env.actions.ClaimAction import is_claimable
from rl_env.objects.Building import BuildingType


class BuildAction(Action, ABC):
    def __init__(self, agent: Agent, position: Tuple[int, int]):
        super().__init__(agent)
        if position is None:
            raise ValueError("Build position is None")
        self.build_position = position

    def validate(self, env) -> bool:
        build_cost = self.get_cost(env)
        if self.agent.money < build_cost:
            print(
                f"Agent {self.agent.id}: Not enough money to build {self.build_type()}."
            )
            return False
        if not env.action_manager.check_position_on_map(self.build_position):
            print(
                f"Agent {self.agent.id}: Build position {self.build_position} is out of bounds."
            )
            return False

        if not fit_building_to_land_type(env, self.build_position, self.build_type()):
            print(
                f"Agent {self.agent.id}: Tile at {self.build_position} is not buildable"
            )
            return False
        if not is_claimable(
            self.agent, self.build_position
        ):  # TODO: might have to adjust this, for road!!
            print(
                f"Agent {self.agent.id}: Tile at {self.build_position} is not claimable for building."
            )
            return False

        return True

    def execute(self, env) -> float:
        self.perform_build(env)
        self.agent.money -= self.get_cost(env)
        reward = self.get_reward(env)
        print(
            f"Agent {self.agent.id}: Built {self.build_type()} at {self.build_position}. Reward: {reward}"
        )
        return reward

    @abstractmethod
    def perform_build(self, env):
        """Execute the build on the map."""
        pass

    @property
    def position(self) -> Tuple[int, int]:
        return self.build_position

    @abstractmethod
    def build_type(self) -> BuildingType:
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

def fit_building_to_land_type(env, position: Tuple[int, int], build_type: BuildingType) -> bool:
    """Check if the land type at the given position is suitable for the building type."""

    land_type_at_position = env.map.get_tile(position).get_land_type()
    if land_type_at_position not in ALLOWED_BUILDING_PLACEMENTS[build_type]:
        return False
    return True
