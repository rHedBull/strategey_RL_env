from typing import Tuple

from agents.Sim_Agent import Agent
from rl_env.actions.BuildAction import BuildAction
from rl_env.objects.Building import BuildingType
from rl_env.objects.city import City


class BuildCityAction(BuildAction):
    def __init__(self, agent: Agent, position: Tuple[int, int]):
        super().__init__(agent, position, BuildingType.CITY)

    def perform_build(self, env):
        building_type_id = self.get_building_type_id(env)
        city = City(self.agent.id, self.position, building_type_id)
        env.map.add_building(city, self.position)
        # TODO: add city to agent's list of buildings
        env.map.claim_tile(self.agent, self.position)
        self.agent.claimed_tiles.add(self.position)
        env.action_manager.update_claimable_tiles(self.agent, self.position)
