from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Tuple
from uuid import uuid1

import pygame

from strategyRLEnv.map import MapPosition


class BuildingType(Enum):
    CITY = "build_city"
    ROAD = "build_road"
    BRIDGE = "build_bridge"
    FARM = "build_farm"


class Building(ABC):
    def __init__(
        self,
        position: MapPosition,
        building_type: BuildingType,
        building_parameters: Dict,
    ):
        self.id = uuid1()

        self.position = position

        self.level = 0
        self.max_level = building_parameters.get("max_level", 1)
        self.building_type = building_type
        self.building_type_id = building_parameters.get("building_type_id")

        self.money_gain_per_turn = building_parameters.get("money_gain_per_turn", 0)
        self.maintenance_cost_per_turn = building_parameters.get(
            "maintenance_cost_per_turn", 0
        )
        self.income_per_turn = 0
        self.calculate_income()

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
        return self.building_type

    def get_building_type_id(self):
        return self.building_type_id

    def upgrade(self):
        new_level = self.level + 1
        self.level = min(new_level, self.max_level)
        self.calculate_income()

    def downgrade(self):
        new_level = self.level - 1
        self.level = max(new_level, 0)
        self.calculate_income()

    def calculate_income(self):
        self.income_per_turn = self.money_gain_per_turn - self.maintenance_cost_per_turn

    def get_income(self):
        return self.income_per_turn
