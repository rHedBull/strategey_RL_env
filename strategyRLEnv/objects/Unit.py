import random
from enum import Enum, auto
from typing import Tuple

import pygame

from strategyRLEnv.map import MapPosition
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
        self.strength = 50  # minimum start strength
        self.shape = UnitPlacement.BASE
        self.owner = agent
        # list with up, down, left, right to keep track of opponent units
        self.opponent_units = []  # list of neighbouring opponents

    def update(self, env):
        # check for other units around and adapt placement

        surounding_tiles = env.map.get_surrounding_tiles(
            self.position, 1, diagonal=True
        )

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

        self.attack_random(env)

    def attack_random(self, env):
        if len(self.opponent_units) < 1:
            return False
        attacked_opponent = random.choice(self.opponent_units)

        # calculate the damage
        dmg_multiplier_self = 0.3
        dmg_multiplier_opponent = 0.7
        minimum_damage = 5

        # normal attack
        diff = self.strength - attacked_opponent.strength
        damage_self = max(minimum_damage, int(dmg_multiplier_self * diff))
        damage_opponent = max(minimum_damage, int(dmg_multiplier_opponent * diff))
        self.strength -= damage_self
        attacked_opponent.strength -= damage_opponent

        if self.strength <= 0:
            self.kill(env)

        if attacked_opponent.strength <= 0:
            attacked_opponent.kill(env)
        return True

    def kill(self, env):
        tile = env.map.get_tile(self.position)
        tile.unit = None  # forget this unit
        self.owner.remove_unit(self)
        tile.update(env)
        env.map.trigger_surrounding_tile_update(self.position)

    def draw(
        self,
        screen: pygame.Surface,
        square_size: int,
        owner_color: Tuple[int, int, int],
    ):

        # Calculate the size of the diamond
        rectangle_size = square_size/3
        x_offset = square_size * self.position.x
        y_offset = square_size * self.position.y

        center_x = x_offset + (square_size / 2)
        center_y = y_offset + (square_size / 2)

        # Define the vertices of the diamond
        top = (center_x, center_y - rectangle_size)
        right = (center_x + rectangle_size, center_y)
        bottom = (center_x, center_y + rectangle_size)
        left = (center_x - rectangle_size, center_y)
        vertices = [top, right, bottom, left]

        pygame.draw.polygon(screen, owner_color, vertices)
