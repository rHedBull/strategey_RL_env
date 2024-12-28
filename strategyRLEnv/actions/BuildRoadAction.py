from strategyRLEnv.actions.BuildAction import BuildAction
from strategyRLEnv.Agent import Agent
from strategyRLEnv.map import MapPosition
from strategyRLEnv.map.map_settings import LandType
from strategyRLEnv.objects.Building import BuildingType
from strategyRLEnv.objects.Road import Bridge, Road, update_road_bridge_shape


def next_to_road_or_bridge(map, position):
    surroundings = map.get_surrounding_tiles(position, 1)
    for tile in surroundings:
        if tile.has_road() or tile.has_bridge():
            return True
    return False


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

        if self.agent.id == env.map.get_tile(self.position).get_owner():
            # tile is owned by agent
            return True

        if env.map.tile_is_next_to_own_building(self.position, self.agent.id):
            return True

        if next_to_road_or_bridge(env.map, self.position):
            return True

        return False

    def perform_build(self, env):
        building_type_id = self.get_building_parameters(env)
        road = Road(self.position, building_type_id)
        env.map.add_building(road, self.position)

        update_road_bridge_shape(road, env.map)

        self.agent.update_local_visibility(self.position)


class BuildBridgeAction(BuildAction):
    def __init__(self, agent: Agent, position: MapPosition):
        super().__init__(agent, position, BuildingType.BRIDGE)

    def validate(self, env) -> bool:
        if not super().validate(env):
            return False

        if self.agent.id == env.map.get_tile(self.position).get_owner():
            # tile is onwed by agent
            return True

        if env.map.tile_is_next_to_own_building(self.position, self.agent.id):
            return True

        if next_to_road_or_bridge(env.map, self.position):
            return True

        return False

    def perform_build(self, env):
        building_type_id = self.get_building_parameters(env)
        bridge = Bridge(self.position, building_type_id)
        env.map.add_building(bridge, self.position)

        update_road_bridge_shape(bridge, env.map)
        self.agent.update_local_visibility(self.position)
