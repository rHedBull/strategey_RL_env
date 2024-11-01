from enum import Enum
from typing import Tuple

import pygame

from rl_env.objects.Building import Building, BuildingType

road_color = (128, 128, 128)

# brown bridge
bridge_color = (139, 69, 19)

class Road(Building):
    def __init__(
        self, position: Tuple[int, int]):
        super().__init__(position, BuildingType.ROAD)

        self.max_level = 3

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

        # TODO: more advanced road drawing

        width = square_size * 2  # Adjust as needed
        height = square_size // 4  # Adjust road thickness

        rect = pygame.Rect(0, 0, width, height)
        rect.center = (
            self.x * square_size + square_size // 2,
            self.y * square_size + square_size // 2,
        )

        pygame.draw.rect(screen, road_color, rect)

class Bridge(Building):
    def __init__(
        self, position: Tuple[int, int]):
        super().__init__(position, BuildingType.BRIDGE)

        self.max_level = 3

    def draw(
        self,
        screen: pygame.Surface,
        square_size: int,
        owner_color: Tuple[int, int, int],
    ):
        """
        Draw the road on the screen.
        :param square_size:
        :param owner_color:
        :param screen: Pygame display surface
        """

        # TODO: more advanced road drawing

        width = square_size * 2  # Adjust as needed
        height = square_size // 4  # Adjust road thickness

        rect = pygame.Rect(0, 0, width, height)
        rect.center = (
            self.x * square_size + square_size // 2,
            self.y * square_size + square_size // 2,
        )

        pygame.draw.rect(screen, bridge_color, rect)