from strategyRLEnv.actions.BuildAction import BuildAction
from strategyRLEnv.Agent import Agent
from strategyRLEnv.map import MapPosition
from strategyRLEnv.map.map_settings import BuildingType, LandType
from strategyRLEnv.objects.Road import Bridge, Road, update_road_bridge_shape


class BuildRoadAction(BuildAction):
    def __init__(self, agent: Agent, position: MapPosition):
        super().__init__(agent, position, BuildingType.ROAD)

    def get_cost(self, env) -> float:
        """Return the cost of the action."""
        cost = super().get_cost(env)
        if env.map.get_tile(self.position).land_type == LandType.MOUNTAIN:
            cost *= 2
        return cost

    def validate(self, env) -> bool:
        if not super().validate(env):
            return False

        next_to_road, _ = env.map.tile_is_next_to_building_type(
            self.position, BuildingType.ROAD, diagonal=False
        )
        if next_to_road:
            return True

        next_to_bridge, _ = env.map.tile_is_next_to_building_type(
            self.position, BuildingType.BRIDGE, diagonal=False
        )
        if next_to_bridge:
            return True

        next_to_city, tile = env.map.tile_is_next_to_building_type(
            self.position, BuildingType.CITY, diagonal=False
        )
        if next_to_city and tile.get_owner() == self.agent.id:
            return True

        return False

    def perform_build(self, env):
        building_type_id = self.get_building_parameters(env)
        road = Road(self.position, building_type_id)

        update_road_bridge_shape(road, env.map)

        return road


class BuildBridgeAction(BuildAction):
    def __init__(self, agent: Agent, position: MapPosition):
        super().__init__(agent, position, BuildingType.BRIDGE)

    def validate(self, env) -> bool:
        if not super().validate(env):
            return False

        next_to_road, _ = env.map.tile_is_next_to_building_type(
            self.position, BuildingType.ROAD, diagonal=False
        )
        if next_to_road:
            return True

        next_to_bridge, _ = env.map.tile_is_next_to_building_type(
            self.position, BuildingType.BRIDGE, diagonal=False
        )
        if next_to_bridge:
            return True

        next_to_city, tile = env.map.tile_is_next_to_building_type(
            self.position, BuildingType.CITY, diagonal=False
        )
        if next_to_city and tile.get_owner() == self.agent.id:
            return True

        return False

    def perform_build(self, env):
        building_type_id = self.get_building_parameters(env)
        bridge = Bridge(self.position, building_type_id)

        update_road_bridge_shape(bridge, env.map)
        return bridge
