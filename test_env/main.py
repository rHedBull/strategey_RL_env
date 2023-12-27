from RL_env.MapEnvironment import MapEnvironment
from test_env.Player import Player

import pygame

Rendering = True
screen_size = 1000


def main():
    screen = None

    game = pygame.init()

    if Rendering:
        # init pygame
        screen = pygame.display.set_mode((screen_size, screen_size))
        pygame.display.set_caption('Agent-based Landmass Generation')
        screen.fill((0, 0, 0))

    env = MapEnvironment("./test_env/env_settings.json", 1, Rendering, screen)

    if Rendering:
        env.render()
        pygame.display.flip()

    # setup my agents
    agents = [Player()]

    # run the game loop
    done = False
    while not done:

        # get actions from agents
        agent_actions = []
        for agent in agents:
            action = agent.get_action(pygame)
            agent_actions.append(action)
            print(action)

        state, reward, dones, info = env.step(agent_actions)
        env.render()
        # flip the display
        pygame.display.flip()

if __name__ == "__main__":
    main()

# TODO write random stepping agent(s) to test environment
# TODO better rendering structure and event handling
