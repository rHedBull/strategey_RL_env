import pygame
default_land_color = (34, 139, 34)
default_water_color = (0, 255, 255)
default_border_color = (255, 255, 255)

default_land_value = 0
default_water_value = 1

default_tile_owner = 0

class MapSquare:
    def __init__(self, x, y, land_value=default_land_value):
        self.x = x
        self.y = y
        self.square_size = 10

        self.default_border_color = default_border_color
        self.default_color = default_land_color
        self.fill_color = default_land_color
        self.border_color = default_border_color

        self.land_value = land_value
        self.owner_value = default_tile_owner

    def set_owner(self, owner_value):
        self.owner_value = owner_value

    def get_owner(self):
        return self.owner_value

    def set_land_value(self, land_value):
        self.land_value = land_value
        if self.land_value == default_land_value:
            self.fill_color = default_land_color
        else:
            self.fill_color = default_water_color


    def get_land_value(self):
        return self.land_value

    def draw(self, screen):
        pygame.draw.rect(screen, self.fill_color, (self.x, self.y, self.square_size, self.square_size))

    def draw_border(self, screen):
        # draw square border
        color = self.default_border_color
        if self.get_owner() == default_tile_owner:
            color = default_border_color
        else:
            color = default_water_color
        pygame.draw.rect(screen, color, (self.x, self.y, self.square_size, self.square_size), 1)
