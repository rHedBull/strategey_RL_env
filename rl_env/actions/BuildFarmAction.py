from typing import Tuple

from agents.Sim_Agent import Agent
from rl_env.actions.BuildAction import BuildAction
from rl_env.objects.Building import BuildingType
from rl_env.objects.Farm import Farm


class BuildFarmAction(BuildAction):
    def __init__(self, agent: Agent, position: Tuple[int, int]):
        super().__init__(agent, position, BuildingType.FARM)

    def perform_build(self, env):
        building_type_id = self.get_building_type_id(env)
        farm = Farm(self.agent.id, self.position, building_type_id)
        env.map.add_building(farm, self.position)
        # TODO: add farm to agent's list of buildings
        env.map.claim_tile(self.agent, self.position)
        self.agent.claimed_tiles.add(self.position)

        self.agent.update_local_visibility(self.position)
