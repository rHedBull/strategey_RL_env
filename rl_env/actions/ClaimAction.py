from typing import Tuple

from agents.Sim_Agent import Agent
from rl_env.actions.Action import Action


class ClaimAction(Action):
    def __init__(self, agent: Agent, position: Tuple[int, int]):
        super().__init__(agent)

        if position is None:
            raise ValueError("Claim position is None")

        self.claim_position = position

    def validate(self, env) -> bool:
        claim_cost = env.env_settings.get_setting("actions")["claim"]["cost"]
        if self.agent.money < claim_cost:
            print(f"Agent {self.agent.id}: Not enough money to claim tile.")
            return False
        if not env.map.check_position_on_map(self.claim_position):
            print(
                f"Agent {self.agent.id}: Claim position {self.claim_position} is out of bounds."
            )
            return False
        if env.map.get_tile(self.claim_position).get_owner() == self.agent:
            print(f"Agent {self.agent.id}: Already owns tile at {self.claim_position}.")
            return False
        if not is_claimable(
            self.agent, self.claim_position
        ):  # TODO: what to do if already claimed by other agent?
            print(
                f"Agent {self.agent.id}: Tile at {self.claim_position} is not claimable."
            )
            return False
        return True

    def execute(self, env) -> int:
        env.map.claim_tile(self.agent, self.claim_position)
        self.agent.claimed_tiles.add(self.claim_position)
        env.action_manager.update_claimable_tiles(self.agent, self.claim_position)
        self.agent.money -= env.action_manager.actions_definition["claim"]["cost"]
        reward = env.action_manager.actions_definition["claim"]["reward"]
        print(
            f"Agent {self.agent.id}: Claimed tile at {self.claim_position}. Reward: {reward}"
        )
        return reward

    @property
    def position(self) -> Tuple[int, int]:
        return self.claim_position


def is_claimable(agent: Agent, position: Tuple[int, int]) -> bool:
    # check if position is in agent's claimable_tiles list

    if position in agent.claimable_tiles:
        return True
    else:
        return False
