from abc import ABC, abstractmethod
from typing import Dict, Tuple
from uuid import uuid1

import pygame

from strategyRLEnv.map import MapPosition
from strategyRLEnv.map.map_settings import ADJACENCY_MULTIPLIERS, BuildingType


class Building(ABC):
    def __init__(
        self,
        position: MapPosition,
        building_type: BuildingType,
        building_parameters: Dict,
    ):
        self.id = uuid1()

        self.position = position

        self.building_type = building_type
        self.building_type_id = building_parameters.get("building_type_id")

        self.base_money_income = building_parameters.get("money_gain_per_turn", 0)
        self.maintenance_cost_per_turn = building_parameters.get(
            "maintenance_cost_per_turn", 0
        )
        self.income_per_turn = float(
            self.base_money_income - self.maintenance_cost_per_turn
        )

    def update(self, env):
        # update building income
        multiplier = self.check_multipliers(env)
        self.income_per_turn = (
            self.base_money_income * multiplier
        ) - self.maintenance_cost_per_turn

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

    def get_income(self):
        return self.income_per_turn

    def check_multipliers(self, env):
        adjacency_rules = ADJACENCY_MULTIPLIERS.get(self.building_type, {})
        total_multiplier = 1.0

        # Iterate over the rules and apply them
        for adjacent_building_type, rule in adjacency_rules.items():
            radius = rule["radius"]
            multiplier = rule["multiplier"]

            applies, tile = env.map.tile_is_next_to_building_type(
                self.position, adjacent_building_type, diagonal=False, radius=radius
            )
            if applies:
                total_multiplier += multiplier
        return total_multiplier
