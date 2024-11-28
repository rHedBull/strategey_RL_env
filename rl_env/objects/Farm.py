import pygame

from map.MapPosition import MapPosition
from rl_env.objects.Building import Building, BuildingType
from rl_env.objects.Ownable import Ownable


class Farm(Building, Ownable):
    def __init__(self, agent_id: int, position: MapPosition, building_type_id: int):
        Ownable.__init__(self, agent_id)
        Building.__init__(self, position, BuildingType.FARM, building_type_id)

    def draw(self, screen: pygame.Surface, square_size: int, colors: dict):
        """
        Draws diagonal lines filling the square from bottom left to top right.

        :param screen: The Pygame surface to draw on.
        :param square_size: The size of the square in pixels.
        :param colors: A dictionary containing color values.
                       Expected keys: 'line' for line color, 'background' for square background.
        """
        # Calculate the top-left corner of the square
        top_left_x = self.x * square_size
        top_left_y = self.y * square_size

        # Define the color for the lines
        line_color = (0, 0, 0)  # Default to black if not specified

        num_lines = 2

        # Calculate spacing between lines
        spacing = square_size / (num_lines + 1)

        for i in range(1, num_lines + 1):
            # Calculate the offset for each line
            offset = spacing * i

            # Start position on the left edge of the tile
            start_pos = (top_left_x, top_left_y + square_size - offset)

            # End position on the top edge of the tile
            end_pos = (top_left_x + square_size, top_left_y + square_size - offset)

            # Draw the diagonal line
            pygame.draw.line(
                screen, line_color, start_pos, end_pos, 2
            )  # Width=2 for better visibility
