from typing import Tuple

from agents.Sim_Agent import Agent
from rl_env.Action import Action
from rl_env.ClaimAction import is_claimable
from rl_env.city import City


class CityAction(Action):
    def __init__(self, agent: Agent, position: Tuple[int, int]):
        super().__init__(agent)

        if position is None:
            raise ValueError("City position is None")

        self.city_position = position

    def validate(self, env) -> bool:
        city_cost = env.env_settings.get_setting("actions")["city"]["cost"]
        if self.agent.money < city_cost:
            print(f"Agent {self.agent.id}: Not enough money to build a city.")
            return False
        if not env.action_manager.check_position_on_map(self.city_position):
            print(f"Agent {self.agent.id}: City position {self.city_position} is out of bounds.")
            return False
        if not is_claimable(self.agent, self.city_position):
            print(f"Agent {self.agent.id}: Cannot build city at {self.city_position}.")
            return False
        return True

    def execute(self, env) -> int:
        city = City(self.agent.id, self.city_position)
        tile = env.map.get_tile(self.city_position)
        tile.buildings.add(city)
        env.map.claim_tile(self.agent, self.city_position)
        self.agent.claimed_tiles.add(self.city_position)
        env.action_manager.update_claimable_tiles(self.agent, self.city_position)

        self.agent.money -= env.action_manager.actions_definition["city"]["cost"]
        reward = env.action_manager.actions_definition["city"]["reward"]
        print(f"Agent {self.agent.id}: Built city at {self.city_position}. Reward: {reward}")
        return reward

    @property
    def position(self) -> Tuple[int, int]:
        return self.city_position

# TODO test and resolve multiple action child classes!!!