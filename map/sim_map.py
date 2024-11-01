import math
import pickle
import random
from typing import Tuple

import numpy as np

from map.map_agent import Map_Agent
from map.map_settings import LandType
from map.map_square import Map_Square
from test_env.Agent import Agent


class Map:
    def __init__(self, screen_size):
        self.tiles = None
        self.tile_size = None
        self.width = None
        self.height = None

        self.screen_size = screen_size

        self.squares = []

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

    def load_settings(
        self,
        settings,
    ):
        self.width = settings.get_setting("map_width")
        self.height = settings.get_setting("map_height")

        self.tiles = self.height * self.width

        if self.height > self.width:
            self.tile_size = int(self.screen_size / self.height)
        else:
            self.tile_size = int(self.screen_size / self.width)
        self.tile_size = max(1, self.tile_size)

        self.continuous_map = settings.get_setting("continuous_map")

        self.water_percentage = settings.get_setting("water_budget_per_agent")
        self.mountain_percentage = settings.get_setting("mountain_budget_per_agent")
        self.dessert_percentage = settings.get_setting("dessert_budget_per_agent")
        self.rivers = settings.get_setting("numb_rivers")
        self.resource_density = settings.get_setting("resource_density")
        self.biomes_definition = settings.get_setting("biomes")
        self.land_resource_definition = settings.get_setting("land_resources")
        self.sea_resource_definition = settings.get_setting("land_resources")
        self.height_values = settings.get_setting("height_values")

    def create_map(self, settings):
        self.load_settings(settings)

        # create map squares
        self.squares = [
            [
                Map_Square(
                    (y_index * self.width + x_index),
                    x_index,
                    y_index,
                    self.tile_size,
                )
                for x_index in range(self.width)
            ]
            for y_index in range(self.height)
        ]

        self.reset()

    def distribute_resources(self, square):
        # resource distribution totally random so far
        i = np.random.randint(0, 10) / 10

        if i < self.resource_density:
            if square.get_land_type() != LandType.OCEAN:
                resource = np.random.randint(0, 6)
                square.add_resource(resource)
            else:
                resource = np.random.randint(0, 1)
                square.add_resource(resource)

    def reset(self):
        for row in self.squares:
            for square in row:
                square.reset()

        # mountain agents
        self.let_map_agent_run(
            self.mountain_percentage, self.tiles, LandType.MOUNTAIN
        )

        # dessert agents
        self.let_map_agent_run(
            self.dessert_percentage, self.tiles, LandType.DESERT
        )

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
                        square.x > 0
                        and self.squares[square.y][square.x - 1].get_land_type()
                        == LandType.OCEAN
                        or square.x < self.width - 1  # check water left
                        and self.squares[square.y][square.x + 1].get_land_type()
                        == LandType.OCEAN
                        or square.y > 0  # check water right
                        and self.squares[square.y - 1][square.x].get_land_type()
                        == LandType.OCEAN
                        or square.y < self.height - 1  # check water up
                        and self.squares[square.y + 1][square.x].get_land_type()
                        == LandType.OCEAN
                    ):  # check water down
                        square.set_land_type(LandType.MARSH)

    def get_observation(self):
        """define here what infor is visible to all agents
        Assuming full observability of map for now
        """
        map_info = np.zeros((self.width, self.height, 5))  # number of features per tile
        for row in self.squares:
            for square in row:
                map_info[square.x][square.y] = square.get_observation_state()
        return map_info

    def get_full_map_as_matrix(self):
        """
        Get the full map as a matrix. Including each square's full information.
        Not really meant for the agents to see. Rather to recreate the map later.
        """

        full_map_info = np.zeros((self.width, self.height, 2))
        for row in self.squares:
            for square in row:
                info = square.get_full_info()
                full_map_info[square.x][square.y] = info
        return full_map_info

    def claim_tile(self, agent: Agent, position: [int, int]) -> None:
        """
        Claim a tile at position (x,y) for an agent
        :param position:
        :param agent:
        :return:
        """
        x, y = position
        self.squares[y][x].claim(agent)

    def add_building(self, building_id, x, y):
        self.squares[y][x].add_building(building_id, x, y)

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
                new_x = (square.x * zoom_level) + pan_x
                new_y = (square.y * zoom_level) + pan_y
                new_size = square.square_size * zoom_level
                square.draw(screen, new_x, new_y, new_size)

    def get_tile(self, position: [int, int]) -> Map_Square:
        """
        Get the tile at position x, y
        :param x:
        :param y:
        :return:
        """
        x, y = position
        return self.squares[y][x]

    def river_agents(self, tiles, rivers):
        numb_agents = rivers
        tile_budget_per_agent = 0.1 * tiles
        agents = [
            Map_Agent(
                random.randint(0, int(math.sqrt(tiles) - 1)),
                random.randint(0, int(math.sqrt(tiles) - 1)),
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
                    random.randint(0, int(math.sqrt(tiles) - 1)),
                    random.randint(0, int(math.sqrt(tiles) - 1)),
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
