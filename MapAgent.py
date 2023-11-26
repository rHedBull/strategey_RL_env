import random

from MapSettings import VALUE_DEFAULT_LAND, VALUE_DEFAULT_WATER


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
            if current_square.get_land_value() == VALUE_DEFAULT_LAND:
                current_square.set_land_value(VALUE_DEFAULT_WATER)
                # current_square.draw(world_map.screen)
                self.water_budget -= 1
