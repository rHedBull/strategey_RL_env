from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple
from uuid import uuid1

import pygame


class BuildingType(Enum):
    CITY = "city"
    ROAD = "road"
    FARM = "farm"
    BRIDGE = "bridge"


class Building(ABC):
    def __init__(self, position: Tuple[int, int], building_type: BuildingType):
        self.id = uuid1()

        self.x, self.y = position

        self.level = 0
        self.max_level = None
        self.building_type = building_type

    @abstractmethod
    def draw(
        self,
        screen: pygame.Surface,
        square_size: int,
        owner_color: Tuple[int, int, int],
    ):
        """
        Draw the building on the given screen.
        """
        pass


    def get_building_type(self) -> BuildingType:
        """
        Return the type of the building (e.g., 'City', 'Road', 'Farm').
        """
        return  self.building_type

    def upgrade(self):
        new_level = self.level + 1
        self.level = min(new_level, self.max_level)

    def downgrade(self):
        new_level = self.level - 1
        self.level = max(new_level, 0)
