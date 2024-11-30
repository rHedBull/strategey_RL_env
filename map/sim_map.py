import math
import pickle

import numpy as np

from map.map_agent import Map_Agent
from map.map_settings import LandType, max_agent_id
from map.map_square import Map_Square
from map.MapPosition import MapPosition
from test_env.Agent import Agent


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
        water_percentage: The percentage of water tiles on the map.
        mountain_percentage: The percentage of mountain tiles on the map.
        dessert_percentage: The percentage of dessert tiles on the map.
        rivers: The number of rivers on the map.
        resource_density: The density of resources on the map.
        biomes_definition: The definition of biomes on the map.
        land_resource_definition: The definition of land resources on the map.
        sea_resource_definition: The definition of sea resources on the map.
        height_values: The height values of the map.
        visibility_map: A 2D numpy array to store the visibility of each tile.
    """

    def __init__(self, env):
        self.env = env

        self.tiles = None
        self.tile_size = None
        self.width = None
        self.height = None

        self.squares = []
        self.continuous_map = None

        # land type percentages
        self.height_values = None
        self.sea_resource_definition = None
        self.land_resource_definition = None
        self.water_percentage = None
        self.mountain_percentage = None
        self.dessert_percentage = None
        self.rivers = None
        self.resource_density = None
        self.biomes_definition = None
        self.resource_definition = None

        # 2D numpy array to store the visibility of each tile
        self.visibility_map = None

        self.create_map(self.env.env_settings)

    def load_settings(
        self,
        settings,
    ):
        self.width = settings.get("map_width")
        self.height = settings.get("map_height")

        self.tiles = self.height * self.width

        if self.env.render_mode == "human":
            if self.height > self.width:
                self.tile_size = int(self.env.screen.get_height() / self.height)
            else:
                self.tile_size = int(self.env.screen.get_width() / self.width)
            self.tile_size = max(1, self.tile_size)
        else:
            self.tile_size = -1  # not needed if no rendering

        self.continuous_map = settings.get("continuous_map")

        self.water_percentage = settings.get("water_budget_per_agent")
        self.mountain_percentage = settings.get("mountain_budget_per_agent")
        self.dessert_percentage = settings.get("dessert_budget_per_agent")
        self.rivers = settings.get("numb_rivers")
        self.resource_density = settings.get("resource_density")
        self.biomes_definition = settings.get("biomes")
        self.land_resource_definition = settings.get("land_resources")
        self.sea_resource_definition = settings.get("land_resources")
        self.height_values = settings.get("height_values")

    def create_map(self, settings):
        self.load_settings(settings)

        # Initialize the 2D list with the appropriate dimensions
        self.squares = [[None for _ in range(self.height)] for _ in range(self.width)]

        # Create map squares
        for x_index in range(self.width):
            for y_index in range(self.height):
                self.squares[x_index][y_index] = Map_Square(
                    (y_index * self.width + x_index), MapPosition(x_index, y_index)
                )

        self.reset()

    def distribute_resources(self, square):
        # resource distribution totally random so far
        i = self.env.np_random.integers(0, 10) / 10

        if i < self.resource_density:
            if square.get_land_type() != LandType.OCEAN:
                resource = self.env.np_random.integers(0, 6)
                square.add_resource(resource)
            else:
                resource = self.env.np_random.integers(0, 1)
                square.add_resource(resource)

    def reset(self):
        for row in self.squares:
            for square in row:
                square.reset()

        # mountain agents
        self.let_map_agent_run(self.mountain_percentage, self.tiles, LandType.MOUNTAIN)

        # dessert agents
        self.let_map_agent_run(self.dessert_percentage, self.tiles, LandType.DESERT)

        # water agents
        self.let_map_agent_run(self.water_percentage, self.tiles, LandType.OCEAN)

        # river agents
        self.river_agents(self.tiles, self.rivers)

        # post processing
        for row in self.squares:
            for square in row:
                self.distribute_resources(square)

                # check if water arround
                if square.get_land_type() != LandType.OCEAN:
                    if (
                        (
                            square.position.x > 0
                            and self.squares[square.position.x - 1][
                                square.position.y
                            ].get_land_type()
                            == LandType.OCEAN
                        )  # left neighbor
                        or (
                            square.position.x < self.width - 1
                            and self.squares[square.position.x + 1][
                                square.position.y
                            ].get_land_type()
                            == LandType.OCEAN
                        )  # right neighbor
                        or (
                            square.position.y > 0
                            and self.squares[square.position.x][
                                square.position.y - 1
                            ].get_land_type()
                            == LandType.OCEAN
                        )  # top neighbor
                        or (
                            square.position.y < self.height - 1
                            and self.squares[square.position.x][
                                square.position.y + 1
                            ].get_land_type()
                            == LandType.OCEAN
                        )
                        # bottom neighbor
                    ):
                        square.set_land_type(LandType.MARSH)

        # set the visibility map to all zeros
        self.visibility_map = np.zeros((self.width, self.height), dtype=np.int64)

    def get_observation(self):
        """
        define here what infor is visible to all agents
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

    def river_agents(self, tiles, rivers):
        numb_agents = rivers
        tile_budget_per_agent = 0.1 * tiles
        agents = [
            Map_Agent(
                self.env.np_random.integers(0, int(math.sqrt(tiles) - 1)),
                self.env.np_random.integers(0, int(math.sqrt(tiles) - 1)),
                tile_budget_per_agent,
            )
            for i in range(numb_agents)
        ]
        for agent in agents:
            agent.river_walk(self, tiles, LandType.RIVER)

    def let_map_agent_run(self, land_type_percentage, tiles, LAND_TYPE_VALUE):
        if land_type_percentage < 0:
            return

        total_tile_budget = tiles * land_type_percentage
        numb_agents = int(min(10, (tiles * 0.01) + 1))
        tile_budget_per_agent = int((total_tile_budget / numb_agents))

        if (numb_agents * tile_budget_per_agent) > 0:
            agents = [
                Map_Agent(
                    self.env.np_random.integers(0, int(math.sqrt(tiles) - 1)),
                    self.env.np_random.integers(0, int(math.sqrt(tiles) - 1)),
                    tile_budget_per_agent,
                )
                for i in range(numb_agents)
            ]

            running = True
            while running:
                for agent in agents:
                    agent.random_walk(self, tiles, LAND_TYPE_VALUE)
                    if agent.tile_budget == 0:
                        agents.remove(agent)
                    if len(agents) == 0:
                        running = False

    def serialize_topography_resources(self):
        """Serialize the topography, resources, and key map attributes."""
        map_data = {
            "width": self.width,
            "height": self.height,
            # "max_x_index": self.max_x_index,
            # "max_y_index": self.max_y_index,
            "water_percentage": self.water_percentage,
            "mountain_percentage": self.mountain_percentage,
            "dessert_percentage": self.dessert_percentage,
            "resource_density": self.resource_density,
            "squares": [
                [
                    {
                        "id": square.tile_id,
                        "x": square.x,
                        "y": square.y,
                        "land_type": square.get_land_type(),
                        "resources": square.get_resources(),  # Assuming this returns a list of resources
                    }
                    for square in row
                ]
                for row in self.squares
            ],
        }
        return map_data

    def save_topography_resources(self, file_path):
        """Save the serialized topography and resources using pickle."""
        map_data = self.serialize_topography_resources()
        with open(file_path, "wb") as file:
            pickle.dump(map_data, file)

    def load_topography_resources(self, file_path, settings):
        """Load the map topography and resources from a pickle file."""

        self.load_settings(settings)
        with open(file_path, "rb") as file:
            map_data = pickle.load(file)

        # Reconstruct the map object

        self.width = map_data["width"]
        self.height = map_data["height"]
        self.tiles = self.height * self.width

        # recalculate tile size since it depends on the tiles and screen size
        # TODO: differentiate between window size and map size !!!
        self.tile_size = int(self.height / math.sqrt(self.tiles))

        self.squares = []
        squares = map_data["squares"]
        for row_data in squares:
            row = [
                Map_Square(
                    id=square_data["id"],
                    x=square_data["x"],
                    y=square_data["y"],
                    square_size=self.tile_size,
                    land_value=square_data["land_type"],
                )
                for square_data in row_data
            ]
            self.squares.append(row)

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
