import math
import random

import numpy as np

from Map.MapAgent import Map_Agent
from Map.MapSettings import VALUE_DEFAULT_WATER, VALUE_DEFAULT_WATER_ADJACENT, VALUE_DEFAULT_MOUNTAIN, \
    VALUE_DEFAULT_DESSERT
from Map.MapSquare import Map_Square
from RL_env.Settings import Settings


class Map:
    def __init__(self):
        self.water_percentage = None # TODO differentiate between lakes, oceans, rivers?
        self.mountain_percentage = None
        self.dessert_percentage = None


        self.tile_size = None
        self.tiles = None
        self.width = None
        self.height = None

        self.squares = []

    def create_map(self, settings):
        self.width = settings.get_setting('map_width')
        self.height = settings.get_setting('map_height')

        self.tiles = settings.get_setting('tiles')
        self.tile_size = int(self.height / math.sqrt(self.tiles))
        self.max_x_index = int(self.width / self.tile_size)
        self.max_y_index = int(self.height / self.tile_size)
        self.water_percentage = settings.get_setting('water_budget_per_agent')
        self.mountain_percentage = settings.get_setting('mountain_budget_per_agent')
        self.dessert_percentage = settings.get_setting('dessert_budget_per_agent')

        # create map squares
        self.squares = [
            [Map_Square((y_index * self.max_x_index + x_index),x_index, y_index, self.tile_size) for x_index in range(self.max_x_index)]
            for y_index in range(self.max_y_index)]

        self.reset()

    def reset(self):
        for row in self.squares:
            for square in row:
                square.reset()

        # mountain agents
        self.let_map_agent_run( self.mountain_percentage, self.tiles, VALUE_DEFAULT_MOUNTAIN)

        # dessert agents
        self.let_map_agent_run( self.dessert_percentage, self.tiles,
                               VALUE_DEFAULT_DESSERT)

        # water agents
        self.let_map_agent_run(self.water_percentage, self.tiles, VALUE_DEFAULT_WATER)

        # TODO: make importance editable water over mountain over dessert
        # TODO: make distribution percentage wise locked to tile count
        # TODO: enable selecttion of land types
        # TODO: enable distribution method

        # post processing
        for row in self.squares:
            for square in row:

                # TODO: add random mountain distribution
                # TODO : make the distribution density and type editable
                """if square.get_land_type() != VALUE_DEFAULT_WATER:
                    j = np.random.randint(0,10)/10

                    if j >0.75 and j < 0.85:
                        square.set_land_type(VALUE_DEFAULT_MOUNTAIN)
                    elif(j > 0.85 and j < 1):
                        square.set_land_type(VALUE_DEFAULT_DESSERT)"""

                # check if water arround
                if square.get_land_type() != VALUE_DEFAULT_WATER:
                    if (square.x > 0 and self.squares[square.y][
                        square.x - 1].get_land_type() == VALUE_DEFAULT_WATER or  # check water left
                            square.x < self.max_x_index - 1 and self.squares[square.y][
                                square.x + 1].get_land_type() == VALUE_DEFAULT_WATER or  # check water right
                            square.y > 0 and self.squares[square.y - 1][
                                square.x].get_land_type() == VALUE_DEFAULT_WATER or  # check water up
                            square.y < self.max_y_index - 1 and self.squares[square.y + 1][
                                square.x].get_land_type() == VALUE_DEFAULT_WATER):  # check water down
                        square.set_land_type(VALUE_DEFAULT_WATER_ADJACENT)

    def get_map_as_matrix(self):

        """define here what infor is visible to all agents
        Assuming full observability of map for now
        """
        map_info = np.zeros((self.max_x_index, self.max_y_index, 2))
        for row in self.squares:
            for square in row:
                map_info[square.x][square.y] = [square.get_land_type(), square.get_owner()]
        return map_info

    def claim_tile(self, agent, x, y):
        """
        Claim a tile at position (x,y) for an agent
        :param agent:
        :param x:
        :param y:
        :return:
        """
        self.squares[y][x].claim(agent)

    def add_building(self, building_id, x,y):
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

    def get_tile(self, x, y):
        """
        Get the tile at position x, y
        :param x:
        :param y:
        :return:
        """
        return self.squares[y][x]

    def let_map_agent_run(self, land_type_percentage, tiles, LAND_TYPE_VALUE):
        total_tile_budget =  tiles * (land_type_percentage /100)
        numb_agents = 10
        tile_budget_per_agent = total_tile_budget / numb_agents

        if (numb_agents * tile_budget_per_agent) > 0:
            agents = [
                Map_Agent(random.randint(0, int(math.sqrt(tiles) - 1)),
                          random.randint(0, int(math.sqrt(tiles) - 1)),
                          tile_budget_per_agent) for i in range(numb_agents)]

            running = True
            while running:

                for agent in agents:
                    agent.walk(self, tiles, LAND_TYPE_VALUE)
                    if agent.tile_budget == 0:
                        agents.remove(agent)
                    if len(agents) == 0:
                        running = False