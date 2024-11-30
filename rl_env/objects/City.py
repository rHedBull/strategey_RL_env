from typing import Tuple

import pygame

from map.MapPosition import MapPosition
from rl_env.objects.Building import Building, BuildingType
from rl_env.objects.Ownable import Ownable


class City(Building, Ownable):
    def __init__(self, agent_id: int, position: MapPosition, building_type_id):
        Ownable.__init__(self, agent_id)
        Building.__init__(self, position, BuildingType.CITY, building_type_id)

        self.max_level = 3

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