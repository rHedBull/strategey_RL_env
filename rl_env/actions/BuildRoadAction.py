from typing import Tuple

from agents.Sim_Agent import Agent
from rl_env.actions.BuildAction import BuildAction
from rl_env.objects.Building import BuildingType
from rl_env.objects.Road import Road, Bridge, update_road_bridge_shape


class BuildRoadAction(BuildAction):
    def __init__(self, agent: Agent, position: Tuple[int, int]):

        super().__init__(agent, position, BuildingType.ROAD)


    def validate(self, env) -> bool:
        if not super().validate(env):
            return False

        return True
        # if self.agent.id == env.map.get_tile(self.position).get_owner():
        #     # tile is onwed by agent
        #     return True
        #
        # # tile_is_visible = env.map.get_tile(self.build_position).is_visible(self.build_position)
        # # tile_is_next_to_road = env.map.get_tile().is_next_to_road(self.build_position)
        # #
        # # # check if on visible tile
        # # if tile_is_visible and tile_is_next_to_road:
        # #     return True
        #
        # return False

    def perform_build(self, env):
        building_type_id = self.get_building_type_id(env)
        road = Road(self.position, building_type_id)
        env.map.add_building(road, self.position)

        update_road_bridge_shape(road, env.map)

        self.agent.update_local_visibility(self.position)

class BuildBridgeAction(BuildAction):
    def __init__(self, agent: Agent, position: Tuple[int, int]):
        super().__init__(agent, position, BuildingType.BRIDGE)

    def validate(self, env) -> bool:
        if not super().validate(env):
            return False

        return True
        # if self.agent.id == env.map.get_tile(self.position).get_owner():
        #     # tile is onwed by agent
        #     return True
        #
        # # tile_is_visible = env.map.get_tile(self.build_position).is_visible(self.build_position)
        # # tile_is_next_to_road = env.map.get_tile().is_next_to_road(self.build_position)
        # #
        # # # check if on visible tile
        # # if tile_is_visible and tile_is_next_to_road:
        # #     return True
        #
        # return False

    def perform_build(self, env):
        building_type_id = self.get_building_type_id(env)
        bridge = Bridge(self.position, building_type_id)
        env.map.add_building(bridge, self.position)

        update_road_bridge_shape(bridge, env.map)

        env.map.claim_tile(self.agent, self.position)
        self.agent.claimed_tiles.add(self.position)
        env.action_manager.update_claimable_tiles(self.agent, self.position)

        self.agent.update_local_visibility(self.position)