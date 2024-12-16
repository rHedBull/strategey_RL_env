from strategyRLEnv.actions.BuildAction import BuildAction
from strategyRLEnv.map.map_settings import OWNER_DEFAULT_TILE
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.objects.Building import BuildingType
from strategyRLEnv.objects.City import City


class BuildCityAction(BuildAction):
    def __init__(self, agent, position: MapPosition):
        super().__init__(agent, position, BuildingType.CITY)

    def validate(self, env) -> bool:
        if not super().validate(env):
            return False

        tile = env.map.get_tile(self.position)
        tile_owner_id = tile.get_owner()

        if tile_owner_id == self.agent.id:
            if tile.has_any_building():
                return False
            else:
                return True

        if tile_owner_id != OWNER_DEFAULT_TILE:
            return False

        return True

    def perform_build(self, env):
        params = self.get_building_parameters(env)
        city = City(self.agent.id, self.position, params)
        env.map.add_building(city, self.position)

        env.map.claim_tile(self.agent, self.position)
        self.agent.add_claimed_tile(self.position)
        self.agent.update_local_visibility(self.position)
