import pygame
import random
import math

from MapSquare import MapSquare
from MapAgent import Map_Agent


def zoom_handler(pan_x, pan_y):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        pan_y += 10  # Move view up
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        pan_y -= 10  # Move view down
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        pan_x += 10  # Move view left
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        pan_x -= 10  # Move view right


class Map:
    def __init__(self, width=500, height=500):
        self.width = width
        self.height = height

        self.squares = []
        self.tiles = 100
        self.tile_size = int(self.height / math.sqrt(self.tiles))

        self.water_budget_per_agent = 1  # Adjust the total amount of land per agent
        self.numb_agents = 10

    def create_map(self, width, height, show=False, dynamic_view=False):
        self.width = width
        self.height = height

        # create map squares
        self.squares = [[MapSquare(x_index, y_index, self.tile_size) for x_index in range(int(math.sqrt(self.tiles)))]
                        for y_index in
                        range(int(math.sqrt(self.tiles)))]

        agents = [
            Map_Agent(random.randint(0, int(math.sqrt(self.tiles) - 1)),
                      random.randint(0, int(math.sqrt(self.tiles) - 1)),
                      self.water_budget_per_agent) for i in range(self.numb_agents)]
        # TODO correct indexing of agents, now they are not in the right place

        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Agent-based Landmass Generation')

        zoom_level = 1.0  # initial zoom level
        pan_x, pan_y = 0, 0  # initial pan position

        # Main loop
        running = True
        while running:

            # Move each agent and draw the world
            for agent in agents:
                agent.walk(self, self.tiles)
                if agent.water_budget == 0:
                    agents.remove(agent)
                if len(agents) == 0:
                    running = False
            if show:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN and dynamic_view:
                        if event.button == 4:  # Mouse wheel up
                            zoom_level *= 1.1  # Zoom in
                        elif event.button == 5:  # Mouse wheel down
                            zoom_level /= 1.1  # Zoom out

                if dynamic_view:
                    zoom_handler(pan_x, pan_y)
                screen.fill((0, 0, 0))

                self.draw(screen, zoom_level, pan_x, pan_y)
                pygame.display.update()

        self.draw(screen, zoom_level, pan_x, pan_y)
        pygame.display.update()

        # Secondary loop to keep the window open
        waiting_for_close = True
        while waiting_for_close:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting_for_close = False

    def get_map_as_matrix(self):
        # Returns the map as a matrix of land values
        return [[square.get_land_value() for square in row] for row in self.squares]

    def draw(self, screen, zoom_level, pan_x, pan_y):
        for row in self.squares:
            for square in row:
                new_x = (square.x * zoom_level) + pan_x
                new_y = (square.y * zoom_level) + pan_y
                new_size = square.square_size * zoom_level
                square.draw(screen, new_x, new_y, new_size)