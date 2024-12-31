from typing import Tuple

import pygame

from strategyRLEnv.map.map_settings import (COLOR_DEFAULT_BORDER,
                                            OWNER_DEFAULT_TILE, LandType,
                                            ResourceType, land_type_color)
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.objects.Building import Building, BuildingType


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

        # building stuff
        self.buildings = set()
        self.building_int = 0  # a bit mask to easily check for buildings present here

        self._land_money_value = 1

        # ui stuff
        self.default_border_color = COLOR_DEFAULT_BORDER
        self.default_color = land_type_color(LandType.LAND)

        self.land_type_color = land_type_color(LandType.LAND)
        self.owner_color = COLOR_DEFAULT_BORDER

    def reset(self):
        self.owner_id = OWNER_DEFAULT_TILE

        self.visibility_bitmask = 0

        self.owner_color = COLOR_DEFAULT_BORDER

        self._land_money_value = 1

        self.buildings.clear()
        self.building_int = 0

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

    def get_round_value(self):
        # in theory add other dynamic effects here
        income = self._land_money_value
        for building in self.buildings:
            income += building.get_income()

        return income

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
        self.buildings.add(building)
        building_id = building.get_building_type_id()
        bit_mask = 2 ** (building_id - 1)
        self.building_int |= bit_mask

    def has_building(self, building_type: BuildingType):
        if building_type == BuildingType.CITY:
            building_id = 1  # 2^0
        elif building_type == BuildingType.ROAD:
            building_id = 2  # 2^1
        elif building_type == BuildingType.BRIDGE:
            building_id = 3  # 2^2
        elif building_type == BuildingType.FARM:
            building_id = 4  # 2^3
        elif building_type == BuildingType.MINE:
            building_id = 5
        else:
            building_id = 0  # Undefined building type

        # convert to 2 potenz
        building_id = int(2 ** (building_id - 1))

        # Perform bitwise AND to check if the building is present
        return (self.building_int & building_id) != 0

    def get_building(self, building_type: BuildingType):
        for building in self.buildings:
            if building.building_type == building_type:
                return building

    def has_any_building(self):
        if self.building_int > 0:
            return True
        return False

    def remove_building(self, building: Building):
        """
        Remove a building from the square.
        """
        if building in self.buildings:
            self.buildings.remove(building)
            building_id = building.get_building_type_id()
            bit_mask = 2 ** (building_id - 1)
            self.building_int &= ~bit_mask

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

        for building in self.buildings:
            building.draw(screen, square_size, self.owner_color)

    # observation stuff #
    def get_full_info(self):
        # these are the features the agent can observe
        state = [self.land_type.value, self.owner_id, self.building_int]
        return state

    def get_observation_state(self):
        return self.get_full_info()

    def get_land_money_value(self):
        return self._land_money_value

    def calculate_land_money_value(self):
        """
        Calculate the value of the land
        :return:
        """
        # base_value = self.land_type
        return 10
        # for (building) in self.buildings:
        #    base_value += self.buildings[building][2]
        #    # TODO test this

    def get_road_or_bridge(self):
        for building in self.buildings:
            if (
                building.building_type == BuildingType.ROAD
                or building.building_type == BuildingType.BRIDGE
            ):
                return building

    def has_road(self):
        if self.has_building(BuildingType.ROAD):
            return True
        return False

    def has_bridge(self):
        if self.has_building(BuildingType.BRIDGE):
            return True
        return False
