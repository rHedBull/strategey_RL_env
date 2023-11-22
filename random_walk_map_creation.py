import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Map dimensions
width, height = 1270, 1000
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Agent-based Landmass Generation')

# Constants
SQUARE_SIZE = 10  # Size of the squares
WATER_COLOR =  (34, 139, 34) # Water color
LAND_COLOR = (70, 130, 180)  # Land color

# Create the world as a 2D array
world = [[WATER_COLOR for _ in range(width // SQUARE_SIZE)] for _ in range(height // SQUARE_SIZE)]

# Agent class
class Agent:
    def __init__(self, x, y, land_budget):
        self.x = x
        self.y = y
        self.land_budget = land_budget  # Total amount of land to create

    def walk(self):
        # Random walk step
        step_x = random.choice([-1, 0, 1])
        step_y = random.choice([-1, 0, 1])
        self.x += step_x
        self.y += step_y
        # Keep the agent within bounds of the world
        self.x = max(0, min(self.x, width // SQUARE_SIZE - 1))
        self.y = max(0, min(self.y, height // SQUARE_SIZE - 1))

        # Create land if there is budget left
        if self.land_budget > 0:
            if world[self.y][self.x] != LAND_COLOR:
                world[self.y][self.x] = LAND_COLOR
                self.land_budget -= 1

# Initialize agents
num_agents = 10
land_per_agent = 500  # Adjust the total amount of land per agent
agents = [Agent(random.randint(0, width // SQUARE_SIZE - 1), random.randint(0, height // SQUARE_SIZE - 1), land_per_agent) for _ in range(num_agents)]

# Function to draw the world
def draw_world():
    for y in range(height // SQUARE_SIZE):
        for x in range(width // SQUARE_SIZE):
            color = world[y][x]
            pygame.draw.rect(screen, color, (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move each agent and draw the world
    for agent in agents:
        agent.walk()
    draw_world()

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
