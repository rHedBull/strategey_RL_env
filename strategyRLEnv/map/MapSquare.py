from typing import Tuple

import pygame

from strategyRLEnv.map.map_settings import (COLOR_DEFAULT_BORDER,
                                            OWNER_DEFAULT_TILE, BuildingType,
                                            LandType, ResourceType,
                                            land_type_color)
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.objects.Building import Building


class Map_Square:
    """
    Class for a single square/ tile on the map
    """

    def __init__(self, tile_id: int, position: MapPosition, land_value=LandType.LAND):
        # coordinates and ids
        self.tile_id = tile_id
        self.position = position

        # land properties
        self.land_type = LandType.LAND
        self.resource = ResourceType.NONE
        self.resources = []

        if land_value is not None:
            self.set_land_type(land_value)

        # owner specific
        self.owner_id = OWNER_DEFAULT_TILE

        self.visibility_bitmask = 0  # init to zero, no agent can see this tile

        self.building = None

        self._land_money_value = 1  # determined by land type
        self.tile_income = 0  # current income of the tile

        self.unit = None

        # ui stuff
        self.default_border_color = COLOR_DEFAULT_BORDER
        self.default_color = land_type_color(LandType.LAND)

        self.land_type_color = land_type_color(LandType.LAND)
        self.owner_color = COLOR_DEFAULT_BORDER

    def reset(self, total_reset: bool = True):
        self.set_owner(OWNER_DEFAULT_TILE, COLOR_DEFAULT_BORDER)

        self._land_money_value = 1

        self.building = None
        self.unit = None

        if total_reset:
            self.visibility_bitmask = 0

    def update(self, env):
        """
        Update the square and then recalculate the tile income
        Args:
            env: The environment object
        """
        building_income = 0
        # update buildings
        if self.building is not None:
            self.building.update(env)
            building_income = self.building.get_income()

        self.tile_income = building_income + self._land_money_value

    def set_owner(self, agent_id: int, agent_color: Tuple[int, int, int]):
        """
        Claim the square for an agent.
        """
        self.owner_id = agent_id
        self.owner_color = agent_color

    def get_owner(self):
        return self.owner_id

    def add_resource(self, resource_type: ResourceType):
        self.resource = resource_type

    def get_resources(self):
        return self.resources

    def remove_resource(self, resource_value):
        self.resources.remove(resource_value)

    def set_land_type(self, land_value: LandType):
        """
        Set the land type of the square
        :param land_value:
        :return:
        """
        if land_value != self.land_type:
            self.land_type = land_value
            self.land_type_color = land_type_color(land_value)

    def get_land_type(self) -> LandType:
        return self.land_type

    # claim stuff #
    def claim(self, agent):
        """
        Claim the square for an agent
        :param agent:
        :return:
        """
        self.owner_id = agent.id
        self.owner_color = agent.color

    # building stuff #
    def add_building(self, building: Building):
        """
        Add a building to the square.
        """
        self.building = building

    def remove_building(self, building_type: BuildingType = None):
        """
        Remove a building from the square.
        """
        if building_type is None:  # remove without checking
            self.building = None

        if self.building is not None:
            if (
                self.building.building_type == building_type
            ):  # only remove if the building type matches
                self.building = None

    def has_building(self, building_type: BuildingType):
        if self.building is not None:
            if self.building.building_type == building_type:
                return True
        return False

    def get_building(self):
        return self.building

    def get_building_value(self):
        if self.building is not None:
            return self.building.get_building_type_id()
        return 0

    def has_any_building(self):
        if self.building is not None:
            return True
        return False

    # drawing stuff #
    def draw(
        self, screen, square_size: int, new_x: int, new_y: int, new_square_size: int
    ):
        """
        Draw the square on the screen
        :param screen:
        :param square_size:
        :param new_x:
        :param new_y:
        :param new_square_size:
        :return:
        """

        pygame.draw.rect(
            screen,
            self.land_type_color,
            (
                self.position.x * square_size,
                self.position.y * square_size,
                square_size,
                square_size,
            ),
        )
        grain_color = (255, 255, 0)
        metal_color = (192, 192, 192)
        if self.resource != ResourceType.NONE:
            if self.resource == ResourceType.GRAIN:
                resource_color = grain_color

            elif self.resource == ResourceType.METAL:
                resource_color = metal_color

            pygame.draw.line(
                screen,
                resource_color,
                (
                    self.position.x * square_size + square_size * 0.3,
                    self.position.y * square_size + square_size,
                ),
                (
                    self.position.x * square_size + square_size * 0.3,
                    self.position.y * square_size + square_size / 2,
                ),
            )

            pygame.draw.line(
                screen,
                resource_color,
                (
                    self.position.x * square_size + square_size * 0.6,
                    self.position.y * square_size,
                ),
                (
                    self.position.x * square_size + square_size * 0.6,
                    self.position.y * square_size + square_size / 2,
                ),
            )

        if self.owner_color != COLOR_DEFAULT_BORDER:
            pygame.draw.rect(
                screen,
                self.owner_color,
                (
                    self.position.x * square_size,
                    self.position.y * square_size,
                    square_size,
                    square_size,
                ),
                1,
            )

        if self.building is not None:
            self.building.draw(screen, square_size, self.owner_color)

    # observation stuff #
    def get_full_info(self):
        # these are the features the agent can observe
        state = [self.land_type.value, self.owner_id, self.get_building_value()]
        return state

    def get_observation_state(self):
        return self.get_full_info()

    def get_tile_income(self):
        return self.tile_income

    def get_road_or_bridge(self):
        if (
            self.building.building_type == BuildingType.ROAD
            or self.building.building_type == BuildingType.BRIDGE
        ):
            return self.building

    def get_unit_strength(self):
        if self.unit is not None:
            return self.unit.strength
        return 0

    def has_road(self):
        if self.has_building(BuildingType.ROAD):
            return True
        return False

    def has_bridge(self):
        if self.has_building(BuildingType.BRIDGE):
            return True
        return False
