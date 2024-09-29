import random
import pygame

from map.MapSettings import AGENT_COLORS, PLAYER_COLOR


class Agent:
    def __init__(self, id, game_mode):
        self.id = id
        self.max_x = None
        self.max_y = None
        self.y = None
        self.x = None

        self.state = None

        # resources
        self.money = None
        self.claimed_tiles = []

        if game_mode == 'player' and id == 0:
            self.color = PLAYER_COLOR
        elif game_mode == 'player':
            # exclude player color id 0
            c = self.id
            if self.id % len(AGENT_COLORS) == 0:
                c = 1
            self.color = AGENT_COLORS[c % len(AGENT_COLORS)]
        else:
            self.color = AGENT_COLORS[id % len(AGENT_COLORS)]

    def create_agent(self, settings, max_x, max_y):

        self.max_x = max_x
        self.max_y = max_y
        self.reset(settings)

    def reset(self, settings):

        self.x = random.randint(0, self.max_x - 1)
        self.y = random.randint(0, self.max_y - 1)

        self.state = 'Running'
        # TODO maybe set intial possition as claimed tile

        initial_money = settings.get_setting('agent_initial_budget')
        if settings.get_setting('agent_initial_budget') == 'equal':
            self.money = initial_money
        elif settings.get_setting('agent_initial_budget') == 'gauss':
            # gauss distributed around initial
            self.money = random.gauss(initial_money, 100)
        else:
            # randomly distributed money
            self.money = random.randint(0, 1000)

    def update(self):
        # Update the agent's state

        for i, tile in enumerate(self.claimed_tiles):
            self.money += tile.get_round_value()

        # TODO define settings matrix?

        if self.money <= 0:  # TODO adapt different state transitions
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
            possible_actions = [1,2,3] # ['move', 'claim_tile', 'build']

        return possible_actions

    def get_state_for_env_info(self):

        # define here what information of all agents is visible to all other agents

        return [self.x, self.y, self.money]
