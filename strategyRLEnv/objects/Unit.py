import random
from enum import Enum, auto
from typing import Tuple

import pygame

from strategyRLEnv.map import MapPosition
from strategyRLEnv.map.map_settings import BuildingType
from strategyRLEnv.objects.Building import Building
from strategyRLEnv.objects.Ownable import Ownable


class UnitPlacement(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    BASE = auto()


class Unit(Ownable):
    def __init__(self, agent, position: MapPosition):
        Ownable.__init__(self, agent.id)
        self.position = position
        self.strength = 100  # minimum start strength
        self.shape = UnitPlacement.BASE
        self.owner = agent
        # list with up, down, left, right to keep track of opponent units
        self.opponent_units = []  # list of neighbouring opponents

    def update(self, env):
        # check for other units around and adapt placement

        self.attack_random(env)
        surounding_tiles = env.map.get_surrounding_tiles(
            self.position, 1, diagonal=False
        )
        opponent_count = 0
        for tile in surounding_tiles:
            if tile.unit is not None:
                unit = tile.unit
                if unit.owner.id != self.owner.id:
                    self.opponent_units.append(unit)
                    # check if the unit is above or below
                    if unit.position.y < self.position.y:
                        self.shape = UnitPlacement.UP
                    if unit.position.y > self.position.y:
                        self.shape = UnitPlacement.DOWN
                    if unit.position.x < self.position.x:
                        self.shape = UnitPlacement.LEFT
                    if unit.position.x > self.position.x:
                        self.shape = UnitPlacement.RIGHT

        if len(self.opponent_units) > 1 or len(self.opponent_units) == 0:
            self.shape = UnitPlacement.BASE

    def attack_random(self, env):
        # pick any random oppponent if True
        if len(self.opponent_units) < 1:
            return
        attacked_opponent = random.choice(self.opponent_units)

        # calculate the damage
        if self.strength / 3 > attacked_opponent.strength:
            # immediate win
            attacked_opponent.strength = 0
        elif self.strength > attacked_opponent.strength:
            # normal attack
            diff = self.strength - attacked_opponent.strength
            damage = max(25, int(diff / 2))
            attacked_opponent.strength -= damage

        if attacked_opponent.strength <= 0:
            attacked_opponent.kill(env)

    def kill(self, env):
        tile = env.map.get_tile(self.position)
        tile.unit = None  # forget this unit
        self.owner.units.remove(self)
        tile.update(env)
        env.map.trigger_surrounding_tile_update(self.position)

    def draw(
        self,
        screen: pygame.Surface,
        square_size: int,
        owner_color: Tuple[int, int, int],
    ):
        scalar_value = 0.5

        # Calculate the maximum size for the rectangle
        max_size = square_size / 2

        # Calculate the size of the rectangle
        rectangle_size = max_size * scalar_value

        # Initialize rectangle position variables
        rect_x = 0
        rect_y = 0
        rect_width = 0
        rect_height = 0

        # Determine the position based on the side
        if self.shape == UnitPlacement.BASE:
            rect_x = self.position.x * square_size + square_size / 4
            rect_y = self.position.y * square_size + square_size / 4
            rect_width = square_size / 2
            rect_height = square_size / 2
        elif self.shape == UnitPlacement.LEFT:
            rect_x = self.position.x * square_size - rectangle_size
            rect_y = self.position.y * square_size
            rect_width = rectangle_size
            rect_height = square_size
        elif self.shape == UnitPlacement.RIGHT:
            rect_x = self.position.x * square_size + square_size
            rect_y = self.position.y * square_size
            rect_width = rectangle_size
            rect_height = square_size
        elif self.shape == UnitPlacement.UP:
            rect_x = self.position.x * square_size
            rect_y = self.position.y * square_size - rectangle_size
            rect_width = square_size
            rect_height = rectangle_size
        elif self.shape == UnitPlacement.DOWN:
            rect_x = self.position.x * square_size
            rect_y = self.position.y * square_size + square_size
            rect_width = square_size
            rect_height = rectangle_size

        # Draw the rectangle
        pygame.draw.rect(screen, owner_color, (rect_x, rect_y, rect_width, rect_height))
