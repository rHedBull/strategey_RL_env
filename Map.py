import pygame
import random


from MapSquare import MapSquare
from MapAgent import Map_Agent

class Map:
    def __init__(self, width=100, height=100):
        self.width = width
        self.height = height
        self.squares = []
        self.square_size = 10

        self.water_budget_per_agent = 50  # Adjust the total amount of land per agent
        self.numb_agents = 10

    def create_map(self, width, height):
        self.width = width
        self.height = height

        # create map squares
        self.squares = [[MapSquare(x, y) for x in range(self.width)] for y in
                        range(self.height)]

        agents = [
            Map_Agent(random.randint(0, self.width - 1), random.randint(0, self.height - 1),
                      self.water_budget_per_agent) for i in range(self.numb_agents)]


        # Main loop
        running = True
        while running:

            #for event in pygame.event.get():
             #   if event.type == pygame.QUIT:
              #      running = False

            # Move each agent and draw the world
            for agent in agents:
                agent.walk(self)
                if agent.water_budget == 0:
                    agents.remove(agent)
                if len(agents) == 0:
                    running = False
            #self.draw(screen)
            #pygame.display.update()

        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Agent-based Landmass Generation')

        self.draw(screen)

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

    def draw(self, screen):
        for row in self.squares:
            for square in row:
                square.draw(screen)