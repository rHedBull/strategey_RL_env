from typing import Tuple

from agents.Sim_Agent import Agent
from rl_env.actions.BuildAction import BuildAction
from rl_env.objects.Road import road_types, Road

road_types = {
    "horizontal",
    "vertical"
}

class BuildRoadAction(BuildAction):
    def __init__(self, agent: Agent, position: Tuple[int, int], road_type):
        super().__init__(agent, position)

        if road_type not in road_types:
            raise ValueError(f"Invalid road type: {road_type}")
        self.road_type = road_type


    def get_cost(self, env) -> float:
        return env.env_settings.get_setting("actions")["road"]["cost"]

    def get_reward(self, env) -> float:
        return env.env_settings.get_setting("actions")["road"]["reward"]

    def perform_build(self, env):
        road = Road(self.build_position, self.road_type)
        tile = env.map.get_tile(self.build_position)
        tile.buildings.add(road)

    def build_type(self) -> str:
        return "road"