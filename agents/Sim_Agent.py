from typing import Tuple

import numpy as np
import pygame

from map.map_settings import AGENT_COLORS, PLAYER_COLOR
from map.MapPosition import MapPosition


def get_visible_mask(agent_id: int, map_v):
    bitmask = 1 << agent_id
    visible = (map_v.visibility_map & bitmask) > 0
    return visible


def calculate_new_position(
    current_position: MapPosition, move_direction: int
) -> MapPosition:
    """
    Calculates the new position based on the current position and move direction.

    Args:
        current_position (Tuple[int, int]): The agent's current position.
        move_direction (int): Direction to move (0: No move, 1: Up, 2: Down, 3: Left, 4: Right).

    Returns:
        Tuple[int, int]: The new position after the move.
    """
    x = current_position.x
    y = current_position.y
    if move_direction == 1:  # Up
        y -= 1
    elif move_direction == 2:  # Down
        y += 1
    elif move_direction == 3:  # Left
        x -= 1
    elif move_direction == 4:  # Right
        x += 1
    # No move if move_direction is 0 or unrecognized
    return MapPosition(x, y)


class Agent:
    """
    Represents an agent in the environment.

    Attributes:
        id (int): Unique identifier for the agent.
        position (Tuple[int, int]): Current position of the agent.
        reward (float): Accumulated reward for the agent.
        done (bool): Whether the agent has completed its task.
    """

    def __init__(self, agent_id: int, env):

        self.id = agent_id
        self.env = env

        self.position = MapPosition(-1, -1)

        self.state = "active"

        # exclude player color id 0
        c = self.id
        if self.id == 0:
            self.color = PLAYER_COLOR
        else:
            if self.id % len(AGENT_COLORS) == 0:
                c = 1
            self.color = AGENT_COLORS[c % len(AGENT_COLORS)]

        # resources
        self._claimed_tiles = set()
        # we only need the positions of the tiles
        # we keep track of the buildings via the tiles we onw, because buildings can only be placed on claimed tiles
        # self.claimable_tiles = set()

        self.money = None
        self.last_money_pl = None

        self.all_visible = False
        self.visibility_range = 1

        self.reward = 0.0
        self.done = False

    def reset(self):
        """
        Resets the agent to the initial state.
        Args:
            env_settings (Dict[str, Any]): Environment settings.
        """
        max_x = self.env.env_settings.get("map_width")
        max_y = self.env.env_settings.get("map_height")

        self.position.x = np.random.randint(0, max_x)
        self.position.y = np.random.randint(0, max_y)

        self._claimed_tiles.clear()
        self._claimed_tiles.add(self.position)  # initial spawn is a claimed tile
        self.update_local_visibility(self.position)

        self.state = "active"

        initial_money = self.env.env_settings.get("agent_initial_budget")
        distribution_mode = self.env.env_settings.get(
            "agent_initial_budget_distribution"
        )
        if distribution_mode == "equal":
            self.money = initial_money
        elif distribution_mode == "gauss":
            # gauss distributed around initial
            self.money = self.env.np_random.gauss(initial_money, 100)
        else:
            # randomly distributed money
            self.money = self.env.np_random.integers(0, 1000)

        self.all_visible = False
        self.visibility_range = 3

        self.reward = 0.0
        self.done = False

    def update(self):
        # Update the agent's state

        # TODO: reenable this
        # for _, tile in enumerate(self.claimed_tiles):
        # self.money += tile.get_round_value()

        if self.money <= 0:  # TODO adapt different state transitions
            self.state = "Done"

    def draw(self, square_size, zoom_level, pan_x, pan_y):
        radius = square_size / 2
        # get a color modulo the number of colors

        pygame.draw.circle(
            self.env.screen,
            self.color,
            (
                (self.position.x * square_size) + radius,
                (self.position.y * square_size) + radius,
            ),
            radius,
        )

    # def get_possible_actions(self):
    #     if self.state == "Done":
    #         possible_actions = []
    #     else:
    #         possible_actions = self.claimable_tiles  # for now only claimable intersting
    #
    #     return possible_actions

    def get_observation(self):
        agent_observation = np.zeros(
            (len(self.env.agent_features)),
            dtype=np.float32
        )

        features = self.env.agent_features

        i = 0
        for feature in features:
            name = feature["name"]

            if name == "agent_money":
                agent_observation[i] = self.money
            elif name == "agent_map_ownership":
                agent_observation[i] = len(self._claimed_tiles)/ (self.env.map.width * self.env.map.height)
            elif name == "last_money_pl":
                agent_observation[i] = self.last_money_pl
            i += 1

        return agent_observation

    # visibility stuff #
    def update_local_visibility(self, position: MapPosition):
        """
        Update the local visibility of the agent based on the map visibility.

        :param map:
        :param position: The position of the agent.
        """
        x = position.x
        y = position.y

        tmp_pos = MapPosition(x, y)
        for i in range(-self.visibility_range, self.visibility_range + 1):
            for j in range(-self.visibility_range, self.visibility_range + 1):
                tmp_pos.x = x + i
                tmp_pos.y = y + j
                if self.env.map.check_position_on_map(tmp_pos):
                    self.env.map.set_visible(tmp_pos, self.id)

    # claiming stuff
    def add_claimed_tile(self, position: MapPosition):
        self._claimed_tiles.add(position)

    def get_claimed_tiles(self):
        return self._claimed_tiles

    # def update_claimable_tiles(self, new_claimed_tile: MapPosition):
    #     """
    #     Updates the agent's set of claimable tiles by adding new adjacent tiles
    #     to the newly claimed tile. Limits the number of additions to 3 (or 5 if diagonals are allowed).
    #
    #     :param agent: The agent who claimed the new tile.
    #     :param new_claimed_tile: The position of the newly claimed tile.
    #     """
    #     x = new_claimed_tile.x
    #     y = new_claimed_tile.y
    #
    #     new_possible = [
    #         (x, y - 1),  # Up
    #         (x, y + 1),  # Down
    #         (x - 1, y),  # Left
    #         (x + 1, y),  # Right
    #     ]
    #
    #     # if allow_diagonal:
    #     # diagonal_positions = [
    #     #         #     (x - 1, y - 1),
    #     #         #     (x + 1, y - 1),
    #     #         #     (x - 1, y + 1),
    #     #         #     (x + 1, y + 1)
    #     #         # ]
    #     claimed_copy = self._claimed_tiles.copy()
    #     #claimable_copy = self.claimable_tiles.copy()
    #
    #     new_claimable = []
    #     for pos in new_possible:
    #         # Check if the position is valid and not already listed as claimed or claimable
    #         if (
    #             self.env.map.check_position_on_map(pos)
    #             and pos not in claimed_copy
    #             and pos not in claimable_copy
    #         ):
    #             new_claimable.append(pos)
    #
    #     self.claimable_tiles.update(new_claimable)
    #     self.update_local_visibility(new_claimed_tile)


