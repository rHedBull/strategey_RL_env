import random
from typing import Any, Dict, List, Tuple

import numpy as np

from agents.Sim_Agent import Agent
from map.map_settings import OWNER_DEFAULT_TILE

buildings = [[], ["improvement-1", 100, 5]]


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

        x = self.env.map.width
        y = self.env.map.height
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
                    position_key = tuple(new_position)
                    if position_key not in self.conflict_map:
                        self.conflict_map[position_key] = []
                    self.conflict_map[position_key].append(
                        {"agent_id": agent.id, "action": selected_action}
                    )

                else:
                    # Invalid move (out of bounds), action denied
                    proposed_actions[agent.id] = None

            elif claim_happens:
                if self.check_claim(agent, selected_action["claim"]):
                    proposed_actions[agent.id] = selected_action
                    claim_pos = selected_action["claim"]
                    position_key = tuple(claim_pos)
                    if position_key not in self.conflict_map:
                        self.conflict_map[position_key] = []
                    self.conflict_map[position_key].append(
                        {"agent_id": agent.id, "action": selected_action}
                    )
                else:
                    proposed_actions[agent.id] = None

            else:
                # No valid action
                # Invalid move (out of bounds), action denied
                proposed_actions[agent.id] = None
                rewards[agent.id] = -1

        # TODO testing if conflicts handled correctly?
        proposed_actions = self.resolve_conflict(proposed_actions)

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
        # clear conflict map
        self.conflict_map = {}

        return rewards, dones

    def resolve_conflict(self, proposed_actions) -> Dict[str, Any]:
        # iterate over conflict map and resolve conflicts
        for position, actions_at_position in self.conflict_map.items():
            if len(actions_at_position) > 1:
                print(f"Potential Conflict at position {position}")

                # Split actions into movements and claims for separate handling
                moves = [
                    action
                    for action in actions_at_position
                    if "move" in action["action"]
                ]
                claims = [
                    action
                    for action in actions_at_position
                    if "claim" in action["action"]
                ]

                # Resolve move conflicts
                if len(moves) > 1:
                    # First mover wins, so we keep the first action and invalidate the rest
                    first_mover = moves[0]
                    print(
                        f"Agent {first_mover['agent_id']} wins the move conflict at {position}."
                    )
                    for move in moves[1:]:
                        agent_id = move["agent_id"]
                        print(f"Invalidating move for agent {agent_id} at {position}.")
                        proposed_actions[agent_id] = None

                # Resolve claim conflicts
                if len(claims) > 1:
                    # Randomly select one agent to win the claim
                    winner = random.choice(claims)
                    print(
                        f"Agent {winner['agent_id']} wins the claim conflict at {position}."
                    )
                    for claim in claims:
                        agent_id = claim["agent_id"]
                        if claim != winner:
                            print(
                                f"Invalidating claim for agent {agent_id} at {position}."
                            )
                            proposed_actions[agent_id] = None

        return proposed_actions

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
        #print(f"Agent {agent.id}: Move successful to position {agent.position}.")
        reward = self.env_settings.get_setting("actions")["move"]["reward"]
        return reward

    # claim a tile

    def check_claim(self, agent: Agent, position: Tuple[int, int]) -> bool:
        # check if move generally possible, ignoring checks for moves of other agents at this stage

        base_claim_cost = self.env_settings.get_setting("actions")["claim"]["cost"]

        #  check if enough money to claim tile
        if agent.money < base_claim_cost:
            return False

        if not self.check_position_on_map(position):
            return False

        # check if agent already owns the tile
        if not self.agent_does_not_own_tile_already(agent, position):
            return False

        # check if tile is next to another claimed tile
        if not self.is_adjacent_to_claimed(agent, position):
            return False

        # all checks passed
        return True

    def agent_does_not_own_tile_already(
        self, agent: Agent, position: Tuple[int, int]
    ) -> bool:
        x, y = position
        if self.env.map.get_tile((x, y)).get_owner() == agent:
            return False
        return True

    def is_adjacent_to_claimed(self, agent: Agent, position: Tuple[int, int]) -> bool:
        x, y = position
        already_claimed = agent.get_claimed_tiles()
        # Define the four possible adjacent positions (up, down, left, right)
        adjacent_positions = [
            (x, y - 1),  # Up
            (x, y + 1),  # Down
            (x - 1, y),  # Left
            (x + 1, y),  # Right
        ]

        for adj in adjacent_positions:
            if self.check_position_on_map(adj) and adj in already_claimed:
                # we found an adjacent claimed tile
                return True

        # Optionally, consider diagonal adjacency by uncommenting the following lines:
        # diagonal_positions = [
        #     (x - 1, y - 1),
        #     (x + 1, y - 1),
        #     (x - 1, y + 1),
        #     (x + 1, y + 1)
        # ]
        # for adj in diagonal_positions:
        #     if self.check_position_on_map(adj) and adj in agent.claimed_tiles:
        #         print(f"Diagonally adjacent claimed tile found at {adj}.")
        #         return True

        return False

    def claim_tile(self, agent: Agent, pos: [int, int]) -> int:
        self.env.map.claim_tile(agent, pos)
        agent.claimed_tiles.add(pos)
        self.update_claimable_tiles(agent, pos)

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
                    self.check_position_on_map(pos) and
                    pos not in claimed_copy and
                    pos not in claimable_copy
            ):
                new_claimable.append(pos)

        agent.claimable_tiles.update(new_claimable)