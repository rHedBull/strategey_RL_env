import math
import random

from strategyRLEnv.map.map_settings import LandType


class Map_Agent:
    def __init__(self, x, y, tile_budget):
        self.last_move_x = None
        self.last_move_y = None
        self.x = x
        self.y = y
        self.tile_budget = tile_budget  # Total amount of tiles to create

    def random_walk(self, world_map:[[]], tiles_in_map, land_type: LandType):
        # Random walk step
        step = random.choice([(1,-1),(1,0), (1,1), (0,-1), (0,1), (-1,-1), (-1,0), (-1,1)])
        step_x = step[0]
        step_y = step[1]
        self.x += step_x
        self.y += step_y

        # Keep the agent within bounds of the world
        self.x = max(0, min(self.x, int(math.sqrt(tiles_in_map)) - 1))
        self.y = max(0, min(self.y, int(math.sqrt(tiles_in_map)) - 1))

        # Create water if the agent has any water budget left
        if self.tile_budget > 0:
            current_square = world_map[self.y][self.x]
            if current_square != land_type.value:
                world_map[self.y][self.x] = land_type.value
                self.tile_budget -= 1
