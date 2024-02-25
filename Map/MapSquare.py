import pygame
from Map.MapSettings import *


class Map_Square:
    """
    Class for a single square/ tile on the map
    """

    def __init__(self, x, y, square_size, land_value=VALUE_DEFAULT_LAND):
        self.x = x
        self.y = y
        self.square_size = square_size

        self.default_border_color = COLOR_DEFAULT_BORDER
        self.default_color = COLOR_DEFAULT_LAND
        self.fill_color = COLOR_DEFAULT_LAND
        self.border_color = COLOR_DEFAULT_BORDER

        self.land_type = land_value
        self.owner_value = OWNER_DEFAULT_TILE

    def reset(self):
        self.owner_value = OWNER_DEFAULT_TILE
        self.land_type = VALUE_DEFAULT_LAND
        self.fill_color = COLOR_DEFAULT_LAND
        self.border_color = COLOR_DEFAULT_BORDER

    def set_owner(self, owner_value):
        """
        Set the owner of the square
        :param owner_value: the id of the owner agent
        """
        self.owner_value = owner_value

    def get_owner(self):
        return self.owner_value

    def set_land_type(self, land_value):
        """
        Set the land type of the square
        :param land_value:
        :return:
        """
        if land_value != self.land_type:
            self.land_type = land_value
            self.fill_color = LAND[self.land_type][2]

    def get_land_type(self):
        return self.land_type

    def get_round_value(self):
        return LAND[self.land_type][1]

    def claim(self, agent):
        """
        Claim the square for an agent
        :param agent:
        :return:
        """
        self.owner_value = agent.id
        self.border_color = agent.color

    def draw(self, screen, new_x, new_y, new_square_size):
        """
        Draw the square on the screen
        :param screen:
        :param new_x:
        :param new_y:
        :param new_square_size:
        :return:
        """
        pygame.draw.rect(screen, self.fill_color,
                         (self.x * self.square_size, self.y * self.square_size, self.square_size, self.square_size))

        if self.border_color != COLOR_DEFAULT_BORDER:
            pygame.draw.rect(screen, self.border_color,
                             (self.x * self.square_size, self.y * self.square_size, self.square_size, self.square_size),
                             1)
