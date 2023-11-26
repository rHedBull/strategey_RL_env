import pygame
import random

default_land_color = (34, 139, 34)
default_water_color = (0, 255, 255)
default_border_color = (255, 255, 255)

default_land_value = 0
default_water_value = 1

default_tile_owner = 0


class MapSquare:
    def __init__(self, x, y, land_value=default_land_value):
        self.x = x
        self.y = y
        self.square_size = 10

        self.default_border_color = default_border_color
        self.default_color = default_land_color
        self.fill_color = default_land_color
        self.border_color = default_border_color

        self.land_value = land_value
        self.owner_value = default_tile_owner

    def set_owner(self, owner_value):
        self.owner_value = owner_value

    def get_owner(self):
        return self.owner_value

    def set_land_value(self, land_value):
        self.land_value = land_value
        if self.land_value == default_land_value:
            self.fill_color = default_land_color
        else:
            self.fill_color = default_water_color


    def get_land_value(self):
        return self.land_value

    def draw(self, screen):
        pygame.draw.rect(screen, self.fill_color, (self.x, self.y, self.square_size, self.square_size))

    def draw_border(self, screen):
        # draw square border
        color = self.default_border_color
        if self.get_owner() == default_tile_owner:
            color = default_border_color
        else:
            color = default_water_color
        pygame.draw.rect(screen, color, (self.x, self.y, self.square_size, self.square_size), 1)


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
        self.squares = [[MapSquare(x , y ) for x in range(self.width)] for y in
                        range(self.height)]

        agents = [
            Map_Agent(random.randint(0, self.width - 1), random.randint(0, self.height - 1),
                      self.water_budget_per_agent) for i in range(self.numb_agents)]

        # Initialize Pygame



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


# Agent class
class Map_Agent:
    def __init__(self, x, y, water_budget):
        self.x = x
        self.y = y
        self.water_budget = water_budget  # Total amount of water to create

    def walk(self, world_map):
        # Random walk step
        step_x = random.choice([-1, 0, 1])
        step_y = random.choice([-1, 0, 1])
        if random.choice([True, False]):  # Randomly decide to move horizontally or vertically
            self.x += step_x
        else:
            self.y += step_y

        # Keep the agent within bounds of the world
        self.x = max(0, min(self.x, world_map.width - 1))
        self.y = max(0, min(self.y, world_map.height - 1))

        if self.water_budget > 0:
            current_square = world_map.squares[self.y][self.x]
            if current_square.get_land_value() == default_land_value:
                current_square.set_land_value(default_water_value)
                #current_square.draw(world_map.screen)
                self.water_budget -= 1
