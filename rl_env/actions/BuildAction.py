from abc import ABC, abstractmethod
from typing import Tuple

from agents.Sim_Agent import Agent
from map.map_settings import ALLOWED_BUILDING_PLACEMENTS
from rl_env.actions.Action import Action, ActionType
from rl_env.objects.Building import BuildingType


class BuildAction(Action, ABC):
    def __init__(
        self, agent: Agent, position: Tuple[int, int], building_type: BuildingType
    ):
        super().__init__(agent, position, ActionType.BUILD)
        self.building_type = building_type

    def validate(self, env) -> bool:
        if not super().validate(env):
            return False

        if not fit_building_to_land_type(env, self.position, self.building_type):
            print(f"Agent {self.agent.id}: Tile at {self.position} is not buildable")
            return False

        if not env.map.is_visible(self.position, self.agent.id):
            print(f"Agent {self.agent.id}: Tile at {self.position} is not visible")
            return False

        if env.map.get_tile(self.position).has_any_building():
            print(
                f"Agent {self.agent.id}: Tile at {self.position} already has a building"
            )
            return False

        return True

    def execute(self, env) -> float:
        self.perform_build(env)
        self.agent.money -= self.get_cost(env)
        reward = self.get_reward(env)
        print(
            f"Agent {self.agent.id}: Built {self.building_type.value} at {self.position}. Reward: {reward}"
        )
        return reward

    @abstractmethod
    def perform_build(self, env):
        """Execute the build on the map."""
        pass

    def get_cost(self, env) -> float:
        """Return the cost of the action."""
        return env.env_settings.get("actions")[self.building_type.value]["cost"]

    def get_reward(self, env) -> float:
        """Return the reward for the action."""
        return env.env_settings.get("actions")[self.building_type.value]["reward"]

    def get_building_type_id(self, env) -> int:
        """Return the building type id."""
        return env.env_settings.get("actions")[self.building_type.value]["build_type_id"]


def fit_building_to_land_type(
    env, position: Tuple[int, int], build_type: BuildingType
) -> bool:
    """Check if the land type at the given position is suitable for the building type."""

    land_type_at_position = env.map.get_tile(position).get_land_type()
    if land_type_at_position not in ALLOWED_BUILDING_PLACEMENTS[build_type]:
        return False
    return True
