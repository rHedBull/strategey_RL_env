from typing import Dict

import pygame

from strategyRLEnv.map import MapPosition
from strategyRLEnv.objects.Building import Building, BuildingType
from strategyRLEnv.objects.Ownable import Ownable


class Mine(Building, Ownable):
    def __init__(self, agent_id: int, position: MapPosition, building_parameters: Dict):
        Ownable.__init__(self, agent_id)
        Building.__init__(self, position, BuildingType.FARM, building_parameters)

    def draw(self, screen: pygame.Surface, square_size: int, colors: dict):
        """
        Draws triangle filling.

        :param screen: The Pygame surface to draw on.
        :param square_size: The size of the square in pixels.
        :param colors: A dictionary containing color values.
                       Expected keys: 'line' for line color, 'background' for square background.
        """
        # Calculate the top-left corner of the square
        top_left_x = self.position.x * square_size
        top_left_y = self.position.y * square_size

        # Define the color for the triangle
        triangle_color = (0, 0, 0)  # Default to black if not specified

        # Scaling factor to make the triangle smaller
        scaling_factor = 0.6
        base_width = int(square_size * scaling_factor)
        height = int(square_size * scaling_factor)

        # Centering coordinates
        base_x_start = top_left_x + (square_size - base_width) // 2
        base_y = top_left_y + square_size - (square_size - height) // 2
        apex_y = base_y - height

        # Vertices of the pyramid triangle
        vertex1 = (base_x_start, base_y)  # Base Left
        vertex2 = (base_x_start + base_width, base_y)  # Base Right
        vertex3 = (top_left_x + square_size // 2, apex_y)  # Apex

        # List of vertices
        vertices = [vertex1, vertex2, vertex3]

        # Draw the filled pyramid triangle
        pygame.draw.polygon(screen, triangle_color, vertices, 0)
