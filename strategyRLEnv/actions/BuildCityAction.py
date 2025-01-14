from strategyRLEnv.actions.BuildAction import BuildAction
from strategyRLEnv.map.map_settings import OWNER_DEFAULT_TILE, BuildingType
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.objects.City import City


class BuildCityAction(BuildAction):
    def __init__(self, agent, position: MapPosition):
        super().__init__(agent, position, BuildingType.CITY)

    def validate(self, env) -> bool:
        if not super().validate(env):
            return False

        city_clearance_radius = env.env_settings.get("city_clearance_radius", 2)

        too_close_to_city, _ = env.map.tile_is_next_to_building_type(
            self.position, BuildingType.CITY, radius=city_clearance_radius
        )
        if too_close_to_city:
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
        city = City(self.agent, self.position, params)

        self.agent.add_city(city)
        return city
