import random
import math

from Map.MapSettings import *


class Map_Agent:
    def __init__(self, x, y, tile_budget):
        self.x = x
        self.y = y
        self.tile_budget = tile_budget  # Total amount of tiles to create

    def walk(self, world_map, tiles_in_map, LAND_TYPE_VALUE):
        # Random walk step
        step_x = random.choice([-1, 0, 1])
        step_y = random.choice([-1, 0, 1])
        if random.choice([True, False]):  # Randomly decide to move horizontally or vertically
            self.x += step_x
        else:
            self.y += step_y

        # Keep the agent within bounds of the world
        self.x = max(0, min(self.x, int(math.sqrt(tiles_in_map)) - 1))
        self.y = max(0, min(self.y, int(math.sqrt(tiles_in_map)) - 1))

        # Create water if the agent has any water budget left
        if self.tile_budget > 0:
            current_square = world_map.squares[self.y][self.x]
            if current_square.get_land_type() != LAND_TYPE_VALUE:
                current_square.set_land_type(LAND_TYPE_VALUE)
                # current_square.draw(world_map.screen)
                self.tile_budget -= 1
