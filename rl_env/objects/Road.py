from enum import Enum, auto
from typing import Tuple

import pygame

from rl_env.objects.Building import Building, BuildingType

road_color = (128, 128, 128)

# brown bridge
bridge_color = (139, 69, 19)

class RoadShape:
    up: bool = False
    down: bool = False
    left: bool = False
    right: bool = False

class Road(Building):
    def __init__(
        self, position: Tuple[int, int], shape=None):
        super().__init__(position, BuildingType.ROAD)

        self.max_level = 3
        self.shape = shape if shape else RoadShape()
        self.shape.left = True

    def draw(
        self,
        screen: pygame.Surface,
        square_size: int,
        owner_color: Tuple[int, int, int],
    ):
        """
        Draw the road on the screen.
        :param owner_color:
        :param square_size:
        :param screen: Pygame display surface
        """

        draw_bridge_road(screen, self.x, self.y, square_size, self.shape, bridge_color)

class Bridge(Building):
    def __init__(
        self, position: Tuple[int, int], shape=None):
        super().__init__(position, BuildingType.BRIDGE)

        self.max_level = 3
        self.shape = shape if shape else RoadShape()
        self.shape.left = True
        self.shape.right = True
        # TODO: function to check surrounding tiles for road or bridge


    def draw(
        self,
        screen: pygame.Surface,
        square_size: int,
        owner_color: Tuple[int, int, int],
    ):
        """
        Draw the road on the screen.
        :param shape:
        :param square_size:
        :param owner_color:
        :param screen: Pygame display surface
        """

        draw_bridge_road(screen, self.x, self.y, square_size, self.shape, bridge_color)


def draw_bridge_road(screen: pygame.Surface, x, y, square_size: int, shape: RoadShape, color: Tuple[int, int, int]):
    """
    Draw the road on the screen based on the RoadShape.

    :param color:
    :param y:
    :param x:
    :param screen: Pygame display surface
    :param square_size: Size of the square tile
    :param shape: RoadShape indicating connections
    """
    center_x = x * square_size + square_size // 2
    center_y = y * square_size + square_size // 2
    half_size = square_size // 2

    road_width = max(2, square_size // 8)  # Adjust road thickness as needed

    # Define end points for each direction
    directions = {
        'up': (center_x, center_y - half_size),
        'down': (center_x, center_y + half_size),
        'left': (center_x - half_size, center_y),
        'right': (center_x + half_size, center_y),
    }

    # Draw roads based on active connections
    if shape.up:
        pygame.draw.line(screen, color, (center_x, center_y), directions['up'], road_width)
    if shape.down:
        pygame.draw.line(screen, color, (center_x, center_y), directions['down'], road_width)
    if shape.left:
        pygame.draw.line(screen, color, (center_x, center_y), directions['left'], road_width)
    if shape.right:
        pygame.draw.line(screen, color, (center_x, center_y), directions['right'], road_width)