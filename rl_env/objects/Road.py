from typing import Tuple
import pygame
from enum import Enum

from rl_env.objects.Building import Building, BuildingType


class RoadType(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class Road(Building):

    def __init__(self, position: Tuple[int, int], road_type: RoadType, image: pygame.Surface):
        super().__init__(position)  # Example color: Gray
        #self.image = pygame.transform.scale(image, (image.get_width(), image.get_height()))
        self.road_type = road_type
        self.max_level = 3
        self.building_type = BuildingType.ROAD

    def draw(self, screen: pygame.Surface, square_size: int, owner_color: Tuple[int, int, int]):
        """
        Draw the road on the screen.
        :param screen: Pygame display surface
        """

        # Draw the road image centered on the tile
        if self.road_type == RoadType.HORIZONTAL:
            width = square_size * 2  # Adjust as needed
            height = square_size // 4  # Adjust road thickness

        elif self.road_type == RoadType.VERTICAL:
            width = square_size // 4
            height = square_size * 2  # Adjust as needed
        else:
            raise ValueError("Direction must be 'horizontal' or 'vertical'")

        # Create the rectangle
        rect = pygame.Rect(0, 0, width, height)
        rect.center = (
            self.x * square_size + square_size // 2,
            self.y * square_size + square_size // 2,
        )

        road_color = (128, 128, 128)
        # Draw the rectangle on the screen
        pygame.draw.rect(screen, road_color, rect)

    def get_building_type(self) -> str:
        return "Road"

    def get_road_type(self) -> RoadType:
        return self.road_type
