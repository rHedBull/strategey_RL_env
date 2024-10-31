from enum import Enum
from typing import Tuple

import pygame

from rl_env.objects.Building import Building, BuildingType


class RoadType(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    BRIDGE = "bridge"


class Road(Building):
    def __init__(
        self, position: Tuple[int, int], road_type: RoadType, image: pygame.Surface
    ):
        super().__init__(position)  # Example color: Gray
        # self.image = pygame.transform.scale(image, (image.get_width(), image.get_height()))
        self.road_type = road_type
        self.max_level = 3

        if self.road_type == RoadType.BRIDGE:
            self.building_type = BuildingType.BRIDGE
        else:
            self.building_type = BuildingType.ROAD

    def draw(
        self,
        screen: pygame.Surface,
        square_size: int,
        owner_color: Tuple[int, int, int],
    ):
        """
        Draw the road on the screen.
        :param screen: Pygame display surface
        """

        # TODO: more advanced road drawing
        # Draw the road image centered on the tile
        if self.road_type == RoadType.HORIZONTAL:
            width = square_size * 2  # Adjust as needed
            height = square_size // 4  # Adjust road thickness

        elif self.road_type == RoadType.VERTICAL:
            width = square_size // 4
            height = square_size * 2  # Adjust as needed
        elif self.road_type == RoadType.BRIDGE:
            width = square_size * 2  # Adjust as needed
            height = square_size // 4  # Adjust road thickness
        else:
            raise ValueError("Direction must be 'horizontal' or 'vertical'")

        # Create the rectangle
        rect = pygame.Rect(0, 0, width, height)
        rect.center = (
            self.x * square_size + square_size // 2,
            self.y * square_size + square_size // 2,
        )

        road_color = (128, 128, 128)

        # brown bridge
        bridge_color = (139, 69, 19)
        if self.road_type == RoadType.BRIDGE:
            color = bridge_color
        else:
            color = road_color

        # Draw the rectangle on the screen
        pygame.draw.rect(screen, color, rect)

    def get_building_type(self) -> BuildingType:
        return self.building_type

    def get_road_type(self) -> RoadType:
        return self.road_type