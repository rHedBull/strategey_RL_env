import uuid

import numpy as np

from strategyRLEnv.Agent import Agent
from strategyRLEnv.map.map_settings import (OWNER_DEFAULT_TILE, BuildingType,
                                            max_agent_id)
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.map.MapSquare import Map_Square


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

    def __init__(self, topology_array):
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

        # ownership map
        # reorder dimensions of numpy array to [feature, x, y]
        topology_array = np.moveaxis(topology_array, 2, 0)
        self.landtype_map = topology_array[0]
        self.resources_map = topology_array[1]
        self.ownership_map = None
        self.building_map = None
        self.unit_strength_map = None

    def reset(self):
        """
        Reset the map to its initial state. Keeps topology, but resets ownership, buildings, visibility.
        """
        for row in self.squares:
            for square in row:
                square.reset()

        self.visibility_map = np.zeros((self.width, self.height), dtype=np.int64)
        self.ownership_map = np.full(
            (self.width, self.height), OWNER_DEFAULT_TILE, dtype=np.int64
        )
        self.building_map = np.zeros((self.width, self.height), dtype=np.int64)
        self.unit_strength_map = np.zeros((self.width, self.height), dtype=np.int64)

    def trigger_surrounding_tile_update(self, position, radius=1):
        surrounding_tiles = self.get_surrounding_tiles(position, radius)
        for tile in surrounding_tiles:
            tile.update(self.env)

    def get_random_position_on_map(self):
        x = np.random.randint(0, self.width)
        y = np.random.randint(0, self.height)
        return MapPosition(x, y)

    def get_observation(self):
        """
        define here what info is visible to all agents
        Assuming full observability of map for now
        """

        features = self.env.features_per_tile
        map_features = np.zeros(
            (len(features), self.width, self.height), dtype=np.float32
        )

        map_features[0] = self.landtype_map
        map_features[1] = self.resources_map
        map_features[2] = self.ownership_map
        map_features[3] = self.building_map
        map_features[4] = self.unit_strength_map

        return map_features, self.visibility_map

    def claim_tile(self, agent: Agent, position: MapPosition) -> None:
        """
        Claim a tile at position (x,y) for an agent
        :param position:
        :param agent:
        :return:
        """
        self.squares[position.x][position.y].set_owner(agent)
        self.ownership_map[(position.x, position.y)] = agent.id

    def unclaim_tile(self, position: MapPosition) -> None:
        """
        Unclaim a tile at position (x,y)
        :param position:
        :return:
        """
        self.squares[position.x][position.y].set_owner(None, default=True)
        self.ownership_map[(position.x, position.y)] = OWNER_DEFAULT_TILE

    def add_building(self, building_object, position: MapPosition) -> None:
        self.get_tile(position).add_building(building_object)
        self.building_map[position.x][
            position.y
        ] = building_object.get_building_type_id()

    def add_unit(self, unit, position: MapPosition) -> None:
        self.get_tile(position).unit = unit
        self.unit_strength_map[position.x][position.y] = unit.strength

    def remove_unit(self, position: MapPosition) -> None:
        tile = self.get_tile(position)
        tile.unit = None
        self.unit_strength_map[position.x][position.y] = 0

    def remove_building(
        self,
        position: MapPosition,
        building_type: BuildingType = None,
    ) -> None:
        tile = self.get_tile(position)
        tile.remove_building(building_type)
        tile.update(self.env)
        self.trigger_surrounding_tile_update(position, 1)
        self.building_map[position.x][position.y] = 0

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

    def tile_is_next_to_own_tile(
        self,
        position: MapPosition,
        agent_id: int,
        radius: int = 1,
        diagonal: bool = True,
    ):
        surrounding_tiles = self.get_surrounding_tiles(position, radius, diagonal)
        for tile in surrounding_tiles:
            if tile.get_owner() == agent_id:
                return True, tile
        return False, None

    def tile_is_next_to_building_type(
        self,
        position: MapPosition,
        building_type,
        radius: int = 1,
        diagonal: bool = True,
    ):
        # check if any of the neighbouring tiles in radius have a building of the given type
        surroundings = self.get_surrounding_tiles(position, radius, diagonal)

        for tile in surroundings:
            if tile.has_building(building_type):
                return True, tile
        return False, None

    def tile_is_next_to_any_building(
        self, position: MapPosition, radius: int = 1, diagonal: bool = True
    ):
        # check if any of the neighbouring tiles in radius have a building of the given type
        surroundings = self.get_surrounding_tiles(position, radius, diagonal)
        for tile in surroundings:
            if tile.has_any_building():
                return True, tile
        return False, None

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

    def get_surrounding_tiles(
        self, position: MapPosition, radius: int, diagonal: bool = True
    ):
        if radius < 1:
            return []

        x = position.x
        y = position.y
        surrounding_tiles = []

        if not diagonal:
            for i in range(-radius, radius + 1):
                if i != 0:
                    tmp_pos = MapPosition(x + i, y)
                    if self.check_position_on_map(tmp_pos):
                        surrounding_tiles.append(self.get_tile(tmp_pos))

            for j in range(-radius, radius + 1):
                if j != 0:
                    tmp_pos = MapPosition(x, y + j)
                    if self.check_position_on_map(tmp_pos):
                        surrounding_tiles.append(self.get_tile(tmp_pos))
        else:
            for i in range(-radius, radius + 1):
                for j in range(-radius, radius + 1):
                    # Skip the center tile
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
