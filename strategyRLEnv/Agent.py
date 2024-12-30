from enum import Enum
from typing import Tuple

import numpy as np
import pygame

from strategyRLEnv.actions.BuildCityAction import BuildCityAction
from strategyRLEnv.map.map_settings import AGENT_COLORS, PLAYER_COLOR
from strategyRLEnv.map.MapPosition import MapPosition


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


class AgentState(Enum):
    ACTIVE = 0
    DONE = 1


class Agent:
    """
    Represents an agent in the environment.

    Attributes:
        id (int): Unique identifier for the agent.
        position MapPosition(): Start position of the agent.
        state (AgentState): The state of the agent.
    """

    def __init__(self, agent_id: int, env):
        self.capital = None
        self.id = agent_id
        self.env = env

        self.position = MapPosition(-1, -1)
        self.state = None

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

        self.money = None
        self.last_money_pl = None

        self.all_visible = False
        self.visibility_range = 1

        self.reset()

    def reset(self):
        """
        Resets the agent to the initial state as defined in the environment settings.
        """

        self.position = self.env.map.get_random_position_on_map()

        self._claimed_tiles.clear()
        self._claimed_tiles.add(self.position)  # initial spawn is a claimed tile

        # create capital
        action = BuildCityAction(self, self.position)
        action.perform_build(self.env)

        self.state = AgentState.ACTIVE

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

    def update(self):
        round_money = 0
        for _, tile in enumerate(self._claimed_tiles):
            round_money += self.env.map.get_tile(tile).get_round_value()

        self.money += round_money
        self.last_money_pl = round_money

        if self.money < 0 or len(self._claimed_tiles) == 0:
            self.state = AgentState.DONE

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

    def get_observation(self):
        agent_observation = np.zeros((len(self.env.agent_features)), dtype=np.float32)

        features = self.env.agent_features

        i = 0
        for feature in features:
            name = feature["name"]

            if name == "agent_money":
                agent_observation[i] = self.money
            elif name == "agent_map_ownership":
                agent_observation[i] = len(self._claimed_tiles) / (
                    self.env.map.width * self.env.map.height
                )
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
