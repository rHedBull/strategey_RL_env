from typing import Tuple

from agents.Sim_Agent import Agent
from rl_env.actions.Action import Action, ActionType


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
        super().__init__(agent, (-1, -1), ActionType.MOVE)

        if direction not in [0, 1, 2, 3, 4]:
            raise ValueError(f"Invalid direction: {direction}")
        self.direction = direction
        self.position = calculate_new_position(self.agent.position, self.direction)

    def execute(self, env) -> int:
        self.agent.position = self.position
        self.agent.money -= env.action_manager.actions_definition["move"]["cost"]
        reward = env.action_manager.actions_definition["move"]["reward"]
        print(
            f"Agent {self.agent.id}: Moved to {self.agent.position}. Reward: {reward}"
        )
        return reward
