from typing import Tuple

from strategyRLEnv.actions.Action import Action, ActionType
from strategyRLEnv.Agent import Agent
from strategyRLEnv.map.map_settings import OWNER_DEFAULT_TILE
from strategyRLEnv.map.MapPosition import MapPosition


class ClaimAction(Action):
    def __init__(self, agent: Agent, position: MapPosition):
        super().__init__(agent, position, ActionType.CLAIM)

    def validate(self, env) -> bool:
        if not super().validate(env):
            return False

        if env.map.get_tile(self.position).get_owner() != OWNER_DEFAULT_TILE:
            return False

        # check if visible for agent
        if not env.map.is_visible(self.position, self.agent.id):
            return False

        # surrounding tiles
        surrounding_tiles = env.map.get_surrounding_tiles(self.position)

        adjacent_claimed = False
        for tile in surrounding_tiles:
            if tile.get_owner() == self.agent.id:
                adjacent_claimed = True
                break

        if not adjacent_claimed:
            return False

        return True

    def execute(self, env) -> int:
        env.map.claim_tile(self.agent, self.position)
        self.agent.add_claimed_tile(self.position)
        self.agent.update_local_visibility(self.position)

        self.agent.money -= env.action_manager.actions_definition["claim"]["cost"]
        reward = env.action_manager.actions_definition["claim"]["reward"]
        return reward


def is_claimable(agent: Agent, position: Tuple[int, int]) -> bool:
    # check if position is in agent's claimable_tiles list

    if position in agent.claimable_tiles:
        return True
    else:
        return False
