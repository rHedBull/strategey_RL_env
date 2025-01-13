import random
from typing import Tuple

import pygame

from strategyRLEnv.map import MapPosition
from strategyRLEnv.map.map_settings import max_unit_strength
from strategyRLEnv.objects.Destroyable import Destroyable
from strategyRLEnv.objects.Ownable import Ownable


class Unit(Ownable):
    def __init__(self, agent, position: MapPosition):
        Ownable.__init__(self, agent)
        self.position = position
        self.strength = 50  # minimum start strength
        self.opponent_targets = []  # list of neighbouring opponents

    def update(self, env):
        # check for other units around and adapt placement

        self.opponent_targets = []
        surounding_tiles = env.map.get_surrounding_tiles(
            self.position, 1, diagonal=True
        )

        for tile in surounding_tiles:
            if tile.unit is not None:
                unit = tile.unit
                if unit.owner.id != self.owner.id:
                    self.opponent_targets.append(unit)
            elif tile.building is not None:
                if isinstance(tile.building, Ownable):
                    if tile.building.owner.id != self.owner.id:
                        self.opponent_targets.append(tile.building)

    def step(self, env):
        self.update(env)
        self.attack_random(env)

    def attack_random(self, env):
        if len(self.opponent_targets) < 1:
            return False
        attacked_target = random.choice(self.opponent_targets)

        # calculate the damage
        dmg_multiplier_self = 0.3
        dmg_multiplier_opponent = 0.7
        minimum_damage = 5

        if isinstance(attacked_target, Unit):
            # normal attack
            diff = self.strength - attacked_target.strength
            damage_self = max(minimum_damage, int(dmg_multiplier_self * diff))
            damage_opponent = max(minimum_damage, int(dmg_multiplier_opponent * diff))
            self.reduce_strength(env, damage_self)
            attacked_target.reduce_strength(env, damage_opponent)

            return True

        if isinstance(attacked_target, Destroyable):  # means this is a building
            # attack building
            building_damage = 20  # fix for now
            attacked_target.reduce_health(env, building_damage)

    def reduce_strength(self, env, damage):
        self.strength -= damage
        if self.strength <= 0:
            self.kill(env)
        else:
            env.map.unit_strength_map[self.position.x][self.position.y] = self.strength

    def increase_strength(self, env, amount):
        new_strength = self.strength + amount
        self.strength = min(max_unit_strength, new_strength)
        env.map.unit_strength_map[self.position.x][self.position.y] = self.strength

    def kill(self, env):
        tile = env.map.get_tile(self.position)
        env.map.remove_unit(self.position)

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
        rectangle_size = square_size / 3
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
