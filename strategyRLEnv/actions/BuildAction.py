from abc import ABC, abstractmethod
from typing import Dict

from strategyRLEnv.actions.Action import Action, ActionType
from strategyRLEnv.map.map_settings import (ALLOWED_BUILDING_PLACEMENTS,
                                            BuildingType, discovery_reward)
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.objects.Ownable import Ownable


class BuildAction(Action, ABC):
    def __init__(self, agent, position: MapPosition, building_type: BuildingType):
        super().__init__(agent, position, ActionType.BUILD)
        self.building_type = building_type

    def validate(self, env) -> bool:
        if not super().validate(env):
            return False

        tile = env.map.get_tile(self.position)

        if not fit_building_to_land_type(env, self.position, self.building_type):
            return False

        if not env.map.is_visible(self.position, self.agent.id):
            return False

        if tile.has_any_building():
            return False

        # check no opponent unit on the tile
        if tile.unit is not None:
            if tile.unit.owner.id != self.agent.id:
                return False

        return True

    def execute(self, env) -> float:
        building = self.perform_build(env)
        env.map.add_building(building, self.position)
        env.map.get_tile(self.position).update(env)
        env.map.trigger_surrounding_tile_update(self.position)
        self.agent.money -= self.get_cost(env)

        if isinstance(self, Ownable):
            env.map.claim_tile(self.agent, self.position)
            self.agent.add_claimed_tile(self.position)

        discovered = self.agent.update_local_visibility(self.position)
        reward = self.get_reward(env) + discovered * discovery_reward
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

    def get_building_parameters(self, env) -> Dict:
        """Return the building type id."""
        action = env.env_settings.get("actions")[self.building_type.value]
        params = {
            "money_gain_per_turn": action.get("money_gain_per_turn", 0),
            "maintenance_cost_per_turn": action.get("maintenance_cost_per_turn", 0),
        }
        return params


def fit_building_to_land_type(
    env, position: MapPosition, build_type: BuildingType
) -> bool:
    """Check if the land type at the given position is suitable for the building type."""

    land_type_at_position = env.map.get_tile(position).get_land_type()
    if land_type_at_position not in ALLOWED_BUILDING_PLACEMENTS[build_type]:
        return False
    return True
