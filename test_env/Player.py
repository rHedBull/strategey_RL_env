import numpy as np
import pygame


class Player:

    def __init__(self, ):
        self.env = None
        self.action = None
        self.state = 'Running'

    def get_action(self, game):

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
            action = 0 #'Move Up'
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            action = 1#'Move Down'
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            action = 2#'Move Left'
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            action = 3 #'Move Right'
        elif keys[pygame.K_c]:
            action = 4 #'Claim'
            action_properties = action_properties = [np.random.randint(0, 10), np.random.randint(0, 10)] # TODO change this to map bounds

        return action, action_properties

    def step(self):
        self.env.step(self.action)
