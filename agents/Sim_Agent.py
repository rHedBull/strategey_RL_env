import random
import pygame

from Map.MapSettings import AGENT_COLORS
from RL_env.Settings import Settings


class Agent:
    def __init__(self, id):
        self.initial_budget = None
        self.budget = None
        self.max_x = None
        self.max_y = None
        self.y = None
        self.x = None
        self.state = None
        self.id = id
        self.color = AGENT_COLORS[id % len(AGENT_COLORS)]

    def create_agent(self, settings, max_x, max_y):
        self.initial_budget = settings.get_setting('agent_budget')

        if self.initial_budget is None:
            raise Exception('Agent budget not set in settings file')

        self.max_x = max_x
        self.max_y = max_y
        self.reset()

    def reset(self):

        self.x = random.randint(0, self.max_x - 1)
        self.y = random.randint(0, self.max_y - 1)
        self.budget = self.initial_budget
        self.state = 'Running'

    def update(self):
        # Update the agent's state

        if self.budget <= 0:
            self.state = 'Done'

    def get_state(self):
        return self.state

    def draw(self, screen, square_size, zoom_level, pan_x, pan_y):
        radius = square_size / 2
        # get a color modulo the number of colors

        pygame.draw.circle(screen, self.color,
                           ((self.x * square_size) + radius, (self.y * square_size) + radius),
                           radius)

    def get_possible_actions(self):

        if self.state == 'Done':
            possible_actions = []
        else:
            possible_actions = ['Left', 'Right', 'Up', 'Down', 'Claim']

        return possible_actions
