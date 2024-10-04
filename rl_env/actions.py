from typing import Any, Dict, List, Tuple

import numpy as np

from agents.Sim_Agent import Agent
from map.map_settings import OWNER_DEFAULT_TILE

buildings = [[], ["improvement-1", 100, 5]]

# TODO : implement graphical building visualization


def _calculate_new_position(
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

        x = self.env.map.max_x_index
        y = self.env.map.max_y_index
        # Define a structured array with the fields 'action' and 'agent_id'.
        self.conflict_map = np.zeros(
            (x, y), dtype=[("action", "O"), ("agent_id", "i4")]
        )

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

        proposed_actions = np.zeros(len(agents), dtype=object)
        rewards = np.zeros(len(agents), dtype=float)
        dones = np.zeros(len(agents), dtype=bool)

        for agent, selected_action in zip(agents, actions):
            move_direction = selected_action["move"].get("direction", None)
            claim_happens = selected_action["claim"] is not None

            if move_direction is not None:
                valid, new_position = self.check_move(agent, move_direction)
                if valid:
                    selected_action["move"]["new_position"] = new_position
                    proposed_actions[
                        agent.id
                    ] = selected_action  # simplify position passing here
                    # add to map conflict map
                    self.conflict_map[new_position[0], new_position[1]][
                        "agent_id"
                    ] = agent.id
                    self.conflict_map[new_position[0], new_position[1]][
                        "action"
                    ] = selected_action

                else:
                    # Invalid move (out of bounds), action denied
                    proposed_actions[agent.id] = None

            elif claim_happens:
                if self.check_claim(agent, selected_action["claim"]):
                    proposed_actions[agent.id] = selected_action
                    claim_pos = selected_action["claim"]
                    self.conflict_map[claim_pos[1], claim_pos[0]]["agent_id"] = agent.id
                    self.conflict_map[claim_pos[1], claim_pos[0]][
                        "action"
                    ] = selected_action
                else:
                    proposed_actions[agent.id] = None

            else:
                # No valid action
                # Invalid move (out of bounds), action denied
                proposed_actions[agent.id] = None
                rewards[agent.id] = -1

        # TODO add some conflict hanlding here

        # apply the actions
        for determined_action, agent in zip(proposed_actions, agents):
            if determined_action:
                move_direction = determined_action["move"].get("direction", None)
                claim_happens = determined_action["claim"] is not None

                reward = 0
                if move_direction:
                    reward = self.move_agent(
                        agent, determined_action["move"]["new_position"]
                    )
                if claim_happens:
                    reward = self.claim_tile(agent, determined_action["claim"])

                rewards[agent.id] = reward
                dones[agent.id] = False

        # TODO : check dones and rewards again after all actions are applied

        return rewards, dones

    # move
    def check_move(self, agent: Agent, direction: int) -> Tuple[bool, Tuple[int, int]]:
        basic_move_cost = self.env_settings.get_setting("actions")["move"]["cost"]
        if agent.money < basic_move_cost:
            return False, (-1, -1)

        new_position = _calculate_new_position(agent.position, direction)
        if not self.check_position_on_map(new_position):
            return False, (-1, -1)

        # all checks passed
        return True, new_position

    def move_agent(self, agent: Agent, new_position: Tuple[int, int]) -> int:
        # Update position
        agent.position = new_position
        agent.money -= self.env_settings.get_setting("actions")["move"]["cost"]
        print(f"Agent {agent.id}: Move successful to position {agent.position}.")
        reward = self.env_settings.get_setting("actions")["move"]["reward"]
        return reward

    # claim a tile

    def check_claim(self, agent: Agent, position: Tuple[int, int]) -> bool:
        # check if move generally possible, ignoring checks for moves of other agents at this stage

        base_claim_cost = self.env_settings.get_setting("actions")["claim"]["cost"]

        if not self.check_position_on_map(position):
            return False

        # # check if the tile is already claimed by someone
        # if self.env.map.squares[x][y].get_owner() != OWNER_DEFAULT_TILE:
        #     return {
        #         "success": False,
        #         "reason": "Invalid move conflict with other Agent",
        #         "reward": self.env_settings.get("invalid_action_penalty", -1),
        #     }
        #
        # # check if enough money to claim tile
        if agent.money < base_claim_cost:
            return False

        # all checks passed
        return True

    def claim_tile(self, agent: Agent, pos: [int, int]) -> int:
        self.env.map.claim_tile(agent, pos)
        agent.claimed_tiles.append(self.env.map.get_tile(pos))
        agent.money -= self.env_settings.get_setting("actions")["claim"]["cost"]
        reward = self.env_settings.get_setting("actions")["claim"]["reward"]
        return reward

    # build a building
    def check_building(self, agent, base_construction_cost, building_id, x, y):
        specific_building_cost = buildings[building_id][1]

        total_cost = base_construction_cost + specific_building_cost
        if agent.money < total_cost:
            return False

        if not self.check_position_on_map((x, y)):
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

    def add_building(self, agent: Agent) -> int:
        reward = self.env_settings.get_setting("actions")["build"]["reward"]
        return reward

        # self.env.map.add_building(building_id, x, y)

    def check_position_on_map(self, position: Tuple[int, int]) -> bool:
        """

        :param self:
        :param position:
        :return:
        """
        x, y = position
        max_x = self.env.map.max_x_index
        max_y = self.env.map.max_y_index  # assuming a square map
        if 0 <= x < max_x and 0 <= y < max_y:
            return True
        return False
