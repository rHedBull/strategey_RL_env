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

        action = None
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            action = 'Move Up'
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            action = 'Move Down'
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            action = 'Move Left'
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            action = 'Move Right'
        elif keys[pygame.K_c]:
            action = 'Claim'

        self.action = action
        return self.action

    def step(self):
        self.env.step(self.action)
