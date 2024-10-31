from typing import Tuple

import pygame

from map.map_settings import (COLOR_DEFAULT_BORDER, COLOR_DEFAULT_LAND, LAND,
                              OWNER_DEFAULT_TILE, VALUE_DEFAULT_LAND)
from rl_env.objects.Building import Building

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

    def __init__(self, id, x, y, square_size, land_value=VALUE_DEFAULT_LAND):
        # coordinates and ids
        self.tile_id = id
        self.x = x
        self.y = y

        # land properties
        self.land_type = VALUE_DEFAULT_LAND
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

        # building stuff
        self.buildings = set()

        self.land_money_value = land_value

        # ui stuff
        self.square_size = square_size
        self.default_border_color = COLOR_DEFAULT_BORDER
        self.default_color = COLOR_DEFAULT_LAND

        self.land_type_color = COLOR_DEFAULT_LAND
        self.owner_color = COLOR_DEFAULT_BORDER

    def reset(self):
        self.owner_id = OWNER_DEFAULT_TILE
        self.land_type = VALUE_DEFAULT_LAND
        self.land_type_color = COLOR_DEFAULT_LAND
        self.owner_color = COLOR_DEFAULT_BORDER

        self.buildings.clear()

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

    def set_land_type(self, land_value):
        """
        Set the land type of the square
        :param land_value:
        :return:
        """
        if land_value != self.land_type:
            self.land_type = land_value
            self.land_type_color = LAND[self.land_type][2]

    def get_land_type(self):
        return self.land_type

    def get_round_value(self):
        return self.land_money_value

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

    def remove_building(self, building: Building):
        """
        Remove a building from the square.
        """
        if building in self.buildings:
            self.buildings.remove(building)

    # drawing stuff #
    def draw(self, screen, new_x, new_y, new_square_size):
        """
        Draw the square on the screen
        :param screen:
        :param new_x:
        :param new_y:
        :param new_square_size:
        :return:
        """

        pygame.draw.rect(
            screen,
            self.land_type_color,
            (
                self.x * self.square_size,
                self.y * self.square_size,
                self.square_size,
                self.square_size,
            ),
        )

        if self.owner_color != COLOR_DEFAULT_BORDER:
            pygame.draw.rect(
                screen,
                self.owner_color,
                (
                    self.x * self.square_size,
                    self.y * self.square_size,
                    self.square_size,
                    self.square_size,
                ),
                1,
            )

        for building in self.buildings:
            building.draw(screen, self.square_size, self.owner_color)

    # observation stuff #
    def get_full_info(self):
        state = [
            self.height,
            self.biome,
            # self.resources,
            self.land_type,
            self.owner_id,
            self.land_money_value,
        ]
        return state

    def get_observation_state(self):
        return self.get_full_info()

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
