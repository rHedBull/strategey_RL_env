from enum import Enum
from typing import Tuple

import numpy as np

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
        self.cities = []

        self.money = None
        self.last_money_pl = None

        self.all_visible = False
        self.visibility_range = 1

        self.units = []

    def reset(self):
        """
        Resets the agent to the initial state as defined in the environment settings.
        """
        self.cities = []

        while True:
            position = self.env.map.get_random_position_on_map()
            tile = self.env.map.get_tile(position)
            if tile.building is None:
                break
        self.position = position

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
        self.units = []

    def update(self):
        if self.state == AgentState.DONE:
            return

        init_money = self.money
        round_money = 0
        for _, tile in enumerate(self._claimed_tiles):
            round_money += self.env.map.get_tile(tile).get_tile_income()

        for unit in self.units:
            unit.step(self.env)

        self.add_money(round_money)
        self.last_money_pl = self.money - init_money

    def kill(self):
        self.state = AgentState.DONE
        # remove all units
        # print("Agent ", self.id, " is dead")
        unit_copy = self.units.copy()
        for unit in unit_copy:
            unit.kill(self.env)

        for pos in self._claimed_tiles:
            self.env.map.get_tile(pos).reset(False)
            self.env.map.remove_building(pos)
            self.env.map.unclaim_tile(pos)
        self._claimed_tiles.clear()

        self.env.done_agents.append(self.id)

    def add_money(self, amount):
        self.money += amount

    def reduce_money(self, amount):
        self.money -= amount
        if self.money < 0:
            self.kill()

    def draw(self, square_size, zoom_level, pan_x, pan_y):
        # draw the units
        for unit in self.units:
            unit.draw(self.env.screen, square_size, self.color)

    def get_observation(self):
        agent_observation = np.zeros((len(self.env.agent_features)), dtype=np.float32)

        features = self.env.agent_features

        i = 0
        for feature in features:
            name = feature["name"]

            if name == "agent_money":
                agent_observation[i] = self.money
            elif name == "agent_map_ownership":
                agent_observation[i] = round(
                    len(self._claimed_tiles)
                    / (self.env.map.width * self.env.map.height),
                    4,
                )
            elif name == "last_money_pl":
                agent_observation[i] = self.last_money_pl
            elif name == "total_unit_strength":
                agent_observation[i] = sum([unit.strength for unit in self.units])
            i += 1

        return agent_observation

    # visibility stuff #
    def update_local_visibility(self, position: MapPosition):
        """
        Update the local visibility of the agent based on the map visibility.

        :param map:
        :param position: The position of the agent.
        """

        surrounding_tiles = self.env.map.get_surrounding_tiles(
            position, self.visibility_range
        )
        discovered_tiles = 0
        for tile in surrounding_tiles:
            if not self.env.map.is_visible(tile.position, self.id):
                self.env.map.set_visible(tile.position, self.id)
                discovered_tiles += 1

        return discovered_tiles

    def add_unit(self, unit):
        if unit.owner.id == self.id:
            self.units.append(unit)

    def remove_unit(self, unit):
        if unit in self.units:
            self.units.remove(unit)

    # claiming stuff
    def add_claimed_tile(self, position: MapPosition):
        self._claimed_tiles.add(position)

    def get_claimed_tiles(self):
        return self._claimed_tiles

    def remove_claimed_tile(self, position: MapPosition):
        if position in self._claimed_tiles:
            self._claimed_tiles.remove(position)

        if len(self._claimed_tiles) == 0:
            self.kill()

    def add_city(self, city):
        self.cities.append(city)

    def remove_city(self, city):
        if city in self.cities:
            self.cities.remove(city)

        if len(self.cities) == 0:
            self.kill()
