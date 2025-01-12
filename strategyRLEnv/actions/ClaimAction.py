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

        tile = env.map.get_tile(self.position)

        if tile.get_owner() != OWNER_DEFAULT_TILE:
            return False

        # check if visible for agent
        if not env.map.is_visible(self.position, self.agent.id):
            return False

        # check no unit on the tile
        if tile.unit is not None:
            if tile.unit.owner.id != self.agent.id:
                return False

        # surrounding tiles
        adjacent_claimed, _ = env.map.tile_is_next_to_own_tile(
            self.position, self.agent.id, 1
        )
        if not adjacent_claimed:
            return False

        return True

    def execute(self, env):
        env.map.claim_tile(self.agent, self.position)
        self.agent.add_claimed_tile(self.position)
        self.agent.update_local_visibility(self.position)

        self.agent.money -= self.get_cost(env)
        reward = self.get_reward(env)
        return reward


def is_claimable(agent: Agent, position: Tuple[int, int]) -> bool:
    # check if position is in agent's claimable_tiles list

    if position in agent.claimable_tiles:
        return True
    else:
        return False
