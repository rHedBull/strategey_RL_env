from typing import Any, Dict, List, Tuple

import numpy as np

from agents.Sim_Agent import Agent
from map.map_settings import OWNER_DEFAULT_TILE

buildings = [[], ["improvement-1", 100, 5]]

# TODO : implement graphical building visualization


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

    def apply_actions(
        self, actions: Any, agents: List[Agent]
    ) -> Dict[int, Dict[str, Any]]:
        """
        Processes the movement actions of all agents, resolves conflicts,
        and returns the outcomes for each agent.

        Args:
            actions (List[Dict[str, Any]]): List of action dictionaries from each agent.
            agents (List[Agent]): List of agent instances.

        Returns:
            Dict[int, Dict[str, Any]]: A dictionary mapping agent IDs to their action outcomes.
        """

        proposed_actions = np.zeros(len(agents), dtype=object)
        rewards = np.zeros(len(agents), dtype=float)
        dones = np.zeros(len(agents), dtype=bool)

        for agent, selected_action in zip(agents, actions):
            move_direction = selected_action.get("move", None)

            if move_direction is not None:
                new_position = self._calculate_new_position(
                    agent.position, move_direction
                )
                if self._is_valid_position(new_position):  # TODO: also check for cost
                    proposed_actions[
                        agent.id
                    ] = selected_action  # simplify position passing here
                    rewards[agent.id] = 1  # TODO: adapt this
                else:
                    # Invalid move (out of bounds), action denied
                    proposed_actions[agent.id] = None
                    rewards[agent.id] = -1

            elif (
                selected_action["claim"]["x"] is not None
                and selected_action["claim"]["y"] is not None
            ):
                # TODO: implement claim checking
                proposed_actions[agent.id] = selected_action

            else:
                # No valid action
                # Invalid move (out of bounds), action denied
                proposed_actions[agent.id] = None
                rewards[agent.id] = -1

        # TODO add some conflict hanlding here or just increased tile purchase cost

        # TODO : make this prettier!!
        # apply the actions
        for determined_action, agent in zip(
            proposed_actions, agents
        ):  # Fix the way the criteria for the actions are tested and the action is later applied
            if determined_action:
                if determined_action.get("move", None) is not None:
                    agent.apply_action(determined_action)
                if (
                    determined_action["claim"]["x"] is not None
                    and determined_action["claim"]["y"] is not None
                ):
                    self.env.map.claim_tile(
                        agent,
                        determined_action["claim"]["x"],
                        determined_action["claim"]["y"],
                    )

                dones[agent.id] = False

        # TODO : check dones and rewards again after all actions are applied

        return rewards, dones

    def _calculate_new_position(
        self, current_position: Tuple[int, int], move_direction: int
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
        return (x, y)

    def _is_valid_position(self, position: Tuple[int, int]) -> bool:
        """
        Checks if the new position is within the environment bounds.

        Args:
            position (Tuple[int, int]): The position to check.

        Returns:
            bool: True if the position is valid, False otherwise.
        """
        x, y = position
        max_x = self.env.map.max_x_index
        max_y = self.env.map.max_y_index  # assuming a square map
        return 0 <= x < max_x and 0 <= y < max_y

    def claim_tile(self, agent, x, y):
        base_claim_cost = self.actions_definition.get("claim", None).get("cost", 0)

        if not self.check_claim_cost(
            agent, base_claim_cost, x, y
        ):  # TODO: remove checks here , this should be just to apply the action, if it is possible has already been checked
            return

        self.env.map.claim_tile(agent, x, y)
        agent.claimed_tiles.append(self.env.map.get_tile(x, y))

    def check_claim_cost(self, agent, base_claim_cost, x, y):
        # check if properties correctly defined
        # check if move generally possible, ignoring cheks for moves of other agents in this round
        if (
            x < 0
            or y < 0
            or x > self.env.map.max_x_index
            or y > self.env.map.max_y_index
            or None in [x, y]
        ):
            return {
                "success": False,
                "reason": "Invalid move (out of bounds)",
                "reward": self.env_settings.get("invalid_action_penalty", -1),
            }

        # check if the tile is already claimed by someone
        if self.env.map.squares[x][y].get_owner() != OWNER_DEFAULT_TILE:
            return {
                "success": False,
                "reason": "Invalid move conflict with other Agent",
                "reward": self.env_settings.get("invalid_action_penalty", -1),
            }

        # check if enough money to claim tile
        if agent.money < base_claim_cost:
            return {
                "success": False,
                "reason": "Not enough money to claim tile",
                "reward": self.env_settings.get("invalid_action_penalty", -1),
            }
        # all checks passed
        return {
            "success": True,
            "reason": "",
            "reward": 0,  # ??
        }

    def add_building(self, agent, action_index, action_properties):
        x = action_properties[0]
        y = action_properties[1]
        base_construction_cost = self.actions_definition[action_index]["cost"]

        building_id = action_properties[2]

        if not self.check_building_cost(
            agent, base_construction_cost, building_id, x, y
        ):
            return

        # self.env.map.add_building(building_id, x, y)

    def check_building_cost(self, agent, base_construction_cost, building_id, x, y):
        specific_building_cost = buildings[building_id][1]

        total_cost = base_construction_cost + specific_building_cost
        if agent.money < total_cost:
            return False

        # check if building is possible
        tile_for_planned_building = self.env.map.get_tile(x, y)

        # check if agent owns the tile to build on
        if tile_for_planned_building.get_owner() != agent:
            return False

        current_buildings_on_tile = tile_for_planned_building.get_buildings()

        # check if building already exists
        for building in current_buildings_on_tile:
            if building == building_id:
                return False

        # all checks passed
        return True

    def check_move_cost(self, agent, basic_move_cost):
        if agent.money < basic_move_cost:
            return False

        # all checks passed
        return True
