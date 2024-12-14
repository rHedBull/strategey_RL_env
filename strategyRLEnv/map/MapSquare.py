from typing import Tuple

import pygame

from strategyRLEnv.map.map_settings import (COLOR_DEFAULT_BORDER, OWNER_DEFAULT_TILE,
                                            LandType, land_type_color)
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.objects.Building import Building, BuildingType

# TODO: zooming, moving?


def calculate_whitaker_biome(precipitation, temperature):
    if temperature <= 0:
        return 0  # Tundra
    elif temperature < 0:
        if precipitation < 25:
            return 6  # cold dessert
        elif precipitation < 50:
            return 5  # woodlands
        else:
            return 1  # boreal forest
    elif temperature < 20:
        if precipitation < 25:
            return 6  # cold dessert
        elif precipitation < 100:
            return 5  # woodlands
        elif precipitation < 200:
            return 4  # temperate forest
        else:
            return 2  # temperate rainforest
    else:
        if precipitation < 75:
            return 7  # subtropical desert
        elif precipitation < 225:
            return 8  # tropical forest
        else:
            return 3  # tropical rainforest


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
        self.height = 0  # height as indicator for water, or ocean tiles
        self.precepitation = 0  # for biomes
        self.temperature = 0  # for biomes
        self.biome = 0  # for biomes
        self.resources = []
        # self.land_type = self.calculate_land_money_value()

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

    def set_height(self, height_value):
        self.height = height_value

    def get_height(self):
        return self.height

    def set_biome(self, biome_value):
        self.biome = biome_value

    def get_biome(self):
        return self.biome

    def add_resource(self, resource_value):
        self.resources.append(resource_value)

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
        self.building_int |= building.building_type_id

    def has_building(self, building_type: BuildingType):
        if building_type == BuildingType.CITY:
            building_id = 1  # 2^0
        elif building_type == BuildingType.ROAD:
            building_id = 2  # 2^1
        elif building_type == BuildingType.BRIDGE:
            building_id = 4  # 2^2
        elif building_type == BuildingType.FARM:
            building_id = 8  # 2^3
        else:
            building_id = 0  # Undefined building type

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
            self.building_int &= ~building.get_building_type_id()

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
        state = [
            # self.height,
            # self.biome,
            # self.resources,
            self.land_type.value,
            self.owner_id,
            self.building_int
            # self.land_money_value,
        ]
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
