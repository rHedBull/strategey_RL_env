import numpy as np
import pygame

from map.map_settings import PLAYER_COLOR


class Player:
    def __init__(
        self,
    ):
        self.env = None
        self.action = None
        self.state = "Running"
        self.reward = 0
        self.color = PLAYER_COLOR

    def get_action(self, game, env):
        # action dictionary mask
        selected_action = {
            "move": {"direction": None, "new_position": None},
            "claim": None,  # position goes here
        }

        # wait for event
        keys = None
        waiting_for_event = True
        while waiting_for_event:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    waiting_for_event = False
                    keys = game.key.get_pressed()

        action = -1
        action_properties = -1

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            action = 1
            selected_action["move"]["direction"] = 1  # 'Move Up'
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            action = 1
            selected_action["move"]["direction"] = 2  # 'Move down'
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            action = 1
            selected_action["move"]["direction"] = 3  # 'Move Left'
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            action = 1
            selected_action["move"]["direction"] = 4  # 'Move Right'
        elif keys[pygame.K_c]:
            x_max = env.map.max_x_index
            y_max = env.map.max_y_index
            position = [np.random.randint(0, x_max), np.random.randint(0, y_max)]
            selected_action["claim"] = position

        elif keys[pygame.K_b]:
            action = 3  # build sthb
            x_max = env.map.max_x_index
            y_max = env.map.max_y_index
            action_properties = [
                np.random.randint(0, x_max),
                np.random.randint(0, y_max),
                1,
            ]  # TODO to make this editable

        return selected_action

    def update(self, reward):
        self.reward += reward
