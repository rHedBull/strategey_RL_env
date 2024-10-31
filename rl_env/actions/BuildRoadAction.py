from typing import Tuple

from agents.Sim_Agent import Agent
from rl_env.actions.BuildAction import BuildAction
from rl_env.objects.Building import BuildingType
from rl_env.objects.Road import Road


class BuildRoadAction(BuildAction):
    def __init__(self, agent: Agent, position: Tuple[int, int], road_type):
        super().__init__(agent, position)
        self.road_type = road_type

    def get_cost(self, env) -> float:
        return env.env_settings.get_setting("actions")["road"]["cost"]

    def get_reward(self, env) -> float:
        return env.env_settings.get_setting("actions")["road"]["reward"]

    def perform_build(self, env):
        road = Road(self.build_position, self.road_type, None)
        tile = env.map.get_tile(self.build_position)
        tile.buildings.add(road)

        # TODO: only until notion of visible tiles is introduced
        # TODO: draw road on the map
        env.map.claim_tile(self.agent, self.build_position)
        self.agent.claimed_tiles.add(self.build_position)
        env.action_manager.update_claimable_tiles(self.agent, self.build_position)

    def build_type(self) -> BuildingType:
        return BuildingType.ROAD
