from typing import Tuple

from agents.Sim_Agent import Agent
from rl_env.actions.BuildAction import BuildAction
from rl_env.objects.Building import BuildingType
from rl_env.objects.Road import Road, Bridge


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
        road = Road(self.position)
        tile = env.map.get_tile(self.position)
        tile.buildings.add(road)

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
        bridge = Bridge(self.position)
        tile = env.map.get_tile(self.position)
        tile.buildings.add(bridge)

        self.agent.update_local_visibility(self.position)