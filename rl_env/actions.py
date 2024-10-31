import random
from typing import Any, Dict, List, Tuple

import numpy as np

from agents.Sim_Agent import Agent
from map.map_settings import OWNER_DEFAULT_TILE
from rl_env.CityAction import CityAction
from rl_env.ClaimAction import ClaimAction
from rl_env.MoveAction import MoveAction

def create_action(agent, action_data):
    move_direction = action_data["move"].get("direction", None)
    claim_happens = action_data["claim"] is not None
    city_build = action_data["city"] is not None

    if move_direction:
        direction = action_data['move'].get("direction")
        return MoveAction(agent, direction)
    elif claim_happens:
        position = action_data['claim']
        return ClaimAction(agent, position)
    elif city_build:
        position = action_data['city']
        return CityAction(agent, position)
    else:
        # Handle unknown action type
        pass


class ActionManager:
    """
    Manages the application of movement actions within the environment,
    detecting conflicts when multiple agents attempt to move to the same tile
    and randomly resolving those conflicts.
    """

    def __init__(self, env, env_settings):
        self.env = env
        self.env_settings = env_settings
        self.actions_definition = self.env_settings.get_setting("actions")

        # Define a structured array with the fields 'action' and 'agent_id'.
        self.conflict_map = {}

    def apply_actions(
        self, actions: Any, agents: List[Agent]
    ) -> Tuple[List[float], List[bool]]:
        """
        Processes the movement actions of all agents, resolves conflicts,
        and returns the outcomes for each agent.

        Args:
            actions (List[Dict[str, Any]]): List of action dictionaries from each agent.
            agents (List[Agent]): List of agent instances.

        Returns:
            Dict[int, Dict[str, Any]]: A dictionary mapping agent IDs to their action outcomes.
        """

        proposed_actions = {}
        rewards = np.zeros(len(agents), dtype=float)
        dones = np.zeros(len(agents), dtype=bool)

        for agent, action in zip(agents, actions):

            action = create_action(agent, action)
            if action.validate(self.env):
                proposed_actions[agent.id] = action
                position_key = action.position
                self.conflict_map.setdefault(position_key, []).append(action)
            else:
                proposed_actions[agent.id] = None
                rewards[agent.id] = -1  # Penalty for invalid action
                dones[agent.id] = False

        self.resolve_conflict(proposed_actions)

        # Execute actions
        for agent_id, action in proposed_actions.items():
            if action:

                reward = action.execute(self.env)
                rewards[agent_id] = reward
                dones[agent_id] = False  # Set to True if the action leads to a terminal state

        # Clear the conflict map for the next turn
        self.conflict_map = {}

        return rewards, dones



    def resolve_conflict(self, proposed_actions):
        for position, actions_at_position in self.conflict_map.items():
            if len(actions_at_position) > 1:
                print(f"Conflict detected at position {position} among agents {[action.agent.id for action in actions_at_position]}.")

                # Implement your conflict resolution strategy here.
                # For fairness, we can randomly select a winner.
                winner = random.choice(actions_at_position)
                print(f"Agent {winner.agent.id} wins the conflict at position {position}.")

                # Invalidate other actions at this position
                for action in actions_at_position:
                    if action != winner:
                        proposed_actions[action.agent.id] = None
                        print(f"Agent {action.agent.id}'s action at position {position} has been invalidated due to conflict.")



    def check_position_on_map(self, position: Tuple[int, int]) -> bool:
        """
        :param self:
        :param position:
        :return:
        """
        x, y = position
        max_x = self.env.map.width
        max_y = self.env.map.height  # assuming a square map
        if 0 <= x < max_x and 0 <= y < max_y:
            return True
        return False

    def update_claimable_tiles(self, agent: Agent, new_claimed_tile: Tuple[int, int]):
        """
        Updates the agent's set of claimable tiles by adding new adjacent tiles
        to the newly claimed tile. Limits the number of additions to 3 (or 5 if diagonals are allowed).

        :param agent: The agent who claimed the new tile.
        :param new_claimed_tile: The position of the newly claimed tile.
        """
        x, y = new_claimed_tile

        # remove claimed tile
        agent.claimable_tiles.discard(new_claimed_tile)

        new_possible = [
            (x, y - 1),  # Up
            (x, y + 1),  # Down
            (x - 1, y),  # Left
            (x + 1, y),  # Right
        ]

        # if allow_diagonal:
        # diagonal_positions = [
        #         #     (x - 1, y - 1),
        #         #     (x + 1, y - 1),
        #         #     (x - 1, y + 1),
        #         #     (x + 1, y + 1)
        #         # ]
        claimed_copy = agent.claimed_tiles.copy()
        claimable_copy = agent.claimable_tiles.copy()

        new_claimable = []
        for pos in new_possible:
            # Check if the position is valid and not already listed as claimed or claimable
            if (
                self.check_position_on_map(pos)
                and pos not in claimed_copy
                and pos not in claimable_copy
            ):
                new_claimable.append(pos)

        agent.claimable_tiles.update(new_claimable)

