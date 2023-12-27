import pygame
from Map.MapSettings import *


class Map_Square:
    def __init__(self, x, y, square_size, land_value=VALUE_DEFAULT_LAND):
        self.x = x
        self.y = y
        self.square_size = square_size

        self.default_border_color = COLOR_DEFAULT_BORDER
        self.default_color = COLOR_DEFAULT_LAND
        self.fill_color = COLOR_DEFAULT_LAND
        self.border_color = COLOR_DEFAULT_BORDER

        self.land_value = land_value
        self.owner_value = OWNER_DEFAULT_TILE

    def reset(self):
        self.owner_value = OWNER_DEFAULT_TILE
        self.land_value = VALUE_DEFAULT_LAND
        self.fill_color = COLOR_DEFAULT_LAND
        self.border_color = COLOR_DEFAULT_BORDER

    def set_owner(self, owner_value):
        self.owner_value = owner_value

    def get_owner(self):
        return self.owner_value

    def set_land_value(self, land_value):
        self.land_value = land_value
        if self.land_value == VALUE_DEFAULT_LAND:
            self.fill_color = COLOR_DEFAULT_LAND
        else:
            self.fill_color = COLOR_DEFAULT_WATER

    def get_land_value(self):
        return self.land_value

    def claim(self, agent):
        self.owner_value = agent.id
        self.border_color = agent.color

    def draw(self, screen, new_x, new_y, new_square_size):
        pygame.draw.rect(screen, self.fill_color,
                         (self.x * self.square_size, self.y * self.square_size, self.square_size, self.square_size))

        if self.border_color != COLOR_DEFAULT_BORDER:
            pygame.draw.rect(screen, self.border_color,
                             (self.x * self.square_size, self.y * self.square_size, self.square_size, self.square_size),
                             1)
