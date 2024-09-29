import math
import random

from map.map_settings import VALUE_DEFAULT_OCEAN


class Map_Agent:
    def __init__(self, x, y, tile_budget):
        self.last_move_x = None
        self.last_move_y = None
        self.x = x
        self.y = y
        self.tile_budget = tile_budget  # Total amount of tiles to create

    def random_walk(self, world_map, tiles_in_map, LAND_TYPE_VALUE):
        # Random walk step
        step_x = random.choice([-1, 0, 1])
        step_y = random.choice([-1, 0, 1])
        if random.choice(
            [True, False]
        ):  # Randomly decide to move horizontally or vertically
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

    def river_walk(self, world_map, tiles_in_map, LAND_TYPE_VALUE):
        # Initialize with a random direction to start
        self.last_move_x = random.choice([-1, 1])
        self.last_move_y = (
            0  # Start with horizontal movement, could also randomize this
        )

        while self.tile_budget > 0:
            # Introduce a slight chance to more drastically change direction
            if (
                random.random() < 0.2
            ):  # 20% chance to consider changing direction more significantly
                step_x_choices = [-1, 0, 1]
                step_y_choices = [-1, 0, 1]
            else:
                step_x_choices = [
                    0,
                    self.last_move_x,
                ]  # Continue or stay, avoid direct reversal
                step_y_choices = [0, self.last_move_y]  # Same for y direction

            # Randomly decide to prioritize horizontal or vertical movement
            if random.choice([True, False]):
                step_x = random.choice(step_x_choices)
                step_y = 0 if step_x != 0 else random.choice(step_y_choices)
            else:
                step_y = random.choice(step_y_choices)
                step_x = 0 if step_y != 0 else random.choice(step_x_choices)

            # Avoid direct reversal if possible
            if step_x == -self.last_move_x and step_y == -self.last_move_y:
                continue  # Skip this iteration and pick new directions

            # Update position based on chosen steps
            self.x += step_x
            self.y += step_y

            # Ensure the agent remains within world bounds
            self.x = max(0, min(self.x, int(math.sqrt(tiles_in_map)) - 1))
            self.y = max(0, min(self.y, int(math.sqrt(tiles_in_map)) - 1))

            # Update the last move direction
            self.last_move_x, self.last_move_y = step_x, step_y

            # Create water if not already water
            current_square = world_map.squares[self.y][self.x]

            if (
                current_square.get_land_type() == VALUE_DEFAULT_OCEAN
                or self.x == 0
                or self.x == int(math.sqrt(tiles_in_map)) - 1
                or self.y == 0
                or self.y == int(math.sqrt(tiles_in_map)) - 1
            ):
                return  # Stop the river if it reaches the ocean

            elif current_square.get_land_type() != LAND_TYPE_VALUE:
                current_square.set_land_type(LAND_TYPE_VALUE)
                self.tile_budget -= 1
