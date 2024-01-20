import math
import random

import numpy as np

from Map.MapAgent import Map_Agent
from Map.MapSquare import Map_Square
from RL_env.Settings import Settings


class Map:
    def __init__(self):
        self.numb_agents = None
        self.water_budget_per_agent = None
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
        self.water_budget_per_agent = settings.get_setting('map_agents_water')
        self.numb_agents = settings.get_setting('map_agents')

        # create map squares
        self.squares = [[Map_Square(x_index, y_index, self.tile_size) for x_index in range(self.max_x_index)]
                        for y_index in
                        range(self.max_y_index)]

        self.reset()

    def reset(self):
        for row in self.squares:
            for square in row:
                square.reset()

        if (self.numb_agents * self.water_budget_per_agent) > 0:
            agents = [
                Map_Agent(random.randint(0, int(math.sqrt(self.tiles) - 1)),
                          random.randint(0, int(math.sqrt(self.tiles) - 1)),
                          self.water_budget_per_agent) for i in range(self.numb_agents)]

            running = True
            while running:

                for agent in agents:
                    agent.walk(self, self.tiles)
                    if agent.water_budget == 0:
                        agents.remove(agent)
                    if len(agents) == 0:
                        running = False

    def get_map_as_matrix(self):

        # define here what infor is visible to all agents
        # Assuming full observability of map for now
        map_info = np.zeros((self.max_x_index, self.max_y_index, 2))
        for row in self.squares:
            for square in row:
                map_info[square.x][square.y] = [square.get_land_type(), square.get_owner()]
        return map_info

    def claim_tile(self, agent):
        self.squares[agent.y][agent.x].claim(agent)

    def draw(self, screen, zoom_level, pan_x, pan_y):
        for row in self.squares:
            for square in row:
                new_x = (square.x * zoom_level) + pan_x
                new_y = (square.y * zoom_level) + pan_y
                new_size = square.square_size * zoom_level
                square.draw(screen, new_x, new_y, new_size)

    def get_tile(self, x, y):
        return self.squares[y][x]
