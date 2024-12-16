import random
from typing import Any, List

import numpy as np

from strategyRLEnv.actions.BuildCityAction import BuildCityAction
from strategyRLEnv.actions.BuildFarmAction import BuildFarmAction
from strategyRLEnv.actions.BuildRoadAction import (BuildBridgeAction,
                                                   BuildRoadAction)
from strategyRLEnv.actions.ClaimAction import ClaimAction
from strategyRLEnv.Agent import Agent
from strategyRLEnv.map.MapPosition import MapPosition


def create_action(agent: Agent, action_type, position: MapPosition):
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
        self.invalid_action_penalty = self.actions_definition.get(
            "invalid_action_penalty"
        )

        # Define a structured array with the fields 'action' and 'agent_id'.
        self.conflict_map = {}

    def apply_actions(self, actions: Any):
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
        rewards = np.full(len(agents), self.invalid_action_penalty, dtype=float)
        dones = np.zeros(len(agents), dtype=bool)

        for agent, agent_actions in zip(agents, actions):
            proposed_turn_actions = []
            for action in agent_actions:
                if action is None:
                    continue

                action_type = self.env.action_mapping.get(action[0])
                if action_type is None:
                    # Handle unknown action type
                    raise ValueError(f"Unknown action type: {action[0]}")

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

            # Implement your conflict resolution strategy here.
            # What when multiple actions of same agent on same position?
            # what how do the different actions interact with each other? of different agents

            # For fairness, we can randomly select a winner.
            winner = random.choice(actions_at_position)
            winner_actions.append(winner)

        return winner_actions
