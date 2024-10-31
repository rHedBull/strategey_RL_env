from typing import Tuple

from agents.Sim_Agent import Agent
from rl_env.Action import Action

def calculate_new_position(
    current_position: Tuple[int, int], move_direction: int
) -> Tuple[int, int]:
    """
    Calculates the new position based on the current position and move direction.

    Args:
        current_position (Tuple[int, int]): The agent's current position.
        move_direction (int): Direction to move (0: No move, 1: Up, 2: Down, 3: Left, 4: Right).

    Returns:
        Tuple[int, int]: The new position after the move.
    """
    x, y = current_position
    if move_direction == 1:  # Up
        y -= 1
    elif move_direction == 2:  # Down
        y += 1
    elif move_direction == 3:  # Left
        x -= 1
    elif move_direction == 4:  # Right
        x += 1
    # No move if move_direction is 0 or unrecognized
    return x, y

class MoveAction(Action):
    def __init__(self, agent: Agent, direction: int):
        super().__init__(agent)

        if direction not in [0, 1, 2, 3, 4]:
            raise ValueError(f"Invalid direction: {direction}")

        self.direction = direction
        self.new_position = None

    def validate(self, env) -> bool:
        move_cost = env.env_settings.get_setting("actions")["move"]["cost"]
        if self.agent.money < move_cost:
            print(f"Agent {self.agent.id}: Not enough money to move.")
            return False

        self.new_position = calculate_new_position(self.agent.position, self.direction)
        if not env.action_manager.check_position_on_map(self.new_position):
            print(f"Agent {self.agent.id}: New position {self.new_position} is out of bounds.")
            return False

        return True

    def execute(self, env) -> int:
        self.agent.position = self.new_position
        self.agent.money -= env.action_manager.actions_definition["move"]["cost"]
        reward = env.action_manager.actions_definition["move"]["reward"]
        print(f"Agent {self.agent.id}: Moved to {self.agent.position}. Reward: {reward}")
        return reward

    @property
    def position(self) -> Tuple[int, int]:
        return self.new_position
