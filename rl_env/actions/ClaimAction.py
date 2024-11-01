from typing import Tuple

from agents.Sim_Agent import Agent
from rl_env.actions.Action import Action, ActionType


class ClaimAction(Action):
    def __init__(self, agent: Agent, position: Tuple[int, int]):
        super().__init__(agent, position, ActionType.CLAIM)

    def validate(self, env) -> bool:
        if not super().validate(env):
            return False

        if env.map.get_tile(self.position).get_owner() == self.agent:
            print(f"Agent {self.agent.id}: Already owns tile at {self.position}.")
            return False

        if not is_claimable(
            self.agent, self.position
        ):  # TODO: what to do if already claimed by other agent?
            print(
                f"Agent {self.agent.id}: Tile at {self.position} is not claimable."
            )
            return False
        return True

    def execute(self, env) -> int:
        env.map.claim_tile(self.agent, self.position)
        self.agent.claimed_tiles.add(self.position)
        env.action_manager.update_claimable_tiles(self.agent, self.position)
        self.agent.money -= env.action_manager.actions_definition["claim"]["cost"]
        reward = env.action_manager.actions_definition["claim"]["reward"]
        print(
            f"Agent {self.agent.id}: Claimed tile at {self.position}. Reward: {reward}"
        )
        return reward


def is_claimable(agent: Agent, position: Tuple[int, int]) -> bool:
    # check if position is in agent's claimable_tiles list

    if position in agent.claimable_tiles:
        return True
    else:
        return False
