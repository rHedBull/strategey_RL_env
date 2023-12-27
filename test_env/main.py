from RL_env.MapEnvironment import MapEnvironment
from test_env.Player import Player

import pygame

Rendering = True
screen_size = 1000

max_steps = 5

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
    step = 0
    while not done and step < max_steps:

        # get actions from agents
        agent_actions = []
        for agent in agents:
            action = agent.get_action(pygame)
            agent_actions.append(action)
            print(action)

        state, reward, dones, info = env.step(agent_actions)

        for i in range(len(dones)):
            if dones[i]:
                print("Agent {} is done".format(i))
                # remove agent from list
                agents.pop(i)

        env.render()
        # flip the display
        pygame.display.flip()

        # check if the game is over
        if len(agents) == 0:
            done = True
            print("All agents are done")
        step += 1

    print("Game Terminated")
    if Rendering:
        # keep the window open until the user closes it manually
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        pygame.quit()

if __name__ == "__main__":
    main()

# TODO write random stepping agent(s) to test environment
