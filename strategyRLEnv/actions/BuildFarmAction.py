from strategyRLEnv.actions.BuildAction import BuildAction
from strategyRLEnv.map import MapPosition
from strategyRLEnv.objects.Building import BuildingType
from strategyRLEnv.objects.Farm import Farm
from strategyRLEnv.Agent import Agent


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
        farm = Farm(self.agent.id, self.position, self.get_building_parameters(env))
        env.map.add_building(farm, self.position)

        env.map.claim_tile(self.agent, self.position)
        self.agent.add_claimed_tile(self.position)
        self.agent.update_local_visibility(self.position)
