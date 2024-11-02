from typing import Tuple

from agents.Sim_Agent import Agent
from rl_env.actions.BuildAction import BuildAction
from rl_env.objects.Building import BuildingType
from rl_env.objects.Farm import Farm


class BuildFarmAction(BuildAction):
    def __init__(self, agent: Agent, position: Tuple[int, int]):
        super().__init__(agent, position, BuildingType.FARM)

    def validate(self, env) -> bool:
        if not super().validate(env):
            return False

        # if not is_claimable( # TODO: check if tile already claimed?
        #     self.agent, self.position
        # ):
        #     print(
        #         f"Agent {self.agent.id}: Tile at {self.position} is not claimable for building."
        #     )
        #     return False

        return True

    def perform_build(self, env):
        building_type_id = self.get_building_type_id(env)
        farm = Farm(self.agent.id, self.position, building_type_id)
        env.map.add_building(farm, self.position)
        # TODO: add farm to agent's list of buildings
        env.map.claim_tile(self.agent, self.position)
        self.agent.claimed_tiles.add(self.position)
        env.action_manager.update_claimable_tiles(self.agent, self.position)
