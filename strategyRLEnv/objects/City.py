from typing import Tuple

import pygame

from strategyRLEnv.map import MapPosition
from strategyRLEnv.objects.Building import Building, BuildingType
from strategyRLEnv.objects.Ownable import Ownable


class City(Building, Ownable):
    def __init__(self, agent_id: int, position: MapPosition, building_parameters: dict):
        Ownable.__init__(self, agent_id)
        Building.__init__(self, position, BuildingType.CITY, building_parameters)

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
                self.position.x * square_size,
                self.position.y * square_size,
                square_size,
                square_size,
            ),
        )
