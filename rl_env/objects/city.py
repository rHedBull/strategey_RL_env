from typing import Tuple

import pygame

from rl_env.objects.Building import Building, BuildingType
from rl_env.objects.Ownable import Ownable


class City(Building, Ownable):
    def __init__(self, agent_id: int, position: Tuple[int, int], image: pygame.Surface):
        Ownable.__init__(self, agent_id)
        Building.__init__(self, position)
        # self.image = pygame.transform.scale(image, (image.get_width(), image.get_height()))

        self.max_level = 3
        self.building_type = BuildingType.CITY

    def draw(
        self,
        screen: pygame.Surface,
        square_size: int,
        owner_color: Tuple[int, int, int],
    ):
        # Draw the city image centered on the tile
        pygame.draw.rect(
            screen,
            owner_color,
            (
                self.x * square_size,
                self.y * square_size,
                square_size,
                square_size,
            ),
        )

    def get_building_type(self) -> str:
        return "City"
