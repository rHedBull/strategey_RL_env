import random

default_land_color = (34, 139, 34)
default_water_color = (0, 255, 255)
default_border_color = (255, 255, 255)

default_land_value = 0
default_water_value = 1

default_tile_owner = 0

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
