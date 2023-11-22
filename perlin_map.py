import pygame
import sys
import numpy as np
from noise import pnoise2
import random

# Initialize Pygame
pygame.init()

# Map dimensions
width, height = 1000, 500
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Perlin Noise Landmass Map')

# Constants
SQUARE_SIZE = 1  # Size of the squares (the smaller, the more detailed)
LAND_THRESHOLD = 0.5  # Threshold of the noise to determine land

# Function to generate Perlin noise
def generate_perlin_noise(width, height, scale=30.0, octaves=1, persistence=0.5, lacunarity=2.0, seed = 0):
    world = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            # Generating noise value with a seed
            noise_value = pnoise2(x / scale,
                                  y / scale,
                                  octaves=octaves,
                                  persistence=persistence,
                                  lacunarity=lacunarity,
                                  repeatx=1024,
                                  repeaty=1024,
                                  base=seed)
            world[y][x] = noise_value
    return world


def draw_landmass(world):
    for y in range(height // SQUARE_SIZE):  # Ensure y is within bounds
        for x in range(width // SQUARE_SIZE):  # Ensure x is within bounds
            if world[y][x] > LAND_THRESHOLD:
                color = (34, 139, 34)  # Land color
            else:
                color = (70, 130, 180)  # Water color
            # Draw the rectangle at the correct position scaled by SQUARE_SIZE
            pygame.draw.rect(screen, color, (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


# Generate Perlin noise based world map
seed = random.randint(0, 10)
world_map = generate_perlin_noise(width // SQUARE_SIZE, height // SQUARE_SIZE, seed=seed)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw the landmass
    draw_landmass(world_map)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
