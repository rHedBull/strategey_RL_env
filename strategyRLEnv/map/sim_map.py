import uuid

import numpy as np

from strategyRLEnv.map.map_settings import max_agent_id
from strategyRLEnv.map.map_square import Map_Square
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.Agent import Agent


def check_valid_agent_id(agent_id: int) -> bool:
    return 0 <= agent_id < max_agent_id


class Map:
    """
    Represents the map of the environment.
    x values in width horizontal, y v
    alues in height vertical
    Position(x,y) with (0,0) in the top left corner
    Attributes:
        env: The environment object.
        tiles: The total number of tiles on the map.
        tile_size: The size of each tile in pixels.
        width: The width of the map.
        height: The height of the map.
        squares: A 2D list of Map_Square objects representing the map.
        continuous_map: Whether the map is continuous or not.
        visibility_map: A 2D numpy array to store the visibility of each tile.
    """

    def __init__(self):
        self.id = uuid.uuid4()
        self.env = None

        self.tiles = None
        self.tile_size = None
        self.width = None
        self.height = None

        self.squares = []
        self.continuous_map = None

        # 2D numpy array to store the visibility of each tile
        self.visibility_map = None
        self.tile_size = 1

    def reset(self):
        """
        Reset the map to its initial state. Keeps topology, but resets ownership, buildings, visibility.
        """
        for row in self.squares:
            for square in row:
                square.reset()
        self.visibility_map = np.zeros((self.width, self.height), dtype=np.int64)

    def get_random_position_on_map(self):
        x = np.random.randint(0, self.width)
        y = np.random.randint(0, self.height)
        return MapPosition(x, y)

    def get_observation(self):
        """
        define here what info is visible to all agents
        Assuming full observability of map for now
        """
        map_info = np.zeros(
            (self.width, self.height, len(self.env.features_per_tile)), dtype=np.float32
        )

        features = self.env.features_per_tile

        for row in self.squares:
            for square in row:
                square_array = np.zeros(len(features), dtype=np.float32)

                i = 0
                for feature in features:
                    name = feature["name"]

                    if name == "tile_ownership":
                        square_array[i] = square.get_owner_id()
                    elif name == "tile_ownership":
                        square_array[i] = square.get_land_type()
                    elif name == "land_money_value":
                        square_array[i] = square.get_land_money_value()
                    elif name == "resources":
                        square_array[i] = square.get_land_type()

                    map_info[square.position.x][square.position.y] = square_array
                    i += 1

        return map_info

    def claim_tile(self, agent: Agent, position: MapPosition) -> None:
        """
        Claim a tile at position (x,y) for an agent
        :param position:
        :param agent:
        :return:
        """
        self.squares[position.x][position.y].claim(agent)

    def add_building(self, building_object, position: MapPosition) -> None:
        self.get_tile(position).add_building(building_object)

    def draw(self, screen, zoom_level, pan_x, pan_y):
        """
        Draw the map on the screen
        :param screen:
        :param zoom_level:
        :param pan_x:
        :param pan_y:
        :return:
        """
        for row in self.squares:
            for square in row:
                new_x = (square.position.x * zoom_level) + pan_x
                new_y = (square.position.x * zoom_level) + pan_y
                new_size = self.tile_size * zoom_level
                square.draw(screen, self.tile_size, new_x, new_y, new_size)

    def get_tile(self, position: MapPosition) -> Map_Square | None:
        """
        Get the tile at position x, y
        :param position:
        :return: Map_Square object or None if position is not on the map
        """
        if self.check_position_on_map(position):
            return self.squares[position.x][position.y]
        return None

    def tile_is_next_to_building(self, position: MapPosition) -> bool:
        # check if any of the neighbouring tiles has a building
        # TODO: switch to just up, down, left, right
        x = position.x
        y = position.y
        for i in range(-1, 2):
            for j in range(-1, 2):
                tmp_pos = MapPosition(x + i, y + j)
                tile = self.get_tile(tmp_pos)
                if tile and tile.has_any_building():
                    return True
        return False

    def check_position_on_map(self, position: MapPosition) -> bool:
        """
        :param position:
        :return:
        """
        x = position.x
        y = position.y

        if 0 <= x < self.width and 0 <= y < self.height:
            return True
        return False

    def get_surrounding_tiles(self, position: MapPosition):
        x = position.x
        y = position.y
        surrounding_tiles = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                tmp_pos = MapPosition(x + i, y + j)
                if self.check_position_on_map(tmp_pos):
                    surrounding_tiles.append(self.get_tile(tmp_pos))
        return surrounding_tiles

    # visibility stuff #
    def set_visible(self, position: MapPosition, agent_id: int):
        if check_valid_agent_id(agent_id):
            self.visibility_map[(position.x, position.y)] |= 1 << agent_id

    def clear_visible(self, position: MapPosition, agent_id: int):
        if check_valid_agent_id(agent_id):
            self.visibility_map[(position.x, position.y)] &= ~(1 << agent_id)

    def is_visible(self, position: MapPosition, agent_id: int) -> bool:
        """
        Check if a tile is visible to an agent.
        :param position: The position of the tile.
        :param agent_id: The ID of the agent.
        :return: True if the tile is visible to the agent, False otherwise.
        """
        if not check_valid_agent_id(agent_id):
            return False

        bit = 1 << agent_id
        numb = self.visibility_map[(position.x, position.y)]
        result = numb & (bit)
        # should return bool
        if result > 0:
            return True
        else:
            return False

    # TODO: maybe enable bulk operations here later, to make exploration in general more efficient
