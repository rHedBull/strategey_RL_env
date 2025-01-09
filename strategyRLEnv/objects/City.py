from typing import Tuple

import pygame

from strategyRLEnv.map import MapPosition
from strategyRLEnv.map.map_settings import BuildingType, city_health
from strategyRLEnv.objects.Building import Building
from strategyRLEnv.objects.Destroyable import Destroyable
from strategyRLEnv.objects.Ownable import Ownable


class City(Building, Ownable, Destroyable):
    def __init__(self, agent_id: int, position: MapPosition, building_parameters: dict):
        super().__init__(
            position=position,
            building_type=BuildingType.CITY,
            building_parameters=building_parameters,
            agent_id=agent_id,
            health=city_health,
        )

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
