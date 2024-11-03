import pygame

from map.map_settings import PLAYER_COLOR
from test_env.Agent import Agent


class Player(Agent):
    def __init__(self, id, x_max, y_max):
        super().__init__(id, x_max, y_max)

        self.color = PLAYER_COLOR

    def get_action(self, game):
        # action dictionary mask
        selected_action = []

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

        if (
            keys[pygame.K_w]
            or keys[pygame.K_UP]
            or keys[pygame.K_s]
            or keys[pygame.K_DOWN]
            or keys[pygame.K_a]
            or keys[pygame.K_LEFT]
            or keys[pygame.K_d]
            or keys[pygame.K_RIGHT]
        ):
            # map the key to the direction
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dir = 1
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dir = 2
            elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dir = 3
            else:
                dir = 4

            move_action = {"type": "move", "props": {"direction": dir}}
            selected_action.append(move_action)
        # elif keys[pygame.K_c]:
        #     position = [
        #         np.random.randint(0, self.x_max),
        #         np.random.randint(0, self.y_max),
        #     ]
        #     claim_action = {
        #         "type":"claim",
        #         "props": {"position": position}
        #     }
        #     selected_action.append(claim_action)

        return selected_action

    def update(self, reward):
        self.reward += reward
