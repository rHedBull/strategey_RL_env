from typing import Tuple

from agents.Sim_Agent import Agent
from rl_env.actions.BuildAction import BuildAction
from rl_env.objects.city import City


class CityAction(BuildAction):
    def __init__(self, agent: Agent, position: Tuple[int, int]):
        super().__init__(agent, position)

    def get_cost(self, env) -> float:
        return env.env_settings.get_setting("actions")["city"]["cost"]

    def get_reward(self, env) -> float:
        return env.env_settings.get_setting("actions")["city"]["reward"]

    def perform_build(self, env):
        city = City(self.agent.id, self.build_position, None)
        tile = env.map.get_tile(self.build_position)
        tile.add_building(city)
        # TODO: add city to agent's list of buildings
        env.map.claim_tile(self.agent, self.build_position)
        self.agent.claimed_tiles.add(self.build_position)
        env.action_manager.update_claimable_tiles(self.agent, self.build_position)

    def build_type(self) -> str:
        return "city"
