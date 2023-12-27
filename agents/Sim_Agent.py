import math
import random

import pygame

from Map.MapSettings import AGENT_COLORS
from RL_env.Settings import Settings


class Agent:
    def __init__(self, id, settings):
        self.budget = None
        self.y = None
        self.x = None
        self.state = None
        self.id = id
        self.reset(settings)

    def reset(self, settings):

        self.x = random.randint(0, settings.get_setting('map_width') - 1)
        self.y = random.randint(0, settings.get_setting('map_height') - 1)
        self.budget = settings.get_setting('water_budget')
        self.state = 'Running'

    def update(self):
        # Update the agent's state
        self.budget -= 1
        if self.budget <= 0:
            self.state = 'Done'

    def get_state(self):
        return self.state

    def draw(self, screen, square_size, zoom_level, pan_x, pan_y):
        radius = square_size / 2
        pygame.draw.circle(screen, AGENT_COLORS[self.id],
                           ((self.x * square_size) + radius, (self.y * square_size) + radius),
                           radius)

    def get_possible_actions(self):

        if self.state == 'Done':
            possible_actions = []
        else:
            possible_actions = ['Left', 'Right', 'Up', 'Down', 'Claim']

        return possible_actions
