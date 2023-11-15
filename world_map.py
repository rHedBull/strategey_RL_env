import pygame
from nation import Nation

class WorldMap:
    def __init__(self, numb_areas):
        # for now map of squares
        # only map data no visualization
        # static map for now
        self.areas_numb = numb_areas
        self.areas = []

        for i in range(self.areas_numb):
            self.areas.append(i)




