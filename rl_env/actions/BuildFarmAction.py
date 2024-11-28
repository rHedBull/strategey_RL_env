from agents.Sim_Agent import Agent
from map.MapPosition import MapPosition
from rl_env.actions.BuildAction import BuildAction
from rl_env.objects.Building import BuildingType
from rl_env.objects.Farm import Farm


class BuildFarmAction(BuildAction):
    def __init__(self, agent: Agent, position: MapPosition):
        super().__init__(agent, position, BuildingType.FARM)

    def validate(self, env) -> bool:
        if not super().validate(env):
            return False

        tile = env.map.get_tile(self.position)
        tile_owner_id = tile.get_owner()

        if tile_owner_id == self.agent.id:
            if tile.has_any_building():
                print(f"Tile{self.position} already has a Building.")
                return False
            else:
                return True

        return False

    def perform_build(self, env):
        building_type_id = self.get_building_type_id(env)
        farm = Farm(self.agent.id, self.position, building_type_id)
        env.map.add_building(farm, self.position)
        # TODO: add farm to agent's list of buildings
        env.map.claim_tile(self.agent, self.position)
        self.agent.claimed_tiles.add(self.position)

        self.agent.update_local_visibility(self.position)
