import random
from typing import Any, List, Tuple

import numpy as np

from MapPosition import MapPosition
from agents.Sim_Agent import Agent
from rl_env.actions.BuildCityAction import BuildCityAction
from rl_env.actions.BuildFarmAction import BuildFarmAction
from rl_env.actions.BuildRoadAction import BuildBridgeAction, BuildRoadAction
from rl_env.actions.ClaimAction import ClaimAction

invalid_action_penalty = -10


def create_action(agent, action_type, position: MapPosition):
    if action_type == "claim":
        return ClaimAction(agent, position)
    elif action_type == "build_city":
        return BuildCityAction(agent, position)
    elif action_type == "build_road":
        return BuildRoadAction(agent, position)
    elif action_type == "build_bridge":
        return BuildBridgeAction(agent, position)
    elif action_type == "build_farm":
        return BuildFarmAction(agent, position)
    # elif action_type == "move":
    #     return MoveAction(agent, position)
    else:
        # Handle unknown action type
        return None


class ActionManager:
    """
    Manages the application of movement actions within the environment,
    detecting conflicts when multiple agents attempt to move to the same tile
    and randomly resolving those conflicts.
    """

    def __init__(self, env):
        self.env = env

        self.actions_definition = self.env.env_settings.get("actions")

        # Define a structured array with the fields 'action' and 'agent_id'.
        self.conflict_map = {}

    def apply_actions(self, actions: Any) -> Tuple[List[float], List[bool]]:
        """
        Processes the movement actions of all agents, resolves conflicts,
        and returns the outcomes for each agent.

        Args:
            actions (List[Dict[str, Any]]): List of action dictionaries from each agent.
            agents (List[Agent]): List of agent instances.

        Returns:
            Dict[int, Dict[str, Any]]: A dictionary mapping agent IDs to their action outcomes.
        """

        agents = self.env.agents
        rewards = np.zeros(
            len(agents), dtype=float
        )  # TODO: init with invalid action penalty
        dones = np.zeros(len(agents), dtype=bool)

        for agent, agent_actions in zip(agents, actions):
            proposed_turn_actions = []
            for action in agent_actions:
                if action is None:
                    continue

                action_type = self.env.action_mapping.get(action[0])
                if action_type is None:
                    # Handle unknown action type
                    rewards[agent.id] += invalid_action_penalty
                    continue
                x = action[1]
                y = action[2]
                position = MapPosition(x, y)

                action = create_action(agent, action_type, position)

                if action.validate(self.env):
                    proposed_turn_actions.append(action)
                    position_key = action.position
                    self.conflict_map.setdefault(position_key, []).append(action)

        determined_actions = self.resolve_conflict()

        # Execute actions
        for action in determined_actions:
            agent_id = action.agent.id
            reward = action.execute(self.env)
            rewards[agent_id] = reward
            dones[agent_id] = False

        # Clear the conflict map for the next turn
        self.conflict_map = {}

        return rewards, dones

    def resolve_conflict(self):
        winner_actions = []
        for position, actions_at_position in self.conflict_map.items():
            if len(actions_at_position) == 1:
                winner_actions.append(actions_at_position[0])
                continue

            print(
                f"Conflict detected at position {position} among agents {[action.agent.id for action in actions_at_position]}."
            )

            # Implement your conflict resolution strategy here.
            # What when multiple actions of same agent on same position?
            # what how do the different actions interact with each other? of different agents

            # For fairness, we can randomly select a winner.
            winner = random.choice(actions_at_position)
            print(f"Agent {winner.agent.id} wins the conflict at position {position}.")
            winner_actions.append(winner)

        return winner_actions

        # # Invalidate other actions at this position
        # for action in actions_at_position:
        #     if action != winner:
        #         proposed_actions[action.agent.id].remove(action)
        #         print(
        #             f"Agent {action.agent.id}'s action at position {position} has been invalidated due to conflict."
        #         )

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
                self.env.map.check_position_on_map(pos)
                and pos not in claimed_copy
                and pos not in claimable_copy
            ):
                new_claimable.append(pos)

        agent.claimable_tiles.update(new_claimable)
